import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
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

start_time = time.time()

# Pennoni Younglings
# league = League(league_id=310334683, year=2023, espn_s2=CRED["legacy_s2_a"], swid=CRED["louie_swid"])
# league = League(league_id=310334683, year=2022, espn_s2=CRED["legacy_s2_a"],swid=CRED["louie_swid"])

# Family League
# league = League(league_id=1725372613, year=2023, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])
# league = League(league_id=1725372613, year=2022, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])

# EBC League
league = League(league_id=1118513122, year=2023, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])
# league = League(league_id=1118513122, year=2022, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])
# league = League(league_id=1118513122, year=2021, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])

# Pennoni Transportation
# league = League(league_id=1339704102, year=2022, espn_s2=CRED["legacy_s2_c"], swid=CRED["legacy_swid"])

# Prahlad Friends League
# league = League(league_id=1781851, year=2022, espn_s2=CRED["legacy_s2_c"], swid=CRED["legacy_swid"])

settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
fileName = leagueName + " 2023"
file = leagueName + " 2023.xlsx"

team_owners = [team.owner for team in league.teams]
team_names = [team.team_name for team in league.teams]

# if "Family League" in fileName:
#    team_names = [team_name.replace("Kuppcakes  .", "The Adams Family")
#               .replace("Wallingford  Wild Hormones", "Waverly Wild Hormones")
#               .replace("Lockett inma pockett", "CHUBBER")
#               for team_name in team_names]
#    print(team_names)
# if "EBC League" in fileName:
#    team_names = [team_name.replace("Kuppcakes  .", "The Adams Family")
#               .replace("Wallingford  Wild Hormones", "Waverly Wild Hormones")
#               .replace("Lockett inma pockett", "CHUBBER")
#               for team_name in team_names]
#    print(team_names)
# if "Pennoni Younglings" in fileName:
#    team_names = [team_name.replace("Kuppcakes  .", "The Adams Family")
#               .replace("Wallingford  Wild Hormones", "Waverly Wild Hormones")
#               .replace("Lockett inma pockett", "CHUBBER")
#               for team_name in team_names]
#    print(team_names)

team_scores = [team.scores for team in league.teams] 
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
# print(current_week)
if current_week is None:
    current_week = settings.reg_season_count
elif current_week != settings.reg_season_count:
  current_week -= 1
# print(current_week)

# Store data in DataFrames 
scores_df = pd.DataFrame(team_scores, index=team_names)
schedules_df = pd.DataFrame(schedules, index=team_names)

# Create empty dataframe  
records_df = pd.DataFrame(index=team_names, columns=team_names)

# Fill diagonal with team names
records_df.fillna('', inplace=True) 

# Initialize a DataFrame to store total wins for each team against all schedules
total_wins_df = pd.DataFrame(0, columns=team_names, index=team_names)

# Iterate through teams
for team in team_names:
  # Get team scores
  team_scores = scores_df.loc[team].tolist() 
  # Iterate through opponents
  for opp in team_names:
    
    # Compare scores
    wins = 0
    losses = 0
    ties = 0
    for i in range(current_week):
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
    
    # Update the total wins DataFrame
    total_wins_df.at[team, opp] = wins

# Calculate the total number of teams
num_teams = len(team_names)

# Initialize lists to store the chances
better_record = []
same_record = []
worse_record = []

# Calculate the diagonal (each team's own record)
diagonal = records_df.values.diagonal()

for team in team_names:
    # Count the number of records greater, equal, and smaller than the team's own record
    better = len([1 for record in records_df[team] if record > diagonal[team_names.index(team)]])
    same = len([1 for record in records_df[team] if record == diagonal[team_names.index(team)]])
    worse = len([1 for record in records_df[team] if record < diagonal[team_names.index(team)]])
    
    # Calculate the chances
    total = better + same + worse
    better_chance = (better / total) * 100
    same_chance = (same / total) * 100
    worse_chance = (worse / total) * 100
    
    better_record.append(str(round(better_chance))+"%")
    same_record.append(str(round(same_chance))+"%")
    worse_record.append(str(round(worse_chance))+"%")

# Create the new DataFrame
chance_df = pd.DataFrame({
    'Teams': team_names,
    "% Chance for a better record": better_record,
    "% Chance for the same record": same_record,
    "% Chance for a worse record": worse_record
})

# Set the 'Teams' column as the index
chance_df.set_index('Teams', inplace=True)

# Display the resulting DataFrame
print(chance_df)