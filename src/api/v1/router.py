
from fastapi import APIRouter
from src.api.v1.endpoints import data
from src.api.v1.endpoints import analysis

api_router = APIRouter()

api_router.include_router(data.router, prefix="/data", tags=["Financial Data"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
