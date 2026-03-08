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
- `SHARIA_SEGMENT_RULES_PATH`
- `SEC_USER_AGENT`

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

# Use unified provider (SEC + yfinance, no supplemental)
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
The unified provider pulls **market data from yfinance** and **financials from SEC**, then applies **best‑estimate heuristics** for fields not explicitly reported. See `docs/ESTIMATES.md` for full details.

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
