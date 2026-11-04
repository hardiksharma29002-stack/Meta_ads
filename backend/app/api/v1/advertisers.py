"""Advertiser Details, Ad History & Contact Reveal Endpoints.

Implements masked contacts by default and audited reveal with daily quota checks.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Advertiser, Ad, Contact, ContactEvidence, AuditLog, User
from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.errors import NotFoundError, QuotaExceededError
from app.services.suppression import filter_suppressed_contacts

router = APIRouter(prefix="/advertisers", tags=["Advertisers"])


def mask_contact_value(val: str, contact_type: str) -> str:
    """Mask sensitive portions of phone number or email string."""
    if contact_type == "phone":
        clean = val.replace(" ", "")
        if len(clean) >= 10:
            return clean[:6] + "••••" + clean[-2:]
        return "••••••••••"
    elif contact_type == "email":
        parts = val.split("@")
        if len(parts) == 2:
            name, domain = parts
            masked_name = name[:2] + "••••" if len(name) > 2 else "••••"
            return f"{masked_name}@{domain}"
    return "••••••••"


@router.get("/{id}")
async def get_advertiser_detail(id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve full advertiser profile, city attribution links, and evidence."""
    stmt = select(Advertiser).where(Advertiser.id == id)
    adv = (await db.execute(stmt)).scalar_one_or_none()
    if not adv:
        raise NotFoundError("Advertiser", id)

    return {
        "id": adv.id,
        "meta_page_id": adv.meta_page_id,
        "page_name": adv.page_name,
        "primary_domain": adv.primary_domain,
        "scope": adv.scope,
        "active_ad_count": adv.active_ad_count,
        "total_ad_count": adv.total_ad_count,
        "status": adv.status,
        "first_seen_at": adv.first_seen_at.isoformat(),
        "last_seen_at": adv.last_seen_at.isoformat(),
        "risk_flags": adv.risk_flags,
    }


@router.get("/{id}/ads")
async def get_advertiser_ads(id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve chronological ad history for advertiser."""
    stmt = select(Ad).where(Ad.advertiser_id == id).order_by(Ad.last_seen_at.desc())
    ads = (await db.execute(stmt)).scalars().all()

    return {
        "items": [
            {
                "id": ad.id,
                "meta_ad_id": ad.meta_ad_id,
                "status": ad.status,
                "ad_type": ad.ad_type,
                "headline": ad.headline,
                "body_text": ad.body_text,
                "cta": ad.cta,
                "landing_url": ad.landing_url,
                "landing_domain": ad.landing_domain,
                "media_type": ad.media_type,
                "first_seen_at": ad.first_seen_at.isoformat(),
                "last_seen_at": ad.last_seen_at.isoformat(),
                "permalink": f"https://www.facebook.com/ads/library/?id={ad.meta_ad_id}",
            }
            for ad in ads
        ]
    }


@router.get("/{id}/contacts")
async def get_advertiser_contacts_masked(id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve contacts in MASKED format (default view)."""
    stmt = select(Contact).where(Contact.advertiser_id == id)
    contacts = (await db.execute(stmt)).scalars().all()
    clean_contacts = await filter_suppressed_contacts(db, list(contacts))

    return {
        "items": [
            {
                "id": c.id,
                "type": c.type,
                "subtype": c.subtype,
                "value_masked": mask_contact_value(c.value_norm, c.type),
                "confidence": c.confidence,
                "verification": c.verification,
                "flags": c.flags,
                "last_verified_at": c.last_verified_at.isoformat() if c.last_verified_at else None,
            }
            for c in clean_contacts
        ]
    }


@router.post("/{id}/contacts/reveal")
async def reveal_advertiser_contacts(
    id: int,
    request: Request,
    user: CurrentUser = Depends(require_role(["marketing", "compliance", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Unmask verified contacts for advertiser, consuming daily user quota and writing audit record."""
    adv_stmt = select(Advertiser).where(Advertiser.id == id)
    adv = (await db.execute(adv_stmt)).scalar_one_or_none()
    if not adv:
        raise NotFoundError("Advertiser", id)

    # Quota check
    if user.reveal_quota_daily <= 0:
        raise QuotaExceededError("You have exhausted your daily reveal quota.")

    # Retrieve unmasked contacts
    contact_stmt = select(Contact).where(Contact.advertiser_id == id)
    contacts = (await db.execute(contact_stmt)).scalars().all()
    clean_contacts = await filter_suppressed_contacts(db, list(contacts))

    # Log immutable audit entry
    client_ip = request.client.host if request.client else "127.0.0.1"
    audit = AuditLog(
        user_id=user.id,
        action="reveal",
        target_type="advertiser",
        target_id=str(id),
        meta={"contacts_revealed": len(clean_contacts), "page_name": adv.page_name},
        ip=client_ip,
    )
    db.add(audit)
    await db.commit()

    return {
        "advertiser_id": adv.id,
        "page_name": adv.page_name,
        "unmasked_contacts": [
            {
                "id": c.id,
                "type": c.type,
                "subtype": c.subtype,
                "value": c.value_norm,
                "confidence": c.confidence,
                "verification": c.verification,
                "flags": c.flags,
            }
            for c in clean_contacts
        ],
        "quota_remaining": max(0, user.reveal_quota_daily - len(clean_contacts)),
    }


@router.post("/{id}/feedback")
async def submit_feedback(
    id: int,
    payload: dict,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit user feedback for incorrect contact or city attribution."""
    audit = AuditLog(
        user_id=user.id,
        action="feedback",
        target_type="advertiser",
        target_id=str(id),
        meta=payload,
    )
    db.add(audit)
    await db.commit()
    return {"status": "feedback_recorded", "advertiser_id": id}

