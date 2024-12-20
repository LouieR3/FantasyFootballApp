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
import openpyxl

start_time = time.time()
espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"

year = 2024
# FileName for the Excel file and sheet
league = League(league_id=310334683, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
fileName = leagueName + " " + str(year) + ".xlsx"
sheet_name = "LPI By Week"

# Read the LPI data
lpi_df = pd.read_excel(fileName, sheet_name=sheet_name, index_col=0)  # Team names as index
settings = league.settings

sheet_name = "LPI By Week"

# Read the LPI data
lpi_df = pd.read_excel(fileName, sheet_name=sheet_name, index_col=0)  # Team names as index
lpi_df = lpi_df.drop(['Change From Last Week'], axis=1)

# --------------------------------------------------------------------------------------
# PLAYOFF RESULTS
# --------------------------------------------------------------------------------------

# team_owners = [team.owners for team in league.teams]
team_names = [team.team_name for team in league.teams]
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

if current_week is None:
    current_week = settings.reg_season_count
elif current_week != settings.reg_season_count:
    current_week -= 1

# Store data in DataFrames 
scores_df = pd.DataFrame(team_scores, index=team_names)
schedules_df = pd.DataFrame(schedules, index=team_names)
# print(scores_df)
last_column_name = scores_df.columns[-1]
# print(schedules_df)

# Playoff teams and seeds
standings = [team.team_name for team in league.standings_weekly(settings.reg_season_count)]
num_playoff_teams = settings.playoff_team_count
playoff_teams = standings[:num_playoff_teams]  # Top teams in the playoffs
reg_season_count = settings.reg_season_count
# Initialize the results list
playoff_results = []

# Function to determine round name based on number of teams
def get_round_name(num_teams):
    if num_teams >= 5:
        return "Quarter Final"
    elif num_teams >= 3:
        return "Semi Final"
    elif num_teams == 2:
        return "Championship"
    else:
        return "Final Team"  # Special case if there's one team left (shouldn't be used in matchups)

# Iterate through playoff weeks
last_column_name = scores_df.columns[-1]
for week in range(reg_season_count, last_column_name+1):
    round_name = get_round_name(len(playoff_teams))
    print(f"Processing Playoff Round {round_name} (Week {week + 1})")
    print(playoff_teams)
    print()
    advancing_teams = []  # Teams that win in the current week
    round_number = week - reg_season_count + 1
    teams_already_processed = set()  # Track teams already in a matchup

    # Matchups: process playoff teams
    for team in playoff_teams:
        # Skip if this team has already been processed in a matchup
        if team in teams_already_processed:
            continue

        opponent = schedules_df.loc[team, week]  # Get opponent for the current week

        # Skip if the team has a bye (e.g., they face themselves)
        if opponent == team:
            playoff_results.append({
                "Round": round_name,
                "Team 1": team,
                "Seed 1": standings.index(team) + 1,
                "Score 1": scores_df.loc[team, week],
                "Team 1 LPI": lpi_df.loc[team, f"Week {week + 1}"],  # Add LPI value
                "Team 2": "Bye",
                "Seed 2": "-",
                "Score 2": "-",
                "Winner": team
            })
            advancing_teams.append(team)  # Auto-advance the team
            continue

        # Skip if the opponent has already been processed
        if opponent in teams_already_processed:
            continue

        # Retrieve team and opponent scores
        score_1 = scores_df.loc[team, week]
        score_2 = scores_df.loc[opponent, week]

        # Retrieve LPI values
        team_1_lpi = lpi_df.loc[team, f"Week {week + 1}"]
        team_2_lpi = lpi_df.loc[opponent, f"Week {week + 1}"]

        # Determine seeds
        seed_1 = standings.index(team) + 1
        seed_2 = standings.index(opponent) + 1

        # Determine winner
        if score_1 > score_2:
            winner = team
        elif score_2 > score_1:
            winner = opponent
        else:
            winner = "Tie"  # Handle tie scenario if needed

        # Append results to the playoff results list
        playoff_results.append({
            "Round": round_name,
            "Team 1": team,
            "Seed 1": seed_1,
            "Score 1": score_1,
            "Team 1 LPI": team_1_lpi,
            "Team 2": opponent,
            "Seed 2": seed_2,
            "Score 2": score_2,
            "Team 2 LPI": team_2_lpi,
            "Winner": winner
        })

        # Add the winner to the advancing teams list
        advancing_teams.append(winner)

        # Mark both teams as processed
        teams_already_processed.add(team)
        teams_already_processed.add(opponent)

    # Update playoff_teams for the next round
    playoff_teams = advancing_teams
    round_number += 1

    # Break the loop if there is only one team left (champion)
    if len(playoff_teams) <= 1:
        break

# Convert results to DataFrame
playoff_df = pd.DataFrame(playoff_results)

# Display the DataFrame
print(playoff_df)

# Add playoff_df as a new sheet to the existing Excel file
# with pd.ExcelWriter(fileName, engine="openpyxl", mode="a") as writer:
#     playoff_df.to_excel(writer, sheet_name="Playoff Results", index=False)