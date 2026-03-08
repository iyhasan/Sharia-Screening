from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from sharia_screener.api import screen_many, screen_ticker
from sharia_screener.exceptions import (
    ConfigurationError,
    ScreeningError,
    UpstreamDataError,
    ValidationError,
)
from sharia_screener.models import CompanyProfile, Financials, ScreeningResult
from sharia_screener.providers.local_json import LocalJsonProvider
from sharia_screener.providers.unified_provider import UnifiedProvider
from sharia_screener.screening import ScreenEngine

try:
    __version__ = version("sharia-screener")
except PackageNotFoundError:  # pragma: no cover - local editable fallback
    __version__ = "0.0.0"

__all__ = [
    "CompanyProfile",
    "ConfigurationError",
    "Financials",
    "LocalJsonProvider",
    "ScreenEngine",
    "ScreeningError",
    "ScreeningResult",
    "UnifiedProvider",
    "UpstreamDataError",
    "ValidationError",
    "screen_many",
    "screen_ticker",
    "__version__",
]
