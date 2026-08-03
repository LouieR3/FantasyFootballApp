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
from operator import itemgetter

import xlsxwriter
from itertools import combinations
import itertools
import math
import numpy as np
import random
import openpyxl
from ffapp.metrics.monte_carlo_odds import (
    calculate_team_stats,
    simulate_remaining_season,
    create_summary_dataframes,
    add_weekly_analysis_to_main,
    calculate_remaining_schedule_difficulty,
)
from ffapp.metrics.owner_overrides import resolve_owner, owner_id_for
from ffapp.espn import week_utils
from ffapp.espn import league_settings
from paths import LEAGUES_DIR


start_time = time.time()
espn_s2 = CRED["louie_s2"]

year = 2025
# Pennoni Younglings
# league = League(league_id=310334683, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])

# Family League
# league = League(league_id=996930954, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])

# # EBC League
# league = League(
#     league_id=1118513122,
#     year=year,
#     espn_s2=espn_s2,
#     swid=CRED["louie_swid"],
# )

# Pennoni Transportation
# league = League(league_id=1339704102, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Game of Yards
# league = League(league_id=1781851, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Brown Munde
# league = League(league_id=367134149, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Turf On Grade 2.0 League
# league = League(league_id=1242265374, year=year, espn_s2=CRED["turf_s2"], swid=CRED["prahlad_swid"])

# Las League
# league = League(league_id=1049459, year=year, espn_s2=CRED["la_s2"], swid=CRED["la_swid"])

# Hannahs League
hannah_s2 = CRED["hannah_s2"]
# league = League(league_id=1399036372, year=2025, espn_s2=hannah_s2, swid=CRED["hannah_swid"])

ava_s2 = CRED["ava_s2"]
matt_s2 = CRED["matt_s2"]
elle_s2 = CRED["elle_s2"]
dave_s2 = CRED["dave_s2"]
ayush_s2 = CRED["ayush_s2"]
nolan_s2 = CRED["nolan_s2"]

# Avas League
# league = League(league_id=417131856, year=year, espn_s2=ava_s2, swid=CRED["ava_swid"])

# Matts League
# league = League(league_id=261375772, year=year, espn_s2=matt_s2, swid=CRED["matt_swid"])

# Elles League
# league = League(league_id=1259693145, year=year, espn_s2=elle_s2, swid=CRED["elle_swid"])

# Dave Work League
# year = 2024
# league = League(league_id= 1675186799, year= year, espn_s2= dave_s2, swid= CRED["dave_swid"])
# Dave Friend League
# league = League(league_id= 1924463077, year= year, espn_s2= dave_s2, swid= CRED["dave_swid"])

# Ayush League
league = League(league_id=558148583, year=year, espn_s2=ayush_s2, swid=CRED["ayush_swid"])
settings = league.settings

# Nolan League
# league = League(
#     league_id=496646254,
#     year=year,
#     espn_s2=nolan_s2,
#     swid=CRED["nolan_swid"],
# )
# settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
league_settings.save_settings(leagueName, year, settings)
fileName = leagueName + " " + str(year)
file = leagueName + ".xlsx"

# team_owners = [team.owners for team in league.teams]
team_names = [team.team_name for team in league.teams]
team_scores = [team.scores for team in league.teams]
team_scores_x = [team.scores for team in league.teams]
schedules = []
for team in league.teams:
    schedule = [opponent.team_name for opponent in team.schedule]
    schedules.append(schedule)

# Store data in DataFrames
scores_df = pd.DataFrame(team_scores, index=team_names)
schedules_df = pd.DataFrame(schedules, index=team_names)
# current_week is the next week to play; range(1, current_week) walks the
# completed weeks. The old inline detection then added 1, counting one week too
# many mid-season; its `shape[1]` fallback also dropped the final week.
current_week = week_utils.current_week(scores_df)
print(f"{current_week - 1} weeks played, current week {current_week}")
print(settings.reg_season_count)
print(settings.playoff_team_count)
print()
# print(schedules_df)
# Create empty dataframe
records_df = pd.DataFrame(index=team_names, columns=team_names)

