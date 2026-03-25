from dash import Dash, html, dcc, Input, Output, State, callback_context
import plotly.express as px
import pandas as pd
from team_colors import assign_plot_colors

app = Dash(__name__)

# Global cache to maintain color consistency across plots
color_cache = {}

df = pd.read_csv('team_stats_by_season.csv')
team_with_most_points = df.loc[df['Points'].idxmax()]['Team']
sorted_teams = df.groupby('Team')['Points'].sum().sort_values(ascending=False)
team_options = [{'label': team, 'value': team} for team in sorted_teams.index]
teams = df['Team'].unique()

season_options = [{'label': season, 'value': season} for season in sorted(df['Season'].unique())]

# Default selections for stores
default_teams = [team_options[0]['value'], team_options[1]['value'], team_options[2]['value'], team_options[3]['value'], team_options[4]['value']]
default_seasons = sorted(df['Season'].unique())[-3:] if len(df['Season'].unique()) >= 3 else sorted(df['Season'].unique())

app.layout = html.Div([
    # Shared state stores for cross-filtering
    dcc.Store(id='shared-teams-store', data=default_teams),
    dcc.Store(id='shared-seasons-store', data=default_seasons),

    # Header
    html.Div([
        html.H1("Premier League Team Stats"),
        html.P("Historical performance across seasons", className='dashboard-subtitle')
    ], className='dashboard-header'),

    html.Div([
        # Unified filters at top
        html.Div([
            html.Div([
                html.Label("Teams"),
                dcc.Dropdown(
                    id='unified-team-dropdown',
                    options=team_options,
                    value=default_teams,
                    multi=True
                ),
            ], className='control-group'),
            html.Div([
                html.Label("Seasons"),
                dcc.Dropdown(
                    id='unified-season-dropdown',
                    options=season_options,
                    value=default_seasons,
                    multi=True
                ),
            ], className='control-group'),
        ], className='unified-controls'),

        # Unified legend
        html.Div(id='unified-legend', className='unified-legend'),

        # Charts grid - 2 columns for first row, 1 for second
        html.Div([
            # Visualization 1: Scatter plot (top-left)
            html.Div([
                html.Div([
                    html.H3("Goals Conceded vs Goals Scored"),
                    html.P("Bubble size represents Points earned | Opacity represents Season recency", className='chart-subtitle')
                ], className='chart-header'),
                dcc.Graph(id='scatter-graph', clickData=None)
            ], className='chart-card chart-half'),

            # Visualization 2: Bar plot (top-right)
            html.Div([
                html.Div([
                    html.H3("Points by Season"),
                ], className='chart-header'),
                dcc.Graph(id='bar-graph', clickData=None)
            ], className='chart-card chart-half'),
        ], className='charts-row'),

        # Visualization 3: Line plot (full width)
        html.Div([
            html.Div([
                html.H3("Goals Scored by Season"),
            ], className='chart-header'),
            dcc.Graph(id='line-graph', clickData=None)
        ], className='chart-card chart-full'),

    ], className='page-wrapper')
])

# Line plot callback
@app.callback(
    Output('line-graph', 'figure'),
    Input('shared-teams-store', 'data')
)

def update_line(selected_teams):
    global color_cache

    if not selected_teams:
        selected_teams = default_teams

    filtered_df = df[df['Team'].isin(selected_teams)]
    color_map, color_cache = assign_plot_colors(selected_teams, cached_colors=color_cache)

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
        color_discrete_map=color_map,
        symbol_map=team_symbols
    )

    fig.update_traces(
        marker=dict(size=8)
    )

    fig.update_layout(
        margin=dict(l=50, r=50, t=15, b=50)
    )

    return fig


# Scatter plot callback
@app.callback(
    Output('scatter-graph', 'figure'),
    [Input('shared-teams-store', 'data'),
     Input('shared-seasons-store', 'data')]
)
def update_scatter(selected_teams, selected_seasons):
    global color_cache

    if not selected_teams:
        selected_teams = default_teams
    if not selected_seasons:
        selected_seasons = default_seasons

    # Handle single season vs list of seasons
    if isinstance(selected_seasons, str):
        selected_seasons = [selected_seasons]

    filtered_df = df[(df['Team'].isin(selected_teams)) & (df['Season'].isin(selected_seasons))]
    color_map, color_cache = assign_plot_colors(selected_teams, cached_colors=color_cache)

    # Use global max points for consistent sizing across all seasons
    global_max_points = df['Points'].max()

    # Sort seasons and assign opacity (recent seasons more opaque, older seasons more faded)
    sorted_seasons = sorted(selected_seasons)
    opacity_map = {}
    for i, season in enumerate(sorted_seasons):
        # Opacity ranges from 0.5 (oldest) to 1.0 (newest)
        opacity_map[season] = 0.5 + (i / max(len(sorted_seasons) - 1, 1)) * 0.5

    fig = px.scatter(
        filtered_df,
        x="Goals Conceded",
        y="Goals Scored",
        color="Team",
        size="Points",
        hover_name="Team",
        hover_data={"Points": True, "Goals Scored": True, "Goals Conceded": True, "Season": True},
        color_discrete_map=color_map
    )

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

    fig.update_layout(
        showlegend=False,
        height=500,
        margin=dict(l=50, r=50, t=15, b=50)
    )

    return fig


