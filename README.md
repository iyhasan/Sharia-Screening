# Islamic Sharia-Compliant Stock Screener

A standalone, open-source tool for screening stocks based on Sharia compliance using the AAOIFI methodology.

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/your-repo/sharia-screener.git
cd sharia-screener
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -r requirements.txt

# Test it immediately (uses REAL data from Yahoo Finance!)
python src/scanner.py --symbol AAPL
```

## 📊 Features

- ✅ **Real-time data** via yfinance (no API key needed - completely free)
- ✅ **AAOIFI methodology** for Sharia screening
- ✅ **Business sector filtering** (blocks prohibited industries)
- ✅ **Financial ratio validation** (debt-to-market-cap < 33%)
- ✅ **Purification amount calculation** for non-compliant revenue
- ✅ **Batch screening** for multiple stocks
- ✅ **Export results** to JSON/CSV

## 🔍 How It Works

The screener follows the AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions) standards:

1. **Business Screening**: Rejects prohibited sectors (banks, insurance, gambling, alcohol, tobacco, weapons)
2. **Financial Screening**: Validates debt-to-market-cap ratio is below 33%
3. **Purification Calculation**: If debt is too high, calculates what percentage of profits must be donated to charity

### Example Output:
```bash
✅ AAPL - Sharia Compliance Analysis
   • Debt/Mkt Cap: 1.72%
   • Purification: 0% (All revenue halal)
   Status: COMPLIANT
```

## 📁 Directory Structure

```
sharia-screener/
├── README.md                 # This file
├── requirements.txt          # Dependencies
├── setup.py                  # For pip install
│
├── src/                     # Core logic
│   ├── __init__.py
│   ├── screener.py          # Main screening engine
│   └── cli.py               # Command-line interface
│
├── docs/                    # Generated outputs
│   ├── sharia-compliance-flowchart.png  # Visual flowchart
│   └── sharia-compliance-flowchart.dot  # Graphviz source code
│
└── scripts/                 # Utility scripts
    └── generate_graphviz_flowchart.py  # Generate diagrams
```

## 🎯 Usage Examples

### Single Stock Analysis
```bash
# Quick check for one stock
python -m src scanner --symbol AAPL

# Detailed analysis with all metrics
python -m src scanner --symbol MSFT --detailed
```

### Batch Screening
```bash
# Screen multiple stocks at once
python -m src scanner --symbols AAPL,MSFT,GOOGL,TGT

# Export results to JSON file
python -m src scanner --symbols AMZN,NFLX,XOM,BAC --export results.json
```

### Using as Python Library
```python
from src.screener import ShariaScreener

screener = ShariaScreener()
result = screener.check_stock("AAPL")

if result.is_compliant:
    print(f"✅ {result.symbol} is Sharia-compliant")
    print(f"   Debt ratio: {result.debt_to_market_cap_pct:.2f}%")
    print(f"   Purification needed: 0%")
else:
    print(f"❌ {result.symbol} rejected: {result.rejection_reason}")
```

## 🖼️ Visual Flowchart

The screening logic is visualized in `docs/sharia-compliance-flowchart.png`:

- **Red boxes**: Stocks REJECTED due to prohibited sector or business type
- **Green boxes**: Fully COMPLIANT stocks (0% purification needed)
- **Yellow boxes**: CONDITIONAL approval (high debt, 2.5-10% purification required)

## 💰 Purification (Washing) Explained

When a stock passes screening but has high debt (>33% of market cap), you must "purify" earnings:

**Formula**: `Purification % = min(10%, max(2.5%, debt_ratio / 330))`

**Example**:
- Dividend received: $1.00 per share
- Purification required: 5%
- Action: Donate $0.05 to charity before using the remaining $0.95

## 📊 Methodology Details

### Prohibited Industries (Immediate Rejection)
- Banking & Financial Services
- Insurance Companies  
- Gambling/Casinos
- Alcohol Production
- Tobacco Manufacturing
- Weapons/Military Contracting
- Adult Entertainment

### Financial Thresholds
| Metric | Limit | Purpose |
|--------|-------|---------|
| Debt/Market Cap | < 33% | Ensures low leverage (AAOIFI standard) |
| Cash Reserves | Tracked | For purification calculation |

## 🔗 Related Projects

- [Alpaca API](https://alpaca.markets/) - Trading platform integration
- [yfinance](https://github.com/ranaroussi/yfinance) - Free market data source
- [Zoya.finance](https://zoya.finance/) - Commercial Sharia screening alternative

## 📄 License

Apache 2.0 - Feel free to use, modify, and distribute!

---

**Developed with ❤️ for the Muslim investing community**

*Note: This tool provides information only and should not be considered financial or religious advice. Always consult qualified scholars for personal guidance.*
