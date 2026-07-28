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
# league = League(league_id=1118513122, year=2023, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])
# league = League(league_id=1118513122, year=2022, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])
league = League(league_id=1118513122, year=2025, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])

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

# Initialize a dictionary to store head-to-head records
head_to_head_records = {team: {opponent: [0, 0, 0] for opponent in team_owners} for team in team_owners}

# Iterate through each week's matchups
for week in range(1, current_week):
    scoreboard = league.scoreboard(week)

    # Iterate through each matchup in the scoreboard
    for matchup in scoreboard:
        home_team = matchup.home_team.owner
        away_team = matchup.away_team.owner
        home_score = matchup.home_score
        away_score = matchup.away_score

        # Determine the winner based on scores
        if home_score > away_score:
            winner = home_team
            loser = away_team
        elif away_score > home_score:
            winner = away_team
            loser = home_team
        else:
            winner = None  # A tie

        # Update the head-to-head records
        if winner:
            head_to_head_records[winner][loser][0] += 1  # Increment wins
            head_to_head_records[loser][winner][1] += 1  # Increment losses
        else:
            # If it's a tie, increment ties for both teams
            head_to_head_records[home_team][away_team][2] += 1
            head_to_head_records[away_team][home_team][2] += 1

# Print the head-to-head records
for team in team_owners:
    print("-------------------------")
    print(f"Head-to-Head Records for {team}:")
    for opponent in team_owners:
        if team != opponent:
            wins, losses, ties = head_to_head_records[team][opponent]
            print(f"Against {opponent}: {wins} - {losses} - {ties}")