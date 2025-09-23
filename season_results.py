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
import os
import openpyxl

start_time = time.time()

espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"

louie_espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
prahlad_espn_s2 = "AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4"
la_espn_s2 = "AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D"

year = 2019

# List of league configurations
leagues = [
    # {"league_id": 310334683, "year": year, "espn_s2": louie_espn_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Pennoni Younglings"},
    # {"league_id": 996930954, "year": year, "espn_s2": louie_espn_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Family League"},
    # {"league_id": 1118513122, "year": year, "espn_s2": louie_espn_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "EBC League"},
    # {"league_id": 1339704102, "year": year, "espn_s2": prahlad_espn_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Pennoni Transportation"},
    {"league_id": 1781851, "year": year, "espn_s2": prahlad_espn_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Game of Yards"},
    # {"league_id": 367134149, "year": year, "espn_s2": prahlad_espn_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Brown Munde"},
    # {"league_id": 1049459, "year": year, "espn_s2": la_espn_s2, "swid": "{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}", "name": "Las League"},
]

# Loop through each league configuration
for league_config in leagues:
    try:
        league = League(
            league_id=league_config["league_id"],
            year=league_config["year"],
            espn_s2=league_config["espn_s2"],
            swid=league_config["swid"],
        )
        print(league.settings)
        print(f"Processing league: {league_config['name']}")

        settings = league.settings

        leagueName = settings.name.replace(" 22/23", "")
        # fileName = leagueName + " " + str(year) +".xlsx"
        fileName = leagueName + " " + str(year)
        sheet_name = "LPI By Week"

        # Read the LPI data
        lpi_df = pd.read_excel(f"leagues/{fileName}.xlsx", sheet_name=sheet_name, index_col=0)  # Team names as index
        lpi_df = lpi_df.drop(['Change From Last Week'], axis=1)

        # --------------------------------------------------------------------------------------
        # PLAYOFF RESULTS
        # --------------------------------------------------------------------------------------

        # team_owners = [team.owners for team in league.teams]
        team_names = [team.team_name for team in league.teams]
        team_scores = [team.scores for team in league.teams] 
        team_records = [f"{team.wins}-{team.losses}-{team.ties}" for team in league.teams]

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
        # Retrieve total points for the first 14 weeks
        scores_df['Total Points'] = scores_df.iloc[:, :14].sum(axis=1)
        schedules_df = pd.DataFrame(schedules, index=team_names)
        record_df = pd.DataFrame(team_records, index=team_names, columns=["Record"])
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
        last_column_name = scores_df.columns[-2]
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
                        "LPI 1": lpi_df.loc[team, f"Week {week + 1}"],  # Add LPI value
                        "Total Points 1": scores_df.loc[team, 'Total Points'],  # Add total points
                        "Record 1": record_df.loc[team, "Record"],
                        "Team 2": "Bye",
                        "Seed 2": "-",
                        "Score 2": "-",
                        "LPI 2": "-",
                        "Total Points 2": "-",  # Bye has no total points
                        "Record 2": "-",  # Bye has no total points
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

                # Retrieve total points
                team_1_total_points = scores_df.loc[team, 'Total Points']
                team_2_total_points = scores_df.loc[opponent, 'Total Points']
                
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
                    "LPI 1": team_1_lpi,
                    "Total Points 1": team_1_total_points,  # Add total points
                    "Record 1": record_df.loc[team, "Record"],
                    "Team 2": opponent,
                    "Seed 2": seed_2,
                    "Score 2": score_2,
                    "LPI 2": team_2_lpi,
                    "Total Points 2": team_2_total_points,  # Add total points
                    "Record 2": record_df.loc[opponent, "Record"],
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

        # Open the workbook
        workbook = openpyxl.load_workbook(f"leagues/{fileName}.xlsx")
        # Check if the sheet already exists
        if "Playoff Results" in workbook.sheetnames:
            # Remove the sheet
            del workbook["Playoff Results"]
        # Save the workbook after removing the sheet
        workbook.save(f"leagues/{fileName}.xlsx")

        # Add playoff_df as a new sheet to the existing Excel file
        with pd.ExcelWriter(f"leagues/{fileName}.xlsx", engine="openpyxl", mode="a") as writer:
            playoff_df.to_excel(writer, sheet_name="Playoff Results", index=False)
        # --------------------------------------------------------------------------------------
    except Exception as e:
        # Handle errors, such as the league not existing
        print(f"Error: League '{league_config['name']}' for year {league_config['year']} does not exist or could not be loaded.")
        print(f"Details: {str(e)}")
        print(f"Details: {str(e)}")
        continue  # Move to the next league
