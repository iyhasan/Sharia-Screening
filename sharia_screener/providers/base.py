from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from sharia_screener.models import CompanyProfile, Financials


class DataProvider(ABC):
    @abstractmethod
    def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        raise NotImplementedError

    @abstractmethod
    def get_financials(self, ticker: str) -> Optional[Financials]:
        raise NotImplementedError
