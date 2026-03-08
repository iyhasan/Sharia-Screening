from decimal import Decimal

import pytest

from sharia_screener import LocalJsonProvider, ScreenEngine
from sharia_screener.exceptions import UpstreamDataError, ValidationError


def test_screening_expected_result():
    provider = LocalJsonProvider("data/example.json")
    engine = ScreenEngine(provider=provider)
    result = engine.screen("AAPL")
    assert result.ticker == "AAPL"
    assert result.status == "non_compliant"
    assert "debt_ratio_exceeded" in result.reason_codes
    assert result.ratios["debt_to_market_cap"] is not None


def test_screening_prohibited_activity():
    provider = LocalJsonProvider("data/example.json")
    engine = ScreenEngine(provider=provider)
    result = engine.screen("SAMPLEHARAM")
    assert result.status == "non_compliant"
    assert "prohibited_activity" in result.reason_codes


def test_investor_wash_amount():
    provider = LocalJsonProvider("data/example.json")
    engine = ScreenEngine(provider=provider)
    result = engine.screen("AAPL", shares_held=Decimal("10"))
    if result.wash_amount_per_share is not None:
        assert result.investor_wash_amount is not None


def test_missing_ticker_raises():
    provider = LocalJsonProvider("data/example.json")
    engine = ScreenEngine(provider=provider)
    with pytest.raises(UpstreamDataError):
        engine.screen("MISSING")


def test_invalid_payload_raises():
    payload = {
        "companies": {
            "BAD": {
                "profile": {"name": "Bad", "sector": "", "industry": ""},
                "financials": {"market_cap": None},
            }
        }
    }
    provider = LocalJsonProvider(payload)
    engine = ScreenEngine(provider=provider)
    with pytest.raises(ValidationError):
        engine.screen("BAD")
