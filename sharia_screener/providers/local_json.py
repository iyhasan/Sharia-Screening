from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Optional

from sharia_screener.models import CompanyProfile, Financials
from sharia_screener.providers.base import DataProvider


class LocalJsonProvider(DataProvider):
    def __init__(self, path: str | Path):
        self.path = Path(path)
        with self.path.open("r", encoding="utf-8") as f:
            self.payload = json.load(f)

    def _get(self, ticker: str) -> Optional[dict]:
        return self.payload.get("companies", {}).get(ticker.upper())

    def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        data = self._get(ticker)
        if not data:
            return None
        profile = data.get("profile")
        if not profile:
            return None
        return CompanyProfile(
            ticker=ticker.upper(),
            name=profile.get("name", ""),
            sector=profile.get("sector", ""),
            industry=profile.get("industry", ""),
            prohibited_activities=profile.get("prohibited_activities", []) or [],
        )

    def get_financials(self, ticker: str) -> Optional[Financials]:
        data = self._get(ticker)
        if not data:
            return None
        fin = data.get("financials")
        if not fin:
            return None
        return Financials(
            market_cap=Decimal(str(fin.get("market_cap", "0"))),
            interest_bearing_debt=Decimal(str(fin.get("interest_bearing_debt", "0"))),
            interest_bearing_deposits=Decimal(str(fin.get("interest_bearing_deposits", "0"))),
            total_income=Decimal(str(fin.get("total_income", "0"))),
            non_permissible_income=Decimal(str(fin.get("non_permissible_income", "0"))),
            total_assets=Decimal(str(fin.get("total_assets", "0"))),
            tangible_assets=Decimal(str(fin.get("tangible_assets", "0"))),
            outstanding_shares=Decimal(str(fin.get("outstanding_shares", "0"))),
            as_of=str(fin.get("as_of", "")),
        )
