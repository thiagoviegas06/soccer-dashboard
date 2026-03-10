from dash import Dash, html, dcc, Input, Output
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
    "Man United": "#DA291C",   # Red
    "Man City": "#6CABDD",     # Sky Blue
    "Chelsea": "#003090",      # Blue
    "Arsenal": "#DA291C",      # Red
    "Liverpool": "#DA291C",    # Red
    "Tottenham": "#132257",    # Navy
    "Leeds": "#FFCD00",        # Yellow
    "Leicester": "#003090",    # Blue
    "Everton": "#003399",      # Blue
    "Newcastle": "#241F20",    # Black
}

# Fallback color pool — wide variety to maximize distinctiveness when picking dynamically
fallback_colors = [
    "#8E44AD",  # Purple
    "#16A085",  # Teal
    "#E67E22",  # Orange
    "#1ABC9C",  # Aqua
    "#9B59B6",  # Violet
    "#F39C12",  # Amber
    "#27AE60",  # Green
    "#D35400",  # Dark Orange
    "#2ECC71",  # Lime Green
    "#7F8C8D",  # Gray
    "#BDC3C7",  # Silver
    "#E91E63",  # Pink
    "#00BCD4",  # Cyan
    "#FF7043",  # Deep Orange
    "#795548",  # Brown
    "#607D8B",  # Blue Gray
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
    html.H1("Team Stats Dashboard"),
    # Visualization 1: Line plot (Goals Scored by Season)
    html.Div([
        html.H3("Goals Scored by Season (Line Plot)"),
        html.Label("Select Teams:"),
        dcc.Dropdown(
            id='line-team-dropdown',
            options=team_options,
            value=[(team_options[0]['value'], team_options[1]['value'], team_options[2]['value'], team_options[3]['value'], team_options[4]['value'])],
            multi=True
        ),
        dcc.Graph(id='line-graph')
    ], style={'width': '80%', 'margin': 'auto', 'padding': '20px', 'backgroundColor': '#f9f9f9', 'marginBottom': '30px', 'borderRadius': '10px'}),

    # Visualization 2: Scatter plot (Goals Conceded vs Goals Scored)
    html.Div([
        html.H3("Goals Conceded vs Goals Scored (Scatter Plot)"),
        html.Label("Select Teams:"),
        dcc.Dropdown(
            id='scatter-team-dropdown',
            options=team_options,
            value=[team_options[0]['value'], team_options[1]['value'], team_options[2]['value'], team_options[3]['value'], team_options[4]['value']],
            multi=True
        ),
        html.Label("Select Season:"),
        dcc.Dropdown(
            id='scatter-season-dropdown',
            options=season_options,
            value=season_options[0]['value'],
            multi=False
        ),
        dcc.Graph(id='scatter-graph')
    ], style={'width': '80%', 'margin': 'auto', 'padding': '20px', 'backgroundColor': '#f9f9f9', 'marginBottom': '30px', 'borderRadius': '10px'}),

    # Visualization 3: Bar plot (Points by Team)
    html.Div([
        html.H3("Points by Team (Bar Plot)"),
        html.Label("Select Season:"),
        dcc.Dropdown(
            id='bar-season-dropdown',
            options=season_options,
            value=season_options[0]['value'],
            multi=False
        ),
        dcc.Graph(id='bar-graph')
    ], style={'width': '80%', 'margin': 'auto', 'padding': '20px', 'backgroundColor': '#f9f9f9', 'marginBottom': '30px', 'borderRadius': '10px'})
])
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
    return fig


# Bar plot callback
@app.callback(
    Output('bar-graph', 'figure'),
    Input('bar-season-dropdown', 'value')
)
def update_bar(selected_season):
    filtered_df = df[df['Season'] == selected_season].copy()
    filtered_df = filtered_df.sort_values('Team')
    filtered_df = filtered_df.head(7)
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


if __name__ == "__main__":
    app.run(debug=True)