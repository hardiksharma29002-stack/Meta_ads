"""Seed Query Generator for Discovery Sweeps.

Generates deterministic batches combining target cities, category keywords,
and language variants. Computes estimated collection costs before execution.
"""

from app.collectors.base import SearchQuery, Money
from app.collectors.registry import adapter_registry


def generate_seed_queries(
    city_slugs: list[str] | None = None,
    category_keywords: list[str] | None = None,
    limit_per_query: int = 50,
) -> list[SearchQuery]:
    """Generate Cartesian product of target cities and category keywords."""
    target_cities = city_slugs or ["mumbai", "delhi", "jaipur", "kolkata", "bengaluru"]
    keywords = category_keywords or [
        "jewellery",
        "coaching",
        "apparel",
        "bakery",
        "interior",
        "dental",
        "fitness",
        "software",
    ]

    queries: list[SearchQuery] = []
    for city in target_cities:
        for kw in keywords:
            queries.append(
                SearchQuery(
                    city_slug=city,
                    keyword=kw,
                    limit=limit_per_query,
                    active_only=True,
                )
            )
    return queries


def calculate_sweep_cost_estimate(queries: list[SearchQuery], adapter_name: str = "adapter_b") -> Money:
    """Project total estimated cost for a proposed sweep."""
    adapter = adapter_registry.get_adapter(adapter_name)
    total_cost = 0.0
    for q in queries:
        est = adapter.estimate_cost(q)
        total_cost += est.amount
    return Money(amount=round(total_cost, 2), currency="USD")

