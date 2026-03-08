from __future__ import annotations

import argparse
import json
from decimal import Decimal
from typing import Dict

from sharia_screener.providers.local_json import LocalJsonProvider
from sharia_screener.providers.yfinance_provider import YFinanceProvider
from sharia_screener.providers.sec_xbrl_provider import SecXbrlProvider
from sharia_screener.screening import ScreenEngine


def parse_holdings(value: str) -> Dict[str, Decimal]:
    payload = json.loads(value)
    return {k.upper(): Decimal(str(v)) for k, v in payload.items()}


def load_json_file(path: str | None) -> dict:
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sharia compliance screening tool")
    parser.add_argument("--ticker", type=str, help="Single ticker")
    parser.add_argument("--tickers", type=str, help="Comma-separated tickers")
    parser.add_argument(
        "--provider",
        type=str,
        default="local",
        choices=["local", "yfinance", "sec"],
        help="Data provider to use",
    )
    parser.add_argument("--data", type=str, help="Path to local JSON data (for local provider)")
    parser.add_argument(
        "--supplemental",
        type=str,
        help="Path to supplemental JSON data (for yfinance/sec providers)",
    )
    parser.add_argument(
        "--sec-user-agent",
        type=str,
        help="SEC requires a descriptive User-Agent (or set SEC_USER_AGENT env var)",
    )
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

    if args.provider == "local":
        if not args.data:
            raise SystemExit("--data is required for local provider")
        provider = LocalJsonProvider(args.data)
    elif args.provider == "yfinance":
        supplemental = load_json_file(args.supplemental)
        provider = YFinanceProvider(supplemental=supplemental)
    else:
        supplemental = load_json_file(args.supplemental)
        provider = SecXbrlProvider(supplemental=supplemental, user_agent=args.sec_user_agent)

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
