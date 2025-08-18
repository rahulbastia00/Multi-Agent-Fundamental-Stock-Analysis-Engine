# src/api/v1/router.py
from fastapi import APIRouter
from .endpoints import data

api_router = APIRouter()
api_router.include_router(data.router, prefix="/data", tags=["Financial Data"])