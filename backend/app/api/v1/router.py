"""Aggregate API v1 Router."""

from fastapi import APIRouter
from app.api.v1.cities import router as cities_router
from app.api.v1.search import router as search_router
from app.api.v1.advertisers import router as advertisers_router
from app.api.v1.compare import router as compare_router
from app.api.v1.exports import router as exports_router
from app.api.v1.optout import router as optout_router
from app.api.v1.admin import router as admin_router

api_v1_router = APIRouter()

api_v1_router.include_router(cities_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(advertisers_router)
api_v1_router.include_router(compare_router)
api_v1_router.include_router(exports_router)
api_v1_router.include_router(optout_router)
api_v1_router.include_router(admin_router)

