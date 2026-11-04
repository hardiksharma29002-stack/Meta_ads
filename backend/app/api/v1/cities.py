"""City Reference & Intelligent Alias Resolution Endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
try:
    from rapidfuzz import fuzz
except ImportError:
    from difflib import SequenceMatcher

    class _FuzzFallback:
        @staticmethod
        def ratio(s1: str, s2: str) -> float:
            return SequenceMatcher(None, str(s1).lower(), str(s2).lower()).ratio() * 100

        @staticmethod
        def token_sort_ratio(s1: str, s2: str) -> float:
            t1 = " ".join(sorted(str(s1).lower().split()))
            t2 = " ".join(sorted(str(s2).lower().split()))
            return SequenceMatcher(None, t1, t2).ratio() * 100

    fuzz = _FuzzFallback()
from app.db.session import get_db
from app.db.models import City, CityAlias
from app.core.errors import NotFoundError

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get("")
async def list_cities(db: AsyncSession = Depends(get_db)):
    """List active target cities with area codes and data freshness."""
    stmt = select(City).where(City.is_active == True)
    cities = (await db.execute(stmt)).scalars().all()
    return {
        "items": [
            {
                "id": c.id,
                "slug": c.slug,
                "name": c.name,
                "state_name": c.state_name,
                "gst_state_code": c.gst_state_code,
                "std_code": c.std_code,
                "urban_population": c.urban_population,
                "is_active": c.is_active,
            }
            for c in cities
        ]
    }


@router.get("/resolve")
async def resolve_city_alias(
    q: str = Query(..., description="Query text: alias, colonial name, typo, or Indic script"),
    db: AsyncSession = Depends(get_db),
):
    """Resolve user input to canonical city slug using alias reference and fuzzy matching (SRCH-01)."""
    clean_q = q.strip().lower()

    # 1. Exact slug or city name match
    stmt = select(City).where((City.slug == clean_q) | (City.name.ilike(clean_q)))
    city = (await db.execute(stmt)).scalar_one_or_none()
    if city:
        return {
            "resolved": True,
            "city_id": city.id,
            "slug": city.slug,
            "name": city.name,
            "matched_by": "exact_name",
        }

    # 2. Match against city_aliases table
    alias_stmt = select(CityAlias, City).join(City, CityAlias.city_id == City.id)
    records = (await db.execute(alias_stmt)).all()

    best_match = None
    highest_score = 0.0

    for alias_obj, city_obj in records:
        alias_str = alias_obj.alias.lower()
        if clean_q == alias_str:
            return {
                "resolved": True,
                "city_id": city_obj.id,
                "slug": city_obj.slug,
                "name": city_obj.name,
                "matched_by": "alias_exact",
                "kind": alias_obj.kind,
            }

        # Fuzzy string comparison (trigram / token sort)
        sim = fuzz.token_sort_ratio(clean_q, alias_str)
        if sim > highest_score:
            highest_score = sim
            best_match = (alias_obj, city_obj)

    # Typo tolerance threshold (>= 75% similarity)
    if best_match and highest_score >= 75.0:
        alias_obj, city_obj = best_match
        return {
            "resolved": True,
            "city_id": city_obj.id,
            "slug": city_obj.slug,
            "name": city_obj.name,
            "matched_by": "fuzzy_trigram",
            "similarity": round(highest_score, 1),
            "did_you_mean": alias_obj.alias,
        }

    raise NotFoundError("City", q)
