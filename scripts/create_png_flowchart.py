#!/usr/bin/env python3
"""
Generate a PNG flowchart of the Sharia compliance logic using Plotly.
Creates a professional, publication-ready diagram.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path


def create_sharia_flowchart_png(output_path: str = "sharia-compliance-flowchart.png"):
    """
    Generate a PNG flowchart showing the Sharia compliance screening logic.
    
    Uses Plotly to create an interactive diagram with:
    - Decision nodes (diamonds)
    - Process nodes (rectangles)  
    - Start/End nodes (rounded rectangles)
    - Color-coded outcomes (pass/reject/conditional)
    """
    
    # Define flowchart nodes with positions and labels
    # Using a left-to-right layout
    node_positions = {
        'start': {'x': 2, 'y': 0, 'label': 'Stock Analysis\nInput', 'shape': 'rect'},
        'sector_check': {'x': 4, 'y': 0, 'label': 'Business Sector Filter\nProhibited?', 'shape': 'diamond'},
        'keywords_check': {'x': 6, 'y': -1, 'label': 'Name/Industry Scan\nProhibited Terms?', 'shape': 'diamond'},
        'rejected_sector': {'x': 5, 'y': 2, 'label': '❌ REJECTED\n- Banking/Finance\n- Insurance\n- Gambling/Casinos\n- Alcohol/Tobacco', 'shape': 'rect', 'color': '#ffebee'},
        'debt_check': {'x': 8, 'y': -1, 'label': 'Financial Screening\nDebt/Mkt Cap < 33%?', 'shape': 'diamond'},
        'compliant': {'x': 10, 'y': 0, 'label': '✅ COMPLIANT\nPurification: 0%', 'shape': 'rect', 'color': '#e8f5e9'},
        'conditional': {'x': 10, 'y': -2, 'label': '⚠️ CONDITIONAL APPROVAL\nPurification: 2.5-10%', 'shape': 'rect', 'color': '#fffde7'},
        'purify_calc': {'x': 12, 'y': -2, 'label': 'Calculate Purification %\nmin(10%, max(2.5%, debt/330))', 'shape': 'rect'},
        'action': {'x': 14, 'y': -2, 'label': '💰 PURIFY\nDonate % of profits to charity', 'shape': 'rect'}
    }
    
    # Define connections with labels
    connections = [
        ('start', 'sector_check', 'Begin'),
        ('sector_check', 'keywords_check', '✅ Allowed Sectors'),
        ('sector_check', 'rejected_sector', '❌ Prohibited Sector'),
        ('keywords_check', 'debt_check', '✅ Clean Business'),
        ('keywords_check', 'rejected_sector', '❌ Contains Forbidden Terms'),
        ('debt_check', 'compliant', 'YES (< 33%)'),
        ('debt_check', 'conditional', 'NO (≥ 33%)'),
        ('conditional', 'purify_calc', 'Calculate Ratio'),
        ('purify_calc', 'action', 'Donate Profits')
    ]
    
    # Create figure with proper sizing
    fig = go.Figure()
    
    # Add connections first (edges)
    for from_node, to_node, label in connections:
        from_pos = node_positions[from_node]
        to_pos = node_positions[to_node]
        
        edge_color = 'black' if to_node != 'rejected_sector' else '#d32f2f'
        edge_width = 3
        
        fig.add_trace(go.Scatter(
            x=[from_pos['x'], to_pos['x']],
            y=[from_pos['y'], to_pos['y']],
            mode='lines',
            name=label,
            line=dict(width=edge_width, color=edge_color),
            text=label,
            textposition="middle center",
            hoverinfo="text"
        ))
    
    # Add node markers
    for node_id, node_data in node_positions.items():
        marker_size = 50 if node_data['shape'] == 'diamond' else 40
        marker_color = {
            'rect': '#e3f2fd',
            'diamond': '#fff3e0',
            'start': '#b3e5fc',
            'compliant': '#c8e6c9',
            'conditional': '#fff9c4'
        }.get(node_id.split('_')[0], '#bbdefb')
        
        if node_data.get('color'):
            marker_color = node_data['color']
        
        fig.add_trace(go.Scatter(
            x=[node_data['x']],
            y=[node_data['y']],
            mode='markers+text',
            marker=dict(size=marker_size, color=marker_color, line=dict(width=2, color='#1976d2')),
            text=node_data['label'],
            textfont=dict(size=10, family='Arial'),
            textposition="middle center",
            hoverinfo="text"
        ))
    
    # Configure layout
    fig.update_layout(
        title={
            'text': '<b>ISLAMIC SHARIA COMPLIANCE SCREENING FLOWCHART</b><br>' +
                    '<i>(AAOIFI Methodology - A Complete Decision Process)</i>',
            'font': {'size': 22, 'family': 'Arial'},
            'xanchor': 'center',
            'y': 0.95
        },
        xaxis=dict(
            visible=False,
            range=[1, 16],
            title=''
        ),
        yaxis=dict(
            visible=False,
            range=[-3.5, 2.5],
            title=''
        ),
        showlegend=True,
        legend=dict(x=0, y=1.05, orientation='h'),
        height=600,
        width=1000,
        margin=dict(l=40, r=40, t=80, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    # Add a legend box explaining the colors
    fig.add_trace(go.Scatter(
        x=[13],
        y=[-2.8],
        mode='markers+text',
        marker=dict(size=10, color='#d32f2f'),
        text='❌ REJECTED',
        hoverinfo='text'
    ))
    
    fig.add_trace(go.Scatter(
        x=[13],
        y=[-2.5],
        mode='markers+text',
        marker=dict(size=10, color='#e8f5e9'),
        text='✅ COMPLIANT',
        hoverinfo='text'
    ))
    
    fig.add_trace(go.Scatter(
        x=[13],
        y=[-2.2],
        mode='markers+text',
        marker=dict(size=10, color='#fffde7'),
        text='⚠️ CONDITIONAL',
        hoverinfo='text'
    ))
    
    # Save to PNG
    fig.write_image(output_path, format='png', width=1200, height=700, scale=2)
    print(f"✅ Flowchart saved to: {output_path}")
    
    return output_path


if __name__ == "__main__":
    import sys
    
    output_dir = Path(__file__).parent
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
        output_dir.mkdir(parents=True, exist_ok=True)
    
    create_sharia_flowchart_png(str(output_dir / "sharia-compliance-flowchart.png"))
