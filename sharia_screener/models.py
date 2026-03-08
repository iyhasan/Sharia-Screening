from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Optional


@dataclass
class CompanyProfile:
    ticker: str
    name: str
    sector: str
    industry: str
    prohibited_activities: List[str] = field(default_factory=list)


@dataclass
class Financials:
    market_cap: Decimal
    interest_bearing_debt: Decimal
    interest_bearing_deposits: Decimal
    total_income: Decimal
    non_permissible_income: Decimal
    total_assets: Decimal
    tangible_assets: Decimal
    outstanding_shares: Decimal
    as_of: str
    estimation_notes: List[str] = field(default_factory=list)


@dataclass
class ScreeningResult:
    ticker: str
    compliant: bool
    status: str
    reason_codes: List[str]
    ratios: Dict[str, Optional[Decimal]]
    wash_percentage: Optional[Decimal]
    wash_amount_per_share: Optional[Decimal]
    citations: List[str]
    report: str
    investor_wash_amount: Optional[Decimal] = None
    estimation_notes: List[str] = field(default_factory=list)
    methodologies: Dict[str, dict] = field(default_factory=dict)
