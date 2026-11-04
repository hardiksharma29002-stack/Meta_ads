"""Advertiser Search & Discovery API Endpoint.

Implements Section 9 and Section 10:
Keyset pagination, category/scope/contact filters, contact masking by default.
"""

from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Advertiser, AdvertiserCityLink, City, Contact, Category
from app.core.errors import NotFoundError

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def search_advertisers(
    city: str = Query(..., description="City slug or alias"),
    q: str | None = Query(None, description="Optional keyword query"),
    category: str | None = Query(None, description="Category slug"),
    tier: str = Query("confirmed,probable", description="Comma-separated tiers"),
    scope: str = Query("local,regional", description="Geographic operational scopes"),
    has_phone: bool | None = Query(None, description="Require verified phone"),
    has_email: bool | None = Query(None, description="Require verified email"),
    has_whatsapp: bool | None = Query(None, description="Require WhatsApp presence"),
    active_ads_min: int = Query(1, ge=0, description="Minimum active ads"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    cursor: int | None = Query(None, description="Keyset offset/ID cursor"),
    db: AsyncSession = Depends(get_db),
):
    """Search attributed advertisers with masked contact indicators."""
    # Resolve city
    stmt = select(City).where(City.slug == city.lower())
    city_obj = (await db.execute(stmt)).scalar_one_or_none()
    if not city_obj:
        raise NotFoundError("City", city)

    tier_list = [t.strip() for t in tier.split(",")]
    scope_list = [s.strip() for s in scope.split(",")]

    # Build keyset query
    query = (
        select(Advertiser, AdvertiserCityLink)
        .join(AdvertiserCityLink, Advertiser.id == AdvertiserCityLink.advertiser_id)
        .where(
            AdvertiserCityLink.city_id == city_obj.id,
            AdvertiserCityLink.tier.in_(tier_list),
            Advertiser.active_ad_count >= active_ads_min,
            Advertiser.status == "active",
        )
    )

    if scope_list:
        query = query.where(Advertiser.scope.in_(scope_list))

    if q:
        query = query.where(Advertiser.page_name_norm.ilike(f"%{q.strip().lower()}%"))

    if cursor:
        query = query.where(Advertiser.id > cursor)

    query = query.order_by(Advertiser.id.asc()).limit(limit + 1)

    records = (await db.execute(query)).all()

    items = []
    has_next = len(records) > limit
    result_slice = records[:limit]

    for adv, link in result_slice:
        # Check contact summary
        contact_stmt = select(Contact).where(Contact.advertiser_id == adv.id)
        contacts = (await db.execute(contact_stmt)).scalars().all()

        has_p = any(c.type == "phone" for c in contacts)
        has_e = any(c.type == "email" for c in contacts)
        has_w = any(c.type == "whatsapp" for c in contacts)

        if has_phone is True and not has_p:
            continue
        if has_email is True and not has_e:
            continue
        if has_whatsapp is True and not has_w:
            continue

        items.append({
            "advertiser_id": adv.id,
            "meta_page_id": adv.meta_page_id,
            "page_name": adv.page_name,
            "primary_domain": adv.primary_domain,
            "scope": adv.scope,
            "city_link": {
                "city_id": link.city_id,
                "tier": link.tier,
                "confidence": round(link.confidence, 2),
                "is_primary": link.is_primary,
            },
            "active_ads": adv.active_ad_count,
            "total_ads": adv.total_ad_count,
            "first_seen_at": adv.first_seen_at.isoformat(),
            "contact_summary": {
                "has_phone": has_p,
                "has_email": has_e,
                "has_whatsapp": has_w,
                "has_website": bool(adv.primary_domain),
                "total_contacts": len(contacts),
            },
            "risk_flags": adv.risk_flags,
        })

    next_cursor = result_slice[-1][0].id if (has_next and result_slice) else None

    return {
        "city": {
            "slug": city_obj.slug,
            "name": city_obj.name,
            "gst_state_code": city_obj.gst_state_code,
        },
        "data_freshness": {
            "snapshot_at": datetime.now(timezone.utc).isoformat(),
            "stale": False,
        },
        "items": items,
        "next_cursor": next_cursor,
        "disclosure": "Based on Meta Ad Library activity. Commercial ad spend is not published by Meta outside the EU and is not estimated.",
    }

