#!/usr/bin/env python3
"""
Generate Sharia compliance flowchart using Graphviz.

Creates publication-quality diagrams showing the complete screening logic.
Requires Graphviz system tool installed (not just Python package).
"""

import subprocess
import sys
from pathlib import Path


def create_dot_file(output_dir: str = "docs"):
    """Create a DOT language file that Graphviz can render."""
    
    dot_code = '''digraph ShariaComplianceFlow {
    // Graph styling
    rankdir=LR;  // Left to right layout
    node [fontname="Arial", fontsize=11];
    edge [fontname="Arial", fontsize=10, fontcolor="#555555"];
    
    label="ISLAMIC SHARIA COMPLIANCE SCREENING FLOWCHART\\n(AAOIFI Methodology - Complete Decision Process)";
    fontsize=16;
    
    // Legend subgraph (top-right corner)
    subgraph cluster_legend {
        label="LEGEND";
        style=filled;
        color=#f5f5f5;
        
        legend_start [label="▶ Start Node", shape=box, style=filled, fillcolor="#63a4ff", fontcolor="white"];
        legend_decision [label="▶ Decision", shape=diamond, style=filled, fillcolor="#ffb74d"];
        legend_reject [label="▶ REJECTED (Red)", shape=box, style=filled, fillcolor="#ffcccb"];
        legend_pass [label="✅ PASS (Green)", shape=box, style=filled, fillcolor="#c8e6c9"];
        legend_cond [label="⚠️ CONDITIONAL", shape=box, style=filled, fillcolor="#fff9c4"];
        
        legend_start -> legend_decision;
        legend_decision -> legend_reject;
        legend_reject -> legend_pass;
        legend_pass -> legend_cond;
    }
    
    // START NODE
    start_node [label="📥 Stock Input\\nSymbol: AAPL, MSFT", shape=box, style=filled, fillcolor="#63a4ff", fontcolor="white"];
    
    // BUSINESS CHECK
    subgraph cluster_business {
        label="STEP 1: BUSINESS SECTOR FILTER";
        style=rounded;
        color=#ddd;
        
        sector_check [label="🔍 Prohibited Sector?", shape=diamond, fillcolor="#ffb74d", fontcolor="black"];
    }
    
    // KEYWORDS CHECK
    subgraph cluster_keywords {
        label="STEP 2: NAME/INDUSTRY SCAN";
        style=rounded;
        color=#ddd;
        
        keyword_check [label="🔍 Forbidden Terms?", shape=diamond, fillcolor="#ffb74d", fontcolor="black"];
    }
    
    // REJECTION NODES (Red)
    rejected_sector [label="❌ REJECTED\\nReason: Prohibited Sector", shape=box, fillcolor="#ffcccb", fontcolor="#d32f2f"];
    rejected_keywords [label="❌ REJECTED\\nReason: Unethical Business", shape=box, fillcolor="#ffcccb", fontcolor="#d32f2f"];
    
    // FINANCIAL CHECK
    subgraph cluster_financial {
        label="STEP 3: FINANCIAL RATIO";
        style=rounded;
        color=#ddd;
        
        debt_check [label="📊 Debt/Mkt Cap < 33%?", shape=diamond, fillcolor="#ffb74d", fontcolor="black"];
    }
    
    // PASS NODE (Green)
    compliant [label="✅ COMPLIANT\\nAll Criteria Met", shape=box, fillcolor="#c8e6c9", fontcolor="#388e3c"];
    
    // CONDITIONAL APPROVAL NODE (Yellow)
    subgraph cluster_conditional {
        label="PURIFICATION REQUIRED";
        style=rounded;
        color=#ddd;
        
        conditional [label="⚠️ CONDITIONAL\\nHigh Debt (>33%)", shape=box, fillcolor="#fff9c4", fontcolor="#f57c00"];
    }
    
    // PURIFICATION CALCULATION (Orange)
    purify_calc [label="💰 Calculate Purification %\\nmin(10%, max(2.5%, debt/330))", shape=box, style=filled, fillcolor="#ffe082"];
    
    // ACTION NODE (Blue)
    action [label="📝 Donate purification% to charity", shape=box, fillcolor="#bbdefb", fontcolor="#1976d2"];
    
    // CONNECTIONS
    start_node -> sector_check [label="Begin", color="#1976d2", penwidth=2];
    
    sector_check -> keyword_check [label="✅ Allowed Sector", color="#388e3c", penwidth=2];
    sector_check -> rejected_sector [label="❌ Prohibited", color="#d32f2f", penwidth=2, style=dashed];
    
    keyword_check -> debt_check [label="✅ Clean Business", color="#388e3c", penwidth=2];
    keyword_check -> rejected_keywords [label="❌ Forbidden Terms", color="#d32f2f", penwidth=2, style=dashed];
    
    debt_check -> compliant [label="YES (< 33%)", color="#388e3c", penwidth=2];
    debt_check -> conditional [label="NO (≥ 33%)", color="#f57c00", penwidth=2, style=dashed];
    
    conditional -> purify_calc [color="#f57c00", penwidth=2];
    purify_calc -> action [color="#f57c00", penwidth=2];
}

'''
    
    path = Path(output_dir)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    dot_path = path / "sharia-compliance-flowchart.dot"
    
    with open(dot_path, 'w') as f:
        f.write(dot_code)
    
    print(f"✅ DOT file created: {dot_path}")
    return dot_path


def generate_image_from_dot(dot_path: Path, output_dir: str):
    """Convert DOT file to PNG using Graphviz command-line tool."""
    
    path = Path(output_dir)
    
    # Try using system graphviz first
    try:
        result = subprocess.run(
            ['dot', '-Tpng', str(dot_path), '-o', str(path / "sharia-compliance-flowchart.png")],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 and (path / "sharia-compliance-flowchart.png").exists():
            print(f"✅ PNG generated successfully!")
            return True
            
    except FileNotFoundError:
        print("⚠️  Graphviz command-line tool not found on system.")
    except Exception as e:
        print(f"⚠️  Error generating image: {e}")
    
    # Fall back to Python graphviz library if available
    try:
        import graphviz
        
        svg = graphviz.Source.from_file(dot_path)
        png_path = path / "sharia-compliance-flowchart.png"
        svg.render(format='png', output_folder=str(path), cleanup=False)
        
        print(f"✅ PNG generated using Python graphviz library!")
        return True
        
    except ImportError:
        print("❌ Neither Graphviz system tool nor Python graphviz library can render the image.")
        print("\nTo generate images, install Graphviz:")
        print("  • macOS:   brew install graphviz")
        print("  • Linux:   sudo apt-get install graphviz")
        print("  • Windows: https://graphviz.org/download/")
        return False
    
    return False


def main():
    """Main entry point."""
    
    import sys
    
    output_dir = Path(__file__).parent.parent / "docs"
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    
    print("🎨 Generating Sharia Compliance Flowchart...")
    print("="*60)
    
    # Step 1: Create DOT file
    dot_path = create_dot_file(output_dir)
    
    # Step 2: Generate PNG image
    success = generate_image_from_dot(dot_path, output_dir)
    
    if not success:
        print(f"\n💡 The DOT file was created at: {dot_path}")
        print("   You can view/edit it with any text editor or import into Graphviz GUI.")
        sys.exit(1)


if __name__ == "__main__":
    main()
