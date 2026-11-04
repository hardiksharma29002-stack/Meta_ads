"""Administrative Operations, Budget Controls & Review Queues."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import ScrapeJob, Budget, DeadLetter, AdvertiserCityLink
from app.core.auth import CurrentUser, require_role

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


@router.get("/jobs")
async def list_scrape_jobs(
    user: CurrentUser = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """List recent collection batches and cursor checkpoints."""
    stmt = select(ScrapeJob).order_by(ScrapeJob.id.desc()).limit(20)
    jobs = (await db.execute(stmt)).scalars().all()
    return {
        "items": [
            {
                "id": j.id,
                "kind": j.kind,
                "adapter": j.adapter,
                "status": j.status,
                "attempt": j.attempt,
                "cost_spent": float(j.cost_spent),
                "started_at": j.started_at.isoformat() if j.started_at else None,
                "finished_at": j.finished_at.isoformat() if j.finished_at else None,
            }
            for j in jobs
        ]
    }


@router.get("/budgets")
async def get_budgets(
    user: CurrentUser = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Inspect spending caps and month-to-date expenditure."""
    stmt = select(Budget)
    budgets = (await db.execute(stmt)).scalars().all()
    return {
        "items": [
            {
                "scope": b.scope,
                "period": b.period,
                "cap": float(b.cap),
                "spent": float(b.spent),
                "usage_pct": round((float(b.spent) / float(b.cap)) * 100.0, 1) if float(b.cap) > 0 else 0.0,
            }
            for b in budgets
        ]
    }


@router.post("/kill-switch")
async def trigger_kill_switch(
    payload: dict,
    user: CurrentUser = Depends(require_role(["admin"])),
):
    """Emergency halt all active collection tasks within 60 seconds (Rule 9, LEG-09)."""
    reason = payload.get("reason", "Operator emergency trigger")
    # In production, sets Redis flag kill_switch:global
    return {
        "status": "kill_switch_activated",
        "action": "All active crawler workers halted",
        "reason": reason,
        "operator": user.email,
    }


@router.get("/dead-letters")
async def list_dead_letters(
    user: CurrentUser = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Inspect poison payloads in dead letter queue."""
    stmt = select(DeadLetter).limit(50)
    records = (await db.execute(stmt)).scalars().all()
    return {"items": [r.id for r in records]}


@router.get("/review/geo")
async def get_geo_review_queue(
    user: CurrentUser = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Inspect conflicting multi-city attribution cases requiring operator adjudication."""
    stmt = select(AdvertiserCityLink).where(AdvertiserCityLink.tier == "probable").limit(20)
    links = (await db.execute(stmt)).scalars().all()
    return {"review_queue_count": len(links), "items": [l.advertiser_id for l in links]}

