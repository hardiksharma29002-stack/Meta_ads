"""Idempotent Reference Data Seeder for AdAtlas India.

Populates cities, aliases, PIN codes, and category taxonomy without duplication.
"""

import os
import yaml
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from app.db.session import async_session_factory, engine, Base
from app.db.models import City, CityAlias, PincodeCityMap, Category, Budget, User
from app.core.logging import logger

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/seed"))


async def seed_cities(session):
    """Seed the 5 core Indian cities."""
    path = os.path.join(DATA_DIR, "cities.yaml")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for item in data:
        stmt = select(City).where(City.slug == item["slug"])
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            city = City(
                slug=item["slug"],
                name=item["name"],
                state_name=item["state_name"],
                gst_state_code=item["gst_state_code"],
                std_code=item["std_code"],
                lat=item.get("lat"),
                lon=item.get("lon"),
                urban_population=item.get("urban_population"),
                population_source=item.get("population_source"),
                population_year=item.get("population_year"),
                is_active=item.get("is_active", True),
            )
            session.add(city)
    await session.commit()
    logger.info("seed_cities_completed")


async def seed_city_aliases(session):
    """Seed city aliases, vernacular spellings, and satellite territories."""
    path = os.path.join(DATA_DIR, "city_aliases.yaml")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for city_slug, aliases in data.items():
        stmt = select(City).where(City.slug == city_slug)
        city = (await session.execute(stmt)).scalar_one_or_none()
        if not city:
            continue

        for item in aliases:
            alias_stmt = select(CityAlias).where(
                CityAlias.city_id == city.id,
                CityAlias.alias == item["alias"],
            )
            existing = (await session.execute(alias_stmt)).scalar_one_or_none()
            if not existing:
                alias = CityAlias(
                    city_id=city.id,
                    alias=item["alias"],
                    lang=item.get("lang"),
                    kind=item["kind"],
                )
                session.add(alias)
    await session.commit()
    logger.info("seed_aliases_completed")


async def seed_pincodes(session):
    """Seed postal PIN code to city mapping."""
    path = os.path.join(DATA_DIR, "pincodes.yaml")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for item in data.get("pincodes", []):
        stmt = select(City).where(City.slug == item["city"])
        city = (await session.execute(stmt)).scalar_one_or_none()
        if not city:
            continue

        pin_stmt = select(PincodeCityMap).where(PincodeCityMap.pincode == item["pincode"])
        existing = (await session.execute(pin_stmt)).scalar_one_or_none()
        if not existing:
            pincode = PincodeCityMap(
                pincode=item["pincode"],
                city_id=city.id,
                locality=item.get("locality"),
                is_core=item.get("is_core", True),
            )
            session.add(pincode)
    await session.commit()
    logger.info("seed_pincodes_completed")


async def seed_categories(session):
    """Seed L1 and L2 category taxonomy."""
    path = os.path.join(DATA_DIR, "categories.yaml")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    version = data.get("taxonomy_version", 1)

    for l1 in data.get("categories", []):
        stmt = select(Category).where(Category.slug == l1["slug"])
        parent = (await session.execute(stmt)).scalar_one_or_none()
        if not parent:
            parent = Category(slug=l1["slug"], name=l1["name"], taxonomy_version=version)
            session.add(parent)
            await session.flush()

        for l2 in l1.get("subcategories", []):
            sub_stmt = select(Category).where(Category.slug == l2["slug"])
            sub = (await session.execute(sub_stmt)).scalar_one_or_none()
            if not sub:
                sub = Category(
                    parent_id=parent.id,
                    slug=l2["slug"],
                    name=l2["name"],
                    taxonomy_version=version,
                )
                session.add(sub)
    await session.commit()
    logger.info("seed_categories_completed")


async def seed_default_budgets_and_users(session):
    """Seed initial budget records and dev user."""
    # Seed budgets
    scopes = [
        ("provider", 150.00),
        ("places", 100.00),
        ("llm", 50.00),
        ("proxy", 0.00),
    ]
    now = datetime.now(timezone.utc)
    for scope, cap in scopes:
        stmt = select(Budget).where(Budget.scope == scope)
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            b = Budget(scope=scope, period="monthly", cap=cap, spent=0.00, resets_at=now)
            session.add(b)

    # Seed local dev user
    dev_email = "dev@adatlas.in"
    user_stmt = select(User).where(User.email == dev_email)
    existing_user = (await session.execute(user_stmt)).scalar_one_or_none()
    if not existing_user:
        u = User(email=dev_email, role="admin", reveal_quota_daily=500)
        session.add(u)

    await session.commit()
    logger.info("seed_budgets_and_users_completed")


async def seed_all():
    """Execute complete reference seeding routine."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        await seed_cities(session)
        await seed_city_aliases(session)
        await seed_pincodes(session)
        await seed_categories(session)
        await seed_default_budgets_and_users(session)
    logger.info("all_seed_tasks_finished_cleanly")


if __name__ == "__main__":
    asyncio.run(seed_all())
