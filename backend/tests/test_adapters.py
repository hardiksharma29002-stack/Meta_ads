"""Contract Test Suite for Collector Adapters (Adapter A, B, C)."""

import pytest
from app.collectors.registry import adapter_registry
from app.collectors.base import SearchQuery


@pytest.mark.asyncio
async def test_adapter_a_contract():
    """Verify Adapter A (Official API) capabilities and mock fixture return."""
    adapter = adapter_registry.get_adapter("adapter_a")
    caps = adapter.capabilities()
    assert caps.political_ads is True
    assert caps.commercial_ads is False
    assert caps.spend_ranges is True

    # Test search query
    q = SearchQuery(city_slug="jaipur", limit=5)
    page = await adapter.search(q)
    assert len(page.items) >= 1
    item = page.items[0]
    assert item.ad_type == "political_issue"
    assert item.spend_lower is not None


@pytest.mark.asyncio
async def test_adapter_b_contract():
    """Verify Adapter B (Managed Commercial Provider) capabilities and commercial ads."""
    adapter = adapter_registry.get_adapter("adapter_b")
    caps = adapter.capabilities()
    assert caps.commercial_ads is True
    assert caps.political_ads is False
    assert caps.spend_ranges is False  # R2: commercial spend is never available

    q = SearchQuery(city_slug="jaipur", limit=10)
    page = await adapter.search(q)
    assert len(page.items) >= 1
    item = page.items[0]
    assert item.ad_type == "commercial"
    assert item.landing_domain is not None
    assert item.spend_lower is None  # Never estimated


@pytest.mark.asyncio
async def test_adapter_c_contract_flagged_off():
    """Verify Adapter C is strictly OFF by default per ADR-0001 & ADR-0002."""
    adapter = adapter_registry.get_adapter("adapter_c")
    health = await adapter.health()
    assert health.is_healthy is False
    assert "Flagged OFF by default" in health.status_message

