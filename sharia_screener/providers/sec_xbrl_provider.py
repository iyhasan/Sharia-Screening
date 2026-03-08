from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sharia_screener.models import CompanyProfile, Financials
from sharia_screener.providers.base import DataProvider
from sharia_screener.screening import PROHIBITED_KEYWORDS


class SecXbrlProvider(DataProvider):
    TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
    FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

    def __init__(self, supplemental: Optional[dict] = None, user_agent: Optional[str] = None):
        self.supplemental = supplemental or {}
        self.user_agent = user_agent or os.getenv(
            "SEC_USER_AGENT", "sharia-screener/0.1 (contact: support@example.com)"
        )
        self._ticker_map = None

    def _fetch_json(self, url: str) -> dict:
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _ticker_map_data(self) -> dict:
        if self._ticker_map is None:
            data = self._fetch_json(self.TICKER_MAP_URL)
            self._ticker_map = {
                item["ticker"].upper(): str(item["cik_str"]).zfill(10)
                for item in data.values()
            }
        return self._ticker_map

    def _get_company_facts(self, ticker: str) -> Optional[dict]:
        cik = self._ticker_map_data().get(ticker.upper())
        if not cik:
            return None
        return self._fetch_json(self.FACTS_URL.format(cik=cik))

    def _supplement(self, ticker: str) -> dict:
        return self.supplemental.get("companies", {}).get(ticker.upper(), {})

    def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        facts = self._get_company_facts(ticker)
        if not facts:
            return None
        supp = self._supplement(ticker)
        profile_override = supp.get("profile", {})

        name = profile_override.get("name") or facts.get("entityName") or ""
        industry = profile_override.get("industry") or facts.get("sicDescription") or ""
        sector = profile_override.get("sector") or ""
        prohibited = profile_override.get("prohibited_activities", []) or []

        if not name and not industry:
            return None

        return CompanyProfile(
            ticker=ticker.upper(),
            name=name,
            sector=sector,
            industry=industry,
            prohibited_activities=prohibited,
        )

    def _latest_fact(self, facts: dict, tags: list[str], unit: str = "USD") -> tuple[Optional[Decimal], Optional[str]]:
        for tag in tags:
            if tag not in facts:
                continue
            units = facts[tag].get("units", {})
            if unit not in units:
                continue
            entries = units[unit]
            latest = None
            for entry in entries:
                end = entry.get("end")
                val = entry.get("val")
                if end is None or val is None:
                    continue
                try:
                    end_dt = datetime.fromisoformat(end)
                except ValueError:
                    continue
                if latest is None or end_dt > latest[0]:
                    latest = (end_dt, Decimal(str(val)), end)
            if latest:
                return latest[1], latest[2]
        return None, None

    def _sum_facts(self, facts: dict, tags: list[str]) -> Optional[Decimal]:
        values = []
        for tag in tags:
            val, _ = self._latest_fact(facts, [tag])
            if val is not None:
                values.append(val)
        if not values:
            return None
        return sum(values)

    def _classify_non_permissible(self, segments: list[dict]) -> Optional[Decimal]:
        if not segments:
            return None
        total = Decimal("0")
        for seg in segments:
            name = str(seg.get("name", "")).lower()
            revenue = seg.get("revenue")
            if revenue is None:
                continue
            if any(keyword in name for keyword in PROHIBITED_KEYWORDS):
                total += Decimal(str(revenue))
        return total

    def get_financials(self, ticker: str) -> Optional[Financials]:
        facts_payload = self._get_company_facts(ticker)
        if not facts_payload:
            return None

        supp = self._supplement(ticker)
        fin_override = supp.get("financials", {})
        assumptions = supp.get("assumptions", {})
        segments = supp.get("revenue_segments", [])

        facts = facts_payload.get("facts", {}).get("us-gaap", {})

        market_cap = fin_override.get("market_cap")
        shares_outstanding = fin_override.get("outstanding_shares")
        if shares_outstanding is None:
            shares_outstanding, _ = self._latest_fact(facts, ["EntityCommonStockSharesOutstanding"], unit="shares")

        total_income, as_of = self._latest_fact(
            facts,
            [
                "Revenues",
                "SalesRevenueNet",
                "RevenueFromContractWithCustomerExcludingAssessedTax",
            ],
        )

        total_assets, _ = self._latest_fact(facts, ["Assets"])
        tangible_assets = fin_override.get("tangible_assets")
        if tangible_assets is None:
            tangible_assets, _ = self._latest_fact(facts, ["NetTangibleAssets"])
            if tangible_assets is None:
                goodwill, _ = self._latest_fact(facts, ["Goodwill"])
                intangibles, _ = self._latest_fact(facts, ["IntangibleAssets"])
                if total_assets is not None and goodwill is not None and intangibles is not None:
                    tangible_assets = total_assets - goodwill - intangibles

        interest_bearing_debt = self._sum_facts(
            facts,
            [
                "LongTermDebt",
                "LongTermDebtCurrent",
                "DebtCurrent",
                "ShortTermBorrowings",
            ],
        )

        cash, _ = self._latest_fact(facts, ["CashAndCashEquivalentsAtCarryingValue"])
        interest_bearing_deposits = fin_override.get("interest_bearing_deposits")
        if interest_bearing_deposits is None and assumptions.get("interest_bearing_deposits_from_cash"):
            interest_bearing_deposits = cash

        non_permissible_income = fin_override.get("non_permissible_income")
        if non_permissible_income is None and segments:
            non_permissible_income = self._classify_non_permissible(segments)

        as_of = fin_override.get("as_of") or as_of

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
        )
