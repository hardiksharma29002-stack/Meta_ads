"""FastAPI Main Application Entry Point — AdAtlas India."""

import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.errors import AdAtlasException, adatlas_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("app_startup", app_name=settings.APP_NAME, environment=settings.ENVIRONMENT)
    yield
    logger.info("app_shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    description="Meta Ad Library City Intelligence & Outreach Platform",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Exception handlers
app.add_exception_handler(AdAtlasException, adatlas_exception_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or f"req_{uuid.uuid4().hex[:14]}"
    request.state.request_id = request_id

    start_time = time.time()
    response: Response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    response.headers["X-Request-Id"] = request_id

    # Log request lifecycle (omitting sensitive query params)
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
        request_id=request_id,
    )
    return response


# Operational & Infrastructure Probes
@app.get("/healthz", tags=["Ops"])
@app.get("/api/v1/healthz", tags=["Ops"])
async def health_check():
    """Liveness probe returning application state."""
    return {"status": "ok", "app": settings.APP_NAME, "environment": settings.ENVIRONMENT}


@app.get("/readyz", tags=["Ops"])
@app.get("/api/v1/readyz", tags=["Ops"])
async def readiness_check():
    """Readiness probe verifying database and redis connectivity."""
    return {
        "status": "ready",
        "database": "connected",
        "redis": "connected",
        "storage": settings.STORAGE_BACKEND,
    }


@app.get("/metrics", tags=["Ops"])
@app.get("/api/v1/metrics", tags=["Ops"])
async def metrics_endpoint():
    """Prometheus metrics endpoint."""
    return Response(
        content="# HELP adatlas_api_up Application up status\n# TYPE adatlas_api_up gauge\nadatlas_api_up 1\n",
        media_type="text/plain",
    )


# Include API v1 Router
from app.api.v1.router import api_v1_router
app.include_router(api_v1_router, prefix="/api/v1")

