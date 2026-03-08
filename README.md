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

## CLI usage
```bash
# Single ticker using local JSON data
sharia-screener --ticker AAPL --data data/example.json

# Multiple tickers
sharia-screener --tickers AAPL,MSFT --data data/example.json

# Provide holdings (per-ticker share count)
sharia-screener --tickers AAPL,MSFT --data data/example.json --holdings '{"AAPL": 120, "MSFT": 50}'
```

## Data input format
The CLI currently supports a **local JSON** data source. See `data/example.json` for the expected structure. Data sources are configurable via provider classes.

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
