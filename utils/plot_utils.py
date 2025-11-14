from typing import List, Dict, Any, Union, Optional, Tuple

import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Define color constants
CHART_COLORS = {
    'primary': '#2A5C8D',  # Primary blue
    'palette': ['#112C4A', '#2A5C8D', '#3E8DCA', '#5AABF0'],  # Blue gradient palette
    'highlight': '#FF5733',  # Highlight color
    'background': 'white'   # Background color
}


def plot_structure_distribution(levels: List[int], structures: List[Dict[str, Any]]) -> go.Figure:
    """
    Plot horizontal bar chart of level structure distribution

    Args:
        levels: List of levels, sorted from low to high (1 to 7)
        structures: List of structure data dictionaries for multiple years, each containing:
            - year: Year identifier (e.g., "Current", "Year 1", etc.)
            - Headcount for each level

    Returns:
        go.Figure: Generated chart object
    """
    # All charts in one row
    n_structures = len(structures)

    # Create subplots
    fig = make_subplots(
        rows=1,
        cols=n_structures,
        subplot_titles=[structure['year'] for structure in structures],
        horizontal_spacing=0.05
    )

    # Calculate maximum percentage value across all charts
    max_percentage = 0
    all_percentages: List[List[float]] = []

    for structure in structures:
        # Sort levels from low to high (1 to 7)
        sorted_levels = sorted(levels)
        total = sum(structure[l] for l in sorted_levels if l in structure)

        # Calculate percentage for each level
        percentages = [
            (structure[l] / total * 100) if total > 0 and l in structure else 0
            for l in sorted_levels
        ]

        all_percentages.append(percentages)
        max_percentage = max(max_percentage, max(percentages) if percentages else 0)

    # Calculate axis maximum (round up to nearest multiple of 5 with some margin)
    axis_max = (int((max_percentage + 4) / 5) + 1) * 5

    # Create a bar chart for each year
    for i, (structure, percentages) in enumerate(zip(structures, all_percentages)):
        # Sort levels from low to high (1 to 7)
        sorted_levels = sorted(levels)

        # Add bar chart
        fig.add_trace(
            go.Bar(
                x=percentages,  # Use percentage data
                y=[f"L{l}" for l in sorted_levels],  # Levels from low to high
                orientation='h',
                text=[f"{p:.1f}%" for p in percentages],  # Display percentage
                textposition='outside',
                marker_color=CHART_COLORS['primary'],  # Use standard blue
                showlegend=False,
                hovertemplate="Level %{y}: %{x:.1f}%<extra></extra>"  # Custom hover tooltip
            ),
            row=1,
            col=i+1
        )

        # Update x-axis for each subplot
        fig.update_xaxes(
            showticklabels=False,  # Hide x-axis tick labels
            showgrid=False,  # Don't show grid lines
            range=[0, axis_max],  # Use calculated maximum
            row=1,
            col=i+1
        )

        # Update y-axis for each subplot
        fig.update_yaxes(
            title_text=None,  # Remove y-axis title
            categoryorder='array',  # Use fixed order
            categoryarray=[f"L{l}" for l in sorted_levels],  # Set fixed level order
            showgrid=False,  # Don't show grid lines
            row=1,
            col=i+1
        )

    # Update overall layout
    fig.update_layout(
        title={
            'text': "Level Structure Distribution Comparison",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=16)
        },
        height=400,  # Fixed height
        margin=dict(t=80, b=20, l=50, r=50),  # Adjust margins
        plot_bgcolor=CHART_COLORS['background'],
        paper_bgcolor=CHART_COLORS['background'],
        showlegend=False,
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    # Adjust subplot title positions
    for i in range(len(structures)):
        fig.layout.annotations[i].update(y=1.05)

    return fig


def plot_trend_charts(years: List[str], metrics: Dict[str, List[float]]) -> go.Figure:
    """
    Plot key metrics trend charts

    Args:
        years: List of years (including "Current" and forecast years)
        metrics: Dictionary containing metric data, key is metric name, value is data list

    Returns:
        go.Figure: Generated chart object
    """
    # Create three subplots
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Average Level', 'Average Age', 'Campus Ratio'),
        horizontal_spacing=0.08
    )

    # Use predefined colors
    colors = CHART_COLORS['palette']

    # Add average level bar chart
    fig.add_trace(
        go.Bar(
            x=years,
            y=metrics['average_level'],
            text=[f"{v:.2f}" for v in metrics['average_level']],
            textposition='outside',
            marker_color=colors[0],
            hovertemplate="Year: %{x}<br>Average Level: %{y:.2f}<extra></extra>"
        ),
        row=1, col=1
    )

    # Add average age bar chart
    fig.add_trace(
        go.Bar(
            x=years,
            y=metrics['average_age'],
            text=[f"{v:.1f}" for v in metrics['average_age']],
            textposition='outside',
            marker_color=colors[1],
            hovertemplate="Year: %{x}<br>Average Age: %{y:.1f}<extra></extra>"
        ),
        row=1, col=2
    )

    # Add campus recruitment ratio bar chart
    fig.add_trace(
        go.Bar(
            x=years,
            y=[v * 100 for v in metrics['campus_ratio']],
            text=[f"{v:.1%}" for v in metrics['campus_ratio']],
            textposition='outside',
            marker_color=colors[2],
            hovertemplate="Year: %{x}<br>Campus Ratio: %{text}<extra></extra>"
        ),
        row=1, col=3
    )

    # Calculate y-axis range for each chart (add 15% space for labels)
    max_level = max(metrics['average_level']) * 1.15
    max_age = max(metrics['average_age']) * 1.15
    max_campus_ratio = max([v * 100 for v in metrics['campus_ratio']]) * 1.15

    # Update y-axes
    fig.update_yaxes(
        showticklabels=True,
        title_text=None,
        showgrid=False,
        range=[0, max_level],
        row=1, col=1
    )
    fig.update_yaxes(
        showticklabels=True,
        title_text=None,
        showgrid=False,
        range=[0, max_age],
        row=1, col=2
    )
    fig.update_yaxes(
        showticklabels=True,
        title_text=None,
        showgrid=False,
        range=[0, max_campus_ratio],
        row=1, col=3
    )

    # Update x-axes
    for col in range(1, 4):
        fig.update_xaxes(
            showgrid=False,
            showticklabels=True,
            tickangle=30 if len(years) > 3 else 0,  # Tilt labels when there are many years
            row=1,
            col=col
        )

    # Update overall layout
    fig.update_layout(
        height=400,
        showlegend=False,
        plot_bgcolor=CHART_COLORS['background'],
        paper_bgcolor=CHART_COLORS['background'],
        margin=dict(t=60, b=40, l=50, r=50),  # Increase bottom margin for tilted labels
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    # Adjust subplot title positions
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].update(y=1.0)

    return fig
