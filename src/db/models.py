# src/db/models.py
from sqlalchemy import Column, String, Integer, Float, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from .session import Base

class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    statement_type = Column(String, nullable=False) # e.g., 'income_statement', 'balance_sheet'
    period = Column(Date, nullable=False)
    data = Column(JSONB, nullable=False) # Store the entire statement as JSON

    __table_args__ = (UniqueConstraint('ticker', 'statement_type', 'period', name='_ticker_statement_period_uc'),)



class OhlcvData(Base):
    __tablename__ = "ohlcv_data"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('ticker', 'date', name='_ticker_date_uc'),)