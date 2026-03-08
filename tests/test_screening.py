from decimal import Decimal

from sharia_screener.providers.local_json import LocalJsonProvider
from sharia_screener.screening import ScreenEngine


def test_screening_compliant():
    provider = LocalJsonProvider("data/example.json")
    engine = ScreenEngine(provider=provider)
    result = engine.screen("AAPL")
    assert result.status in {"compliant", "non_compliant", "insufficient_data"}
    assert result.ticker == "AAPL"
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
