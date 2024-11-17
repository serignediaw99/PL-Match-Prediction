import os

# Premier League team colors for 2023/24 season
TEAM_COLORS = {
    'Arsenal': '#EF0107',
    'Aston-Villa': '#95BFE5',
    'Bournemouth': '#DA291C',
    'Brentford': '#e30613',
    'Brighton-and-Hove-Albion': '#0057B8',
    'Burnley': '#6C1D45',
    'Chelsea': '#034694',
    'Crystal-Palace': '#1B458F',
    'Everton': '#003399',
    'Fulham': '#000000',
    'Liverpool': '#C8102E',
    'Luton': '#F78F1E',
    'Manchester-City': '#6CABDD',
    'Manchester-United': '#DA291C',
    'Newcastle-United': '#241F20',
    'Nottingham-Forest': '#DD0000',
    'Ipswich-Town': '#3A64A3',
    'Tottenham-Hotspur': '#132257',
    'West-Ham-United': '#7A263A',
    'Wolverhampton-Wanderers': '#FDB913',
    'Leicester-City': '#003090',
    'Southampton': '#D71920'
}

# Common color palettes for different visualization types
COLOR_PALETTES = {
    'diverging': ['#d73027', '#f46d43', '#fdae61', '#fee090', '#ffffbf', 
                 '#e0f3f8', '#abd9e9', '#74add1', '#4575b4'],
    'sequential': ['#fef0d9', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', 
                  '#d7301f', '#990000'],
    'qualitative': ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', 
                   '#ffff33', '#a65628', '#f781bf']
}

# Common figure sizes for different plot types
FIGURE_SIZES = {
    'small': (8, 6),
    'medium': (10, 7),
    'large': (12, 8),
    'wide': (15, 8),
    'tall': (8, 12)
}

# Common text styling configurations
TEXT_STYLES = {
    'title': {
        'size': 24,
        'family': 'Arial Black',
        'color': '#2F2F2F'
    },
    'axis_title': {
        'size': 14,
        'family': 'Arial',
        'color': '#2F2F2F'
    },
    'axis_ticks': {
        'size': 12,
        'family': 'Arial',
        'color': '#2F2F2F'
    }
}

def get_team_color(team_name: str, default_color: str = '#808080') -> str:
    """
    Get the primary color for a given team.
    
    Args:
        team_name (str): Name of the team
        default_color (str): Color to return if team not found
        
    Returns:
        str: Hex color code for the team
    """
    return TEAM_COLORS.get(team_name, default_color)

def create_plotly_layout(
    title: str,
    width: int = 900,
    height: int = 600,
    show_legend: bool = False
) -> dict:
    """
    Create a consistent Plotly layout with predefined styling.
    
    Args:
        title (str): Plot title
        width (int): Figure width in pixels
        height (int): Figure height in pixels
        show_legend (bool): Whether to show the legend
        
    Returns:
        dict: Plotly layout configuration
    """
    return {
        'width': width,
        'height': height,
        'title': {
            'text': title,
            'font': TEXT_STYLES['title'],
            'x': 0.5,
            'y': 0.95
        },
        'xaxis': {
            'title': None,
            'tickfont': TEXT_STYLES['axis_ticks'],
            'gridcolor': 'lightgrey',
            'gridwidth': 0.5
        },
        'yaxis': {
            'tickfont': TEXT_STYLES['axis_ticks'],
            'gridcolor': 'lightgrey',
            'gridwidth': 0.5
        },
        'showlegend': show_legend,
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'margin': {'t': 100, 'b': 50, 'l': 50, 'r': 50}
    }