# Bar plot callback
@app.callback(
    Output('bar-graph', 'figure'),
    [Input('shared-teams-store', 'data'),
     Input('shared-seasons-store', 'data')]
)
def update_bar(selected_teams, selected_seasons):
    global color_cache

    if not selected_teams:
        selected_teams = default_teams
    if not selected_seasons:
        selected_seasons = default_seasons

    # Handle single season vs list of seasons
    if isinstance(selected_seasons, str):
        selected_seasons = [selected_seasons]

    # Calculate placement based on ALL teams in each season, then filter
    season_filtered_df = df[df['Season'].isin(selected_seasons)].copy()
    season_filtered_df['Placement'] = season_filtered_df.groupby('Season')['Points'].rank(method='min', ascending=False).astype(int)

    # Now filter to only selected teams
    filtered_df = season_filtered_df[season_filtered_df['Team'].isin(selected_teams)].copy()

    color_map, color_cache = assign_plot_colors(selected_teams, cached_colors=color_cache)

    fig = px.bar(
        filtered_df,
        x="Season",
        y="Points",
        color="Team",
        barmode="group",
        color_discrete_map=color_map,
        hover_data={"Season": True, "Team": True, "Points": True, "Placement": True},
        text="Placement"  # Show tournament placement instead of points
    )

    fig.update_traces(
        textposition="outside",  # Position text above the bars
        texttemplate="%{text}º"  # Show placement with ordinal indicator
    )

    fig.update_layout(
        xaxis_title="Season",
        yaxis_title="Points",
        margin=dict(l=50, r=50, t=15, b=50),
        height=500,
        showlegend=False
    )

    return fig


# Consolidated callback for team selection - handles dropdown and click events
@app.callback(
    [Output('shared-teams-store', 'data'),
     Output('unified-team-dropdown', 'value')],
    [Input('unified-team-dropdown', 'value'),
     Input('line-graph', 'clickData'),
     Input('scatter-graph', 'clickData'),
     Input('bar-graph', 'clickData')],
    State('shared-teams-store', 'data')
)
def update_teams(dropdown_teams, line_click, scatter_click, bar_click, current_store):
    if not callback_context.triggered:
        return current_store, current_store

    trigger_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    selected_teams = current_store or default_teams

    # Handle dropdown change
    if trigger_id == 'unified-team-dropdown':
        selected_teams = dropdown_teams or default_teams

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

    return selected_teams, selected_teams


# Consolidated callback for season selection
@app.callback(
    [Output('shared-seasons-store', 'data'),
     Output('unified-season-dropdown', 'value')],
    Input('unified-season-dropdown', 'value'),
    State('shared-seasons-store', 'data')
)
def update_seasons(dropdown_seasons, current_store):
    if not callback_context.triggered:
        return current_store, current_store

    selected_seasons = dropdown_seasons or current_store or default_seasons

    return selected_seasons, selected_seasons


# Callback for unified legend
@app.callback(
    Output('unified-legend', 'children'),
    Input('shared-teams-store', 'data')
)
def update_legend(selected_teams):
    global color_cache

    if not selected_teams:
        selected_teams = default_teams

    # Get color map for current teams
    color_map, color_cache = assign_plot_colors(selected_teams, cached_colors=color_cache)

    # Create legend items
    legend_items = []
    for team in sorted(selected_teams):
        color = color_map.get(team, '#999999')
        legend_items.append(
            html.Div([
                html.Div(style={'background-color': color, 'width': '16px', 'height': '16px', 'border-radius': '3px', 'display': 'inline-block', 'margin-right': '8px', 'vertical-align': 'middle'}),
                html.Span(team, style={'vertical-align': 'middle'})
            ], className='legend-item')
        )

    return html.Div(legend_items, className='legend-items')


if __name__ == "__main__":
    app.run(debug=True)
