#!/usr/bin/env python3
"""
Create a Sharia Compliance Flowchart PNG using Plotly (no Graphviz dependency).

This creates a publication-quality flowchart without needing external tools.
"""

import plotly.graph_objects as go
from pathlib import Path


def create_flowchart_png(output_path: str = "docs/flowchart.png"):
    """Generate a clean, professional flowchart using Plotly."""
    
    path = Path(output_path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    
    # Node positions (x, y coordinates)
    nodes = {
        'start': {'x': 2, 'y': 0, 'label': '📥 Stock Input', 
                  'shape': 'rounded_rect', 'color': '#63a4ff'},
        'sector': {'x': 4, 'y': 1, 'label': '🔍 Prohibited Sector?', 
                   'shape': 'diamond', 'color': '#ffb74d'},
        'keywords': {'x': 6, 'y': -1, 'label': '🔍 Forbidden Terms?', 
                     'shape': 'diamond', 'color': '#ffb74d'},
        'rej_sector': {'x': 5, 'y': 3, 'label': '❌ REJECTED\nProhibited Sector', 
                       'shape': 'rect', 'color': '#ffcdd2', 'text_color': '#c62828'},
        'rej_keywords': {'x': 7, 'y': -4, 'label': '❌ REJECTED\nUnethical Business', 
                          'shape': 'rect', 'color': '#ffcdd2', 'text_color': '#c62828'},
        'debt': {'x': 8, 'y': -1, 'label': '📊 Debt/Mkt Cap < 33%?', 
                 'shape': 'diamond', 'color': '#ffb74d'},
        'compl': {'x': 10, 'y': 0, 'label': '✅ COMPLIANT\nPurification: 0%', 
                  'shape': 'rect', 'color': '#c8e6c9', 'text_color': '#2e7d32'},
        'cond': {'x': 10, 'y': -2, 'label': '⚠️ CONDITIONAL\nHigh Debt (>33%)', 
                 'shape': 'rect', 'color': '#fff59d', 'text_color': '#f57f17'},
        'purify': {'x': 12, 'y': -2, 'label': '💰 Purification %\nmin(10%, max(2.5%, debt/330))', 
                   'shape': 'rounded_rect', 'color': '#ffe082'},
        'action': {'x': 14, 'y': -2, 'label': '📝 Donate to charity', 
                   'shape': 'rect', 'color': '#bbdefb', 'text_color': '#1565c0'}
    }
    
    # Connections with labels
    connections = [
        ('start', 'sector', 'Begin'),
        ('sector', 'keywords', '✅ Allowed Sector'),
        ('sector', 'rej_sector', '❌ Prohibited'),
        ('keywords', 'debt', '✅ Clean Business'),
        ('keywords', 'rej_keywords', '❌ Forbidden'),
        ('debt', 'compl', 'YES (<33%)'),
        ('debt', 'cond', 'NO (≥33%)'),
        ('cond', 'purify', 'Calculate'),
        ('purify', 'action', 'Apply Formula')
    ]
    
    # Create figure
    fig = go.Figure()
    
    # Add edges (lines with labels)
    for from_id, to_id, label in connections:
        from_pos = nodes[from_id]
        to_pos = nodes[to_id]
        
        edge_color = '#1976d2' if 'YES' in label or label == 'Begin' else \
                     '#f57c00' if 'NO' in label else '#d32f2f'
        
        fig.add_trace(go.Scatter(
            x=[from_pos['x'], to_pos['x']],
            y=[from_pos['y'], to_pos['y']],
            mode='lines',
            line=dict(width=3, color=edge_color),
            text=label,
            hoverinfo="text"
        ))
    
    # Add nodes
    for node_id, node_data in nodes.items():
        marker_size = 40 if node_data['shape'] == 'diamond' else 35
        
        fig.add_trace(go.Scatter(
            x=[node_data['x']],
            y=[node_data['y']],
            mode='markers+text',
            marker=dict(size=marker_size, color=node_data['color']),
            text=node_data['label'],
            hoverinfo="text"
        ))
    
    # Configure layout
    fig.update_layout(
        title={
            'text': '<b>ISLAMIC SHARIA COMPLIANCE SCREENING FLOWCHART</b><br>' +
                    '<i style="font-weight:normal;">AAOIFI Methodology - Complete Decision Process</i>',
            'font': {'size': 20, 'family': 'Arial'},
            'xanchor': 'center',
            'y': 0.98
        },
        xaxis=dict(visible=False, range=[1, 16]),
        yaxis=dict(visible=False, range=[-5, 4]),
        showlegend=False,
        height=600,
        width=1200,
        margin=dict(l=60, r=60, t=80, b=60),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    # Save to PNG
    fig.write_image(str(output_path), format='png', width=1200, height=700, scale=2)
    print(f"✅ Flowchart saved to: {output_path}")
    
    return str(output_path)


if __name__ == "__main__":
    import sys
    
    output_dir = Path(__file__).parent.parent / "docs"
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    
    create_flowchart_png(str(output_dir / "flowchart.png"))
