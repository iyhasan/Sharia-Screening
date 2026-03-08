from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional

from sharia_screener.models import ScreeningResult
from sharia_screener.providers.base import DataProvider


AAOIFI_CITATIONS = {
    "sector_exclusion": "AAOIFI §2/1, §3/4/1",
    "debt_ratio": "AAOIFI §3/4/2",
    "deposits_ratio": "AAOIFI §3/4/3",
    "non_perm_income": "AAOIFI §3/4/4",
    "tangible_assets": "AAOIFI §3/1 note, Basis B item 18",
    "data_period": "AAOIFI §3/4/5",
    "purification": "AAOIFI §3/4/6/1–§3/4/6/4",
}

DEFAULT_THRESHOLDS = {
    "debt_to_market_cap": Decimal("0.30"),
    "deposits_to_market_cap": Decimal("0.30"),
    "non_perm_income_pct": Decimal("0.05"),
    "tangible_assets_pct": Decimal("0.3333"),
}

PROHIBITED_KEYWORDS = {
    "alcohol",
    "liquor",
    "pork",
    "swine",
    "gambling",
    "casino",
    "riba",
    "interest-based lending",
    "conventional banking",
    "tobacco",
}


class ScreenEngine:
    def __init__(self, provider: DataProvider, thresholds: Optional[dict] = None):
        self.provider = provider
        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    def _ratio(self, numerator: Decimal, denominator: Decimal) -> Optional[Decimal]:
        try:
            if denominator == 0:
                return None
            return (numerator / denominator).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ZeroDivisionError):
            return None

    def _pct(self, numerator: Decimal, denominator: Decimal) -> Optional[Decimal]:
        ratio = self._ratio(numerator, denominator)
        if ratio is None:
            return None
        return (ratio * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _report(self, result: ScreeningResult) -> str:
        if result.status == "insufficient_data":
            return f"{result.ticker}: insufficient data to evaluate."
        verdict = "compliant" if result.compliant else "non-compliant"
        lines = [f"{result.ticker}: {verdict}."]
        if result.reason_codes:
            lines.append("Reasons: " + ", ".join(result.reason_codes))
        ratios = result.ratios
        lines.append(
            "Ratios: debt/market_cap={d}, deposits/market_cap={dep}, non_perm_income%={npi}, tangible_assets%={ta}".format(
                d=ratios.get("debt_to_market_cap"),
                dep=ratios.get("interest_deposits_to_market_cap"),
                npi=ratios.get("non_permissible_income_pct"),
                ta=ratios.get("tangible_assets_pct"),
            )
        )
        if result.wash_percentage is not None:
            lines.append(f"Wash %: {result.wash_percentage}")
        if result.wash_amount_per_share is not None:
            lines.append(f"Wash per share: {result.wash_amount_per_share}")
        if result.investor_wash_amount is not None:
            lines.append(f"Investor wash amount: {result.investor_wash_amount}")
        return " ".join(lines)

    def screen(self, ticker: str, shares_held: Optional[Decimal] = None) -> ScreeningResult:
        ticker = ticker.upper()
        profile = self.provider.get_company_profile(ticker)
        financials = self.provider.get_financials(ticker)

        if not profile or not financials:
            return ScreeningResult(
                ticker=ticker,
                compliant=False,
                status="insufficient_data",
                reason_codes=["missing_required_data"],
                ratios={
                    "debt_to_market_cap": None,
                    "interest_deposits_to_market_cap": None,
                    "non_permissible_income_pct": None,
                    "tangible_assets_pct": None,
                },
                wash_percentage=None,
                wash_amount_per_share=None,
                citations=[AAOIFI_CITATIONS["data_period"]],
                report=f"{ticker}: insufficient data to evaluate.",
            )

        # Sector/activity exclusions
        prohibited = set(map(str.lower, profile.prohibited_activities or []))
        if any(keyword in prohibited for keyword in PROHIBITED_KEYWORDS):
            result = ScreeningResult(
                ticker=ticker,
                compliant=False,
                status="non_compliant",
                reason_codes=["prohibited_activity"],
                ratios={
                    "debt_to_market_cap": None,
                    "interest_deposits_to_market_cap": None,
                    "non_permissible_income_pct": None,
                    "tangible_assets_pct": None,
                },
                wash_percentage=None,
                wash_amount_per_share=None,
                citations=[AAOIFI_CITATIONS["sector_exclusion"]],
                report="",
            )
            result.report = self._report(result)
            return result

        debt_ratio = self._ratio(financials.interest_bearing_debt, financials.market_cap)
        deposits_ratio = self._ratio(
            financials.interest_bearing_deposits, financials.market_cap
        )
        non_perm_income_ratio = self._ratio(
            financials.non_permissible_income, financials.total_income
        )
        tangible_assets_ratio = self._ratio(
            financials.tangible_assets, financials.total_assets
        )

        ratios = {
            "debt_to_market_cap": debt_ratio,
            "interest_deposits_to_market_cap": deposits_ratio,
            "non_permissible_income_pct": self._pct(
                financials.non_permissible_income, financials.total_income
            ),
            "tangible_assets_pct": self._pct(financials.tangible_assets, financials.total_assets),
        }

        reason_codes = []
        citations = [
            AAOIFI_CITATIONS["debt_ratio"],
            AAOIFI_CITATIONS["deposits_ratio"],
            AAOIFI_CITATIONS["non_perm_income"],
            AAOIFI_CITATIONS["tangible_assets"],
        ]

        compliant = True

        if debt_ratio is None or deposits_ratio is None or non_perm_income_ratio is None or tangible_assets_ratio is None:
            return ScreeningResult(
                ticker=ticker,
                compliant=False,
                status="insufficient_data",
                reason_codes=["invalid_ratio_calculation"],
                ratios=ratios,
                wash_percentage=None,
                wash_amount_per_share=None,
                citations=[AAOIFI_CITATIONS["data_period"]],
                report=f"{ticker}: insufficient data to evaluate.",
            )

        if debt_ratio > self.thresholds["debt_to_market_cap"]:
            compliant = False
            reason_codes.append("debt_ratio_exceeded")
        if deposits_ratio > self.thresholds["deposits_to_market_cap"]:
            compliant = False
            reason_codes.append("deposit_ratio_exceeded")
        if non_perm_income_ratio > self.thresholds["non_perm_income_pct"]:
            compliant = False
            reason_codes.append("non_permissible_income_exceeded")
        if tangible_assets_ratio < self.thresholds["tangible_assets_pct"]:
            compliant = False
            reason_codes.append("tangible_assets_below_threshold")

        wash_percentage = None
        wash_amount_per_share = None
        investor_wash = None

        if compliant and financials.non_permissible_income > 0 and financials.total_income > 0:
            wash_percentage = self._pct(
                financials.non_permissible_income, financials.total_income
            )
            if financials.outstanding_shares > 0:
                wash_amount_per_share = (
                    financials.non_permissible_income / financials.outstanding_shares
                ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                if shares_held is not None:
                    investor_wash = (wash_amount_per_share * shares_held).quantize(
                        Decimal("0.0001"), rounding=ROUND_HALF_UP
                    )

        result = ScreeningResult(
            ticker=ticker,
            compliant=compliant,
            status="compliant" if compliant else "non_compliant",
            reason_codes=reason_codes,
            ratios=ratios,
            wash_percentage=wash_percentage,
            wash_amount_per_share=wash_amount_per_share,
            citations=citations + [AAOIFI_CITATIONS["purification"]],
            report="",
            investor_wash_amount=investor_wash,
        )
        result.report = self._report(result)
        return result
