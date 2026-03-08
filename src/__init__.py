"""
Islamic Sharia-Compliant Stock Screener
A standalone tool for screening stocks based on AAOIFI methodology.
"""

__version__ = "1.0.0"

from .screener import ShariaScreener, ShariaComplianceResult
from .flowchart import FlowchartGenerator

__all__ = ["ShariaScreener", "ShariaComplianceResult", "FlowchartGenerator"]
