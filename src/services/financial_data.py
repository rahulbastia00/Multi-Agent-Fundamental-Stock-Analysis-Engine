# src/services/financial_data.py
import yfinance as yf
import pandas as pd
import json
import numpy as np
from sqlalchemy.orm import Session
from src.db import models

def fetch_and_store_statements(db: Session, ticker: str):
    """Fetches and stores income statement, balance sheet, and cash flow for a ticker."""
    stock = yf.Ticker(ticker)
        
    # This is a dictionary mapping each type of financial statement to its actual data from Yahoo Finance
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

def convert_numpy_types(value):
    """Convert NumPy types to standard Python types."""
    if pd.isna(value):
        return None
    if isinstance(value, np.integer):
        return int(value)
    elif isinstance(value, np.floating):
        return float(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, (np.number)):
        # Catch any other numpy number types
        return float(value)
    return value

def get_ohlcv(ticker: str, period: str = "1y", db: Session = None) -> pd.DataFrame:
    """Fetches OHLCV data and stores it in the database."""
    print(f"--- RUNNING get_ohlcv for {ticker} with period {period} ---")
    
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    
    print(f"--- Fetched {len(hist)} records from yfinance ---")

    if db and not hist.empty:
        print("--- Starting database insertion ---")
        try:
            records_processed = 0
            records_skipped = 0
            
            # Iterate over the fetched data and save it to the database
            for date, row in hist.iterrows():
                ticker_upper = ticker.upper()
                record_date = date.date()
                
                # Check if record already exists
                existing_record = db.query(models.OhlcvData).filter(
                    models.OhlcvData.ticker == ticker_upper,
                    models.OhlcvData.date == record_date
                ).first()
                
                if existing_record:
                    print(f"--- Record for {record_date} already exists, skipping ---")
                    records_skipped += 1
                    continue
                
                # Convert values to handle NumPy types
                open_val = convert_numpy_types(row['Open'])
                high_val = convert_numpy_types(row['High'])
                low_val = convert_numpy_types(row['Low'])
                close_val = convert_numpy_types(row['Close'])
                volume_val = convert_numpy_types(row['Volume'])
                
                # Create new record
                db_record = models.OhlcvData(
                    ticker=ticker_upper,
                    date=record_date,
                    open=open_val,
                    high=high_val,
                    low=low_val,
                    close=close_val,
                    volume=volume_val
                )
                
                db.add(db_record)
                records_processed += 1
                    
            print(f"--- Committing {records_processed} new records to database ---")
            print(f"--- Skipped {records_skipped} duplicate records ---")
            db.commit()
            print("--- Database commit successful ---")
            
        except Exception as e:
            print(f"--- Database error occurred: {str(e)} ---")
            db.rollback()
            raise e
    else:
        print("--- Skipping database insertion (no db session or empty data) ---")

    return hist