# src/services/financial_data.py
import yfinance as yf
import pandas as pd
import json
from sqlalchemy.orm import Session
from src.db import models

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
            
        # yfinance returns columns as periods, so we transpose and iterate
        data_df = data_df.T
        for period, statement_data in data_df.iterrows():
            # This serializes the pandas data to a JSON string and then parses it back
            # into a Python dictionary. This effectively converts all NumPy numeric types
            # into standard Python int/float types, which are safe for the database.
            record_data = json.loads(statement_data.to_json())
            
            db_record = models.FinancialStatement(
                ticker=ticker.upper(),
                statement_type=statement_type,
                period=period.date(),
                data=record_data
            )
            
            # Use merge to avoid duplicates based on the unique constraint
            db.merge(db_record)
            new_records.append(db_record)

    db.commit()
    return {"message": f"Successfully fetched and stored {len(new_records)} statements for {ticker}"}

def get_ohlcv(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetches OHLCV data."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist