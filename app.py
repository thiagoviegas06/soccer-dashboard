<<<<<<< HEAD
from dash import Dash, html, dcc, Input, Output
=======
from dash import Dash, html, dcc, Input, Output, State, callback_context
>>>>>>> f57de73 (updated dashboard)
import plotly.express as px
import pandas as pd

app = Dash(__name__)

df = pd.read_csv('team_stats_by_season.csv')
team_with_most_points = df.loc[df['Points'].idxmax()]['Team']
sorted_teams = df.groupby('Team')['Points'].sum().sort_values(ascending=False)
team_options = [{'label': team, 'value': team} for team in sorted_teams.index]

team_with_most_points_per_season = df.groupby('Season').apply(lambda x: x.loc[x['Points'].idxmax()]['Team'])
print("Team with the most points per season:")
for season, team in team_with_most_points_per_season.items():
    print(f"{season}: {team}")  

# Define consistent team colors
team_color_map = {
    "Man United": "#DA291C",   
    "Man City": "#6CABDD",     
    "Chelsea": "#003090",      
    "Arsenal": "#DA291C",      
    "Liverpool": "#DA291C",    
    "Tottenham": "#132257",    
    "Leeds": "#FFCD00",        
    "Leicester": "#003090",    
    "Everton": "#003399",      
    "Newcastle": "#241F20",    
}

# Fallback color pool — wide variety to maximize distinctiveness when picking dynamically
fallback_colors = [
    "#8E44AD",  
    "#16A085",  
    "#E67E22",  
    "#1ABC9C",  
    "#9B59B6",  
    "#F39C12",  
    "#27AE60",  
    "#D35400",  
    "#2ECC71",  
    "#7F8C8D",  
    "#BDC3C7",  
    "#E91E63",  
    "#00BCD4", 
    "#FF7043",  
    "#795548",  
    "#607D8B", 
]

def _hex_to_rgb(color):
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

def _color_distance(c1, c2):
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5

def _pick_most_distinct(candidates, used_colors):
    """Return the candidate that maximizes its minimum distance to all used colors."""
    if not used_colors:
        return candidates[0]
    return max(candidates, key=lambda c: min(_color_distance(c, u) for u in used_colors))

def get_team_color_map(displayed_teams):
    """
    Returns a color map for the given teams, using team_color_map if available.
    If two or more teams share the same preferred color, all of them get fallback colors.
    Fallbacks are chosen greedily to maximize perceptual distance from already-used colors.
    """
    # Find preferred colors claimed by more than one displayed team
    color_usage = {}
    for team in displayed_teams:
        preferred = team_color_map.get(team)
        if preferred:
            color_usage.setdefault(preferred, []).append(team)
    conflicted_colors = {color for color, teams in color_usage.items() if len(teams) > 1}

    color_map = {}
    used_colors = set()

    # First pass: assign unique preferred colors (no conflicts)
    for team in displayed_teams:
        preferred = team_color_map.get(team)
        if preferred and preferred not in conflicted_colors:
            color_map[team] = preferred
            used_colors.add(preferred)

    # Second pass: assign fallbacks, picking the most distinct color each time
    remaining_fallbacks = [c for c in fallback_colors if c not in used_colors]
    for team in displayed_teams:
        if team not in color_map:
            if remaining_fallbacks:
                chosen = _pick_most_distinct(remaining_fallbacks, used_colors)
                remaining_fallbacks.remove(chosen)
            else:
                chosen = "#888888"
            color_map[team] = chosen
            used_colors.add(chosen)

    return color_map
season_options = [{'label': season, 'value': season} for season in sorted(df['Season'].unique())]

def position_to_symbol(position):
    if position == 1:
        return "🏆"
    elif position <= 4:
        return "🔝"
    elif position >= 18:
        return "⚠️"
    else:
        return ""

def bar_chart(selected_season):
    filtered_df = df[df['Season'] == selected_season]
    fig = px.bar(
        filtered_df,
        x="Points",
        y="Year",
        color="Team",
        title=f"Points by Team in {selected_season} Season"
    )
    return fig