# Fill diagonal with team names
records_df.fillna("", inplace=True)

# Initialize a DataFrame to store total wins for each team against all schedules
total_wins_weekly_df = pd.DataFrame(0, columns=team_names, index=team_names)

# Initialize an empty DataFrame to store LPI scores for each week
lpi_weekly_df = pd.DataFrame()

# Iterate through each week
for week in range(1, current_week):
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
                        opp_scores = [
                            scores_df.loc[o][i] for i, o in enumerate(opp_schedule)
                        ]
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
    lpi_scores = (
        ((team_wins - schedule_wins) * (12 / num_teams_in_league)).round().astype(int)
    )
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
rank_df = pd.DataFrame(
    {
        "Team": team_names,
        "Expected Wins": avg_team_wins,
        "Difference": differences,
        "Record": actual_records,
    }
)
# print(rank_df)
# Create schedule_rank_df
schedule_rank_df = pd.DataFrame(
    {
        "Teams": rank_df["Team"],
        "Wins Against Schedule": [
            sum(total_wins_weekly_df[team]) / len(team_names)
            for team in rank_df["Team"]
        ],
        "Record": rank_df["Record"],
    }
)
# print(schedule_rank_df)


# Function to format the change value
def format_change(change):
    if change > 0:
        return f"↑{change}"
    elif change < 0:
        return f"↓{abs(change)}"
    else:
        return str(change)


# lpi_weekly_df.insert(loc = 0, column = 'Teams', value = lpi_weekly_df.index)
# lpi_weekly_df.reset_index(drop=True, inplace=True)

# Needs two completed weeks to diff. With one week played the old
# `> 1` test still ran and looked up a non-existent 'Week 0'.
if current_week > 2:
    # Calculate the "Change from last week" column
    lpi_weekly_df["Change From Last Week"] = (
        lpi_weekly_df[week_name] - lpi_weekly_df["Week " + str(week - 1)]
    )
    # Apply the formatting function to the "Change from last week" column
    lpi_weekly_df["Change From Last Week"] = lpi_weekly_df[
        "Change From Last Week"
    ].apply(format_change)
else:
    lpi_weekly_df["Change From Last Week"] = 0


def owner_df_creation(league):
    """
    Creates a DataFrame mapping owner IDs to Display Names and Team Names for a given league.

    Parameters:
    - league (League): The league object.

    Returns:
    - pd.DataFrame: A DataFrame with columns 'Display Name', 'ID', and 'Team Name'.
    """
    # Co-owned teams resolve to their canonical owner (owner_overrides.py)
    data = []
    for team in league.teams:
        owner = resolve_owner(league, team)
        data.append(
            {
                "Display Name": f"{owner.get('firstName', '')} {owner.get('lastName', '')}".strip(),
                "ID": owner.get("id"),
                "Team Name": team.team_name,
            }
        )

    # Create the DataFrame
    return pd.DataFrame(data)


owner_df = owner_df_creation(league)
team_dict = dict(zip(owner_df["Team Name"], owner_df["Display Name"]))
# Display the updated DataFrame
print(lpi_weekly_df)
lpi_df = lpi_weekly_df[[week_name, "Change From Last Week"]]
lpi_df = lpi_df.rename(columns={week_name: "Louie Power Index (LPI)"})
lpi_df.insert(loc=0, column="Teams", value=lpi_df.index)

lpi_df.insert(loc=1, column="Owners", value="")
# Map the records to lpi_df based on matching team names
lpi_df["Owners"] = lpi_df["Teams"].map(team_dict)

lpi_df.reset_index(drop=True, inplace=True)
lpi_df.index = lpi_df.index + 1
lpi_df.insert(loc=3, column="Record", value="")
# Create a dictionary to map team names to records from rank_df
team_to_record = dict(zip(rank_df["Team"], rank_df["Record"]))

# Map the records to lpi_df based on matching team names
lpi_df["Record"] = lpi_df["Teams"].map(team_to_record)
# team_dict = dict(zip(team_names, team_owners))

# Apply dictionary mapping to Teams column
# lpi_df.insert(1, "Owner", lpi_df['Teams'].map(team_dict))
print(lpi_df)

