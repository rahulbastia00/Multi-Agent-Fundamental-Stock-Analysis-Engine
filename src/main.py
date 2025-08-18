# src/main.py
from fastapi import FastAPI
from src.api.v1.router import api_router
from src.db.session import engine
from src.db import models

# Create DB tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Financial AI Agent API",
    description="API for fetching and processing financial data.",
    version="1.0.0"
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

# Include the versioned API router
app.include_router(api_router, prefix="/api/v1")

# To run: uvicorn src.main:app --reload