"""RFC 9457 Problem Details Exception Architecture.

Standardizes all API error responses under application/problem+json.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ProblemDetails(BaseModel):
    type: str = Field(default="about:blank", description="URI reference identifying the problem type")
    title: str = Field(description="Short human-readable summary of problem")
    status: int = Field(description="HTTP status code")
    detail: str = Field(description="Human-readable explanation specific to this occurrence")
    instance: str | None = Field(default=None, description="URI reference identifying the specific occurrence")
    request_id: str | None = Field(default=None, description="Traceable request identifier")


class AdAtlasException(Exception):
    def __init__(self, title: str, status_code: int, detail: str, type_uri: str = "about:blank"):
        super().__init__(detail)
        self.title = title
        self.status_code = status_code
        self.detail = detail
        self.type_uri = type_uri


class NotFoundError(AdAtlasException):
    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            title="Resource Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with identifier '{identifier}' was not found.",
            type_uri="https://errors.adatlas.in/not-found",
        )


class QuotaExceededError(AdAtlasException):
    def __init__(self, detail: str = "Daily reveal quota exhausted."):
        super().__init__(
            title="Quota Exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            type_uri="https://errors.adatlas.in/quota-exceeded",
        )


class SSRFBlockedError(AdAtlasException):
    def __init__(self, target_ip: str):
        super().__init__(
            title="SSRF Request Blocked",
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Outbound connection to restricted IP target ({target_ip}) was denied.",
            type_uri="https://errors.adatlas.in/ssrf-blocked",
        )


class KillSwitchActiveError(AdAtlasException):
    def __init__(self):
        super().__init__(
            title="Service Temporarily Halted",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data collection is currently halted under an operational kill-switch directive.",
            type_uri="https://errors.adatlas.in/kill-switch-active",
        )


class AuthorizationError(AdAtlasException):
    def __init__(self, detail: str = "Permission denied for the requested action."):
        super().__init__(
            title="Forbidden",
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            type_uri="https://errors.adatlas.in/forbidden",
        )


async def adatlas_exception_handler(request: Request, exc: AdAtlasException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    problem = ProblemDetails(
        type=exc.type_uri,
        title=exc.title,
        status=exc.status_code,
        detail=exc.detail,
        instance=str(request.url.path),
        request_id=request_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(exclude_none=True),
        headers={"Content-Type": "application/problem+json"},
    )

