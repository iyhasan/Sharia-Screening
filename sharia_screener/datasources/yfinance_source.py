from __future__ import annotations

from decimal import Decimal
from typing import Optional

import yfinance as yf


class YFinanceSource:
    def get_profile(self, ticker: str) -> dict:
        info = yf.Ticker(ticker).info or {}
        return {
            "name": info.get("shortName") or info.get("longName") or "",
            "sector": info.get("sector") or "",
            "industry": info.get("industry") or "",
            "business_summary": info.get("longBusinessSummary") or "",
        }

    def get_market_data(self, ticker: str) -> dict:
        info = yf.Ticker(ticker).info or {}
        return {
            "market_cap": info.get("marketCap"),
            "shares_outstanding": info.get("sharesOutstanding"),
        }

    def get_financials(self, ticker: str) -> dict:
        t = yf.Ticker(ticker)
        balance_sheet = t.balance_sheet
        income_stmt = t.financials

        def _latest_value(df, key: str) -> Optional[Decimal]:
            if df is None or df.empty or key not in df.index:
                return None
            value = df.loc[key].iloc[0]
            if value is None:
                return None
            return Decimal(str(value))

        total_income = (
            _latest_value(income_stmt, "Total Revenue")
            or _latest_value(income_stmt, "TotalRevenue")
        )
        total_assets = _latest_value(balance_sheet, "Total Assets")
        tangible_assets = _latest_value(balance_sheet, "Net Tangible Assets")
        cash_equivalents = _latest_value(balance_sheet, "Cash And Cash Equivalents") or _latest_value(
            balance_sheet, "Cash And Cash Equivalents At Carrying Value"
        )

        short_term_debt = _latest_value(balance_sheet, "Short Long Term Debt") or _latest_value(
            balance_sheet, "Short Term Debt"
        )
        long_term_debt = _latest_value(balance_sheet, "Long Term Debt") or _latest_value(
            balance_sheet, "Long Term Debt And Capital Lease Obligation"
        )
        interest_bearing_debt = None
        if short_term_debt is not None or long_term_debt is not None:
            interest_bearing_debt = (short_term_debt or Decimal("0")) + (long_term_debt or Decimal("0"))

        return {
            "total_income": total_income,
            "total_assets": total_assets,
            "tangible_assets": tangible_assets,
            "cash_equivalents": cash_equivalents,
            "interest_bearing_debt": interest_bearing_debt,
        }
