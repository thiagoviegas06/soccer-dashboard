from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

df = pd.read_csv('team_stats_by_season.csv')
team_with_most_points = df.loc[df['Points'].idxmax()]['Team']
sorted_teams = df.groupby('Team')['Points'].sum().sort_values(ascending=False)
team_options = [{'label': team, 'value': team} for team in sorted_teams.index]

# Define consistent team colors
team_color_map = {
    "Man United": "#DA291C",   # Red
    "Man City": "#6CABDD",     # Sky Blue
    "Chelsea": "#034694",      # Blue
    "Arsenal": "#EF0107",      # Red
    "Liverpool": "#C8102E",    # Red
    "Tottenham": "#132257",    # Navy
    "Leeds": "#FFCD00",        # Yellow
    "Leicester": "#003090",    # Blue
    "Everton": "#003399",      # Blue
    "Newcastle": "#241F20",    # Black
}


season_options = [{'label': season, 'value': season} for season in sorted(df['Season'].unique())]


app.layout = html.Div([
    html.H1("Team Stats Dashboard"),
    # Visualization 1: Line plot (Goals Scored by Season)
    html.Div([
        html.H3("Goals Scored by Season (Line Plot)"),
        html.Label("Select Teams:"),
        dcc.Dropdown(
            id='line-team-dropdown',
            options=team_options,
            value=[team_options[0]['value']],
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
            value=[team_options[0]['value']],
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
    fig = px.line(
        filtered_df,
        x="Season",
        y="Goals Scored",
        color="Team",
        title="Goals Scored by Season",
        color_discrete_map=team_color_map
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
    fig = px.scatter(
        filtered_df,
        x="Goals Conceded",
        y="Goals Scored",
        color="Team",
        size="Points",
        hover_name="Team",
        title=f"Goals Conceded vs Goals Scored ({selected_season})",
        color_discrete_map=team_color_map
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
    fig = px.bar(
        filtered_df,
        x="Team",
        y="Points",
        color="Team",
        title=f"Points by Team ({selected_season})",
        color_discrete_map=team_color_map
    )
    return fig

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



if __name__ == "__main__":
    app.run(debug=True)