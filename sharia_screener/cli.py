from __future__ import annotations

import argparse
import json
from decimal import Decimal
from typing import Dict

from sharia_screener.providers.local_json import LocalJsonProvider
from sharia_screener.screening import ScreenEngine


def parse_holdings(value: str) -> Dict[str, Decimal]:
    payload = json.loads(value)
    return {k.upper(): Decimal(str(v)) for k, v in payload.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Sharia compliance screening tool")
    parser.add_argument("--ticker", type=str, help="Single ticker")
    parser.add_argument("--tickers", type=str, help="Comma-separated tickers")
    parser.add_argument("--data", type=str, required=True, help="Path to local JSON data")
    parser.add_argument(
        "--holdings",
        type=str,
        help="JSON map of holdings, e.g. '{""AAPL"": 10}'",
    )

    args = parser.parse_args()

    tickers = []
    if args.ticker:
        tickers.append(args.ticker)
    if args.tickers:
        tickers.extend([t.strip() for t in args.tickers.split(",") if t.strip()])
    if not tickers:
        raise SystemExit("Provide --ticker or --tickers")

    holdings = parse_holdings(args.holdings) if args.holdings else {}

    provider = LocalJsonProvider(args.data)
    engine = ScreenEngine(provider=provider)

    results = []
    for ticker in tickers:
        shares = holdings.get(ticker.upper())
        result = engine.screen(ticker, shares_held=shares)
        results.append(
            {
                "ticker": result.ticker,
                "compliant": result.compliant,
                "status": result.status,
                "reason_codes": result.reason_codes,
                "ratios": {k: (str(v) if v is not None else None) for k, v in result.ratios.items()},
                "wash_percentage": str(result.wash_percentage) if result.wash_percentage is not None else None,
                "wash_amount_per_share": str(result.wash_amount_per_share) if result.wash_amount_per_share is not None else None,
                "investor_wash_amount": str(result.investor_wash_amount) if result.investor_wash_amount is not None else None,
                "citations": result.citations,
                "report": result.report,
            }
        )

    print(json.dumps({"results": results}, indent=2))


if __name__ == "__main__":
    main()
