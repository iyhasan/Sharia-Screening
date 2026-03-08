#!/usr/bin/env python3
"""
Generate a professional flowchart using Graphviz (DOT language).

Creates publication-quality diagrams with:
- Proper node shapes (rect, diamond, rounded)
- Clear edge labels and connections
- Color-coded decision paths
- Subgraphs for logical groupings
- Legend/key box for reference
"""

from pathlib import Path


def generate_dot_diagram():
    """Generate DOT language diagram definition."""
    
    dot_code = '''digraph ShariaComplianceFlow {
    // Graph styling
    rankdir=LR;  // Left to right layout
    node [fontname="Arial", fontsize=11];
    edge [fontname="Arial", fontsize=10, fontcolor="#555555"];
    labelloc="t";
    label="ISLAMIC SHARIA COMPLIANCE SCREENING FLOWCHART\\n(AAOIFI Methodology - Complete Decision Process)";
    fontsize=16;
    
    // Legend subgraph (top-right corner)
    subgraph cluster_legend {
        label="LEGEND";
        style=filled;
        color=#f5f5f5;
        box_width=0;
        
        legend_start [label="▶ Start", shape=box, style=filled, fillcolor="#63a4ff", fontcolor="white"];
        legend_decision [label="▶ Decision", shape=diamond, style=filled, fillcolor="#ffb74d"];
        legend_reject [label="▶ REJECTED (Red)", shape=box, style=filled, fillcolor="#ffcccb"];
        legend_pass [label="✅ PASS (Green)", shape=box, style=filled, fillcolor="#c8e6c9"];
        legend_cond [label="⚠️ CONDITIONAL", shape=box, style=filled, fillcolor="#fff9c4"];
        
        // Add arrows to show it's a legend
        legend_arrow [shape=point, width=0.5, height=0.1];
        legend_start -> legend_arrow [style=invis];
        legend_decision -> legend_arrow [style=invis];
        legend_reject -> legend_arrow [style=invis];
        legend_pass -> legend_arrow [style=invis];
        legend_cond -> legend_arrow [style=invis];
        
        // Arrange legend vertically
        legend_start -> legend_decision;
        legend_decision -> legend_reject;
        legend_reject -> legend_pass;
        legend_pass -> legend_cond;
    }
    
    // Main flow diagram (separate from legend)
    node [shape=box, style=filled, fillcolor="#63a4ff", fontcolor="white"];
    
    // START NODE
    start_node [label="📥 Stock Input\\nSymbol: AAPL, MSFT, etc.", fillcolor="#63a4ff"];
    
    // First decision - Business Sector Filter
    subgraph cluster_business_check {
        label="STEP 1: BUSINESS SECTOR FILTER";
        style=rounded;
        color="#ddd";
        
        sector_check [label="🔍 Prohibited Sector?", shape=diamond, fillcolor="#ffb74d", fontcolor="black"];
    }
    
    // Keywords check
    subgraph cluster_keywords_check {
        label="STEP 2: NAME/INDUSTRY SCAN";
        style=rounded;
        color="#ddd";
        
        keyword_check [label="🔍 Contains Forbidden Terms?", shape=diamond, fillcolor="#ffb74d", fontcolor="black"];
    }
    
    // Financial screening
    subgraph cluster_financial_check {
        label="STEP 3: FINANCIAL RATIO CHECK";
        style=rounded;
        color="#ddd";
        
        debt_check [label="📊 Debt/Mkt Cap < 33%?", shape=diamond, fillcolor="#ffb74d", fontcolor="black"];
    }
    
    // REJECTION NODES (Red)
    rejected_sector [label="❌ REJECTED\\nReason: Prohibited Sector", shape=box, fillcolor="#ffcccb", fontcolor="#d32f2f"];
    rejected_keywords [label="❌ REJECTED\\nReason: Unethical Business", shape=box, fillcolor="#ffcccb", fontcolor="#d32f2f"];
    
    // PASS NODE (Green)
    compliant [label="✅ COMPLIANT\\nAll Criteria Met", shape=box, fillcolor="#c8e6c9", fontcolor="#388e3c"];
    
    // CONDITIONAL APPROVAL NODE (Yellow)
    subgraph cluster_purification {
        label="PURIFICATION REQUIRED";
        style=rounded;
        color="#ddd";
        
        conditional [label="⚠️ CONDITIONAL APPROVAL\\nHigh Debt (>33%)", shape=box, fillcolor="#fff9c4", fontcolor="#f57c00"];
    }
    
    // PURIFICATION CALCULATION NODE (Orange/Yellow)
    purify_calc [label="💰 Calculate Purification %\\nFormula: min(10%, max(2.5%, debt/330))", shape=box, style=filled, fillcolor="#ffe082"];
    
    // ACTION NODE (Blue)
    action [label="📝 ACTION REQUIRED\\nDonate purification% of profits to charity", shape=box, fillcolor="#bbdefb", fontcolor="#1976d2"];
    
    // CONNECTIONS
    // From Start to Sector Check
    start_node -> sector_check [label="Begin Analysis", color="#1976d2", penwidth=2];
    
    // From Sector Check - YES path (allowed sectors) to Keywords
    sector_check -> keyword_check [label="✅ Allowed Sector", color="#388e3c", penwidth=2];
    
    // From Sector Check - NO path (prohibited) to Rejected
    sector_check -> rejected_sector [label="❌ Prohibited Sector", color="#d32f2f", penwidth=2, style=dashed];
    
    // From Keywords Check - YES path (clean business) to Financial
    keyword_check -> debt_check [label="✅ No Forbidden Terms", color="#388e3c", penwidth=2];
    
    // From Keywords Check - NO path (forbidden terms) to Rejected
    keyword_check -> rejected_keywords [label="❌ Contains Prohibited Terms", color="#d32f2f", penwidth=2, style=dashed];
    
    // From Debt Check - YES path (low debt) to Compliant
    debt_check -> compliant [label="✅ YES (< 33%)", color="#388e3c", penwidth=2];
    
    // From Debt Check - NO path (high debt) to Conditional
    debt_check -> conditional [label="❌ NO (≥ 33%)", color="#f57c00", penwidth=2, style=dashed];
    
    // From Conditional to Purification Calculation
    conditional -> purify_calc [color="#f57c00", penwidth=2];
    
    // From Purification Calculation to Action
    purify_calc -> action [color="#f57c00", penwidth=2];
    
    // Legend arrows (invisible lines)
    legend_arrow -> rejected_start [style=invis, color=white];
    
}

'''
    
    return dot_code


