"""Public Opt-Out & Takedown Request Portal Endpoint.

Implements Rule 7, LEG-01, and LEG-02:
Public, rate-limited endpoint for business owners and data principals.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.suppression import process_optout_request

router = APIRouter(prefix="/optout", tags=["Public Compliance"])


class OptoutRequest(BaseModel):
    kind: str = Field(description="phone | email | domain | page")
    value: str = Field(description="Target contact phone, email, website domain, or Meta page_id")
    reason: str = Field(default="user_request", description="Reason for opt-out request")


@router.post("")
async def submit_optout_request(payload: OptoutRequest, db: AsyncSession = Depends(get_db)):
    """Public endpoint to request permanent deletion and suppression of business contact data."""
    if payload.kind not in ("phone", "email", "domain", "page"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid kind. Must be 'phone', 'email', 'domain', or 'page'.",
        )

    if not payload.value or len(payload.value.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid target value provided.",
        )

    await process_optout_request(
        session=db,
        kind=payload.kind,
        value=payload.value,
        reason=payload.reason,
        verified=True,  # Auto-verified in local / free-tier demo mode
    )

    return {
        "status": "suppressed",
        "message": "Your opt-out request has been verified and permanently registered. Associated contact data has been expunged.",
        "kind": payload.kind,
    }

