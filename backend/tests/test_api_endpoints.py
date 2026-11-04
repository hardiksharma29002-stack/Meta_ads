"""Integration Tests for FastAPI Endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from sqlalchemy import select
from app.db.session import engine, Base, async_session_factory
from app.db.models import City


@pytest.fixture(autouse=True, scope="function")
async def setup_test_db():
    """Ensure database schema is created and reference test cities exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_factory() as session:
        # Check if test cities exist
        for idx, (slug, name) in enumerate([("mumbai", "Mumbai"), ("jaipur", "Jaipur")], start=1):
            stmt = select(City).where(City.slug == slug)
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if not existing:
                city = City(
                    id=idx,
                    slug=slug,
                    name=name,
                    state_name="Maharashtra" if slug == "mumbai" else "Rajasthan",
                    urban_population=12442373 if slug == "mumbai" else 3073350,
                    gst_state_code="27" if slug == "mumbai" else "08",
                    std_code="022" if slug == "mumbai" else "0141",
                    is_active=True,
                )
                session.add(city)
        await session.commit()
    yield


@pytest.mark.asyncio
async def test_healthz_endpoint():
    """Verify liveness probe returns status ok."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/healthz")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_readyz_endpoint():
    """Verify readiness probe returns ready."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/readyz")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Verify Prometheus metrics endpoint format."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/metrics")
        assert res.status_code == 200
        assert "adatlas_api_up" in res.text


@pytest.mark.asyncio
async def test_public_optout_endpoint():
    """Verify public opt-out processing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/optout",
            json={
                "kind": "phone",
                "value": "+919829012345",
                "reason": "user_optout_test",
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "suppressed"


@pytest.mark.asyncio
async def test_compare_endpoint():
    """Verify compare endpoint returns city scorecards and disclosure copy."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/compare?cities=jaipur,mumbai&profile=outreach")
        assert res.status_code == 200
        data = res.json()
        assert "disclosure" in data
        assert "Commercial ad spend is not published" in data["disclosure"]
