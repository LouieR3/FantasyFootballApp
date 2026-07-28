from credentials import CRED
import pandas as pd
from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
# import xlsxwriter
from itertools import combinations
import itertools
import math
import numpy as np
import random

start_time = time.time()

# Pennoni Younglings
# league = League(league_id=310334683, year=2023, espn_s2=CRED["legacy_s2_a"], swid=CRED["louie_swid"])
league = League(league_id=310334683, year=2022, espn_s2=CRED["legacy_s2_a"],swid=CRED["louie_swid"])

# Family League
# league = League(league_id=1725372613, year=2023, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])
# league = League(league_id=1725372613, year=2022, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])

# EBC League
# league = League(league_id=1118513122, year=2023, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])
# league = League(league_id=1118513122, year=2022, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])
# league = League(league_id=1118513122, year=2021, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])

# Pennoni Transportation
# league = League(league_id=1339704102, year=2023, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])
# league = League(league_id=1339704102, year=2022, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Game of Yards
# league = League(league_id=1781851, year=2023, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])
# league = League(league_id=1781851, year=2022, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Brown Munde
# league = League(league_id=367134149, year=2023, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
fileName = leagueName + " 2023"
file = leagueName + ".xlsx"

team_owners = [team.owner for team in league.teams]
team_names = [team.team_name for team in league.teams]
team_scores = [team.scores for team in league.teams] 
team_scores_x = [team.scores for team in league.teams] 
schedules = []
for team in league.teams:
  schedule = [opponent.team_name for opponent in team.schedule]
  schedules.append(schedule)

# Precompute current week 
current_week = None
for week in range(1, settings.reg_season_count+1):
    scoreboard = league.scoreboard(week)
    if not any(matchup.home_score for matchup in scoreboard):
        current_week = week
        break 
# print()
if current_week is None:
    current_week = settings.reg_season_count
elif current_week != settings.reg_season_count:
  current_week -= 1
current_week = 17
# Store data in DataFrames 
scores_df = pd.DataFrame(team_scores, index=team_names)
schedules_df = pd.DataFrame(schedules, index=team_names)

# Create empty dataframe  
records_df = pd.DataFrame(index=team_names, columns=team_names)

# Fill diagonal with team names
records_df.fillna('', inplace=True) 

# Initialize a DataFrame to store total wins for each team against all schedules
total_wins_weekly_df = pd.DataFrame(0, columns=team_names, index=team_names)

# Initialize an empty DataFrame to store LPI scores for each week
lpi_weekly_df = pd.DataFrame()
matchup_results_df = pd.DataFrame(columns=['Week', 'HomeTeam', 'AwayTeam', 'HomeLPI', 'AwayLPI', 'LPI_Difference', 'Winner'])

# Iterate through each week
for week in range(1, current_week+1):
    # Initialize a DataFrame to store total wins for each team against all schedules for this week
    total_wins_weekly_df = pd.DataFrame(0, columns=team_names, index=team_names)

    # Iterate through teams (similar to your previous code)
    for team in team_names:
      # Get team scores
      team_scores = scores_df.loc[team].tolist() 
      # Iterate through opponents
      for opp in team_names:
        
        # Compare scores
        wins = 0
        losses = 0
        ties = 0
        for i in range(week):
          # Get opponent schedule
          opp_schedule = schedules_df.loc[opp].tolist()
          
          # Get opponent scores
          opp_scores = [scores_df.loc[o][i] for i, o in enumerate(opp_schedule)]
          if team == opp:
            # Get team's opponent this week 
            opp_team = schedules_df.loc[team, i]
            
            # Get team and opponent score
            team_score = scores_df.loc[team, i]
            opp_score = scores_df.loc[opp_team, i]

            if team_score > opp_score:
              wins += 1
            elif team_score < opp_score:
              losses += 1
            else:
              ties += 1

          else:
            # Check if opponent is the same 
            if opp == schedules_df.loc[team, i]:
              # Opponent is the same, get correct scores
              team_score = scores_df.loc[team, i]
              opp_score = scores_df.loc[schedules_df.loc[team, i], i]

            else:  
              # Opponent is different
              opp_schedule = schedules_df.loc[opp].tolist()
              opp_scores = [scores_df.loc[o][i] for i, o in enumerate(opp_schedule)]
              team_score = team_scores[i]
              opp_score = opp_scores[i]

            # Compare scores
            if team_score > opp_score:
              wins += 1
            elif team_score < opp_score:
              losses += 1
            else:
              ties += 1
        
        # Record result
        record = f"{wins}-{losses}-{ties}"
        records_df.at[team, opp] = record 
        # Update the total wins DataFrame for this week
        total_wins_weekly_df.at[team, opp] = wins  # Set wins for all opponents

    # Calculate LPI scores for this week
    team_wins = total_wins_weekly_df.sum(axis=1)
    schedule_wins = [sum(total_wins_weekly_df[team]) for team in team_names]
    num_teams_in_league = len(team_names)
    lpi_scores = ((team_wins - schedule_wins) * (12 / num_teams_in_league)).round().astype(int)
    week_name = "Week " + str(week)
    # Add LPI scores for this week to the weekly DataFrame
    lpi_weekly_df[week_name] = lpi_scores
    lpi_weekly_df = lpi_weekly_df.sort_values(by=[week_name], ascending=[False])
    # lpi_df.reset_index(drop=True, inplace=True)
# Display the DataFrame with LPI scores for each week

# Calculate actual wins
actual_records = records_df.values.diagonal()
# Calculate the total wins for each team
team_wins = total_wins_weekly_df.sum(axis=1)
avg_team_wins = team_wins / len(team_names)
# Calculate expected wins
expected_wins = total_wins_weekly_df.mean(axis=1)

# Calculate differences
differences = avg_team_wins - total_wins_weekly_df.values.diagonal()
# Create a DataFrame for ranking
rank_df = pd.DataFrame({
    'Team': team_names,
    'Expected Wins': avg_team_wins,
    'Difference': differences,
    'Record': actual_records,
})
# print(rank_df)
# Create schedule_rank_df
schedule_rank_df = pd.DataFrame({
    'Teams': rank_df['Team'],
    'Wins Against Schedule': [sum(total_wins_weekly_df[team]) / len(team_names) for team in rank_df['Team']],
    'Record': rank_df['Record']
})
# print(schedule_rank_df)

# Calculate the "Change from last week" column
lpi_weekly_df['Change From Last Week'] = lpi_weekly_df[week_name] - lpi_weekly_df['Week ' + str(week - 1)]

# Function to format the change value
def format_change(change):
    if change > 0:
        return f'↑{change}'
    elif change < 0:
        return f'↓{abs(change)}'
    else:
        return str(change)

# Apply the formatting function to the "Change from last week" column
lpi_weekly_df['Change From Last Week'] = lpi_weekly_df['Change From Last Week'].apply(format_change)
# lpi_weekly_df.insert(loc = 0, column = 'Teams', value = lpi_weekly_df.index)
# lpi_weekly_df.reset_index(drop=True, inplace=True)

# Display the updated DataFrame
print(lpi_weekly_df)