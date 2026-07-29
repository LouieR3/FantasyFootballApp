import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
from credentials import CRED
import pandas as pd
from espn_api.football import League
import time

# Initialize an empty dictionary to store head-to-head records for each year
head_to_head_records_by_year = {}

# Define the league information for each year
league_info = [
    {'year': 2021, 'espn_s2': CRED["legacy_s2_b"], 'league_id': '1118513122'},
    {'year': 2022, 'espn_s2': CRED["legacy_s2_b"], 'league_id': '1118513122'},
    {'year': 2023, 'espn_s2': CRED["legacy_s2_b"], 'league_id': '1118513122'}
]

for league_data in league_info:
    year = league_data['year']
    espn_s2 = league_data['espn_s2']
    league_id = league_data['league_id']
    swid=CRED["louie_swid"]

    # Create the league instance for the specific year
    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

    # Precompute the current week
    current_week = None
    for week in range(1, league.settings.reg_season_count + 1):
        scoreboard = league.scoreboard(week)
        if not any(matchup.home_score for matchup in scoreboard):
            current_week = week
            break

    if current_week is None:
        current_week = league.settings.reg_season_count
    elif current_week != league.settings.reg_season_count:
        current_week -= 1

    # Initialize a dictionary to store head-to-head records for this year
    team_owners = [team.owner for team in league.teams]
    head_to_head_records = {owner: {opponent: [0, 0, 0] for opponent in league.teams if opponent.owner == owner} for owner in set(team.owner for team in league.teams)}

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

    # Store the head-to-head records for this year
    head_to_head_records_by_year[year] = head_to_head_records

# Print the head-to-head records for each year
for year, head_to_head_records in head_to_head_records_by_year.items():
    print(f"-------------------------")
    print(f"Head-to-Head Records for {year}:")
    for owner in head_to_head_records:
        print(f"Head-to-Head Records for {owner}:")
        for opponent in head_to_head_records[owner]:
            if owner != opponent:
                wins, losses, ties = head_to_head_records[owner][opponent]
                print(f"Against {opponent}: {wins} - {losses} - {ties}")