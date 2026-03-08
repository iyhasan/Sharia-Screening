from __future__ import annotations

import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from typing import Optional


class SecXbrlSource:
    TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
    FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"

    def __init__(self, user_agent: Optional[str] = None):
        self.user_agent = user_agent or os.getenv(
            "SEC_USER_AGENT", "sharia-screener/0.1 (contact: support@example.com)"
        )
        self._ticker_map = None

    def _fetch_json(self, url: str) -> dict:
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _fetch_text(self, url: str) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode("utf-8")

    def _ticker_map_data(self) -> dict:
        if self._ticker_map is None:
            data = self._fetch_json(self.TICKER_MAP_URL)
            self._ticker_map = {
                item["ticker"].upper(): str(item["cik_str"]).zfill(10)
                for item in data.values()
            }
        return self._ticker_map

    def _get_cik(self, ticker: str) -> Optional[str]:
        return self._ticker_map_data().get(ticker.upper())

    def get_company_facts(self, ticker: str) -> Optional[dict]:
        cik = self._get_cik(ticker)
        if not cik:
            return None
        return self._fetch_json(self.FACTS_URL.format(cik=cik))

    def get_profile(self, ticker: str) -> Optional[dict]:
        facts = self.get_company_facts(ticker)
        if not facts:
            return None
        return {
            "name": facts.get("entityName") or "",
            "industry": facts.get("sicDescription") or "",
            "sector": "",
        }

    def _latest_fact(self, facts: dict, tags: list[str], unit: str = "USD") -> tuple[Optional[Decimal], Optional[str]]:
        best = None
        for tag in tags:
            if tag not in facts:
                continue
            units = facts[tag].get("units", {})
            if unit not in units:
                continue
            entries = units[unit]
            for entry in entries:
                end = entry.get("end")
                val = entry.get("val")
                if end is None or val is None:
                    continue
                try:
                    end_dt = datetime.fromisoformat(end)
                except ValueError:
                    continue
                if best is None or end_dt > best[0]:
                    best = (end_dt, Decimal(str(val)), end)
        if best:
            return best[1], best[2]
        return None, None

    def _sum_facts(self, facts: dict, tags: list[str]) -> Optional[Decimal]:
        values = []
        for tag in tags:
            val, _ = self._latest_fact(facts, [tag])
            if val is not None:
                values.append(val)
        if not values:
            return None
        return sum(values)

    def get_financials(self, ticker: str) -> dict:
        facts_payload = self.get_company_facts(ticker)
        if not facts_payload:
            return {}

        facts = facts_payload.get("facts", {}).get("us-gaap", {})

        total_income, as_of = self._latest_fact(
            facts,
            [
                "Revenues",
                "SalesRevenueNet",
                "RevenueFromContractWithCustomerExcludingAssessedTax",
            ],
        )

        total_assets, _ = self._latest_fact(facts, ["Assets"])
        tangible_assets, _ = self._latest_fact(facts, ["NetTangibleAssets"])

        # Components for tangible assets (fallback)
        ppe, _ = self._latest_fact(
            facts,
            [
                "PropertyPlantAndEquipmentNet",
                "PropertyPlantAndEquipmentNetIncludingCapitalizedInterest",
            ],
        )
        inventory, _ = self._latest_fact(facts, ["InventoryNet", "InventoryFinishedGoods"])
        receivables, _ = self._latest_fact(
            facts,
            [
                "AccountsReceivableNetCurrent",
                "AccountsReceivableNet",
                "ReceivablesNetCurrent",
            ],
        )
        operating_lease_assets, _ = self._latest_fact(facts, ["OperatingLeaseRightOfUseAsset"])
        cash, _ = self._latest_fact(facts, ["CashAndCashEquivalentsAtCarryingValue"])

        goodwill, _ = self._latest_fact(facts, ["Goodwill"])
        intangibles, _ = self._latest_fact(facts, ["IntangibleAssets"])
        short_term_investments, _ = self._latest_fact(
            facts, ["ShortTermInvestments", "MarketableSecuritiesCurrent"]
        )

        if tangible_assets is None:
            parts = [p for p in [ppe, inventory, receivables, operating_lease_assets] if p is not None]
            if parts:
                tangible_assets = sum(parts)
            elif total_assets is not None and goodwill is not None and intangibles is not None:
                tangible_assets = total_assets - goodwill - intangibles


        interest_bearing_debt = self._sum_facts(
            facts,
            [
                "LongTermDebt",
                "LongTermDebtCurrent",
                "DebtCurrent",
                "ShortTermBorrowings",
            ],
        )

        shares_outstanding, _ = self._latest_fact(facts, ["EntityCommonStockSharesOutstanding"], unit="shares")

        interest_income = self._sum_facts(
            facts,
            [
                "InterestIncome",
                "InterestIncomeNonoperating",
                "InvestmentIncomeInterest",
                "InterestAndDividendIncomeOperating",
                "InterestAndOtherIncome",
            ],
        )

        return {
            "total_income": total_income,
            "total_assets": total_assets,
            "tangible_assets": tangible_assets,
            "interest_bearing_debt": interest_bearing_debt,
            "cash_equivalents": cash,
            "shares_outstanding": shares_outstanding,
            "interest_income": interest_income,
            "as_of": as_of,
        }

    def get_revenue_segments(self, ticker: str) -> list[dict]:
        cik = self._get_cik(ticker)
        if not cik:
            return []

        submissions = self._fetch_json(self.SUBMISSIONS_URL.format(cik=cik))
        recent = submissions.get("filings", {}).get("recent", {})
        form_list = recent.get("form", [])
        accession_list = recent.get("accessionNumber", [])
        primary_doc_list = recent.get("primaryDocument", [])

        # pick latest 10-K/10-Q
        accession = None
        primary_doc = None
        for form, acc, doc in zip(form_list, accession_list, primary_doc_list):
            if form in {"10-K", "10-Q"}:
                accession = acc
                primary_doc = doc
                break
        if not accession or not primary_doc:
            return []

        accession_nodash = accession.replace("-", "")
        base_url = f"https://data.sec.gov/Archives/edgar/data/{int(cik)}/{accession_nodash}/"

        # try primary doc as instance; if not XML, bail
        if not primary_doc.endswith((".xml", ".xbrl")):
            return []

        xbrl_text = self._fetch_text(base_url + primary_doc)

        # parse XML
        root = ET.fromstring(xbrl_text)
        ns = {
            "xbrli": "http://www.xbrl.org/2003/instance",
            "xbrldi": "http://xbrl.org/2006/xbrldi",
        }

        # map context id -> (end_date, segment_names)
        context_map = {}
        for context in root.findall("xbrli:context", ns):
            ctx_id = context.attrib.get("id")
            period = context.find("xbrli:period", ns)
            end_date = None
            if period is not None:
                end_el = period.find("xbrli:endDate", ns)
                if end_el is not None and end_el.text:
                    end_date = end_el.text

            segment_names = []
            segment = context.find("xbrli:entity/xbrli:segment", ns)
            if segment is not None:
                for member in segment.findall("xbrldi:explicitMember", ns):
                    if member.text:
                        segment_names.append(member.text.split(":")[-1].replace("Member", ""))

            context_map[ctx_id] = (end_date, segment_names)

        # collect revenue facts with segments
        revenue_tags = {
            "Revenues",
            "SalesRevenueNet",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
        }

        segments = {}
        latest_date = None

        for elem in root.iter():
            tag = elem.tag.split("}")[-1]
            if tag not in revenue_tags:
                continue
            ctx = elem.attrib.get("contextRef")
            if not ctx or ctx not in context_map:
                continue
            end_date, segs = context_map[ctx]
            if not segs or end_date is None:
                continue
            try:
                val = Decimal(elem.text)
            except Exception:
                continue

            if latest_date is None or end_date > latest_date:
                latest_date = end_date
                segments = {}

            if end_date == latest_date:
                for seg in segs:
                    segments[seg] = segments.get(seg, Decimal("0")) + val

        return [{"name": k, "revenue": float(v)} for k, v in segments.items()]
