from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sharia_screener.models import CompanyProfile, Financials
from sharia_screener.providers.base import DataProvider
from sharia_screener.screening import PROHIBITED_KEYWORDS
from sharia_screener.datasources.yfinance_source import YFinanceSource
from sharia_screener.datasources.sec_xbrl_source import SecXbrlSource


class UnifiedProvider(DataProvider):
    """
    Single provider that combines multiple data sources (SEC XBRL + yfinance)
    and applies best-estimate heuristics when direct values are unavailable.
    """

    def __init__(self, sec_user_agent: Optional[str] = None, segment_rules: Optional[dict] = None):
        self.sec = SecXbrlSource(user_agent=sec_user_agent)
        self.yf = YFinanceSource()
        self.segment_rules = segment_rules or {}

    def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        profile = self.sec.get_profile(ticker) or {}
        if not profile:
            profile = self.yf.get_profile(ticker) or {}

        if not profile:
            return None

        return CompanyProfile(
            ticker=ticker.upper(),
            name=profile.get("name", ""),
            sector=profile.get("sector", ""),
            industry=profile.get("industry", ""),
            prohibited_activities=[],
        )

    def _segment_rules(self) -> tuple[list[str], list[str]]:
        prohibited = [k.lower() for k in self.segment_rules.get("prohibited_keywords", [])]
        allowed = [k.lower() for k in self.segment_rules.get("allowed_keywords", [])]
        if not prohibited:
            prohibited = [k.lower() for k in PROHIBITED_KEYWORDS]
        return prohibited, allowed

    def _estimate_non_permissible_from_segments(self, segments: list[dict]) -> Optional[Decimal]:
        if not segments:
            return None
        prohibited, allowed = self._segment_rules()
        total = Decimal("0")
        for seg in segments:
            name = str(seg.get("name", "")).lower()
            revenue = seg.get("revenue")
            if revenue is None:
                continue
            if any(k in name for k in allowed):
                continue
            if any(k in name for k in prohibited):
                total += Decimal(str(revenue))
        return total

    def get_financials(self, ticker: str) -> Optional[Financials]:
        sec_fin = self.sec.get_financials(ticker)
        yf_fin = self.yf.get_financials(ticker)
        yf_market = self.yf.get_market_data(ticker)
        yf_profile = self.yf.get_profile(ticker)

        market_cap = yf_market.get("market_cap")
        interest_bearing_debt = sec_fin.get("interest_bearing_debt") or yf_fin.get("interest_bearing_debt")
        total_income = sec_fin.get("total_income") or yf_fin.get("total_income")
        total_assets = sec_fin.get("total_assets") or yf_fin.get("total_assets")
        tangible_assets = sec_fin.get("tangible_assets") or yf_fin.get("tangible_assets")
        outstanding_shares = sec_fin.get("shares_outstanding") or yf_market.get("shares_outstanding")
        as_of = sec_fin.get("as_of")

        estimation_notes = []
        if market_cap is not None and as_of:
            estimation_notes.append(f"market cap is current; financials as of {as_of}")

        # Estimate interest-bearing deposits using cash equivalents
        cash_equivalents = sec_fin.get("cash_equivalents") or yf_fin.get("cash_equivalents")
        if cash_equivalents is not None:
            interest_bearing_deposits = cash_equivalents
            estimation_notes.append("interest_bearing_deposits estimated from cash and cash equivalents")
        else:
            interest_bearing_deposits = Decimal("0")
            estimation_notes.append("interest_bearing_deposits assumed 0 due to missing cash data")

        # Estimate non-permissible income
        non_permissible_income = Decimal("0")
        has_non_perm_signal = False

        interest_income = sec_fin.get("interest_income")
        if interest_income is not None:
            non_permissible_income += interest_income
            has_non_perm_signal = True
            estimation_notes.append("non_permissible_income includes SEC-reported interest income")

        segments = self.sec.get_revenue_segments(ticker)
        segment_estimate = self._estimate_non_permissible_from_segments(segments)
        if segment_estimate is not None:
            non_permissible_income += segment_estimate
            has_non_perm_signal = True
            estimation_notes.append("non_permissible_income includes prohibited SEC segment revenues")

        if not has_non_perm_signal and total_income is not None:
            summary = (yf_profile.get("business_summary") or "").lower()
            prohibited, allowed = self._segment_rules()
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
