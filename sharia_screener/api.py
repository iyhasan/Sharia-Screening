from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Mapping, Optional

from sharia_screener.models import ScreeningResult
from sharia_screener.providers.base import DataProvider
from sharia_screener.screening import ScreenEngine


def screen_ticker(
    ticker: str,
    provider: DataProvider,
    *,
    shares_held: Optional[Decimal] = None,
    fail_on_insufficient_data: bool = True,
) -> ScreeningResult:
    """Screen a single ticker using the provided data provider."""
    engine = ScreenEngine(provider=provider)
    return engine.screen(
        ticker,
        shares_held=shares_held,
        fail_on_insufficient_data=fail_on_insufficient_data,
    )


def screen_many(
    tickers: Iterable[str],
    provider: DataProvider,
    *,
    holdings: Optional[Mapping[str, Decimal]] = None,
    fail_on_insufficient_data: bool = True,
) -> list[ScreeningResult]:
    """Screen multiple tickers using a shared provider."""
    engine = ScreenEngine(provider=provider)
    results: list[ScreeningResult] = []
    holdings = holdings or {}
    for ticker in tickers:
        shares = holdings.get(ticker.upper())
        results.append(
            engine.screen(
                ticker,
                shares_held=shares,
                fail_on_insufficient_data=fail_on_insufficient_data,
            )
        )
    return results
