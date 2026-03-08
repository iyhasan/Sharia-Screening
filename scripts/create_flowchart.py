#!/usr/bin/env python3
"""
Create a clean Sharia Compliance Flowchart using Graphviz.

This script generates both:
1. A DOT source file (.dot) - can be edited or opened in GUI tools
2. A PNG image - publication-ready diagram

Fixes the parameter ordering issue with graphviz library.
"""

import subprocess
from pathlib import Path


def create_dot_source(output_dir: str):
    """Create DOT language source file."""
    
    path = Path(output_dir)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    dot_content = '''digraph ShariaCompliance {
    rankdir=LR;
    node [fontname="Arial", fontsize=11];
    edge [fontname="Arial", fontsize=10];
    label="Islamic Sharia Compliance Flowchart (AAOIFI)";
    fontsize=14;
    
    // Legend
    subgraph cluster_legend {
        label="LEGEND"; style=filled color=#f0f0f0;
        l_start [label="▶ Start", shape=box, style=filled fillcolor="#63a4ff" fontcolor="white"];
        l_dec [label="▶ Decision", shape=diamond, style=filled fillcolor="#ffb74d"];
        l_rep [label="❌ Reject", shape=box, style=filled fillcolor="#ffccec" fontcolor="#d32f2f"];
        l_pas [label="✅ Pass", shape=box, style=filled fillcolor="#c8e6c9" fontcolor="#2e7d32"];
        l_con [label="⚠️ Conditional", shape=box, style=filled fillcolor="#fff59d" fontcolor="#f57f17"];
        l_start -> l_dec; l_dec -> l_rep; l_rep -> l_pas; l_pas -> l_con;
    }
    
    // Start node
    start [label="Stock Input", shape=box, style=filled fillcolor="#63a4ff" fontcolor="white"];
    
    // Business Check
    subgraph cluster_business {
        label="Business Sector Filter"; style=rounded color=#e0e0e0;
        sector [label="Prohibited?\n(Insurers, Banks,\nGambling, Alcohol)", shape=diamond, fillcolor="#ffca28" fontcolor="black"];
    }
    
    // Keywords Check  
    subgraph cluster_keywords {
        label="Name Scan"; style=rounded color=#e0e0e0;
        keywords [label="Forbidden Terms?\n(Casino, Weapons,\nMilitary, Adult)", shape=diamond, fillcolor="#ffca28" fontcolor="black"];
    }
    
    // Rejection boxes (Red)
    rej_sector [label="❌ REJECTED\nProhibited Sector", shape=box, style=filled fillcolor="#ffcdd2" fontcolor="#c62828"];
    rej_keywords [label="❌ REJECTED\nUnethical Business", shape=box, style=filled fillcolor="#ffcdd2" fontcolor="#c62828"];
    
    // Financial Check
    subgraph cluster_financial {
        label="Financial Screening"; style=rounded color=#e0e0e0;
        debt [label="Debt/Mkt Cap <33%?", shape=diamond, fillcolor="#ffca28" fontcolor="black"];
    }
    
    # Compliant box (Green)
    compl [label="✅ COMPLIANT\nPurification: 0%", shape=box, style=filled fillcolor="#c8e6c9" fontcolor="#2e7d32"];
    
    # Conditional box (Yellow)
    cond [label="⚠️ CONDITIONAL\nHigh Debt", shape=box, style=filled fillcolor="#fff59d" fontcolor="#f57f17"];
    
    # Purification calculation
    purify [label="Calculate:\nmin(10%, max(2.5%, debt/330))", shape=box, style=filled fillcolor="#ffe082" fontcolor="black"];
    
    # Final action (Blue)
    action [label="Donate purification% to charity", shape=box, style=filled fillcolor="#bbdefb" fontcolor="#1565c0"];
    
    # Connections
    start -> sector;
    sector -> keywords [label="✅ Allowed Sector"];
    sector -> rej_sector [label="❌ Prohibited", color="#d32f2f" style=dashed];
    
    keywords -> debt [label="✅ Clean Business"];
    keywords -> rej_keywords [label="❌ Forbidden", color="#d32f2f" style=dashed];
    
    debt -> compl [label="YES (<33%)"];
    debt -> cond [label="NO (≥33%)", color="#f57c00" style=dashed];
    
    cond -> purify;
    purify -> action;
}
'''
    
    dot_path = path / "flowchart.dot"
    with open(dot_path, 'w') as f:
        f.write(dot_content)
    
    print(f"✅ DOT file created: {dot_path}")
    return dot_path


def render_png_dot(dot_path: Path, output_dir: str):
    """Render PNG from DOT using subprocess."""
    
    path = Path(output_dir)
    png_path = path / "flowchart.png"
    
    try:
        # Use system 'dot' command to generate image
        result = subprocess.run(
            ['dot', '-Tpng', str(dot_path), '-o', str(png_path)],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 and png_path.exists():
            print(f"✅ PNG generated: {png_path}")
            return True
            
    except FileNotFoundError:
        pass  # Will try alternative method
    
    # Try graphviz Python library
    try:
        import graphviz
        
        gv = graphviz.Source.from_file(str(dot_path))
        gv.render(output_folder=str(path), cleanup=False, format='png')
        
        if png_path.exists():
            print(f"✅ PNG generated via Python graphviz: {png_path}")
            return True
            
    except ImportError:
        pass
    except Exception as e:
        print(f"⚠️  Graphviz render error: {e}")
    
    print(f"❌ Could not generate image. DOT source saved at: {dot_path}")
    print("\n   To install Graphviz system tool:")
    print("     • macOS: brew install graphviz")
    print("     • Linux: sudo apt-get install graphviz")
    print("     • Windows: https://graphviz.org/download/")
    
    return False


def main():
    """Main entry point."""
    
    import sys
    
    output_dir = Path(__file__).parent.parent / "docs"
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    
    print("🎨 Generating Sharia Compliance Flowchart...")
    print("="*60)
    
    # Step 1: Create DOT source
    dot_path = create_dot_source(output_dir)
    
    # Step 2: Render PNG
    success = render_png_dot(dot_path, output_dir)
    
    if success:
        print("\n✅ Flowchart successfully generated!")
    else:
        print("\n💡 The DOT file was created and can be viewed with:")
        print("   • Graphviz GUI tool")
        print("   • Any text editor (it's plain text)")
        print("   • Online DOT viewers")


if __name__ == "__main__":
    main()