def create_dot_file(output_dir: str = "."):
    """Create a DOT file that can be rendered with graphviz."""
    
    path = Path(output_dir)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    dot_path = path / "sharia-compliance-flowchart.dot"
    
    with open(dot_path, 'w') as f:
        f.write(generate_dot_diagram())
    
    print(f"✅ DOT file created: {dot_path}")
    
    return dot_path


def generate_all_formats(output_dir: str = "."):
    """Generate flowchart in multiple formats using Graphviz."""
    
    from pathlib import Path
    
    path = Path(output_dir)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    # Create DOT file first
    dot_path = create_dot_file(path)
    
    # Try to generate PNG (requires graphviz installed on system)
    try:
        import graphviz
        
        # Load the DOT file
        svg = graphviz.Source.from_file(dot_path)
        
        # Render to PNG
        png_path = path / "sharia-compliance-flowchart.png"
        svg.render(format='png', directory=output_dir, cleanup=False)
        print(f"✅ PNG generated: {png_path}")
        
    except ImportError:
        print("⚠️  graphviz Python package not installed. Install with: pip install graphviz")
        
        # Try using system graphviz command instead
        import subprocess
        try:
            result = subprocess.run(
                ['dot', '-Tpng', str(dot_path), '-o', str(path / 'sharia-compliance-flowchart.png')],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print(f"✅ PNG generated using system graphviz: {path / 'sharia-compliance-flowchart.png'}")
            else:
                print(f"⚠️  System graphviz not found. DOT file created but images not generated.")
                
        except FileNotFoundError:
            print("⚠️  Graphviz tool not installed on system. Install from: https://graphviz.org/download/")
    
    return dot_path


if __name__ == "__main__":
    import sys
    
    output_dir = Path(__file__).parent
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    
    generate_all_formats(output_dir)
    print(f"\n📁 All files generated in: {output_dir}")
    print("\nNext steps:")
    print("  1. Install graphviz system tool: brew install graphviz (Mac) or apt-get install graphviz (Linux)")
    print("  2. Then run the script again to generate PNG/SVG outputs")
    print("  3. OR open the .dot file in Graphviz GUI viewer for interactive viewing")
