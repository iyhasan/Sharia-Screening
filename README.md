# Sharia Screener

AAOIFI-based Sharia compliance screening tool. Provides a CLI and a Python library for evaluating tickers against AAOIFI Shari’ah Standard No. 21 criteria.

## Features
- Sector/activity exclusions (hard rules)
- Financial ratio screens (30% / 30% / 5% / 33.33%)
- Purification (wash) calculations
- Machine-readable JSON output + human-readable report
- Dual methodology outputs (book-value vs market-cap for tangible assets)
- Explicit failure on missing or invalid data (no fabricated defaults)

## Install
```bash
pip install sharia-screener
```

## Environment configuration (CLI)
Copy `.env.example` to `.env` and set your defaults. The CLI reads these environment variables:
- `SHARIA_PROVIDER`
- `SHARIA_DATA_PATH`
- `SHARIA_SEGMENT_RULES_PATH`
- `SEC_USER_AGENT`

> The SEC requires a descriptive User-Agent for API calls. You **must** set `SEC_USER_AGENT` (or pass `--sec-user-agent`) when using the unified provider.

## CLI usage
```bash
# Single ticker using local JSON data
sharia-screener --ticker AAPL --provider local --data data/example.json

# Inline JSON payload (no file required)
sharia-screener --ticker AAPL --provider local --json '{"companies": {"AAPL": {"profile": {...}, "financials": {...}}}}'

# Multiple tickers
sharia-screener --tickers AAPL,MSFT --provider local --data data/example.json

# Provide holdings (per-ticker share count)
sharia-screener --tickers AAPL,MSFT --provider local --data data/example.json --holdings '{"AAPL": 120, "MSFT": 50}'

# Use unified provider (SEC + yfinance)
sharia-screener --ticker AAPL --provider unified \
  --segment-rules data/segment_rules.json \
  --sec-user-agent "Your Name contact@example.com"
```

## Data input format
The CLI supports a **local JSON** data source. See `data/example.json` for the expected structure.

Template files live in `config/`:
- `config/supplemental.template.json`
- `config/segment_rules.template.json`

### Unified provider (SEC + yfinance)
The unified provider pulls **market data from yfinance** and **financials from SEC**, then applies documented heuristics for fields not explicitly reported. See `docs/ESTIMATES.md` for full details.

Output includes `methodologies.aaoifi_book_method` (ratios vs total assets) and `methodologies.market_cap_method` (ratios vs market cap). Tangible assets always use **total assets** in both methodologies.

Edit `data/segment_rules.json` to tune prohibited/allowed keywords (e.g., remove weapons/defense if you don’t want to exclude them).

## Library usage
```python
from sharia_screener import LocalJsonProvider, ScreenEngine

provider = LocalJsonProvider("data/example.json")
engine = ScreenEngine(provider=provider)
result = engine.screen("AAPL")
print(result)

# If you want a non-raising result for missing data:
# result = engine.screen("AAPL", fail_on_insufficient_data=False)
```

### Convenience API
```python
from sharia_screener import screen_ticker, screen_many, LocalJsonProvider

provider = LocalJsonProvider("data/example.json")
print(screen_ticker("AAPL", provider))
print(screen_many(["AAPL", "MSFT"], provider))
```

### Exceptions
The package raises explicit exceptions on configuration, upstream data, and validation failures:
- `ConfigurationError`
- `UpstreamDataError`
- `ValidationError`

Catch `ScreeningError` to handle all screening failures.

## Common failure modes
- Missing or invalid local JSON data
- Missing `SEC_USER_AGENT` when using the unified provider
- Upstream SEC data unavailable or incomplete for a ticker

## License
MIT
