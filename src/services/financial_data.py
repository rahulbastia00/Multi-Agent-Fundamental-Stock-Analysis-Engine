# src/services/financial_data.py
import yfinance as yf
import pandas as pd
import json
from sqlalchemy.orm import Session
from src.db import models
from src.core.config import settings

def fetch_and_store_statements(db: Session, ticker: str):
    """
    Fetches and stores income statement, balance sheet, and cash flow for a ticker.
    This function is idempotent and will skip records that already exist.
    """
    stock = yf.Ticker(ticker)
    
    statement_map = {
        "income_statement": stock.income_stmt,
        "balance_sheet": stock.balance_sheet,
        "cash_flow": stock.cashflow
    }

    new_records_count = 0
    for statement_type, data_df in statement_map.items():
        if data_df.empty:
            continue
            
        data_df = data_df.T
        for period, statement_data in data_df.iterrows():
            record_date = period.date()
            
            # --- FIX: Check if the record already exists ---
            exists = db.query(models.FinancialStatement).filter(
                models.FinancialStatement.ticker == ticker.upper(),
                models.FinancialStatement.statement_type == statement_type,
                models.FinancialStatement.period == record_date
            ).first()

            # If it doesn't exist, create and add it
            if not exists:
                record_data = json.loads(statement_data.to_json())
                
                db_record = models.FinancialStatement(
                    ticker=ticker.upper(),
                    statement_type=statement_type,
                    period=record_date,
                    data=record_data
                )
                db.add(db_record)
                new_records_count += 1

    if new_records_count > 0:
        db.commit()
        return {"message": f"Successfully fetched and stored {new_records_count} new statements for {ticker}."}
    else:
        return {"message": f"All financial statements for {ticker} are already up-to-date."}


def get_ohlcv(ticker: str, period: str = "1y", db: Session = None) -> pd.DataFrame:
    """Fetches OHLCV data and stores it in the database."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    if db and not hist.empty:
        for date, row in hist.iterrows():
            db_record = models.OhlcvData(
                ticker=ticker.upper(),
                date=date.date(),
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume'])
            )
            db.merge(db_record)
        db.commit()

    return hist

def get_earnings_calendar(ticker: str, horizon: str = "3month") -> dict:
    """
    Fetches the earnings calendar for a given ticker from Alpha Vantage by reading the CSV endpoint.
    """
    api_key = settings.ALPHA_VANTAGE_API_KEY
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return {"error": "Alpha Vantage API key is not configured."}
        
    try:
        url = f"https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon={horizon}&apikey={api_key}&datatype=csv"
        data_df = pd.read_csv(url)
        
        if data_df.empty:
            return {"error": "Failed to fetch data from Alpha Vantage. The API returned no data."}

        earnings_data = data_df[data_df['symbol'] == ticker.upper()]
        
        if earnings_data.empty:
            return {"message": f"No earnings data found for {ticker} in the next {horizon}."}
            
        return earnings_data.to_dict(orient='records')
        
    except Exception as e:
        return {"error": f"An unexpected error occurred while fetching earnings data: {str(e)}"}