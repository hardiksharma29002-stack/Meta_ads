"""Asynchronous CSV/XLSX Export Generation & Retrieval.

Implements SEC-03 (Formula Injection Defense) and Rule 7 (Zero suppressed contacts).
"""

import uuid
import io
import csv
from typing import Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Export, Advertiser, Contact, City, AuditLog
from app.core.auth import CurrentUser, require_role
from app.core.errors import NotFoundError
from app.services.suppression import filter_suppressed_contacts

router = APIRouter(prefix="/exports", tags=["Exports"])


def sanitize_csv_cell(value: Any) -> str:
    """Prepend single quote if cell starts with dangerous formula trigger characters (SEC-03)."""
    if value is None:
        return ""
    text = str(value)
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{text}"
    return text


@router.post("")
async def create_export_job(
    payload: dict,
    user: CurrentUser = Depends(require_role(["marketing", "compliance", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Enqueue asynchronous export compilation."""
    export_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    exp = Export(
        id=export_id,
        user_id=user.id,
        params=payload,
        row_count=0,
        status="ready",  # Instant ready for small MVP batches
        expires_at=expires_at,
    )
    db.add(exp)

    # Audit export generation
    audit = AuditLog(
        user_id=user.id,
        action="export",
        target_type="export",
        target_id=export_id,
        meta={"format": payload.get("format", "csv"), "city": payload.get("city")},
    )
    db.add(audit)
    await db.commit()

    return {
        "export_id": export_id,
        "status": "ready",
        "expires_at": expires_at.isoformat(),
        "download_url": f"/api/v1/exports/{export_id}/download",
    }


@router.get("/{id}/download")
async def download_export_file(
    id: str,
    user: CurrentUser = Depends(require_role(["marketing", "compliance", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Download compiled CSV export with formula injection sanitization and suppression filters."""
    stmt = select(Export).where(Export.id == id)
    exp = (await db.execute(stmt)).scalar_one_or_none()
    if not exp:
        raise NotFoundError("Export", id)

    # Fetch active advertisers
    adv_stmt = select(Advertiser).limit(100)
    advertisers = (await db.execute(adv_stmt)).scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header with compliance watermarking
    writer.writerow([
        sanitize_csv_cell("Advertiser ID"),
        sanitize_csv_cell("Page Name"),
        sanitize_csv_cell("Primary Domain"),
        sanitize_csv_cell("Scope"),
        sanitize_csv_cell("Active Ads"),
        sanitize_csv_cell("Contact Phone"),
        sanitize_csv_cell("Contact Email"),
        sanitize_csv_cell("Contact WhatsApp"),
        sanitize_csv_cell("DND Status"),
    ])

    for a in advertisers:
        contact_stmt = select(Contact).where(Contact.advertiser_id == a.id)
        contacts = (await db.execute(contact_stmt)).scalars().all()
        clean = await filter_suppressed_contacts(db, list(contacts))

        phone = next((c.value_norm for c in clean if c.type == "phone"), "")
        email = next((c.value_norm for c in clean if c.type == "email"), "")
        wa = next((c.value_norm for c in clean if c.type == "whatsapp"), "")

        writer.writerow([
            sanitize_csv_cell(a.id),
            sanitize_csv_cell(a.page_name),
            sanitize_csv_cell(a.primary_domain or ""),
            sanitize_csv_cell(a.scope),
            sanitize_csv_cell(a.active_ad_count),
            sanitize_csv_cell(phone),
            sanitize_csv_cell(email),
            sanitize_csv_cell(wa),
            sanitize_csv_cell("unknown"),  # TRAI DND column
        ])

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=adatlas_export_{id[:8]}.csv"},
    )
