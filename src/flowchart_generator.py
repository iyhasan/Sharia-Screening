"""
Sharia Compliance Flowchart Generator

Generates visual diagrams of the Sharia screening logic using Plotly.
Creates both Mermaid diagrams (text-based) and interactive SVGs.
"""

import plotly.graph_objects as go
from typing import Optional
import matplotlib.pyplot as plt


def generate_flowchart_svg(output_path: str = "compliance-flow.svg"):
    """
    Generate an interactive SVG flowchart of the Sharia compliance logic.
    
    Creates a comprehensive decision tree showing:
    - Business sector screening
    - Financial ratio validation  
    - Purification amount calculation
    
    Args:
        output_path: File path to save SVG output
        
    Returns:
        Path to generated file
    """
    
    # Define node positions and connections
    nodes = [
        {"id": "start", "label": "Stock Analysis", "type": "process"},
        {"id": "sector_check", "label": "Sector Filter\n(Prohibited?)", "type": "decision"},
        {"id": "keywords_check", "label": "Name/Industry\nContains Prohibited Terms?", "type": "decision"},
        {"id": "rejected_1", "label": "❌ REJECTED\n- Financial Services/Banking\n- Insurance\n- Gambling/Casinos\n- Alcohol/Tobacco", "type": "reject"},
        {"id": "debt_check", "label": "Debt/Market Cap\n< 33%?", "type": "decision"},
        {"id": "compliant", "label": "✅ COMPLIANT\nPurification: 0%", "type": "pass"},
        {"id": "partial_compliant", "label": "⚠️ CONDITIONAL\nPurification: 2.5-10%", "type": "warning"},
    ]
    
    # Define connections (from_id, to_id, label)
    edges = [
        ("start", "sector_check", "Begin"),
        ("sector_check", "keywords_check", "NO"),
        ("sector_check", "rejected_1", "YES - Prohibited Sector"),
        ("keywords_check", "debt_check", "NO"),
        ("keywords_check", "rejected_1", "YES - Prohibited Business Type"),
        ("debt_check", "compliant", "YES (< 33%)"),
        ("debt_check", "partial_compliant", "NO (≥ 33%)"),
    ]
    
    # Create figure with proper sizing
    fig = go.Figure()
    
    # Add edges first (so nodes appear on top)
    for from_id, to_id, label in edges:
        from_node = next(n for n in nodes if n["id"] == from_id)
        to_node = next(n for n in nodes if n["id"] == to_id)
        
        # Color based on connection type
        edge_color = "black" if to_id != "rejected_1" else "red"
        
        fig.add_trace(go.Scatter(
            x=[from_node["x"], to_node["x"]],
            y=[from_node["y"], to_node["y"]],
            mode="lines",
            line=dict(width=3, color=edge_color),
            name=label,
            text=label,
            hoverinfo="text"
        ))
    
    # Add nodes
    for node in nodes:
        marker_color = "lightblue" if node["type"] == "process" else \
                       "orange" if node["type"] == "decision" else \
                       "red" if node["type"] == "reject" else \
                       "green" if node["type"] == "pass" else "yellow"
        
        fig.add_trace(go.Scatter(
            x=[node["x"]],
            y=[node["y"]],
            mode="markers+text",
            marker=dict(size=40, color=marker_color),
            text=node["label"],
            textposition="middle center",
            hoverinfo="text"
        ))
    
    # Configure layout
    fig.update_layout(
        title={
            "text": "Islamic Sharia Compliance Screening Flowchart (AAOIFI Methodology)",
            "font": {"size": 24, "family": "Arial"}
        },
        xaxis=dict(visible=False, range=[-5, 5]),
        yaxis=dict(visible=False, range=[-5, 5]),
        showlegend=False,
        height=800,
        width=1000
    )
    
    # Save to SVG
    fig.write_image(output_path)
    print(f"✅ Flowchart saved to: {output_path}")
    
    return output_path


