# These are the public-facing HTTP endpoints. They depend on 
# the service layer to perform actions.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.services import financial_data
from src.db.session import get_db 

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

# @router.get("/ohlcv/{ticker}")
@router.get("/ohlcv/{ticker}")
def get_ohlcv_data(ticker: str, period: str = "1y", db: Session = Depends(get_db)):
    """
    Retrieves and caches historical OHLCV data for a given ticker.
    """
    try:
        # Pass the db session to the service function
        data = financial_data.get_ohlcv(ticker, period, db)
        return data.to_dict(orient="index")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Data not found for ticker {ticker}: {e}")
    
@router.get("/earnings/{ticker}")
def get_earnings_data(ticker: str, horizon: str = "3month"):
    """
    Retrieves the earnings calendar for a given ticker from Alpha Vantage.
    """
    try:
        data = financial_data.get_earnings_calendar(ticker, horizon)
        if "error" in data:
            raise HTTPException(status_code=429, detail=data["error"])
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))