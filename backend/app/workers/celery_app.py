"""Celery Distributed Worker & Task Queue Architecture."""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "adatlas",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.workers.tasks.collect_*": {"queue": "q.collect"},
        "app.workers.tasks.normalize_*": {"queue": "q.normalize"},
        "app.workers.tasks.geo_*": {"queue": "q.geo"},
        "app.workers.tasks.enrich_*": {"queue": "q.enrich"},
        "app.workers.tasks.classify_*": {"queue": "q.classify"},
        "app.workers.tasks.analytics_*": {"queue": "q.analytics"},
        "app.workers.tasks.export_*": {"queue": "q.export"},
    },
    beat_schedule={
        # Tier 1 refresh: daily at 02:00 IST
        "t1-daily-refresh": {
            "task": "app.workers.tasks.refresh_t1_advertisers",
            "schedule": crontab(hour=2, minute=0),
        },
        # Daily city metrics analytics rollup: 04:00 IST
        "daily-analytics-rollup": {
            "task": "app.workers.tasks.compute_daily_city_metrics",
            "schedule": crontab(hour=4, minute=0),
        },
    },
)


@celery_app.task(name="app.workers.tasks.refresh_t1_advertisers")
def refresh_t1_advertisers():
    """Scheduled task refreshing high-priority advertisers."""
    return {"status": "t1_refresh_completed", "refreshed_count": 0}


@celery_app.task(name="app.workers.tasks.compute_daily_city_metrics")
def compute_daily_city_metrics():
    """Scheduled task computing trailing analytics rollups."""
    return {"status": "analytics_rollup_completed"}