matchup_results = []
# Iterate through each week's matchups
for week in range(1, current_week + 1):
    matchups = league.scoreboard(week)
    for matchup in matchups:
        if matchup.home_score == 0 or matchup.away_score == 0:
            # Skip this matchup
            continue
        home_team = matchup.home_team.team_name
        away_team = matchup.away_team.team_name
        # Get LPI for home and away teams for this week
        home_lpi = lpi_weekly_df.at[home_team, "Week " + str(week)]
        away_lpi = lpi_weekly_df.at[away_team, "Week " + str(week)]
        # Calculate LPI difference
        higher_lpi = max(home_lpi, away_lpi)
        lower_lpi = min(home_lpi, away_lpi)
        lpi_difference = higher_lpi - lower_lpi
        # Determine the winner of the matchup
        winner = home_team if matchup.home_score > matchup.away_score else away_team
        # Record the matchup results and LPI differences
        matchup_result = {
            "Week": week,
            "Home Team": home_team,
            "Away Team": away_team,
            "Home LPI": home_lpi,
            "Away LPI": away_lpi,
            "LPI Difference": lpi_difference,
            "Winner": winner,
        }
        # Append the dictionary to the list
        matchup_results.append(matchup_result)
# Convert the list of matchup results to a DataFrame
matchup_results_df = pd.DataFrame(matchup_results)
# Find the biggest upsets based on LPI difference
biggest_upsets = matchup_results_df.nlargest(30, "LPI Difference")
# Filter for rows where the LPI_Difference is negative and the AwayTeam won
upsets_df = biggest_upsets[
    (
        (biggest_upsets["Winner"] == biggest_upsets["Away Team"])
        & (biggest_upsets["Home LPI"] > biggest_upsets["Away LPI"])
    )
    | (
        (biggest_upsets["Winner"] == biggest_upsets["Home Team"])
        & (biggest_upsets["Away LPI"] > biggest_upsets["Home LPI"])
    )
]
upsets_df.reset_index(drop=True, inplace=True)

schedule_rank_df = schedule_rank_df.sort_values(
    by=["Wins Against Schedule"], ascending=[True]
)
schedule_rank_df.reset_index(drop=True, inplace=True)
schedule_rank_df.index = schedule_rank_df.index + 1
# print(schedule_rank_df)

# Sort the DataFrame by total wins and difference
rank_df = rank_df.sort_values(
    by=["Expected Wins", "Difference"], ascending=[False, True]
)
rank_df.reset_index(drop=True, inplace=True)
rank_df.index = rank_df.index + 1


reg_season_count = settings.reg_season_count
teams = league.teams
num_playoff_teams = settings.playoff_team_count
# Then use them step by step in your existing code
team_stats = calculate_team_stats(teams, scores_df, current_week, reg_season_count)
final_records, playoff_makes, last_place_finishes, seed_counts = (
    simulate_remaining_season(
        teams, team_stats, current_week, reg_season_count, num_playoff_teams
    )
)
summary_df, seed_df = create_summary_dataframes(
    team_stats,
    final_records,
    playoff_makes,
    last_place_finishes,
    seed_counts,
    num_playoff_teams,
    1000,
    len(teams),
    reg_season_count,
)
print(summary_df)
summary_df = (
    summary_df.sort_values("Playoff_Chance_Pct", ascending=False)
    .reset_index(drop=True)
    .set_index("Team")
)
print(seed_df)

# This script used to skip Remaining Schedule Difficulty entirely, so running it
# on one league deleted that sheet (the write below recreates the workbook) and
# broke that section on the league's page until the all-league script ran again.
remaining_schedue_df = calculate_remaining_schedule_difficulty(
    team_stats, schedules_df, lpi_df, current_week, reg_season_count
)

seed_df = (
    seed_df.sort_values("Chance of Making Playoffs", ascending=False)
    .reset_index(drop=True)
    .set_index("Team")
)

