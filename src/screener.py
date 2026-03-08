"""
Sharia Compliance Screener Core Module

Implements AAOIFI-based screening methodology using yfinance for data.
Supports business sector filtering and financial ratio validation.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ShariaComplianceResult:
    """Result of sharia compliance verification."""
    
    symbol: str
    is_compliant: bool
    business_screen: str  # "PASS" or "REJECTED"
    financial_screen: str  # "PASS" or "FAIL"
    debt_to_market_cap_pct: float
    cash_reserves_ratio: float
    purification_ratio: float
    sector: Optional[str]
    rejection_reason: Optional[str]
    screening_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary for export."""
        return {
            "symbol": self.symbol,
            "status": "COMPLIANT" if self.is_compliant else "NON_COMPLIANT",
            "business_screen": self.business_screen,
            "financial_screen": self.financial_screen,
            "debt_to_market_cap_pct": round(self.debt_to_market_cap_pct, 2),
            "cash_reserves_ratio_pct": round(self.cash_reserves_ratio * 100, 2),
            "purification_ratio_pct": round(self.purification_ratio * 100, 2),
            "sector": self.sector,
            "rejection_reason": self.rejection_reason,
            "screened_at": self.screening_timestamp.isoformat()
        }


class ShariaScreener:
    """
    Screen stocks for Sharia compliance using AAOIFI methodology.
    
    Uses yfinance for real market data and implements custom screening rules:
    - Business sector filtering (prohibited industries)
    - Financial ratio validation (debt < 33% of market cap)
    - Purification calculation for non-compliant revenue portions
    
    Environment variables:
    - None required - uses free yfinance API
    """
    
    # Prohibited sectors and keywords (immediate rejection)
    PROHIBITED_SECTORS = {
        "Financial Services", "Banks", "Insurance", "Asset Management",
        "Investment Banking", "Credit Unions", "Mortgage Lenders"
    }
    
    PROHIBITED_KEYWORDS = [
        "Alcohol", "Tobacco", "Gambling", "Casino",
        "Weapons", "Military", "Adult Entertainment", "Pornography"
    ]
    
    # Thresholds
    DEBT_RATIO_THRESHOLD = 33.0  # Maximum debt as % of market cap
    
    def __init__(self):
        pass
    
    def check_stock(self, symbol: str) -> ShariaComplianceResult:
        """
        Perform complete Sharia compliance check for a single stock.
        
        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "MSFT")
            
        Returns:
            ShariaComplianceResult with screening details
            
        Process:
        1. Fetch real-time data from Yahoo Finance
        2. Check business sector (immediate rejection if prohibited)
        3. Validate debt-to-market-cap ratio
        4. Calculate purification requirements
        """
        
        try:
            # Step 1: Download stock data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Step 2: Business sector screening
            business_result, rejection_reason = self._check_business_compliance(ticker, symbol)
            
            if not business_result["is_compliant"]:
                return ShariaComplianceResult(
                    symbol=symbol,
                    is_compliant=False,
                    business_screen="REJECTED",
                    financial_screen="N/A",
                    debt_to_market_cap_pct=0.0,
                    cash_reserves_ratio=0.0,
                    purification_ratio=0.0,
                    sector=info.get("sector"),
                    rejection_reason=rejection_reason
                )
            
            # Step 3: Financial ratio screening
            financial_result = self._check_financial_compliance(ticker, symbol)
            
            is_compliant = financial_result["is_compliant"]
            purification_ratio = financial_result["purification_ratio"] if not is_compliant else 0.0
            
            return ShariaComplianceResult(
                symbol=symbol,
                is_compliant=is_compliant,
                business_screen="PASS",
                financial_screen="PASS" if is_compliant else "FAIL",
                debt_to_market_cap_pct=financial_result["debt_ratio"],
                cash_reserves_ratio=financial_result["cash_ratio"],
                purification_ratio=purification_ratio,
                sector=info.get("sector"),
                rejection_reason=None
            )
            
        except Exception as e:
            return ShariaComplianceResult(
                symbol=symbol,
                is_compliant=False,
                business_screen="ERROR",
                financial_screen="ERROR",
                debt_to_market_cap_pct=0.0,
                cash_reserves_ratio=0.0,
                purification_ratio=0.0,
                sector=None,
                rejection_reason=f"Data fetch failed: {str(e)}"
            )
    
    def _check_business_compliance(self, ticker, symbol: str) -> Dict:
        """Check if company's business is Sharia-compliant."""
        
        try:
            # Get sector and industry info
            sector = ticker.info.get("sector", "")
            industry = ticker.info.get("industry", "")
            business_description = ticker.info.get("longBusinessSummary", "").lower()
            
            # Check prohibited sectors first
            if any(prohibited in sector for prohibited in self.PROHIBITED_SECTORS):
                return {
                    "is_compliant": False,
                    "reason": f"Prohibited sector: {sector}"
                }
            
            # Check prohibited keywords in name/description
            if any(keyword.lower() in business_description or keyword.lower() in industry.lower() 
                   for keyword in self.PROHIBITED_KEYWORDS):
                return {
                    "is_compliant": False,
                    "reason": f"Prohibited business type detected in: {sector} - {industry}"
                }
            
            # Check company name for prohibited items
            if any(keyword.lower() in ticker.info.get("shortName", "").lower() 
                   for keyword in self.PROHIBITED_KEYWORDS):
                return {
                    "is_compliant": False,
                    "reason": f"Prohibited item in company name: {ticker.info.get('shortName')}"
                }
            
            return {"is_compliant": True, "reason": None}
            
        except Exception as e:
            return {"is_compliant": False, "reason": str(e)}
    
    def _check_financial_compliance(self, ticker, symbol: str) -> Dict:
        """Check financial ratios for Sharia compliance."""
        
        try:
            # Get latest balance sheet data
            stats = ticker.stats
            
            # Calculate debt-to-market-cap ratio
            market_cap = float(ticker.info.get("marketCap", 0))
            total_debt = self._get_total_debt_from_financials(ticker)
            
            if market_cap > 0:
                debt_ratio = (total_debt / market_cap) * 100
            else:
                debt_ratio = 100.0  # Assume fail if no market cap
            
            # Check debt ratio threshold
            is_compliant = debt_ratio <= self.DEBT_RATIO_THRESHOLD
            
            # Get cash reserves for purification calculation
            balance_sheet = ticker.balance_sheet
            
            if not balance_sheet.empty:
                latest_cash = float(balance_sheet.iloc[0].get("Cash And Cash Equivalents", 0))
                total_assets = float(balance_sheet.iloc[0].get("Total Assets", 1))
                
                cash_ratio = latest_cash / total_assets if total_assets > 0 else 0
            else:
                cash_ratio = 0.0
            
            # Calculate purification ratio (simplified AAOIFI formula)
            # For companies with debt < 33% but not meeting other criteria
            purification_ratio = 0.0
            if not is_compliant and market_cap > 0:
                # Assume 2.5-10% non-compliant revenue based on debt level
                purification_ratio = min(0.10, max(0.025, debt_ratio / 330))
            
            return {
                "is_compliant": is_compliant,
                "debt_ratio": debt_ratio,
                "cash_ratio": cash_ratio,
                "purification_ratio": purification_ratio
            }
            
        except Exception as e:
            return {
                "is_compliant": False,
                "debt_ratio": 100.0,
                "cash_ratio": 0.0,
                "purification_ratio": 0.0,
                "error": str(e)
            }
    
    def _get_total_debt_from_financials(self, ticker) -> float:
        """Extract total debt from balance sheet."""
        
        try:
            balance_sheet = ticker.balance_sheet
            
            if balance_sheet.empty:
                return 0.0
            
            latest_row = balance_sheet.iloc[0]
            
            # Sum of short-term and long-term debt
            short_term_debt = float(latest_row.get("Short Long Term Debt", 0) or 
                                   latest_row.get("Short Term Debt", 0))
            long_term_debt = float(latest_row.get("Long Term Debt", 0) or 
                                  latest_row.get("Long Term Debt Capital Lease Obligation", 0))
            
            return short_term_debt + long_term_debt
            
        except Exception as e:
            return 0.0


# Global screener instance for convenience use
screener = ShariaScreener()
