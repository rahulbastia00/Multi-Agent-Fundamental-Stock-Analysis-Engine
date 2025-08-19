# src/services/financial_data.py
import yfinance as yf
import pandas as pd
import json
from sqlalchemy.orm import Session
from src.db import models
from src.core.config import settings

def fetch_and_store_statements(db: Session, ticker: str):
    """Fetches and stores income statement, balance sheet, and cash flow for a ticker."""
    stock = yf.Ticker(ticker)
    
    statement_map = {
        "income_statement": stock.income_stmt,
        "balance_sheet": stock.balance_sheet,
        "cash_flow": stock.cashflow
    }

    new_records = []
    for statement_type, data_df in statement_map.items():
        if data_df.empty:
            continue
            
        data_df = data_df.T
        for period, statement_data in data_df.iterrows():
            record_data = json.loads(statement_data.to_json())
            
            db_record = models.FinancialStatement(
                ticker=ticker.upper(),
                statement_type=statement_type,
                period=period.date(),
                data=record_data
            )
            
            db.merge(db_record)
            new_records.append(db_record)

    db.commit()
    return {"message": f"Successfully fetched and stored {len(new_records)} statements for {ticker}"}

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
    print("--- [DEBUG] Attempting to fetch earnings calendar from CSV endpoint ---")
    
    api_key = settings.ALPHA_VANTAGE_API_KEY
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("--- [DEBUG] Alpha Vantage API key is missing. ---")
        return {"error": "Alpha Vantage API key is not configured."}
        
    try:
        # Construct the API URL for the CSV data
        url = f"https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon={horizon}&apikey={api_key}&datatype=csv"
        
        # Use pandas to directly read the CSV data from the URL
        data_df = pd.read_csv(url)
        
        if data_df.empty:
            return {"error": "Failed to fetch data from Alpha Vantage. The API returned no data."}

        print(f"--- [DEBUG] Fetched {len(data_df)} total earnings events ---")

        # Filter the DataFrame for the specific ticker
        earnings_data = data_df[data_df['symbol'] == ticker.upper()]
        
        if earnings_data.empty:
            return {"message": f"No earnings data found for {ticker} in the next {horizon}."}
            
        return earnings_data.to_dict(orient='records')
        
    except Exception as e:
        print(f"--- [DEBUG] An unexpected error occurred: {e} ---")
        return {"error": f"An unexpected error occurred while fetching earnings data: {str(e)}"}
