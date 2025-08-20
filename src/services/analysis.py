import yfinance as yf
from sqlalchemy.orm import Session
from src.db import models
import pandas as pd

def get_market_cap(ticker: str) -> float:
    """Gets the current market capitalization for a ticker."""
    stock = yf.Ticker(ticker)
    return stock.info.get('marketCap', 0)

def get_financial_data(db: Session, ticker: str) -> (pd.Series, pd.Series):
    """
    Retrieves the most recent balance sheet and income statement for a ticker.
    """
    # Fetch the latest balance sheet
    balance_sheet_record = db.query(models.FinancialStatement).filter(
        models.FinancialStatement.ticker == ticker.upper(),
        models.FinancialStatement.statement_type == 'balance_sheet'
    ).order_by(models.FinancialStatement.period.desc()).first()

    # Fetch the latest income statement
    income_statement_record = db.query(models.FinancialStatement).filter(
        models.FinancialStatement.ticker == ticker.upper(),
        models.FinancialStatement.statement_type == 'income_statement'
    ).order_by(models.FinancialStatement.period.desc()).first()

    if not balance_sheet_record or not income_statement_record:
        raise ValueError(f"Financial data not found for {ticker}. Please fetch it first.")

    balance_sheet = pd.Series(balance_sheet_record.data)
    income_statement = pd.Series(income_statement_record.data)
    
    return balance_sheet, income_statement

def calculate_financial_ratios(db: Session, ticker: str) -> dict:
    """
    Calculates a suite of financial ratios for a given ticker.
    """
    try:
        balance_sheet, income_statement = get_financial_data(db, ticker)
        market_cap = get_market_cap(ticker)

        # Helper to safely get values with multiple possible field names
        def safe_get(series, keys, default=0):
            """Try multiple field names and return the first non-null value found."""
            if isinstance(keys, str):
                keys = [keys]
            
            for key in keys:
                value = series.get(key)
                if value is not None and pd.notna(value):
                    return float(value) if value != 0 else 0
            return default

        # --- DEBUG: Print available keys ---
        print(f"DEBUG - Available Balance Sheet keys: {list(balance_sheet.keys())[:10]}...")
        print(f"DEBUG - Available Income Statement keys: {list(income_statement.keys())[:10]}...")

        # --- Ratio Calculations with Correct Field Names ---
        
        # P/E Ratio = Market Cap / Net Income
        net_income = safe_get(income_statement, [
            'Net Income', 'NetIncome', 'Net Income Common Stockholders'
        ])
        pe_ratio = market_cap / net_income if net_income and market_cap else None

        # P/B Ratio = Market Cap / Total Stockholder Equity (Book Value)
        book_value = safe_get(balance_sheet, [
            'Stockholders Equity', 'StockholdersEquity', 
            'Total Stockholders Equity', 'Total Equity'
        ])
        pb_ratio = market_cap / book_value if book_value and market_cap else None

        # ROE = Net Income / Total Stockholder Equity
        roe = (net_income / book_value) * 100 if book_value and net_income else None

        # Altman Z-Score Components
        total_assets = safe_get(balance_sheet, [
            'Total Assets', 'TotalAssets'
        ])
        
        # Working Capital = Current Assets - Current Liabilities
        current_assets = safe_get(balance_sheet, [
            'Current Assets', 'CurrentAssets', 'Total Current Assets'
        ])
        current_liabilities = safe_get(balance_sheet, [
            'Current Liabilities', 'CurrentLiabilities', 'Total Current Liabilities'
        ])
        working_capital = current_assets - current_liabilities if current_assets and current_liabilities else 0
        
        retained_earnings = safe_get(balance_sheet, [
            'Retained Earnings', 'RetainedEarnings'
        ])
        
        # EBIT calculation: Operating Income or EBIT
        ebit = safe_get(income_statement, [
            'EBIT', 'Operating Income', 'OperatingIncome'
        ])
        # If EBIT not available, calculate as: Net Income + Interest Expense + Tax
        if not ebit:
            interest_expense = safe_get(income_statement, [
                'Interest Expense', 'InterestExpense', 'Interest Expense Non Operating'
            ])
            tax_provision = safe_get(income_statement, [
                'Tax Provision', 'TaxProvision', 'Income Tax Expense'
            ])
            ebit = net_income + abs(interest_expense) + tax_provision if net_income else 0
        
        total_liabilities = safe_get(balance_sheet, [
            'Total Liabilities Net Minority Interest', 'TotalLiabilitiesNetMinorityInterest',
            'Total Liabilities', 'TotalLiabilities'
        ])
        
        total_revenue = safe_get(income_statement, [
            'Total Revenue', 'TotalRevenue', 'Revenue'
        ])

        # Calculate Altman Z-Score
        if total_assets > 0:
            A = working_capital / total_assets
            B = retained_earnings / total_assets
            C = ebit / total_assets
            D = market_cap / total_liabilities if total_liabilities else 0
            E = total_revenue / total_assets
            z_score = (1.2 * A) + (1.4 * B) + (3.3 * C) + (0.6 * D) + (1.0 * E)
        else:
            z_score = None

        # DEBUG: Print calculated values
        print(f"DEBUG - Calculated values for {ticker}:")
        print(f"  Net Income: {net_income}")
        print(f"  Book Value: {book_value}")
        print(f"  Market Cap: {market_cap}")
        print(f"  Total Assets: {total_assets}")

        return {
            "p_e_ratio": pe_ratio,
            "p_b_ratio": pb_ratio,
            "return_on_equity_percent": roe,
            "altman_z_score": z_score
        }

    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        return {"error": f"An unexpected error occurred during analysis: {str(e)}"}