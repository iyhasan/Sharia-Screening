from __future__ import annotations

from decimal import Decimal
from typing import Optional

import yfinance as yf

from sharia_screener.models import CompanyProfile, Financials
from sharia_screener.providers.base import DataProvider
from sharia_screener.providers.sec_xbrl_provider import SecXbrlProvider
from sharia_screener.screening import PROHIBITED_KEYWORDS


class CombinedProvider(DataProvider):
    """
    Combine SEC XBRL (filings) + yfinance (market data) without supplemental inputs.
    Returns None if any required field is missing.
    """

    def __init__(self, sec_user_agent: Optional[str] = None, segment_rules: Optional[dict] = None):
        self.sec = SecXbrlProvider(user_agent=sec_user_agent, segment_rules=segment_rules)
        self.segment_rules = segment_rules or {}

    def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        # Prefer SEC profile, fallback to yfinance
        profile = self.sec.get_company_profile(ticker)
        if profile:
            return profile

        info = yf.Ticker(ticker).info or {}
        if not info:
            return None
        return CompanyProfile(
            ticker=ticker.upper(),
            name=info.get("shortName") or info.get("longName") or "",
            sector=info.get("sector") or "",
            industry=info.get("industry") or "",
            prohibited_activities=[],
        )

    def _yfinance_financials(self, ticker: str) -> dict:
        t = yf.Ticker(ticker)
        info = t.info or {}
        balance_sheet = t.balance_sheet
        income_stmt = t.financials
        business_summary = info.get("longBusinessSummary") or ""

        def _latest_value(df, key: str) -> Optional[Decimal]:
            if df is None or df.empty or key not in df.index:
                return None
            value = df.loc[key].iloc[0]
            if value is None:
                return None
            return Decimal(str(value))

        market_cap = info.get("marketCap")
        shares_outstanding = info.get("sharesOutstanding")
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
            "market_cap": market_cap,
            "outstanding_shares": shares_outstanding,
            "total_income": total_income,
            "total_assets": total_assets,
            "tangible_assets": tangible_assets,
            "interest_bearing_debt": interest_bearing_debt,
            "cash_equivalents": cash_equivalents,
            "business_summary": business_summary,
        }

    def get_financials(self, ticker: str) -> Optional[Financials]:
        # Start with SEC data
        sec_fin = self.sec.get_financials(ticker)
        yf_fin = self._yfinance_financials(ticker)

        # Combine required fields, preferring SEC for filings-based values and yfinance for market cap
        market_cap = yf_fin.get("market_cap")
        interest_bearing_debt = sec_fin.interest_bearing_debt if sec_fin else yf_fin.get("interest_bearing_debt")
        total_income = sec_fin.total_income if sec_fin else yf_fin.get("total_income")
        total_assets = sec_fin.total_assets if sec_fin else yf_fin.get("total_assets")
        tangible_assets = sec_fin.tangible_assets if sec_fin else yf_fin.get("tangible_assets")
        outstanding_shares = sec_fin.outstanding_shares if sec_fin else yf_fin.get("outstanding_shares")
        as_of = sec_fin.as_of if sec_fin else None

        estimation_notes = []

        # Estimate interest-bearing deposits using cash equivalents when available
        cash_equivalents = yf_fin.get("cash_equivalents")
        if cash_equivalents is not None:
            interest_bearing_deposits = cash_equivalents
            estimation_notes.append("interest_bearing_deposits estimated from cash and cash equivalents")
        else:
            interest_bearing_deposits = Decimal("0")
            estimation_notes.append("interest_bearing_deposits assumed 0 due to missing cash data")

        # Estimate non-permissible income using keyword match on business summary
        non_permissible_income = None
        if total_income is not None:
            summary = (yf_fin.get("business_summary") or "").lower()
            rules = self.segment_rules or {}
            prohibited = [k.lower() for k in rules.get("prohibited_keywords", [])] or [
                k.lower() for k in PROHIBITED_KEYWORDS
            ]
            allowed = [k.lower() for k in rules.get("allowed_keywords", [])]

            if any(k in summary for k in allowed):
                non_permissible_income = Decimal("0")
                estimation_notes.append("non_permissible_income estimated at 0% (allowed keyword match)")
            elif any(k in summary for k in prohibited):
                non_permissible_income = (total_income * Decimal("0.05")).quantize(Decimal("0.0001"))
                estimation_notes.append("non_permissible_income estimated at 5% of total income (keyword match)")
            else:
                non_permissible_income = Decimal("0")
                estimation_notes.append("non_permissible_income estimated at 0% (no prohibited keywords found)")

        required = {
            "market_cap": market_cap,
            "interest_bearing_debt": interest_bearing_debt,
            "interest_bearing_deposits": interest_bearing_deposits,
            "total_income": total_income,
            "non_permissible_income": non_permissible_income,
            "total_assets": total_assets,
            "tangible_assets": tangible_assets,
            "outstanding_shares": outstanding_shares,
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
            outstanding_shares=Decimal(str(outstanding_shares)),
            as_of=str(as_of),
            estimation_notes=estimation_notes,
        )
