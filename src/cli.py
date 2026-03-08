"""
Command Line Interface for Sharia Compliance Screener

Provides interactive and batch screening capabilities.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


def analyze_single_symbol(symbol: str, detailed: bool = False):
    """Analyze a single stock symbol."""
    
    from src.screener import ShariaScreener
    
    screener = ShariaScreener()
    result = screener.check_stock(symbol)
    
    # Print formatted output
    status_icon = "✅" if result.is_compliant else ("❌" if result.business_screen == "REJECTED" else "⚠️")
    
    print(f"\n{'='*70}")
    print(f"{status_icon}  {symbol.upper()} - Sharia Compliance Analysis")
    print('='*70)
    
    print(f"\n📊 Business Screening:")
    print(f"   • Sector:     {result.sector or 'N/A'}")
    print(f"   • Status:     {'✅ PASS' if result.business_screen == 'PASS' else '❌ REJECTED'}")
    if not result.is_compliant and result.rejection_reason:
        print(f"   • Reason:     {result.rejection_reason}")
    
    print(f"\n📈 Financial Screening:")
    print(f"   • Debt/Mkt Cap: {result.debt_to_market_cap_pct:.2f}%")
    print(f"   • Cash Reserves: {result.cash_reserves_ratio*100:.1f}% of assets")
    if result.financial_screen != "N/A":
        print(f"   • Status:       {'✅ PASS' if result.financial_screen == 'PASS' else '❌ FAIL'}")
    
    print(f"\n💰 Purification (Washing) Amount:")
    purif = result.purification_ratio * 100
    print(f"   • Required Rate: {purif:.2f}% of dividend/profits")
    if purif > 0:
        print(f"   • Action: Donate this portion of earnings to charity")
    
    print(f"\n🕐 Screened at: {result.screening_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*70)
    
    if detailed and result.is_compliant:
        print(f"\n🎯 Summary: This stock meets AAOIFI Sharia compliance standards.")
        return True
    elif not result.is_compliant:
        print(f"\n❌ Summary: Stock fails Sharia compliance screening.")
        print(f"   - Cannot be traded under Islamic finance principles")
        return False
    else:
        print(f"\n⚠️ Summary: Conditional approval pending purification of {purif:.2f}% of earnings.")
        return True


def analyze_batch_symbols(symbols: str, export_file: str = None):
    """Analyze multiple stock symbols."""
    
    from src.screener import ShariaScreener
    
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    screener = ShariaScreener()
    
    print(f"\n🔍 Starting batch screening for {len(symbol_list)} symbols...")
    print('='*70)
    
    results = []
    compliant_count = 0
    rejected_count = 0
    
    for symbol in symbol_list:
        print(f"\n📋 Analyzing: {symbol}")
        
        try:
            result = screener.check_stock(symbol)
            results.append(result.to_dict())
            
            if result.is_compliant:
                compliant_count += 1
                print(f"   ✅ {symbol}: COMPLIANT")
            else:
                rejected_count += 1
                print(f"   ❌ {symbol}: REJECTED ({result.rejection_reason})")
                
        except Exception as e:
            print(f"   ⚠️  {symbol}: ERROR - {str(e)}")
    
    print(f"\n{'='*70}")
    print("📊 BATCH ANALYSIS SUMMARY")
    print('='*70)
    print(f"Total symbols analyzed: {len(symbol_list)}")
    print(f"✅ Compliant stocks:     {compliant_count} ({compliant_count/len(symbol_list)*100:.1f}%)")
    print(f"❌ Non-compliant stocks: {rejected_count} ({rejected_count/len(symbol_list)*100:.1f}%)")
    
    if export_file:
        export_data = {
            "screening_date": datetime.now().isoformat(),
            "total_analyzed": len(symbol_list),
            "compliant_count": compliant_count,
            "results": results
        }
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n✅ Results exported to: {export_file}")
    
    return results


def generate_visualizations(output_path: str = "sharia-visuals"):
    """Generate flowchart and comparison visualizations."""
    
    from src.flowchart_generator import create_complete_documentation
    
    path = Path(output_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    print(f"🎨 Generating compliance documentation...")
    print('='*70)
    
    try:
        flowchart, mermaid = create_complete_documentation(path)
        
        print(f"\n✅ Generated files:")
        print(f"   • {flowchart}")
        print(f"   • {mermaid}")
        print(f"\n📁 Output directory: {path.absolute()}")
        
    except ImportError as e:
        print(f"\n❌ Error: Missing dependency ({e})")
        print("   Install with: pip install plotly matplotlib graphviz")


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        description="Islamic Sharia-Compliant Stock Screener (AAOIFI Methodology)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single stock
  python src/cli.py --symbol AAPL
  
  # Detailed analysis with all metrics
  python src/cli.py --symbol MSFT --detailed
  
  # Batch screening multiple stocks
  python src/cli.py --symbols AAPL,GOOGL,TSLA
  
  # Export results to JSON file
  python src/cli.py --symbols AMZN,NFLX,XOM --export results.json
  
  # Generate flowchart documentation
  python src/cli.py --generate-visuals

Methodology: Implements AAOIFI Sharia screening standards for Sunni compliance.
        """
    )
    
    parser.add_argument(
        '--symbol', '-s', 
        type=str, 
        help='Single stock symbol to analyze (e.g., AAPL)'
    )
    
    parser.add_argument(
        '--symbols', '-m',
        type=str,
        help='Comma-separated list of symbols for batch screening'
    )
    
    parser.add_argument(
        '--detailed', '-d',
        action='store_true',
        help='Show detailed analysis output'
    )
    
    parser.add_argument(
        '--export', '-e',
        type=str,
        help='Export batch results to JSON file'
    )
    
    parser.add_argument(
        '--generate-visuals',
        action='store_true',
        help='Generate flowchart and documentation'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not any([args.symbol, args.symbols, args.generate_visuals]):
        parser.print_help()
        print("\n⚠️  Please provide at least one argument (--symbol, --symbols, or --generate-visuals)")
        sys.exit(1)
    
    # Execute requested action
    if args.generate_visuals:
        generate_visualizations()
        
    elif args.symbol:
        analyze_single_symbol(args.symbol, detailed=args.detailed)
        
    elif args.symbols:
        analyze_batch_symbols(args.symbols, export_file=args.export)


if __name__ == "__main__":
    main()
