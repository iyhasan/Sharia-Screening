from __future__ import annotations

from abc import ABC, abstractmethod
from sharia_screener.models import CompanyProfile, Financials


class DataProvider(ABC):
    @abstractmethod
    def get_company_profile(self, ticker: str) -> CompanyProfile:
        """Return a company profile or raise a ScreeningError on failure."""
        raise NotImplementedError

    @abstractmethod
    def get_financials(self, ticker: str) -> Financials:
        """Return financials or raise a ScreeningError on failure."""
        raise NotImplementedError
