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

        # Helper to safely get values, returning 0 if key is missing
        def safe_get(series, key, default=0):
            return series.get(key, default) or default

        # --- Ratio Calculations ---
        
        # P/E Ratio = Market Cap / Net Income
        net_income = safe_get(income_statement, 'NetIncome')
        pe_ratio = market_cap / net_income if net_income else None

        # P/B Ratio = Market Cap / Total Stockholder Equity (Book Value)
        book_value = safe_get(balance_sheet, 'StockholdersEquity')
        pb_ratio = market_cap / book_value if book_value else None

        # ROE = Net Income / Total Stockholder Equity
        roe = (net_income / book_value) * 100 if book_value else None

        # Altman Z-Score (for public, non-manufacturing firms)
        # Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
        # A = Working Capital / Total Assets
        # B = Retained Earnings / Total Assets
        # C = EBIT / Total Assets
        # D = Market Cap / Total Liabilities
        # E = Total Revenue / Total Assets
        total_assets = safe_get(balance_sheet, 'TotalAssets')
        working_capital = safe_get(balance_sheet, 'WorkingCapital')
        retained_earnings = safe_get(balance_sheet, 'RetainedEarnings')
        ebit = safe_get(income_statement, 'EBIT')
        total_liabilities = safe_get(balance_sheet, 'TotalLiabilitiesNetMinorityInterest')
        total_revenue = safe_get(income_statement, 'TotalRevenue')

        if total_assets > 0:
            A = working_capital / total_assets
            B = retained_earnings / total_assets
            C = ebit / total_assets
            D = market_cap / total_liabilities if total_liabilities else 0
            E = total_revenue / total_assets
            z_score = (1.2 * A) + (1.4 * B) + (3.3 * C) + (0.6 * D) + (1.0 * E)
        else:
            z_score = None

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
