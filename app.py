from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

df = pd.read_csv('team_stats_by_season.csv')
team_with_most_points = df.loc[df['Points'].idxmax()]['Team']
sorted_teams = df.groupby('Team')['Points'].sum().sort_values(ascending=False)
team_options = [{'label': team, 'value': team} for team in sorted_teams.index]


season_options = [{'label': season, 'value': season} for season in sorted(df['Season'].unique())]

app.layout = html.Div([
    html.H1("Team Stats Visualization"),
    html.Div([
        html.Label("Select Teams:"),
        dcc.Dropdown(
            id='team-dropdown',
            options=team_options,
            value=[team_options[0]['value'], team_options[1]['value'], team_options[2]['value'], team_options[3]['value'], team_options[4]['value']],
            multi=True
        ),
        html.Br(),
        html.Label("Select Season:"),
        dcc.Dropdown(
            id='season-dropdown',
            options=season_options,
            value=season_options[0]['value'],
            multi=False
        )
    ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    html.Div([
        dcc.Graph(id='team-graph')
    ], style={'width': '70%', 'display': 'inline-block'})
])


@app.callback(
    Output('team-graph', 'figure'),
    [Input('team-dropdown', 'value'),
     Input('season-dropdown', 'value')]
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
        title=f"Goals Conceded vs Goals Scored ({selected_season})"
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