app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Premier League Team Stats"),
        html.P("Historical performance across seasons", className='dashboard-subtitle')
    ], className='dashboard-header'),

    html.Div([
        # Visualization 1: Line plot
        html.Div([
            html.H3("Goals Scored by Season"),
            html.Div([
                html.Div([
                    html.Label("Teams"),
                    dcc.Dropdown(
                        id='line-team-dropdown',
                        options=team_options,
                        value=[team_options[0]['value'], team_options[1]['value'], team_options[2]['value'], team_options[3]['value'], team_options[4]['value']],
                        multi=True
                    ),
                ], className='control-group'),
            ], className='controls-row'),
            dcc.Graph(id='line-graph')
        ], className='chart-card'),

        # Visualization 2: Scatter plot
        html.Div([
            html.H3("Goals Conceded vs Goals Scored"),
            html.Div([
                html.Div([
                    html.Label("Teams"),
                    dcc.Dropdown(
                        id='scatter-team-dropdown',
                        options=team_options,
                        value=[team_options[0]['value'], team_options[1]['value'], team_options[2]['value'], team_options[3]['value'], team_options[4]['value']],
                        multi=True
                    ),
                ], className='control-group'),
                html.Div([
                    html.Label("Season"),
                    dcc.Dropdown(
                        id='scatter-season-dropdown',
                        options=season_options,
                        value=season_options[0]['value'],
                        multi=False
                    ),
                ], className='control-group'),
            ], className='controls-row'),
            dcc.Graph(id='scatter-graph')
        ], className='chart-card'),

        # Visualization 3: Bar plot
        html.Div([
            html.H3("Points by Team"),
            html.Div([
                html.Div([
                    html.Label("Teams"),
                    dcc.Dropdown(
                        id='bar-team-dropdown',
                        options=team_options,
                        value=[team_options[0]['value'], team_options[1]['value'], team_options[2]['value'], team_options[3]['value'], team_options[4]['value']],
                        multi=True
                    ),
                ], className='control-group'),
                html.Div([
                    html.Label("Season"),
                    dcc.Dropdown(
                        id='bar-season-dropdown',
                        options=season_options,
                        value=season_options[0]['value'],
                        multi=False
                    ),
                ], className='control-group'),
            ], className='controls-row'),
            dcc.Graph(id='bar-graph')
        ], className='chart-card'),

    ], className='page-wrapper')
])
<<<<<<< HEAD
=======

>>>>>>> f57de73 (updated dashboard)
# Line plot callback
@app.callback(
    Output('line-graph', 'figure'),
    Input('line-team-dropdown', 'value')
)

def update_line(selected_teams):
    filtered_df = df[df['Team'].isin(selected_teams)]
    color_map = get_team_color_map(selected_teams)
    # Define a list of unique symbols (Plotly supports many)
    symbol_list = [
        "circle", "square", "diamond", "cross", "x", "triangle-up", "triangle-down", "triangle-left", "triangle-right", "star", "hexagram", "hourglass", "bowtie", "asterisk", "hash"
    ]
    # Map each team to a symbol
    team_symbols = {team: symbol_list[i % len(symbol_list)] for i, team in enumerate(selected_teams)}
    fig = px.line(
        filtered_df,
        x="Season",
        y="Goals Scored",
        color="Team",
        symbol="Team",
        title="Goals Scored by Season",
        color_discrete_map=color_map,
        symbol_map=team_symbols
    )
    return fig


# Scatter plot callback
@app.callback(
    Output('scatter-graph', 'figure'),
    [Input('scatter-team-dropdown', 'value'),
     Input('scatter-season-dropdown', 'value')]
)
def update_scatter(selected_teams, selected_season):
    filtered_df = df[(df['Team'].isin(selected_teams)) & (df['Season'] == selected_season)]
    color_map = get_team_color_map(filtered_df['Team'].unique())
    fig = px.scatter(
        filtered_df,
        x="Goals Conceded",
        y="Goals Scored",
        color="Team",
        size="Points",
        hover_name="Team",
        title=f"Goals Conceded vs Goals Scored ({selected_season})",
        color_discrete_map=color_map
    )
<<<<<<< HEAD
=======

    # Apply opacity based on season
    for trace in fig.data:
        season = trace.customdata[0][3] if trace.customdata is not None and len(trace.customdata[0]) > 3 else None
        if season in opacity_map:
            trace.marker.opacity = opacity_map[season]

    # Enhance size encoding to make point differences more pronounced
    fig.update_traces(
        marker=dict(
            sizemode='area',
            sizeref= global_max_points / (40.0 ** 2),  # Smaller denominator = smaller markers
            sizemin=4,  # Minimum marker size
            line=dict(width=1.5, color='white')  # White border for clarity
        )
    )
