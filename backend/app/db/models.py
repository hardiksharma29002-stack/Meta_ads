"""SQLAlchemy Declarative Models for AdAtlas India.

Adheres strictly to docs/DATA_MODEL.md specification.
"""

import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    BigInteger,
    String,
    Text,
    Boolean,
    Float,
    Numeric,
    DateTime,
    Date,
    LargeBinary,
    ForeignKey,
    JSON,
    ARRAY,
    Index,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================================
# 1. REFERENCE DATA
# ============================================================================

# Cross-dialect integer primary key types (Postgres BigInt / SmallInt, SQLite Integer rowid)
AutoBigId = BigInteger().with_variant(Integer, "sqlite")
AutoSmallId = SmallInteger().with_variant(Integer, "sqlite")


class City(Base):
    __tablename__ = "cities"

    id = Column(AutoSmallId, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    state_name = Column(String(100), nullable=False)
    gst_state_code = Column(String(2), nullable=False)
    std_code = Column(String(10), nullable=False)
    lat = Column(Numeric(8, 5), nullable=True)
    lon = Column(Numeric(8, 5), nullable=True)
    urban_population = Column(Integer, nullable=True)
    population_source = Column(String(100), nullable=True)
    population_year = Column(SmallInteger, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    aliases = relationship("CityAlias", back_populates="city", cascade="all, delete-orphan")
    pincodes = relationship("PincodeCityMap", back_populates="city", cascade="all, delete-orphan")
    advertiser_links = relationship("AdvertiserCityLink", back_populates="city")


class CityAlias(Base):
    __tablename__ = "city_aliases"

    city_id = Column(AutoSmallId, ForeignKey("cities.id", ondelete="CASCADE"), primary_key=True)
    alias = Column(String(150), primary_key=True)
    lang = Column(String(10), nullable=True)
    kind = Column(String(50), nullable=False)  # name | old_name | transliteration | locality | satellite

    city = relationship("City", back_populates="aliases")


class PincodeCityMap(Base):
    __tablename__ = "pincode_city_map"

    pincode = Column(String(6), primary_key=True)
    city_id = Column(AutoSmallId, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    locality = Column(String(200), nullable=True)
    is_core = Column(Boolean, default=True, nullable=False)

    city = relationship("City", back_populates="pincodes")


class Category(Base):
    __tablename__ = "categories"

    id = Column(AutoSmallId, primary_key=True, autoincrement=True)
    parent_id = Column(AutoSmallId, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    taxonomy_version = Column(SmallInteger, default=1, nullable=False)


# ============================================================================
# 2. CORE ADVERTISERS & ADS
# ============================================================================

class Advertiser(Base):
    __tablename__ = "advertisers"

    id = Column(AutoBigId, primary_key=True, autoincrement=True)
    meta_page_id = Column(String(100), unique=True, nullable=False, index=True)
    page_name = Column(String(255), nullable=False)
    page_name_norm = Column(String(255), nullable=False, index=True)
    page_url = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    primary_domain = Column(String(255), nullable=True, index=True)
    category_id = Column(AutoSmallId, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    category_conf = Column(Float, nullable=True)
    scope = Column(String(50), default="unknown")  # local | regional | national | unknown
    risk_flags = Column(JSON, default=list, nullable=False)
    entity_group_id = Column(BigInteger, nullable=True)
    status = Column(String(50), default="active", nullable=False, index=True)
    active_ad_count = Column(Integer, default=0, nullable=False)
    total_ad_count = Column(Integer, default=0, nullable=False)
    first_seen_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    ads = relationship("Ad", back_populates="advertiser", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="advertiser", cascade="all, delete-orphan")
    city_links = relationship("AdvertiserCityLink", back_populates="advertiser", cascade="all, delete-orphan")


class AdvertiserNameHistory(Base):
    __tablename__ = "advertiser_name_history"

    advertiser_id = Column(AutoBigId, ForeignKey("advertisers.id", ondelete="CASCADE"), primary_key=True)
    page_name = Column(String(255), primary_key=True)
    seen_from = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class AdvertiserCityLink(Base):
    __tablename__ = "advertiser_city_links"

    advertiser_id = Column(AutoBigId, ForeignKey("advertisers.id", ondelete="CASCADE"), primary_key=True)
    city_id = Column(AutoSmallId, ForeignKey("cities.id", ondelete="CASCADE"), primary_key=True, index=True)
    confidence = Column(Float, nullable=False)
    tier = Column(String(50), nullable=False, index=True)  # confirmed | probable | weak
    is_primary = Column(Boolean, default=False, nullable=False)
    branch_count = Column(SmallInteger, default=1)
    evidence = Column(JSON, default=list, nullable=False)
    model_version = Column(String(50), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    advertiser = relationship("Advertiser", back_populates="city_links")
    city = relationship("City", back_populates="advertiser_links")


class Ad(Base):
    __tablename__ = "ads"

    id = Column(AutoBigId, primary_key=True, autoincrement=True)
    meta_ad_id = Column(String(100), unique=True, nullable=False, index=True)
    advertiser_id = Column(AutoBigId, ForeignKey("advertisers.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # adapter_a | adapter_b | adapter_c
    ad_type = Column(String(50), default="commercial", nullable=False)  # commercial | political_issue
    status = Column(String(50), default="active", nullable=False, index=True)  # active | inactive | disappeared
    delivery_start = Column(DateTime(timezone=True), nullable=True)
    delivery_stop = Column(DateTime(timezone=True), nullable=True)
    first_seen_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    disappeared_at = Column(DateTime(timezone=True), nullable=True)
    body_text = Column(Text, nullable=True)
    headline = Column(Text, nullable=True)
    cta = Column(String(100), nullable=True)
    landing_url = Column(Text, nullable=True)
    landing_domain = Column(String(255), nullable=True, index=True)
    media_type = Column(String(50), nullable=True)
    platforms = Column(JSON, default=list)
    languages = Column(JSON, default=list)
    collation_id = Column(String(100), nullable=True)
    collation_count = Column(Integer, default=1)
    content_hash = Column(LargeBinary, nullable=False, index=True)

    # Political ad fields (Adapter A only)
    spend_lower = Column(BigInteger, nullable=True)
    spend_upper = Column(BigInteger, nullable=True)
    impressions_lower = Column(BigInteger, nullable=True)
    impressions_upper = Column(BigInteger, nullable=True)
    currency = Column(String(10), nullable=True)

    raw_payload_id = Column(BigInteger, nullable=True)
    schema_version = Column(SmallInteger, default=1, nullable=False)

    advertiser = relationship("Advertiser", back_populates="ads")


# ============================================================================
# 3. CONTACTS & SUPPRESSION
# ============================================================================

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(AutoBigId, primary_key=True, autoincrement=True)
    advertiser_id = Column(AutoBigId, ForeignKey("advertisers.id", ondelete="CASCADE"), nullable=False, index=True)
    city_id = Column(AutoSmallId, ForeignKey("cities.id", ondelete="SET NULL"), nullable=True)
    type = Column(String(50), nullable=False)  # phone | email | whatsapp | website | socials
    subtype = Column(String(50), nullable=True)  # mobile | landline | tollfree | role_email
    value_raw = Column(Text, nullable=False)
    value_norm = Column(Text, nullable=False)
    value_hash = Column(LargeBinary, nullable=False, index=True)  # sha256(value_norm)
    confidence = Column(Float, nullable=False)
    verification = Column(String(50), default="unverified", nullable=False)
    flags = Column(JSON, default=list, nullable=False)
    first_seen_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("advertiser_id", "type", "value_hash", name="uq_adv_type_value_hash"),
    )

    advertiser = relationship("Advertiser", back_populates="contacts")
    evidence = relationship("ContactEvidence", back_populates="contact", cascade="all, delete-orphan")


class ContactEvidence(Base):
    __tablename__ = "contact_evidence"

    id = Column(AutoBigId, primary_key=True, autoincrement=True)
    contact_id = Column(AutoBigId, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    source_url = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False)
    page_kind = Column(String(50), nullable=True)
    fetched_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    raw_payload_id = Column(BigInteger, nullable=True)

    contact = relationship("Contact", back_populates="evidence")


class Suppression(Base):
    __tablename__ = "suppression"

    value_hash = Column(LargeBinary, primary_key=True)  # sha256(norm_value)
    kind = Column(String(50), nullable=False)  # phone | email | domain | page
    reason = Column(String(100), nullable=False)
    requested_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)


# ============================================================================
# 4. OPERATIONS, JOBS & BUDGETS
# ============================================================================

class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id = Column(AutoBigId, primary_key=True, autoincrement=True)
    kind = Column(String(50), nullable=False)
    adapter = Column(String(50), nullable=False)
    params = Column(JSON, default=dict, nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    cursor = Column(Text, nullable=True)
    attempt = Column(SmallInteger, default=0, nullable=False)
    budget_cap = Column(Numeric(12, 2), nullable=True)
    cost_spent = Column(Numeric(12, 2), default=0.00, nullable=False)
    stats = Column(JSON, default=dict, nullable=False)
    error = Column(Text, nullable=True)
    heartbeat_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    idempotency_key = Column(String(200), unique=True, nullable=True)


class RawPayload(Base):
    __tablename__ = "raw_payloads"

    id = Column(AutoBigId, primary_key=True, autoincrement=True)
    job_id = Column(AutoBigId, ForeignKey("scrape_jobs.id", ondelete="SET NULL"), nullable=True)
    adapter = Column(String(50), nullable=False)
    schema_version = Column(SmallInteger, default=1, nullable=False)
    s3_key = Column(Text, nullable=False)
    sha256 = Column(LargeBinary, nullable=False)
    bytes = Column(Integer, nullable=False)
    fetched_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class DeadLetter(Base):
    __tablename__ = "dead_letters"

    id = Column(AutoBigId, primary_key=True, autoincrement=True)
    queue = Column(String(100), nullable=False)
    task = Column(String(150), nullable=False)
    payload = Column(JSON, nullable=False)
    error = Column(Text, nullable=False)
    attempts = Column(SmallInteger, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    replayed_at = Column(DateTime(timezone=True), nullable=True)


class Budget(Base):
    __tablename__ = "budgets"

    scope = Column(String(50), primary_key=True)  # provider | places | llm | proxy
    period = Column(String(50), default="monthly", nullable=False)
    cap = Column(Numeric(12, 2), nullable=False)
    spent = Column(Numeric(12, 2), default=0.00, nullable=False)
    resets_at = Column(DateTime(timezone=True), nullable=False)


# ============================================================================
# 5. ANALYTICS ROLLUPS
# ============================================================================

class CityMetricsDaily(Base):
    __tablename__ = "city_metrics_daily"

    city_id = Column(AutoSmallId, ForeignKey("cities.id", ondelete="CASCADE"), primary_key=True)
    day = Column(Date, primary_key=True)
    scope = Column(String(50), primary_key=True)  # all | local | regional
    active_advertisers = Column(Integer, default=0, nullable=False)
    new_advertisers_30d = Column(Integer, default=0, nullable=False)
    active_ads = Column(Integer, default=0, nullable=False)
    distinct_creatives = Column(Integer, default=0, nullable=False)
    median_longevity_days = Column(Float, nullable=True)
    creative_refresh_rate = Column(Float, nullable=True)
    contact_coverage = Column(Float, nullable=True)
    smb_share = Column(Float, nullable=True)
    whatsapp_cta_share = Column(Float, nullable=True)
    category_hhi = Column(Float, nullable=True)
    sample_ok = Column(Boolean, default=True, nullable=False)
    metrics_version = Column(String(50), default="v1.0", nullable=False)


# ============================================================================
# 6. APPLICATION USERS & AUDIT
# ============================================================================

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(50), default="viewer", nullable=False)  # viewer | marketing | compliance | admin
    reveal_quota_daily = Column(Integer, default=200, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(AutoBigId, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # reveal | export | search | optout
    target_type = Column(String(50), nullable=True)
    target_id = Column(String(100), nullable=True)
    meta = Column(JSON, default=dict)
    ip = Column(String(50), nullable=True)
    at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class Export(Base):
    __tablename__ = "exports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    params = Column(JSON, default=dict, nullable=False)
    row_count = Column(Integer, default=0)
    status = Column(String(50), default="pending", nullable=False)
    s3_key = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    params = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
