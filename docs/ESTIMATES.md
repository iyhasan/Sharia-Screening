# Estimation Notes (Unified Provider)

The **unified provider** uses SEC filings + yfinance market data. Some required fields are not explicitly reported in public filings, so we apply transparent, documented heuristics. These estimates are always flagged in the output under `estimation_notes`.

## 1) Interest‑bearing deposits
**Goal:** Estimate interest‑bearing deposits for the AAOIFI ratio screen.

**Heuristic:**
- Use **cash and cash equivalents** from yfinance balance sheet when available.
- If cash is not available, assume **0**.

**Rationale:** Public filings don’t provide a clean “interest‑bearing deposits” tag for non‑financial companies. Cash equivalents are the closest observable proxy. If missing, we avoid guessing and default to 0 (flagged).

## 2) Non‑permissible income
**Goal:** Estimate non‑permissible income for purification and the 5% screen.

**Heuristic (priority order):**
1. **Interest income from SEC** (if reported) → treated as non‑permissible.
2. **Segment revenues** from SEC XBRL → prohibited segments summed and added.
3. If neither exists, fall back to **business summary keyword** estimate:
   - Prohibited keyword match → **5% of total income**
   - No match → **0%**

**Rationale:** Interest income is explicitly reported in filings and is a legitimate non‑permissible component. Segment-level revenue provides a more precise split when available; otherwise, the keyword fallback is a conservative proxy.

## 3) Tangible assets
**Goal:** Determine tangible assets for the 33.33% asset‑composition screen.

**Heuristic:**
- Use **Net Tangible Assets** when reported.
- Otherwise, sum **PPE + Inventory + Receivables + Operating Lease ROU Assets** when available.
- If still missing, use **Total Assets − (Cash + Short‑term Investments + Goodwill + Intangibles)**.

**Rationale:** This uses reported line items to approximate tangible/operating assets without manual input.

---

### Output Transparency
All estimates are explicitly noted in the output under `estimation_notes`, for example:

```json
"estimation_notes": [
  "interest_bearing_deposits estimated from cash and cash equivalents",
  "non_permissible_income estimated at 0% (no prohibited keywords found)"
]
```
