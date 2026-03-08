#!/usr/bin/env python3
"""
Test script for Sharia Compliance Screener (new engine)

Uses the unified provider only. Configure via env vars:
- SHARIA_SEGMENT_RULES_PATH
- SEC_USER_AGENT
"""

import os
import sys
import json
from pathlib import Path

from sharia_screener.screening import ScreenEngine

def build_engine() -> ScreenEngine:
    segment_rules_path = os.getenv("SHARIA_SEGMENT_RULES_PATH")
    sec_user_agent = os.getenv("SEC_USER_AGENT")

    segment_rules = {}
    if segment_rules_path and Path(segment_rules_path).exists():
        with open(segment_rules_path, "r", encoding="utf-8") as f:
            segment_rules = json.load(f)

    from sharia_screener.providers.unified_provider import UnifiedProvider
    provider_obj = UnifiedProvider(sec_user_agent=sec_user_agent, segment_rules=segment_rules)

    return ScreenEngine(provider=provider_obj)


def test_single_stock(engine: ScreenEngine, symbol: str):
    print(f"\n{'='*80}")
    print(f"📊 SHARIA COMPLIANCE TEST: {symbol.upper()}")
    print('='*80)

    result = engine.screen(symbol)
    print(result.report)
    if result.estimation_notes:
        print("Estimation notes:")
        for note in result.estimation_notes:
            print(f"  - {note}")
    return result


def test_batch_symbols(engine: ScreenEngine, symbols: list):
    print("\n" + "="*80)
    print("🔍 BATCH SCREENING TEST")
    print("="*80)

    results = []
    for symbol in symbols:
        result = engine.screen(symbol)
        results.append(result)
        status_icon = "✅" if result.status == "compliant" else ("❌" if result.status == "non_compliant" else "⚠️")
        print(f"{status_icon} {symbol}: status={result.status}")

    print(f"\n{'='*80}")
    print("📊 BATCH RESULTS SUMMARY")
    print('='*80)
    print(f"Total symbols: {len(symbols)}")
    print(f"✅ Compliant: {sum(1 for r in results if r.status == 'compliant')}")
    print(f"❌ Non-compliant: {sum(1 for r in results if r.status == 'non_compliant')}")
    print(f"⚠️ Insufficient data: {sum(1 for r in results if r.status == 'insufficient_data')}")


def main():
    print("\n" + "="*80)
    print("🧪 SHARIA SCREENER - TEST RUN")
    print("="*80)

    engine = build_engine()

    test_single_stock(engine, "AAPL")
    test_single_stock(engine, "MSFT")

    symbols_to_test = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "BAC", "JPM"]
    test_batch_symbols(engine, symbols_to_test)

    print("\n" + "="*80)
    print("✅ TESTING COMPLETE")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
