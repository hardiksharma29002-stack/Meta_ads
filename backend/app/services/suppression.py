"""Suppression Registry & Opt-Out Enforcement Service.

Enforces Rule 7, LEG-01, and LEG-02:
Suppression pre-flight checks executed synchronously on write, read, and export paths.
"""

import hashlib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Suppression, Contact, ContactEvidence, Advertiser
from app.core.logging import logger


def compute_value_hash(value: str) -> bytes:
    """Normalize and compute SHA-256 hash for contact or identifier."""
    clean = value.strip().lower()
    return hashlib.sha256(clean.encode("utf-8")).digest()


async def is_suppressed(session: AsyncSession, value_hash: bytes) -> bool:
    """Synchronously verify whether a value hash exists in the suppression registry."""
    stmt = select(Suppression).where(
        Suppression.value_hash == value_hash,
        Suppression.verified == True,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def filter_suppressed_contacts(session: AsyncSession, contacts: list[Contact]) -> list[Contact]:
    """Filter out any contact whose hash exists in the suppression list."""
    if not contacts:
        return []

    hashes = [c.value_hash for c in contacts]
    stmt = select(Suppression.value_hash).where(
        Suppression.value_hash.in_(hashes),
        Suppression.verified == True,
    )
    suppressed_hashes = set((await session.execute(stmt)).scalars().all())

    return [c for c in contacts if c.value_hash not in suppressed_hashes]


async def process_optout_request(
    session: AsyncSession,
    kind: str,
    value: str,
    reason: str,
    verified: bool = True,
) -> bool:
    """Register suppression hash and purge active matching contacts."""
    v_hash = compute_value_hash(value)

    # 1. Insert into suppression table
    stmt = select(Suppression).where(Suppression.value_hash == v_hash)
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if not existing:
        suppression_entry = Suppression(
            value_hash=v_hash,
            kind=kind,
            reason=reason,
            verified=verified,
        )
        session.add(suppression_entry)
    else:
        existing.verified = verified

    # 2. Immediately purge matching contacts from active database
    contact_stmt = select(Contact).where(Contact.value_hash == v_hash)
    matching_contacts = (await session.execute(contact_stmt)).scalars().all()

    for c in matching_contacts:
        # Cascade deletes evidence
        await session.delete(c)

    await session.commit()
    logger.info("optout_processed", kind=kind, value_hash_prefix=v_hash.hex()[:8], purged_count=len(matching_contacts))
    return True

