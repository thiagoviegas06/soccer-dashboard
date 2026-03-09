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
    season_year = "2000/01"
    teams = get_unique_teams(season_year)
    print(f"Teams in {season_year} season: {teams}")

    team_name = 'Man United'
    team_data = get_team_data(team_name, season_year)
    print(f"Data for {team_name} in {season_year} season:\n{team_data.head()}")

    performance = get_team_performance(team_name, season_year)
    print(f"Performance of {team_name} in {season_year} season: {performance}")

    goals = get_team_goals(team_name, season_year)
    print(f"Goals of {team_name} in {season_year} season: {{'Goals Scored': {goals['Goals Scored']}, 'Goals Conceded': {goals['Goals Conceded']}}}")

    points = calculate_team_points(team_name, season_year)
    print(f"Points of {team_name} in {season_year} season: {points}")

    seasons = master['Season'].unique()
    print(f"Available seasons: {seasons}")

    print("++++++++++++++++++++")

    print("Team stats by season:")

    rows = []
    for season in seasons:
        teams = get_unique_teams(season)
        for team in teams:
            goals = get_team_goals(team, season)
            points = calculate_team_points(team, season)
            rows.append({
                'Season': season,
                'Team': team,
                'Goals Scored': goals['Goals Scored'],
                'Points': points,
                "Goals Conceded": goals['Goals Conceded']
            })


    stats_df = pd.DataFrame(rows)
    print(stats_df.head(10))

    stats_df.to_csv('team_stats_by_season.csv', index=False)

