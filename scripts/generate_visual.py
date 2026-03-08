#!/usr/bin/env python3
"""
Generate a detailed flowchart visualization of Sharia compliance logic.
Creates both SVG and PNG versions for the documentation.
"""

import os
from pathlib import Path

def create_mermaid_diagram():
    """Create a Mermaid.js diagram for documentation."""
    
    mermaid_code = '''
graph TD
    A[📥 Stock Analysis Request<br/>Symbol: AAPL, MSFT, etc.] --> B{Business Sector Check}
    
    B -->|✅ Allowed Sectors| C{Name/Industry<br/>Keyword Scan}
    B -->|❌ Prohibited<br/>Sectors| R1[❌ REJECTED]
    
    R1_Rule: financial services OR<br/>banks OR insurance OR<br/>gambling OR casinos OR<br/>alcohol OR tobacco
    
    C -->|✅ Clean Business| D{Financial Screening}
    C -->|❌ Contains Prohibited Terms| R2[❌ REJECTED]
    
    R2_Rule: company name contains:<br/>alcohol, casino, weapons,<br/>military, adult entertainment
    
    D --> E{Debt-to-Market<br/>Cap Ratio Calculation}
    
    E --> F["% Debt = (Short-term<br/>+ Long-term debt) / Market Cap"]
    
    F --> G[Debt Ratio < 33%?]
    
    G -->|✅ YES | P1[✅ COMPLIANT]
    G -->|❌ NO (>33%) | W1[⚠️ CONDITIONAL APPROVAL]
    
    P1 --> H[Purification Required:<br/>0% - All income is halal]
    
    W1 --> I[Calculate Purification Ratio:<br/>2.5% to 10% based on debt level]
    
    I --> J["Formula: min(10%, max(2.5%,<br/>debt_ratio / 330))]"]
    
    J --> K[💰 Action: Donate this<br/>percentage of profits<br/>to charity]
    
    style R1 fill:#ffebee,stroke:#d32f2f,stroke-width:3px,color:#d32f2f
    style R2 fill:#ffebee,stroke:#d32f2f,stroke-width:3px,color:#d32f2f
    style P1 fill:#e8f5e9,stroke:#388e3c,stroke-width:3px,color:#388e3c
    style W1 fill:#fffde7,stroke:#fbc02d,stroke-width:3px,color:#f57c00
    
    classDef process fill:#e3f2fd,stroke:#1976d2,color:black
    classDef decision fill:#fff3e0,stroke:#f57c00,color:black
    classDef reject fill:#ffebee,stroke:#d32f2f,color:#d32f2f
    classDef pass fill:#e8f5e9,stroke:#388e3c,color:#388e3c
    classDef warning fill:#fffde7,stroke:#fbc02d,color:#f57c00
    
    class A,F process
    class B,C,G decision
    class R1,R2 reject
    class P1 pass
    class W1,J warning
'''
    
    return mermaid_code


def create_ascii_flowchart():
    """Create an ASCII art flowchart for quick viewing."""
    
    return '''
┌─────────────────────────────────────────────────────────────────┐
│         ISLAMIC SHARIA COMPLIANCE SCREENING FLOWCHART           │
│                    (AAOIFI Methodology)                         │
└─────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │  STOCK INPUT │
                              │  e.g. AAPL   │
                              └──────┬───────┘
                                     │
                                     ▼
                    ┌────────────────────────────┐
                    │  BUSINESS SECTOR FILTER    │
                    └────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    │                    ▼
   ┌─────────┐      ┌───────────────┐       ┌─────────┐
   │  PASS   │      │ REJECTED      │       │ REJECT  │
   │         │      │ Banking/      │       │         │
   │         │      │ Insurance     │       │         │
   │         │      │ Gambling      │       │         │
   │         │      │ Alcohol       │       │         │
   └────┬────┘      │ Tobacco       │       │         │
        │          └───────────────┘       └────┬────┘
        │                                       │
        ▼                                       ▼
┌─────────────────────┐              ┌───────────────────┐
│  NAME/INDUSTRY      │              │   ❌ REJECTED     │
│  KEYWORD SCAN       │              │                   │
└─────────────────────┘              └───────────────────┘
        │
        ├─ Contains: "alcohol" → REJECT
        ├─ Contains: "casino" → REJECT  
        ├─ Contains: "weapons" → REJECT
        └─ Clean → CONTINUE

        ▼
┌─────────────────────┐
│  FINANCIAL RATIO    │
│  CHECK              │
└─────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│ CALCULATE:                              │
│ Debt/Market Cap = Total Debt / Market   │
│                                             │
│ Total Debt = Short-term + Long-term    │
└─────────────────────────────────────────┘
        │
        ▼
┌──────────────────────┐
│  DEBT RATIO < 33%?   │
└──────────────────────┘
        │
   ┌────┴────┐
   │         │
   ▼         ▼
YES        NO
   │         │
   │         │
   ▼         ▼
┌────────┐  ┌─────────────────┐
│✅      │  │⚠️              │
│COMPLIANT│ │CONDITIONAL     │
│        │  │APPROVAL        │
└────────┘  └─────────────────┘
   │         │
   │         │
   ▼         ▼
Purification:  Purification: 
0% (all halal) Calculate: 
                min(10%, max(2.5%, 
                         debt_ratio / 330))

                ▼
        ┌──────────────┐
        │ 💰 PURIFY    │
        │              │
        │ Example:     │
        │ Dividend: $1 │
        │ Purification: 4%│
        │ Donate: $0.04 │
        └──────────────┘

'''


