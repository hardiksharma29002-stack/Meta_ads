"""Authentication & Role-Based Access Control (RBAC).

Supports Free-Tier local development mock auth mode and production Google OAuth JWT validation.
"""

from typing import Annotated
from datetime import datetime, timezone, timedelta
import jwt
from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel
from app.core.config import settings
from app.core.errors import AuthorizationError


class CurrentUser(BaseModel):
    id: str
    email: str
    role: str  # viewer | marketing | compliance | admin
    reveal_quota_daily: int = 200


def create_access_token(user_id: str, email: str, role: str) -> str:
    """Generate signed HMAC-SHA256 JWT for testing or BFF communication."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET_PRIMARY, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(authorization: Annotated[str | None, Header()] = None) -> CurrentUser:
    """Extract and validate user context from Bearer token or mock auth."""
    # Free-Tier / Local Dev Mode: automatic mock admin user
    if settings.AUTH_MODE == "mock" and not authorization:
        return CurrentUser(
            id="00000000-0000-0000-0000-000000000001",
            email="dev@adatlas.in",
            role="admin",
            reveal_quota_daily=500,
        )

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Bearer authentication header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_PRIMARY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return CurrentUser(
            id=str(payload.get("sub", "")),
            email=str(payload.get("email", "")),
            role=str(payload.get("role", "viewer")),
            reveal_quota_daily=200,
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(allowed_roles: list[str]):
    """Dependency factory checking that user holds one of the allowed roles."""
    async def role_checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_roles and user.role != "admin":
            raise AuthorizationError(f"Action requires one of roles: {', '.join(allowed_roles)}")
        return user
    return role_checker

