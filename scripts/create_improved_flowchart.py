#!/usr/bin/env python3
"""
Create an improved PNG flowchart with better clarity, labels, and legend.
Uses a grid-based layout for maximum readability.
"""

import plotly.graph_objects as go
from pathlib import Path


def create_improved_sharia_flowchart_png(output_path: str = "sharia-compliance-flowchart.png"):
    """
    Generate an improved PNG flowchart with:
    - Clear node shapes and colors
    - Labeled edge connections
    - Legend/key box explaining symbols
    - Professional styling for publication quality
    
    Returns the output path.
    """
    
    # Define nodes in a clear left-to-right grid layout
    # Grid coordinates (x, y) where higher x = right, higher y = up
    nodes = [
        # Column 1: Start
        {'id': 'start', 'label': '📥 Stock Input\nSymbol (e.g., AAPL)', 
         'shape': 'rounded_rect', 'color': '#63a4ff', 'text_color': 'white', 'x': 2, 'y': 0},
        
        # Column 2: Business Check
        {'id': 'sector_check', 'label': '🔍 BUSINESS SECTOR FILTER\nIs prohibited sector?', 
         'shape': 'diamond', 'color': '#ffb74d', 'text_color': 'black', 'x': 5, 'y': 1},
        
        # Column 2: Keywords Check (branch from YES)
        {'id': 'keyword_check', 'label': '🔍 NAME SCAN\nContains prohibited terms?', 
         'shape': 'diamond', 'color': '#ffb74d', 'text_color': 'black', 'x': 5, 'y': -2},
        
        # Column 3: Rejected nodes (top)
        {'id': 'rejected_sector', 'label': '❌ REJECTED\nReason: Prohibited Sector', 
         'shape': 'rect', 'color': '#ffcccb', 'text_color': '#d32f2f', 
         'subtext': ['• Banking/Finance', '• Insurance', '• Gambling/Casinos', 
                    '• Alcohol/Tobacco'], 'x': 7, 'y': 3},
        
        # Column 3: Rejected node (bottom)
        {'id': 'rejected_keywords', 'label': '❌ REJECTED\nReason: Prohibited Business Type', 
         'shape': 'rect', 'color': '#ffcccb', 'text_color': '#d32f2f', 
         'subtext': ['• Company name has forbidden terms'], 'x': 7, 'y': -4},
        
        # Column 4: Financial Check
        {'id': 'debt_check', 'label': '📊 FINANCIAL SCREENING\nDebt/Mkt Cap < 33%?', 
         'shape': 'diamond', 'color': '#ffb74d', 'text_color': 'black', 'x': 9, 'y': -2},
        
        # Column 5: Compliant (top)
        {'id': 'compliant', 'label': '✅ COMPLIANT\nStatus: Pass All Criteria', 
         'shape': 'rect', 'color': '#c8e6c9', 'text_color': '#388e3c', 
         'subtext': ['• Debt ≤ 33% of market cap', 'Purification: 0%', 'All revenue halal'], 
         'x': 12, 'y': 0},
        
        # Column 5: Conditional (bottom)
        {'id': 'conditional', 'label': '⚠️ CONDITIONAL APPROVAL\nStatus: High Debt', 
         'shape': 'rect', 'color': '#fff9c4', 'text_color': '#fbc02d', 
         'subtext': ['• Debt > 33% of market cap', 'Purification: 2.5-10%'], 
         'x': 12, 'y': -3},
        
        # Column 6: Purify Calculation
        {'id': 'purify_calc', 'label': '💰 PURIFICATION CALCULATION\nmin(10%, max(2.5%, debt/330))', 
         'shape': 'rounded_rect', 'color': '#ffe082', 'text_color': 'black', 
         'subtext': ['Formula ensures 2.5%-10% range'], 'x': 15, 'y': -3},
        
        # Column 7: Final Action
        {'id': 'action', 'label': '📝 ACTION REQUIRED\nDonate purification % to charity', 
         'shape': 'rect', 'color': '#bbdefb', 'text_color': '#1976d2', 
         'subtext': ['e.g., 5% of $1 dividend = $0.05 donation'], 'x': 18, 'y': -3},
    ]
    
    # Define connections (from_id -> to_id, label)
    edges = [
        ('start', 'sector_check', 'Begin Analysis'),
        ('sector_check', 'keyword_check', '✅ Allowed Sector'),
        ('sector_check', 'rejected_sector', '❌ Prohibited Sector'),
        ('keyword_check', 'debt_check', '✅ No Forbidden Terms'),
        ('keyword_check', 'rejected_keywords', '❌ Contains Forbidden Terms'),
        ('debt_check', 'compliant', 'YES (< 33%)'),
        ('debt_check', 'conditional', 'NO (≥ 33%)'),
        ('conditional', 'purify_calc', 'Calculate Ratio'),
        ('purify_calc', 'action', 'Apply Formula'),
    ]
    
    # Define shape mappings for Plotly
    shape_map = {
        'rounded_rect': 'path:M-10,-25Q-10,-35,0,-35T10,-35Q10,-25,10,0V25Q10,35,0,35T-10,35Q-10,25,-10,0Z',
        'diamond': 'path:M0,-40L35,0L0,40L-35,0Z',
        'rect': 'M-25,-25H25V25H-25Z'
    }
    
    # Create figure
    fig = go.Figure()
    
    # Add edges (lines with labels)
    for from_node, to_node, label in edges:
        from_pos = next(n for n in nodes if n['id'] == from_node)
        to_pos = next(n for n in nodes if n['id'] == to_node)
        
        # Color based on connection type
        if 'REJECTED' in label:
            edge_color = '#d32f2f'  # Red for rejection paths
            arrow_color = '#d32f2f'
        else:
            edge_color = '#1976d2'  # Blue for success paths
            arrow_color = '#1976d2'
        
        fig.add_trace(go.Scatter(
            x=[from_pos['x'], to_pos['x']],
            y=[from_pos['y'], to_pos['y']],
            mode='lines',
            name=label,
            line=dict(width=3, color=edge_color),
            text=label,
            textfont=dict(size=9, family='Arial'),
            hoverinfo="text",
            showlegend=False
        ))
    
    # Add each node
    for i, node in enumerate(nodes):
        shape = node['shape']
        marker_size = 45 if shape == 'diamond' else 35
        
        fig.add_trace(go.Scatter(
            x=[node['x']],
            y=[node['y']],
            mode='markers+text',
            marker=dict(size=marker_size, color=node['color']),
            text=node['label'],
            textfont=dict(size=10 if shape == 'diamond' else 9, family='Arial'),
            textposition="middle center",
            textangle=0,
            hoverinfo="text"
        ))
        
        # Add subtext for nodes that have it
        if node.get('subtext'):
            y_offset = -1.2 if len(node['subtext']) == 1 else -1.4
            for line in node['subtext']:
                fig.add_trace(go.Scatter(
                    x=[node['x']],
                    y=[node['y'] * y_offset + (i*0.03)],
                    mode='text',
                    text=line,
                    textfont=dict(size=8, family='Arial'),
                    hoverinfo="skip"
                ))
    
    # Create legend/key box
    fig.add_annotation(
        x=14.5, y=-4.5,
        xref="x", yref="y",
        text="<b>LEGEND</b>",
        showarrow=False,
        font=dict(size=10, family='Arial', color='black'),
        align="left",
        bgcolor="white",
        bordercolor="#388e3c",
        borderwidth=2,
        borderpad=5
    )
    
    # Add legend items
    fig.add_trace(go.Scatter(
        x=[14.5], y=[-5.0], mode='markers',
        marker=dict(size=15, color='#63a4ff'),
        text="▶ Start Node", hoverinfo="text", showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=[14.5], y=[-5.3], mode='markers',
        marker=dict(size=15, color='#ffb74d'),
        text="▶ Decision/Diamond", hoverinfo="text", showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=[14.5], y=[-5.6], mode='markers',
        marker=dict(size=15, color='#ffcccb'),
        text="▶ Rejected Status (Red)", hoverinfo="text", showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=[14.5], y=[-5.9], mode='markers',
        marker=dict(size=15, color='#c8e6c9'),
        text="▶ Compliant Status (Green)", hoverinfo="text", showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=[14.5], y=[-6.2], mode='markers',
        marker=dict(size=15, color='#fff9c4'),
        text="▶ Conditional Status (Yellow)", hoverinfo="text", showlegend=True
    ))
    
    # Configure layout with proper styling
    fig.update_layout(
        title={
            'text': '<b>ISLAMIC SHARIA COMPLIANCE SCREENING FLOWCHART</b><br>' +
                    '<i style="font-weight:normal;">AAOIFI Methodology - Complete Decision Process for Halal Trading</i>',
            'font': {'size': 24, 'family': 'Arial'},
            'xanchor': 'center',
            'y': 0.98
        },
        xaxis=dict(
            visible=False,
            range=[1, 20],
            zeroline=False,
            title=''
        ),
        yaxis=dict(
            visible=False,
            range=[-7, 4],
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
            title=''
        ),
        showlegend=False,
        height=700,
        width=1300,
        margin=dict(l=60, r=80, t=100, b=120),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    # Add title subtitle
    fig.add_annotation(
        x=13.5, y=-4.5,
        xref="x", yref="y",
        text="<b>METHODOLOGY:</b> AAOIFI (Accounting & Auditing Org for Islamic Financial Institutions)<br>" +
             "<b>DATA SOURCE:</b> yfinance - Real-time market data via Yahoo Finance<br>" +
             "<b>CURRENT STATUS:</b> Operational - Testing phase",
        showarrow=False,
        font=dict(size=8, family='Arial'),
        align="center",
        bgcolor="white",
        bordercolor="#1976d2",
        borderwidth=1,
        borderpad=5
    )
    
    # Save to PNG with high resolution
    fig.write_image(output_path, format='png', width=1600, height=900, scale=2)
    print(f"✅ Flowchart saved to: {output_path}")
    
    return output_path


if __name__ == "__main__":
    import sys
    
    output_dir = Path(__file__).parent
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
        output_dir.mkdir(parents=True, exist_ok=True)
    
    create_improved_sharia_flowchart_png(str(output_dir / "sharia-compliance-flowchart.png"))