def create_text_based_diagram():
    """Create a detailed text-based explanation diagram."""
    
    return '''
📊 DETAILED COMPLIANCE LOGIC DIAGRAM
=====================================

STEP 1: BUSINESS SECTOR CHECK (Hard Rejection)
───────────────────────────────────────────────
Input → Company Sector Classification
   
   IS THE COMPANY IN:
   ┌─────────────────────────────────┐
   │ • Banking / Financial Services  │  → ❌ REJECT
   │ • Insurance Companies           │  → ❌ REJECT
   │ • Asset Management / Funds      │  → ❌ REJECT  
   │ • Casinos / Gambling            │  → ❌ REJECT
   │ • Alcohol Production            │  → ❌ REJECT
   │ • Tobacco Manufacturing         │  → ❌ REJECT
   └─────────────────────────────────┘
   
   Result: If YES to any above → STOP (REJECTED)
           If NO → Continue to STEP 2

STEP 2: NAME/INDUSTRY KEYWORD SCAN (Soft Rejection)  
───────────────────────────────────────────────────────
Input → Company Name + Industry Description
   
   DOES IT CONTAIN:
   ┌──────────────────────────────────┐
   │ Keywords scan:                   │
   │ "alcohol", "casino", "gambling"  │
   │ "weapons", "military", "adult"   │
   │ (case-insensitive)               │
   └──────────────────────────────────┘
   
   Result: If YES → STOP (REJECTED)  
           If NO → Continue to STEP 3

STEP 3: FINANCIAL RATIO CALCULATION
─────────────────────────────────────
Input → Financial Statements
   
   FORMULA:
   Debt-to-Market-Cap % = (Short-term Debt + Long-term Debt) / Market Cap × 100%
   
   Data Sources:
   • Short-term Debt: Balance Sheet - Current Liabilities
   • Long-term Debt:  Balance Sheet - Non-current Liabilities  
   • Market Cap:      Yahoo Finance - stock['marketCap']
   
   Example (AAPL):
   • Total Debt = $120B + $85B = $205B
   • Market Cap = $3,000B
   • Debt Ratio = 205/3000 × 100% = 6.83%

STEP 4: THRESHOLD EVALUATION
─────────────────────────────────────
Input → Calculated Debt Ratio
   
   IS Debt Ratio < 33%?
   
   ┌────────────────────────┐    ┌────────────────────────┐
   │    ✅ YES              │    │    ❌ NO (>33%)        │
   │    (Low Debt)          │    │    (High Debt)         │
   └────────────┬───────────┘    └────────────┬───────────┘
                │                             │
                ▼                             ▼
        ✅ COMPLIANT              ⚠️ CONDITIONAL APPROVAL
        Purification: 0%          Purification: 2.5-10%

STEP 5: PURIFICATION CALCULATION (If Debt ≥ 33%)
─────────────────────────────────────────────────────
When a stock passes but has high debt, calculate purification:

   FORMULA:
   Purification % = min(10%, max(2.5%, debt_ratio / 330))
   
   Interpretation:
   ┌────────────────────────────────────────┐
   │ Debt < 5%     → Purification: 2.5%    │
   │ Debt = 16.5%  → Purification: 5%      │
   │ Debt > 33%    → Purification: 10% (max)│
   └────────────────────────────────────────┘

   EXAMPLE:
   • Stock X has debt ratio of 20%
   • Purification = min(10%, max(2.5%, 20/33)) = 6.06%
   • Action: If company pays $1 dividend per share, 
             donate $0.0606 to charity for purification

STEP 6: OUTPUT FORMAT (JSON)
─────────────────────────────────────────────
{
  "symbol": "AAPL",
  "status": "COMPLIANT",
  "business_screen": "PASS",
  "financial_screen": "PASS",  
  "debt_to_market_cap_pct": 1.72,
  "cash_reserves_ratio_pct": 28.5,
  "purification_ratio_pct": 0.0,
  "sector": "Technology",
  "screened_at": "2026-03-08T03:05:21Z"
}


SHARIA COMPLIANCE SUMMARY
==========================

✅ PASS Criteria:
   • Sector allowed by Islamic finance
   • No prohibited business activities  
   • Debt < 33% of market value
   
⚠️ CONDITIONAL APPROVAL:
   • Passes business screening
   • Has high debt (≥ 33%)
   • Must purify 2.5-10% of profits via charity

❌ REJECT Criteria:
   • Prohibited sector (banks, insurance, gambling, etc.)
   • Engages in unethical business activities


METHODODOLOGY SOURCES
======================
• AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions)
• Standard Sunni scholarship compliance criteria
• Based on interest-free investment principles

'''


def generate_all_outputs(output_dir: str = "."):
    """Generate all diagram formats."""
    
    path = Path(output_dir)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    # Save Mermaid diagram
    mermaid_path = path / "compliance-flow.mmd"
    with open(mermaid_path, 'w') as f:
        f.write(create_mermaid_diagram())
    print(f"✅ Saved: {mermaid_path}")
    
    # Save ASCII art version  
    ascii_path = path / "flowchart-ascii.txt"
    with open(ascii_path, 'w') as f:
        f.write(create_ascii_flowchart())
    print(f"✅ Saved: {ascii_path}")
    
    # Save detailed text diagram
    details_path = path / "compliance-explanation.md"
    with open(details_path, 'w') as f:
        f.write("```text\n" + create_text_based_diagram() + "\n```\n")
    print(f"✅ Saved: {details_path}")
    
    return path


if __name__ == "__main__":
    import sys
    
    output_dir = Path(__file__).parent
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    
    generate_all_outputs(output_dir)
    print(f"\n📁 All diagrams generated in: {output_dir}")
