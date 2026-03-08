#!/usr/bin/env python3
"""
Test script for Sharia Compliance Screener

Run this to verify the screening logic works with REAL data (no mock data!)
Tests multiple stocks and displays results.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from screener import ShariaScreener


def test_single_stock(symbol: str):
    """Test screening for a single stock."""
    
    print(f"\n{'='*80}")
    print(f"📊 SHARIA COMPLIANCE TEST: {symbol.upper()}")
    print('='*80)
    
    screener = ShariaScreener()
    result = screener.check_stock(symbol)
    
    print(f"\n📝 Company Details:")
    print(f"   • Symbol:     {result.symbol}")
    print(f"   • Sector:     {result.sector or 'N/A'}")
    
    print(f"\n✅ Business Screening:")
    if result.business_screen == "PASS":
        print(f"   • Status:     ✅ PASS - Allowed sector and business type")
    elif result.business_screen == "REJECTED":
        print(f"   • Status:     ❌ REJECTED")
        print(f"   • Reason:     {result.rejection_reason}")
    else:
        print(f"   • Status:     ⚠️ ERROR - {result.business_screen}")
    
    print(f"\n📈 Financial Screening:")
    print(f"   • Debt/Mkt Cap:    {result.debt_to_market_cap_pct:.2f}%")
    print(f"   • Cash Reserves:   {result.cash_reserves_ratio*100:.1f}% of assets")
    print(f"   • Threshold:       < 33.0% required")
    
    if result.financial_screen == "PASS":
        print(f"   • Status:           ✅ PASS - Within Sharia limits")
    elif result.financial_screen == "FAIL":
        print(f"   • Status:           ⚠️  FAIL - Exceeds debt threshold")
        print(f"   • Purification:     {result.purification_ratio*100:.2f}% of profits must be donated to charity")
    else:
        print(f"   • Status:           ❌ ERROR - {result.financial_screen}")
    
    print(f"\n💰 Purification (Washing) Amount:")
    purif_pct = result.purification_ratio * 100
    if purif_pct == 0.0:
        print(f"   • Required Rate:    0% - All revenue is halal")
        print(f"   • Action:           No purification needed")
    else:
        print(f"   • Required Rate:    {purif_pct:.2f}% of dividend/profits")
        print(f"   • Action:           Donate this portion to charity before using earnings")
    
    print(f"\n📅 Screened at:      {result.screening_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if result.is_compliant and not result.rejection_reason:
        return True
    elif not result.is_compliant:
        print(f"\n❌ SUMMARY: Stock does NOT meet Sharia compliance standards")
        return False
    else:
        print(f"\n⚠️ SUMMARY: Conditional approval - purify {purif_pct:.2f}% of earnings")
        return True


def test_batch_symbols(symbols: list):
    """Test screening for multiple stocks."""
    
    print("\n" + "="*80)
    print("🔍 BATCH SCREENING TEST (REAL DATA)")
    print("="*80)
    
    screener = ShariaScreener()
    results = []
    
    for symbol in symbols:
        result = screener.check_stock(symbol)
        results.append(result)
        
        status_icon = "✅" if result.is_compliant else ("❌" if result.business_screen == "REJECTED" else "⚠️")
        print(f"{status_icon} {symbol}: Status={result.financial_screen}, Debt={result.debt_to_market_cap_pct:.1f}%")
    
    # Summary statistics
    compliant = sum(1 for r in results if r.is_compliant)
    rejected = sum(1 for r in results if not r.is_compliant and r.business_screen == "REJECTED")
    conditional = sum(1 for r in results if not r.is_compliant and r.financial_screen == "FAIL")
    
    print(f"\n{'='*80}")
    print("📊 BATCH RESULTS SUMMARY")
    print('='*80)
    print(f"Total symbols: {len(symbols)}")
    print(f"✅ Fully Compliant:    {compliant} ({compliant/len(symbols)*100:.1f}%)")
    print(f"❌ Rejected:           {rejected} ({rejected/len(symbols)*100:.1f}%)")
    print(f"⚠️ Conditional (needs purification): {conditional} ({conditional/len(symbols)*100:.1f}%)")


def demonstrate_compliance_logic():
    """Walk through the complete compliance logic with examples."""
    
    print("\n" + "="*80)
    print("📊 COMPLIANCE LOGIC DEMONSTRATION")
    print("="*80)
    
    # Test cases with known outcomes
    test_cases = [
        ("AAPL", "Apple Inc. - Expected: APPROVED (Tech company, low debt)"),
        ("MSFT", "Microsoft - Expected: APPROVED (Software, manageable debt)"),
        ("BAC",  "Bank of America - Expected: REJECTED (Banking sector)"),
        ("TGT",  "Target Corp. - Expected: APPROVED (Retail, low debt)"),
    ]
    
    screener = ShariaScreener()
    
    for symbol, expected in test_cases:
        print(f"\n{'─'*80}")
        print(f"📋 Testing: {symbol.upper()}")
        print(f"   Expected: {expected}")
        
        result = screener.check_stock(symbol)
        
        # Verify the logic worked correctly
        if "APPROVED" in expected and (result.is_compliant or (not result.is_compliant and result.financial_screen == "FAIL")):
            status = "✅ Correctly assessed"
        elif "REJECTED" in expected and not result.is_compliant and result.business_screen == "REJECTED":
            status = "✅ Correctly rejected"
        else:
            status = f"⚠️  Need to review - got {result.status}"
        
        print(f"   Result:   {status}")
        print(f"   Business: {result.business_screen}")
        print(f"   Financial: {result.financial_screen}")
        print(f"   Debt Ratio: {result.debt_to_market_cap_pct:.1f}%")


def main():
    """Main test runner."""
    
    print("\n" + "="*80)
    print("🧪 SHARIA SCREENER - UNIT TESTS (REAL DATA)")
    print("="*80)
    print("\nThis script uses yfinance to get REAL market data.")
    print("No mock data is used - all results are calculated live.\n")
    
    # Run individual tests
    test_single_stock("AAPL")
    test_single_stock("MSFT")
    
    # Batch test
    print("\n" + "="*80)
    print("📦 BATCH TESTING - Common large-cap stocks")
    print("="*80)
    symbols_to_test = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "BAC", "JPM"]
    test_batch_symbols(symbols_to_test)
    
    # Demonstrate logic
    demonstrate_compliance_logic()
    
    print("\n" + "="*80)
    print("✅ TESTING COMPLETE - Review results above")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
