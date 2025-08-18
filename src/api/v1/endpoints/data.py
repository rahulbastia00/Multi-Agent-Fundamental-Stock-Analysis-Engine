
# These are the public-facing HTTP endpoints. They depend on 
# the service layer to perform actions.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.services import financial_data

router = APIRouter()

@router.post("/fetch/{ticker}", status_code=201)
def fetch_financials(ticker: str, db: Session = Depends(get_db)):
    """
    Triggers fetching and storing of financial statements for a given ticker.
    """
    try:
        result = financial_data.fetch_and_store_statements(db, ticker)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ohlcv/{ticker}")
def get_ohlcv_data(ticker: str, period: str = "1y"):
    """
    Retrieves historical OHLCV data for a given ticker.
    """
    try:
        data = financial_data.get_ohlcv(ticker, period)
        return data.to_dict(orient="index")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Data not found for ticker {ticker}: {e}")