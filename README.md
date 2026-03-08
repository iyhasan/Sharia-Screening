# Sharia Screener

AAOIFI-based Sharia compliance screening tool. Provides a CLI and a Python library for evaluating tickers against AAOIFI Shari’ah Standard No. 21 criteria.

## Features
- Sector/activity exclusions (hard rules)
- Financial ratio screens (30% / 30% / 5% / 33.33%)
- Purification (wash) calculations
- Machine-readable JSON output + human-readable report
- Strict `insufficient_data` handling (no fabricated defaults)

## Install (local)
```bash
pip install -e .
```

## Environment configuration
Copy `.env.example` to `.env` and set your defaults. The CLI will read these environment variables:
- `SHARIA_PROVIDER`
- `SHARIA_DATA_PATH`
- `SHARIA_SUPPLEMENTAL_PATH`
- `SHARIA_SEGMENT_RULES_PATH`
- `SEC_USER_AGENT`

## CLI usage
```bash
# Single ticker using local JSON data
sharia-screener --ticker AAPL --provider local --data data/example.json

# Multiple tickers
sharia-screener --tickers AAPL,MSFT --provider local --data data/example.json

# Provide holdings (per-ticker share count)
sharia-screener --tickers AAPL,MSFT --provider local --data data/example.json --holdings '{"AAPL": 120, "MSFT": 50}'

# Use yfinance (requires supplemental data for non-permissible income, etc.)
sharia-screener --ticker AAPL --provider yfinance --supplemental data/supplemental.json

# Use SEC XBRL (requires a valid User-Agent + supplemental data)
sharia-screener --ticker AAPL --provider sec \
  --supplemental data/sec_supplemental.json \
  --segment-rules data/segment_rules.json \
  --sec-user-agent "Your Name contact@example.com"

# Use combined (SEC + yfinance, no supplemental)
sharia-screener --ticker AAPL --provider combined \
  --segment-rules data/segment_rules.json \
  --sec-user-agent "Your Name contact@example.com"
```

## Data input format
The CLI supports a **local JSON** data source. See `data/example.json` for the expected structure.

Template files live in `config/`:
- `config/supplemental.template.json`
- `config/segment_rules.template.json`

### yfinance + supplemental data
yfinance does not provide non-permissible income or interest-bearing deposits directly. To keep results auditable and avoid fabricated defaults, use a supplemental JSON file for those fields (and any missing values). Format mirrors the local JSON schema, but you only need to supply the fields that yfinance cannot.

### SEC XBRL + supplemental data
SEC XBRL provides core financials (assets, revenue, debt, shares) but not non-permissible income. The SEC provider supports:
- `revenue_segments` (rules-based classification using `segment_rules.json`)
- explicit overrides for `non_permissible_income` and `interest_bearing_deposits`
- optional assumption: `interest_bearing_deposits_from_cash: true` (explicit opt-in)

### Combined provider (SEC + yfinance)
The combined provider pulls **market data from yfinance** and **financials from SEC**. It returns `insufficient_data` if required fields (like non-permissible income or interest-bearing deposits) cannot be sourced without assumptions.

## Library usage
```python
from sharia_screener.providers.local_json import LocalJsonProvider
from sharia_screener.screening import ScreenEngine

provider = LocalJsonProvider("data/example.json")
engine = ScreenEngine(provider=provider)
result = engine.screen("AAPL")
print(result)
```

## Notes
- This tool enforces **hard-stop** behavior: missing or stale data returns `insufficient_data`.
- AAOIFI citations are included in results for traceability.

## License
MIT
