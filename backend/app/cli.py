"""Command Line Interface for Operational Tasks.

Provides CLI commands for data collection sweeps, raw replay, and administrative utilities.
"""

import asyncio
import argparse
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.collectors.base import SearchQuery
from app.collectors.registry import adapter_registry
from app.pipeline.seed_queries import generate_seed_queries, calculate_sweep_cost_estimate
from app.core.logging import logger
from app.db.seed import seed_all


async def cmd_collect(args):
    """Execute collection sweep or dry-run estimate."""
    adapter = adapter_registry.get_adapter(args.adapter)
    q = SearchQuery(city_slug=args.city, keyword=args.keyword, limit=args.limit)

    cost_est = adapter.estimate_cost(q)
    print(f"\n==================================================")
    print(f"[RUN] ADATLAS COLLECTION: {args.city.upper()}")
    print(f"Adapter: {args.adapter} | Limit: {args.limit} | Keyword: {args.keyword or 'ALL'}")
    print(f"Estimated Cost: ${cost_est.amount:.4f} {cost_est.currency}")
    print(f"==================================================")

    if args.dry_run:
        print("[OK] Dry-run complete. No external requests or database writes executed.")
        return

    print("Executing collection query...")
    page = await adapter.search(q)
    print(f"[OK] Successfully collected {len(page.items)} ad items.")
    for item in page.items[:3]:
        print(f"  - [{item.meta_ad_id}] {item.page_name}: {item.headline or item.body_text[:40]}...")


async def cmd_seed(args):
    """Seed reference data."""
    print("Seeding reference cities, aliases, PIN codes, and categories...")
    await seed_all()
    print("[OK] Seeding complete.")


def main():
    parser = argparse.ArgumentParser(description="AdAtlas India CLI Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # collect
    col_parser = subparsers.add_parser("collect", help="Execute collection sweep")
    col_parser.add_argument("--city", default="jaipur", help="City slug")
    col_parser.add_argument("--adapter", default="adapter_b", help="Source adapter name")
    col_parser.add_argument("--keyword", default=None, help="Optional search keyword")
    col_parser.add_argument("--limit", type=int, default=20, help="Max ads to collect")
    col_parser.add_argument("--dry-run", action="store_true", help="Estimate cost without fetching")

    # seed
    seed_parser = subparsers.add_parser("seed", help="Seed database reference tables")

    args = parser.parse_args()

    if args.command == "collect":
        asyncio.run(cmd_collect(args))
    elif args.command == "seed":
        asyncio.run(cmd_seed(args))


if __name__ == "__main__":
    main()