# Or use the integrated function for full output
weekly_df = add_weekly_analysis_to_main(
    teams, scores_df, reg_season_count, num_playoff_teams, current_week
)
# print(odds_df)
playoff_df = None   # set below once playoff rounds have been played
# Only report playoff rounds that have actually been played.
playoff_week_indices = week_utils.completed_playoff_week_indices(
    scores_df, settings.reg_season_count
)
if playoff_week_indices:
    # Was `lpi_df = pd.read_excel(...)`, which clobbered the Louie Power Index
    # table with LPI-By-Week data (corrupting that sheet at line ~616) and
    # reassigned `fileName` to a full path, so the final write became
    # data/leagues/data/leagues/<name>.xlsx.xlsx. Both only bit during playoffs.
    lpi_week_df = lpi_weekly_df.drop(columns=["Change From Last Week"], errors="ignore")

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

    # (Removed a second, buggy current_week calculation here. It reassigned
    # current_week with the old `shape[1]` fallback, so during the playoffs the
    # Monte Carlo calls further down ran with a different week than the rest of
    # the script.)

    # Store data in DataFrames
    scores_df = pd.DataFrame(team_scores, index=team_names)
    schedules_df = pd.DataFrame(schedules, index=team_names)
    # print(scores_df)
    last_column_name = scores_df.columns[-1]
    # print(schedules_df)

    # Playoff teams and seeds
    standings = [
        team.team_name for team in league.standings_weekly(settings.reg_season_count)
    ]
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
    for week in playoff_week_indices:
        round_name = get_round_name(len(playoff_teams))
        # print(f"Processing Playoff Round {round_name} (Week {week + 1})")
        # print(playoff_teams)
        # print()
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
                playoff_results.append(
                    {
                        "Round": round_name,
                        "Team 1": team,
                        "Seed 1": standings.index(team) + 1,
                        "Score 1": scores_df.loc[team, week],
                        "LPI 1": lpi_week_df.loc[team, f"Week {week + 1}"],  # Add LPI value
                        "Team 2": "Bye",
                        "Seed 2": "-",
                        "Score 2": "-",
                        "LPI 2": "-",
                        "Winner": team,
                    }
                )
                advancing_teams.append(team)  # Auto-advance the team
                continue

            # Skip if the opponent has already been processed
            if opponent in teams_already_processed:
                continue

            # Retrieve team and opponent scores
            score_1 = scores_df.loc[team, week]
            score_2 = scores_df.loc[opponent, week]

            # Retrieve LPI values
            team_1_lpi = lpi_week_df.loc[team, f"Week {week + 1}"]
            team_2_lpi = lpi_week_df.loc[opponent, f"Week {week + 1}"]

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
            playoff_results.append(
                {
                    "Round": round_name,
                    "Team 1": team,
                    "Seed 1": seed_1,
                    "Score 1": score_1,
                    "LPI 1": team_1_lpi,
                    "Team 2": opponent,
                    "Seed 2": seed_2,
                    "Score 2": score_2,
                    "LPI 2": team_2_lpi,
                    "Winner": winner,
                }
            )

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
    # print(playoff_df)

    # Written with the rest of the sheets below - the xlsxwriter call that
    # follows recreates the workbook and used to wipe this sheet every run.

writer = pd.ExcelWriter(f"{LEAGUES_DIR}/{fileName}.xlsx", engine="xlsxwriter")
records_df.to_excel(writer, sheet_name="Schedule Grid")
schedule_rank_df.to_excel(writer, sheet_name="Wins Against Schedule")
rank_df.to_excel(writer, sheet_name="Expected Wins")
seed_df.to_excel(writer, sheet_name="Playoff Odds")
weekly_df.to_excel(writer, sheet_name="Playoff Odds By Week")
remaining_schedue_df.to_excel(writer, sheet_name="Remaining Schedule Difficulty")
summary_df.to_excel(writer, sheet_name="Record Odds")
lpi_df.to_excel(writer, sheet_name="Louie Power Index")
lpi_weekly_df.to_excel(writer, sheet_name="LPI By Week")
upsets_df.to_excel(writer, sheet_name="Biggest Upsets")
if playoff_df is not None:
    playoff_df.to_excel(writer, sheet_name="Playoff Results", index=False)
writer.close()

print("--- %s seconds ---" % (time.time() - start_time))