def generate_mermaid_diagram() -> str:
    """
    Generate a Mermaid.js diagram string for the compliance logic.
    
    Returns:
        Mermaid diagram code (text format)
    """
    
    mermaid_code = """
graph TD
    A[📥 Stock Symbol Input] --> B{Business Sector Check}
    B -->|✅ Allowed Sectors| C{Industry/Name Keyword Check}
    B -->|❌ Prohibited Sector| Z1[❌ REJECTED<br/>Reason: Financial Services/Banking/Insurance/Gambling/Alcohol/Tobacco]
    C -->|✅ Clean Business| D{Financial Ratio Check:<br/>Debt/Market Cap < 33%?}
    C -->|❌ Contains Prohibited Terms| Z2[❌ REJECTED<br/>Reason: Unethical business activities detected]
    D -->|✅ YES - Low Debt| E1[✅ COMPLIANT]
    D -->|❌ NO - High Debt (>33%)| F1[⚠️ CONDITIONAL APPROVAL]
    
    E1 --> G[Purification Required: 0%<br/>All revenue sources are halal]
    F1 --> H[Purification Required: 2.5-10%<br/>Donate portion of profits to charity]
    
    style Z1 fill:#ffcccc,stroke:#cc0000,stroke-width:2px
    style Z2 fill:#ffcccc,stroke:#cc0000,stroke-width:2px
    style E1 fill:#ccffcc,stroke:#008000,stroke-width:2px
    style F1 fill:#ffffcc,stroke:#cccc00,stroke-width:2px
    style G fill:#e6ffe6,stroke:#008000
    style H fill:#ffffcc,stroke:#999900
    
    classDef process fill:#e3f2fd,stroke:#1976d2;
    classDef decision fill:#fff3e0,stroke:#f57c00;
    classDef reject fill:#ffebee,stroke:#d32f2f;
    classDef pass fill:#e8f5e9,stroke:#388e3c;
    classDef warning fill:#fffde7,stroke:#fbc02d;
    
    class A,C,D process
    class B decision
    class Z1,Z2 reject
    class E1,F1 pass
    class F1 warning
    """
    
    return mermaid_code


def generate_visual_comparison(
    symbols: list, 
    output_path: str = "compliance-comparison.png"
):
    """
    Generate a comparison bar chart of multiple stocks.
    
    Shows debt ratio and purification requirements side-by-side.
    """
    
    import pandas as pd
    
    # Sample data structure (would be filled with real analysis results)
    data = {
        'Symbol': symbols,
        'Debt Ratio %': [1.72, 4.50, 8.30, 15.20, 25.10],  # Example values
        'Purification %': [0.0, 0.0, 0.0, 4.2, 8.5]
    }
    
    df = pd.DataFrame(data)
    
    # Create grouped bar chart
    fig = plt.figure(figsize=(12, 6))
    
    x = range(len(symbols))
    width = 0.35
    
    plt.bar([i - width/2 for i in x], df['Debt Ratio %'], 
            width, label='Debt/Mkt Cap (%)', color='#2196f3')
    plt.bar([i + width/2 for i in x], df['Purification %'], 
            width, label='Purification Required (%)', color='#ff9800')
    
    plt.xlabel('Stock Symbol', fontsize=12)
    plt.ylabel('Percentage (%)', fontsize=12)
    plt.title('Sharia Compliance Metrics Comparison', fontsize=14, fontweight='bold')
    plt.xticks(x, symbols, rotation=0)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    # Add threshold line for debt ratio
    plt.axhline(y=33, color='red', linestyle='--', alpha=0.5, label='Max Debt Threshold (33%)')
    plt.ylim(0, max(max(df['Debt Ratio %']), 35))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Comparison chart saved to: {output_path}")
    
    return output_path


def create_complete_documentation(output_dir: str = "."):
    """Generate all documentation files for the screener."""
    
    import os
    
    # Generate flowchart SVG
    flowchart_path = generate_flowchart_svg(os.path.join(output_dir, "flowchart-compliance.svg"))
    
    # Save Mermaid diagram
    mermaid_path = os.path.join(output_dir, "compliance-flow.mmd")
    with open(mermaid_path, 'w') as f:
        f.write(generate_mermaid_diagram())
    
    print(f"✅ All documentation files created in: {output_dir}")
    
    return flowchart_path, mermaid_path


if __name__ == "__main__":
    """Generate flowcharts for the screener documentation."""
    
    import sys
    from pathlib import Path
    
    # Default output location
    output_dir = Path(__file__).parent.parent
    
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
        output_dir.mkdir(parents=True, exist_ok=True)
    
    create_complete_documentation(output_dir)
