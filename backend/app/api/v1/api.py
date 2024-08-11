# backend/app/api/v1/api.py

from fastapi import APIRouter
from app.api.v1.endpoints.analysis import router as analysis_router

api_router = APIRouter()
api_router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])