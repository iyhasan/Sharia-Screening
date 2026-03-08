from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

from sharia_screener.exceptions import ConfigurationError, UpstreamDataError, ValidationError
from sharia_screener.models import CompanyProfile, Financials
from sharia_screener.providers.base import DataProvider


class LocalJsonProvider(DataProvider):
    def __init__(self, path_or_payload: str | Path | dict):
        if isinstance(path_or_payload, (str, Path)):
            self.path = Path(path_or_payload)
            if not self.path.exists():
                raise ConfigurationError(f"Local JSON data file not found: {self.path}")
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    self.payload = json.load(f)
            except json.JSONDecodeError as exc:
                raise ValidationError(f"Invalid JSON in data file: {self.path}") from exc
        elif isinstance(path_or_payload, dict):
            self.path = None
            self.payload = path_or_payload
        else:
            raise ConfigurationError("LocalJsonProvider expects a file path or dict payload")

    def _get(self, ticker: str) -> dict:
        data = self.payload.get("companies", {}).get(ticker.upper())
        if not data:
            raise UpstreamDataError(f"Ticker {ticker.upper()} not found in local JSON payload")
        return data

    def _decimal(self, value: object, field: str) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError) as exc:
            raise ValidationError(f"Invalid decimal value for '{field}': {value}") from exc

    def get_company_profile(self, ticker: str) -> CompanyProfile:
        data = self._get(ticker)
        profile = data.get("profile")
        if not profile:
            raise ValidationError(f"Missing 'profile' section for ticker {ticker.upper()}")

        return CompanyProfile(
            ticker=ticker.upper(),
            name=str(profile.get("name", "")),
            sector=str(profile.get("sector", "")),
            industry=str(profile.get("industry", "")),
            prohibited_activities=profile.get("prohibited_activities", []) or [],
        )

    def get_financials(self, ticker: str) -> Financials:
        data = self._get(ticker)
        fin = data.get("financials")
        if not fin:
            raise ValidationError(f"Missing 'financials' section for ticker {ticker.upper()}")

        required_fields = [
            "market_cap",
            "interest_bearing_debt",
            "interest_bearing_deposits",
            "total_income",
            "non_permissible_income",
            "total_assets",
            "tangible_assets",
            "outstanding_shares",
            "as_of",
        ]
        missing = [field for field in required_fields if fin.get(field) is None]
        if missing:
            raise ValidationError(
                f"Missing required financial fields for {ticker.upper()}: {', '.join(missing)}"
            )

        return Financials(
            market_cap=self._decimal(fin.get("market_cap"), "market_cap"),
            interest_bearing_debt=self._decimal(fin.get("interest_bearing_debt"), "interest_bearing_debt"),
            interest_bearing_deposits=self._decimal(
                fin.get("interest_bearing_deposits"), "interest_bearing_deposits"
            ),
            total_income=self._decimal(fin.get("total_income"), "total_income"),
            non_permissible_income=self._decimal(
                fin.get("non_permissible_income"), "non_permissible_income"
            ),
            total_assets=self._decimal(fin.get("total_assets"), "total_assets"),
            tangible_assets=self._decimal(fin.get("tangible_assets"), "tangible_assets"),
            outstanding_shares=self._decimal(fin.get("outstanding_shares"), "outstanding_shares"),
            as_of=str(fin.get("as_of")),
            estimation_notes=[],
        )
