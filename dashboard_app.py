import streamlit as st
import pandas as pd
import numpy as np
from main import get_unique_teams, get_team_data, get_team_performance, get_team_goals

# Load data (adjust path if needed)
data = pd.read_csv('epl_final.csv')

st.title('Premier League Dashboard')

# Select season
distinct_seasons = data['Season'].unique()
season_year = st.selectbox('Select Season', sorted(distinct_seasons))

# Select team
teams = get_unique_teams(season_year)
team_name = st.selectbox('Select Team', sorted(teams))

# Show team data
if team_name:
    team_data = get_team_data(team_name, season_year)
    st.subheader(f"Data for {team_name} in {season_year} season")
    st.dataframe(team_data)

    performance = get_team_performance(team_name, season_year)
    st.subheader(f"Performance of {team_name} in {season_year} season")
    st.write(performance)

    goals = get_team_goals(team_name, season_year)
    st.subheader(f"Goals of {team_name} in {season_year} season")
    st.write({'Goals Scored': int(goals['Goals Scored']), 'Goals Conceded': int(goals['Goals Conceded'])})

# Optionally add charts
    st.bar_chart(pd.DataFrame([goals]))