>>>>>>> f57de73 (updated dashboard)
    return fig


# Bar plot callback
@app.callback(
    Output('bar-graph', 'figure'),
    [Input('bar-team-dropdown', 'value'),
     Input('bar-season-dropdown', 'value')]
)
def update_bar(selected_teams, selected_season):
    filtered_df = df[(df['Season'] == selected_season) & (df['Team'].isin(selected_teams))].copy()
    filtered_df = filtered_df.sort_values('Points', ascending=False)
    color_map = get_team_color_map(filtered_df['Team'].unique())
    fig = px.bar(
        filtered_df,
        x="Team",
        y="Points",
        color="Team",
        title=f"Points by Team ({selected_season})",
        color_discrete_map=color_map
    )
    return fig


<<<<<<< HEAD
=======
# Consolidated callback for team selection - handles dropdowns and click events
@app.callback(
    [Output('shared-teams-store', 'data'),
     Output('line-team-dropdown', 'value'),
     Output('scatter-team-dropdown', 'value'),
     Output('bar-team-dropdown', 'value')],
    [Input('line-team-dropdown', 'value'),
     Input('scatter-team-dropdown', 'value'),
     Input('bar-team-dropdown', 'value'),
     Input('line-graph', 'clickData'),
     Input('scatter-graph', 'clickData'),
     Input('bar-graph', 'clickData')],
    State('shared-teams-store', 'data')
)
def update_teams(line_teams, scatter_teams, bar_teams, line_click, scatter_click, bar_click, current_store):
    if not callback_context.triggered:
        return current_store, current_store, current_store, current_store

    trigger_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    selected_teams = current_store or default_teams

    # Handle dropdown changes
    if trigger_id == 'line-team-dropdown':
        selected_teams = line_teams or default_teams
    elif trigger_id == 'scatter-team-dropdown':
        selected_teams = scatter_teams or default_teams
    elif trigger_id == 'bar-team-dropdown':
        selected_teams = bar_teams or default_teams

    # Handle click-to-filter
    elif trigger_id == 'line-graph' and line_click:
        try:
            clicked_team = line_click['points'][0]['legendgroup']
            if clicked_team in selected_teams:
                selected_teams = [t for t in selected_teams if t != clicked_team]
            else:
                selected_teams = list(selected_teams) + [clicked_team]
        except (KeyError, IndexError, TypeError):
            pass
    elif trigger_id == 'scatter-graph' and scatter_click:
        try:
            clicked_team = scatter_click['points'][0]['legendgroup']
            if clicked_team in selected_teams:
                selected_teams = [t for t in selected_teams if t != clicked_team]
            else:
                selected_teams = list(selected_teams) + [clicked_team]
        except (KeyError, IndexError, TypeError):
            pass
    elif trigger_id == 'bar-graph' and bar_click:
        try:
            clicked_team = bar_click['points'][0]['legendgroup']
            if clicked_team in selected_teams:
                selected_teams = [t for t in selected_teams if t != clicked_team]
            else:
                selected_teams = list(selected_teams) + [clicked_team]
        except (KeyError, IndexError, TypeError):
            pass

    # Enforce max 7 teams
    if selected_teams and len(selected_teams) > 7:
        selected_teams = selected_teams[:7]

    if not selected_teams:
        selected_teams = default_teams

    return selected_teams, selected_teams, selected_teams, selected_teams


# Consolidated callback for season selection
@app.callback(
    [Output('shared-seasons-store', 'data'),
     Output('scatter-season-dropdown', 'value'),
     Output('bar-season-dropdown', 'value')],
    [Input('scatter-season-dropdown', 'value'),
     Input('bar-season-dropdown', 'value')],
    State('shared-seasons-store', 'data')
)
def update_seasons(scatter_seasons, bar_seasons, current_store):
    if not callback_context.triggered:
        return current_store, current_store, current_store

    trigger_id = callback_context.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'scatter-season-dropdown':
        selected_seasons = scatter_seasons or default_seasons
    elif trigger_id == 'bar-season-dropdown':
        selected_seasons = bar_seasons or default_seasons
    else:
        selected_seasons = current_store or default_seasons

    return selected_seasons, selected_seasons, selected_seasons


>>>>>>> f57de73 (updated dashboard)
if __name__ == "__main__":
    app.run(debug=True)
