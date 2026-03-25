import pandas as pd

master = pd.read_csv('epl_final.csv')
print(master.head())

def get_unique_teams(season_year):
    teams = master[master['Season'] == season_year]['HomeTeam'].unique()
    return teams

def get_team_data(team_name, season_year):
    team_data = master[(master['HomeTeam'] == team_name) | (master['AwayTeam'] == team_name)]
    return team_data[team_data['Season'] == season_year]

def get_team_performance(team_name, season_year):
    team_data = get_team_data(team_name, season_year)
    wins = team_data[((team_data['HomeTeam'] == team_name) & (team_data['FullTimeResult'] == 'H')) | 
                     ((team_data['AwayTeam'] == team_name) & (team_data['FullTimeResult'] == 'A'))].shape[0]
    losses = team_data[((team_data['HomeTeam'] == team_name) & (team_data['FullTimeResult'] == 'A')) | 
                       ((team_data['AwayTeam'] == team_name) & (team_data['FullTimeResult'] == 'H'))].shape[0]
    draws = team_data[team_data['FullTimeResult'] == 'D'].shape[0]
    
    return {'Wins': wins, 'Losses': losses, 'Draws': draws}

def get_team_goals(team_name, season_year):
    team_data = get_team_data(team_name, season_year)
    goals_scored = team_data.apply(lambda row: row['FullTimeHomeGoals'] if row['HomeTeam'] == team_name else row['FullTimeAwayGoals'], axis=1).sum()
    goals_conceded = team_data.apply(lambda row: row['FullTimeAwayGoals'] if row['HomeTeam'] == team_name else row['FullTimeHomeGoals'], axis=1).sum()
    
    return {'Goals Scored': goals_scored, 'Goals Conceded': goals_conceded}

def calculate_team_points(team_name, season_year):
    performance = get_team_performance(team_name, season_year)
    points = performance['Wins'] * 3 + performance['Draws']
    return points


if __name__ == "__main__":
    df = pd.read_csv('team_stats_by_season.csv')
    teams = df['Team'].unique()
    sorted_teams = sorted(teams)

    print(sorted_teams)
