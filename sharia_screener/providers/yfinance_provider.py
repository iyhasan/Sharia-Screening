from __future__ import annotations

from decimal import Decimal
from typing import Optional

import yfinance as yf

from sharia_screener.models import CompanyProfile, Financials
from sharia_screener.providers.base import DataProvider


class YFinanceProvider(DataProvider):
    def __init__(self, supplemental: Optional[dict] = None):
        self.supplemental = supplemental or {}

    def _supplement(self, ticker: str) -> dict:
        return self.supplemental.get("companies", {}).get(ticker.upper(), {})

    def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        info = yf.Ticker(ticker).info or {}
        supp = self._supplement(ticker)
        profile_override = supp.get("profile", {})

        name = profile_override.get("name") or info.get("shortName") or info.get("longName") or ""
        sector = profile_override.get("sector") or info.get("sector") or ""
        industry = profile_override.get("industry") or info.get("industry") or ""
        prohibited = profile_override.get("prohibited_activities", []) or []

        if not name and not sector and not industry:
            return None

        return CompanyProfile(
            ticker=ticker.upper(),
            name=name,
            sector=sector,
            industry=industry,
            prohibited_activities=prohibited,
        )

    def get_financials(self, ticker: str) -> Optional[Financials]:
        t = yf.Ticker(ticker)
        info = t.info or {}
        supp = self._supplement(ticker)
        fin_override = supp.get("financials", {})

        balance_sheet = t.balance_sheet
        income_stmt = t.financials

        def _latest_value(df, key: str) -> Optional[Decimal]:
            if df is None or df.empty or key not in df.index:
                return None
            value = df.loc[key].iloc[0]
            if value is None:
                return None
            return Decimal(str(value))

        market_cap = info.get("marketCap") or fin_override.get("market_cap")
        shares_outstanding = info.get("sharesOutstanding") or fin_override.get("outstanding_shares")
        total_income = (
            _latest_value(income_stmt, "Total Revenue")
            or _latest_value(income_stmt, "TotalRevenue")
            or fin_override.get("total_income")
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

        total_assets = _latest_value(balance_sheet, "Total Assets") or fin_override.get("total_assets")
        tangible_assets = (
            _latest_value(balance_sheet, "Net Tangible Assets")
            or fin_override.get("tangible_assets")
        )

        interest_bearing_deposits = fin_override.get("interest_bearing_deposits")
        non_permissible_income = fin_override.get("non_permissible_income")
        as_of = fin_override.get("as_of")

        required = {
            "market_cap": market_cap,
            "interest_bearing_debt": interest_bearing_debt,
            "interest_bearing_deposits": interest_bearing_deposits,
            "total_income": total_income,
            "non_permissible_income": non_permissible_income,
            "total_assets": total_assets,
            "tangible_assets": tangible_assets,
            "outstanding_shares": shares_outstanding,
            "as_of": as_of,
        }

        if any(v is None for v in required.values()):
            return None

        return Financials(
            market_cap=Decimal(str(market_cap)),
            interest_bearing_debt=Decimal(str(interest_bearing_debt)),
            interest_bearing_deposits=Decimal(str(interest_bearing_deposits)),
            total_income=Decimal(str(total_income)),
            non_permissible_income=Decimal(str(non_permissible_income)),
            total_assets=Decimal(str(total_assets)),
            tangible_assets=Decimal(str(tangible_assets)),
            outstanding_shares=Decimal(str(shares_outstanding)),
            as_of=str(as_of),
            estimation_notes=[],
        )
