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
import openpyxl
import os
from monte_carlo_odds import (
    calculate_team_stats, 
    simulate_remaining_season, 
    create_summary_dataframes
)
from season_results import add_playoff_results
from draft_data import pull_draft_data
from all_matchups import get_years_matchups
from all_playoffs import create_playoff_df

start_time = time.time()

espn_s2 = CRED["louie_s2"]
ava_s2 = CRED["ava_s2"]
matt_s2 = CRED["matt_s2"]
elle_s2 = CRED["elle_s2"]
hannah_s2 = CRED["hannah_s2"]

year = 2025

# Pennoni Younglings
# league = League(league_id=310334683, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])

# Family League
# league = League(league_id=996930954, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])

# EBC League
league = League(league_id=1118513122, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])

# Pennoni Transportation
# league = League(league_id=1339704102, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Game of Yards
# league = League(league_id=1781851, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Brown Munde
# league = League(league_id=367134149, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Turf On Grade 2.0 League
league = League(league_id=1242265374, year=year, espn_s2=CRED["turf_s2"], swid=CRED["prahlad_swid"])

# Las League
# league = League(league_id=1049459, year=year, espn_s2=CRED["la_s2"], swid=CRED["la_swid"])

# Hannahs League
# league = League(league_id=1399036372, year=2025, espn_s2=hannah_s2, swid=CRED["hannah_swid"])

# Avas League
# league = League(league_id=417131856, year=year, espn_s2=ava_s2, swid=CRED["ava_swid"])

# Matts League
# league = League(league_id=261375772, year=year, espn_s2=matt_s2, swid=CRED["matt_swid"])

# Elles League
# league = League(league_id=1259693145, year=year, espn_s2=elle_s2, swid=CRED["elle_swid"])

def pull_league_data(league):
    settings = league.settings

    leagueName = settings.name.replace(" 22/23", "")
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
    # Calculate current week
    zero_week = (scores_df == 0.0).all(axis=0)
    if zero_week.any():
        current_week = zero_week.idxmax() + 1
    else:
        current_week = scores_df.shape[1]
    schedules_df = pd.DataFrame(schedules, index=team_names)
    print(current_week)
    print(settings.reg_season_count)
    print(settings.playoff_team_count)
    print()
    # print(schedules_df)
    # Create empty dataframe  
    records_df = pd.DataFrame(index=team_names, columns=team_names)

    # Fill diagonal with team names
    records_df.fillna('', inplace=True) 

    # Initialize a DataFrame to store total wins for each team against all schedules
    total_wins_weekly_df = pd.DataFrame(0, columns=team_names, index=team_names)

    # Initialize an empty DataFrame to store LPI scores for each week
    lpi_weekly_df = pd.DataFrame()

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


    # Function to format the change value
    def format_change(change):
        if change > 0:
            return f'↑{change}'
        elif change < 0:
            return f'↓{abs(change)}'
        else:
            return str(change)

    # lpi_weekly_df.insert(loc = 0, column = 'Teams', value = lpi_weekly_df.index)
    # lpi_weekly_df.reset_index(drop=True, inplace=True)

    if current_week > 1:
        # Calculate the "Change from last week" column
        lpi_weekly_df['Change From Last Week'] = lpi_weekly_df[week_name] - lpi_weekly_df['Week ' + str(week - 1)]
        # Apply the formatting function to the "Change from last week" column
        lpi_weekly_df['Change From Last Week'] = lpi_weekly_df['Change From Last Week'].apply(format_change)
    else:
        lpi_weekly_df['Change From Last Week'] = 0

    def owner_df_creation(league):
        """
        Creates a DataFrame mapping owner IDs to Display Names and Team Names for a given league.

        Parameters:
        - league (League): The league object.

        Returns:
        - pd.DataFrame: A DataFrame with columns 'Display Name', 'ID', and 'Team Name'.
        """
        team_owners = [team.owners for team in league.teams]
        team_names = [team.team_name for team in league.teams]

        # Create a list of dictionaries for the DataFrame
        data = []
        for team, team_name in zip(team_owners, team_names):
            team = team[0]
            data.append({
                "Display Name": team['firstName'] + " " + team['lastName'],
                "ID": team['id'],
                "Team Name": team_name
            })

        # Create the DataFrame
        return pd.DataFrame(data)

    owner_df = owner_df_creation(league)
    team_dict = dict(zip(owner_df['Team Name'], owner_df['Display Name']))
    # Display the updated DataFrame
    print(lpi_weekly_df)
    lpi_df = lpi_weekly_df[[week_name, 'Change From Last Week']]
    lpi_df = lpi_df.rename(columns={week_name: "Louie Power Index (LPI)"})
    lpi_df.insert(loc = 0, column = 'Teams', value = lpi_df.index)

    lpi_df.insert(loc = 1, column = 'Owners', value = "")
    # Map the records to lpi_df based on matching team names
    lpi_df['Owners'] = lpi_df['Teams'].map(team_dict)

    lpi_df.reset_index(drop=True, inplace=True)
    lpi_df.index = lpi_df.index + 1 
    lpi_df.insert(loc = 3, column = 'Record', value = "")
    # Create a dictionary to map team names to records from rank_df
    team_to_record = dict(zip(rank_df['Team'], rank_df['Record']))

    # Map the records to lpi_df based on matching team names
    lpi_df['Record'] = lpi_df['Teams'].map(team_to_record)
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
            home_lpi = lpi_weekly_df.at[home_team, 'Week ' + str(week)]
            away_lpi = lpi_weekly_df.at[away_team, 'Week ' + str(week)]
            # Calculate LPI difference
            higher_lpi = max(home_lpi, away_lpi)
            lower_lpi = min(home_lpi, away_lpi)
            lpi_difference = higher_lpi - lower_lpi
            # Determine the winner of the matchup
            winner = home_team if matchup.home_score > matchup.away_score else away_team
            # Record the matchup results and LPI differences
            matchup_result = {
                'Week': week,
                'Home Team': home_team,
                'Away Team': away_team,
                'Home LPI': home_lpi,
                'Away LPI': away_lpi,
                'LPI Difference': lpi_difference,
                'Winner': winner
            }
            # Append the dictionary to the list
            matchup_results.append(matchup_result)
    # Convert the list of matchup results to a DataFrame
    matchup_results_df = pd.DataFrame(matchup_results)
    # Find the biggest upsets based on LPI difference
    biggest_upsets = matchup_results_df.nlargest(30, 'LPI Difference')
    # Filter for rows where the LPI_Difference is negative and the AwayTeam won
    upsets_df = biggest_upsets[((biggest_upsets['Winner'] == biggest_upsets['Away Team']) & (biggest_upsets['Home LPI'] > biggest_upsets['Away LPI'])) | ((biggest_upsets['Winner'] == biggest_upsets['Home Team']) & (biggest_upsets['Away LPI'] > biggest_upsets['Home LPI']))]
    upsets_df.reset_index(drop=True, inplace=True)

    schedule_rank_df = schedule_rank_df.sort_values(by=['Wins Against Schedule'], ascending=[True])
    schedule_rank_df.reset_index(drop=True, inplace=True)
    schedule_rank_df.index = schedule_rank_df.index + 1 
    # print(schedule_rank_df)

    # Sort the DataFrame by total wins and difference
    rank_df = rank_df.sort_values(by=['Expected Wins', 'Difference'], ascending=[False, True])
    rank_df.reset_index(drop=True, inplace=True)
    rank_df.index = rank_df.index + 1


    reg_season_count = settings.reg_season_count
    teams= league.teams
    num_playoff_teams = settings.playoff_team_count
    # Then use them step by step in your existing code
    team_stats = calculate_team_stats(teams, scores_df, current_week, reg_season_count)
    final_records, playoff_makes, seed_counts = simulate_remaining_season(
        teams, team_stats, current_week, reg_season_count, num_playoff_teams
    )
    summary_df, seed_df = create_summary_dataframes(
        team_stats, final_records, playoff_makes, seed_counts, 1000, len(teams), reg_season_count
    )
    print(summary_df)
    summary_df = (
        summary_df.sort_values('Playoff_Chance_Pct', ascending=False)
        .reset_index(drop=True)
        .set_index("Team")
    )
    print(seed_df)

    seed_df = (
        seed_df.sort_values('Chance of Making Playoffs', ascending=False)
            .reset_index(drop=True)
            .set_index("Team")
    )
    writer = pd.ExcelWriter(f"leagues/{fileName}.xlsx", engine='xlsxwriter')
    records_df.to_excel(writer, sheet_name='Schedule Grid')
    schedule_rank_df.to_excel(writer, sheet_name='Wins Against Schedule')
    rank_df.to_excel(writer, sheet_name='Expected Wins')
    seed_df.to_excel(writer, sheet_name='Playoff Odds')
    summary_df.to_excel(writer, sheet_name='Record Odds')
    lpi_df.to_excel(writer, sheet_name='Louie Power Index')
    lpi_weekly_df.to_excel(writer, sheet_name='LPI By Week')
    upsets_df.to_excel(writer, sheet_name='Biggest Upsets')
    writer.close()

# # First: pull all league data from each week
# pull_league_data(league)

# # Second: go back in and add playoff results
# add_playoff_results(league, year)

# # Third: create the draft results and free agent results csvs, then regrade
# # every season together so grades stay comparable:
# pull_draft_data(league, year)
# from draft_grading import regrade_all; regrade_all()

# # Fourth: add all matchups to csv
# all_matchups_df = get_years_matchups(league, year)
# if not all_matchups_df.empty:
#     try:
#         current_matchups = pd.read_csv("all_matchups.csv")
#         print(current_matchups)
#         all_matchups_df = pd.concat([current_matchups, all_matchups_df]).drop_duplicates().reset_index(drop=True)
#         print(all_matchups_df)
#         all_matchups_df["Home Predicted Score"] = all_matchups_df["Home Predicted Score"].round(2)
#         all_matchups_df["Away Predicted Score"] = all_matchups_df["Away Predicted Score"].round(2)
#         all_matchups_df["Predicted Winner"] = all_matchups_df.apply(lambda row: row["Home Team"] if row["Home Predicted Score"] > row["Away Predicted Score"] else (row["Away Team"] if row["Away Predicted Score"] > row["Home Predicted Score"] else "Tie"), axis=1)
#         all_matchups_df["Actual Winner"] = all_matchups_df.apply(lambda row: row["Home Team"] if row["Home Score"] > row["Away Score"] else (row["Away Team"] if row["Away Score"] > row["Home Score"] else "Tie"), axis=1)
#         print("Merged with existing all_matchups.csv")
#         print(all_matchups_df)
#         all_matchups_df.to_csv("all_matchups.csv", index=False)
#     except FileNotFoundError:
#         print("No existing all_matchups.csv found, creating a new one.")
        
# # Fifth: add all playoff matchups to csv
# leagues = [league]
# years = [year]
# all_matchups_df = create_playoff_df(leagues, years)

# Sixth: add into the Draft Grade with Standings csv

# CHECK FOR MISSING INFORMATION
def missing_info_checker():
    louie_s2 = CRED["louie_s2"]
    prahlad_s2 = CRED["prahlad_s2"]
    la_s2 = CRED["la_s2"]
    hannah_s2 = CRED["hannah_s2"]
    ava_s2 = CRED["ava_s2"]
    matt_s2 = CRED["matt_s2"]
    elle_s2 = CRED["elle_s2"]
    dave_s2 = CRED["dave_s2"]
    ayush_s2 = CRED["ayush_s2"]
    # List of league configurations
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    years = [2019, 2020, 2021, 2023, 2024]
    years = [2021, 2023, 2024]
    year = 2025
    leagues = [
        # # Pennoni Younglings
        # {"league_id": 310334683, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "Pennoni Younglings"},
        # # Family League
        # {"league_id": 996930954, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "Family League"},
        # # EBC League
        # {"league_id": 1118513122, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "EBC League"},
        # # Pennoni Transportation
        # {"league_id": 1339704102, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "0755 Fantasy Football"},
        # # Game of Yards
        # {"league_id": 1781851, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "Game of Yards!"},
        # # Brown Munde
        # {"league_id": 367134149, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "Brown Munde"},
        # # Turf On Grade 2.0 League
        # {"league_id":1242265374, "year":year, "espn_s2":CRED["turf_s2"], "swid":CRED["prahlad_swid"], "name": "Turf On Grade 2.0"},
        # # Las League
        # {"league_id": 1049459, "year": year, "espn_s2": la_s2, "swid": CRED["la_swid"], "name": "THE BEST OF THE BEST"},
        # # Hannahs League
        # {"league_id": 1399036372, "year": year, "espn_s2": hannah_s2, "swid": CRED["hannah_swid"], "name": "The Girl's Room 💞🏈"},
        # # Avas League
        # {"league_id": 417131856, "year": year, "espn_s2": ava_s2, "swid": CRED["ava_swid"], "name": "Philly Extra Special"},
        # # Matts League
        # {"league_id": 261375772, "year": year, "espn_s2": matt_s2, "swid": CRED["matt_swid"], "name": "BP- Loudoun 2025"},
        # # Elles League
        # {"league_id": 1259693145, "year": year, "espn_s2": elle_s2, "swid": CRED["elle_swid"], "name": "Operators Football League"},
        # Dave Work League
        # {"league_id": 1675186799, "year": year, "espn_s2": dave_s2, "swid": CRED["dave_swid"], "name": "OnP Fantasy"},
        # Dave Friend League
        # {"league_id": 1924463077, "year": year, "espn_s2": dave_s2, "swid": CRED["dave_swid"], "name": "The Mike Daisy Sports IQ League"},
        # Ayush League
        {"league_id": 558148583, "year": year, "espn_s2": ayush_s2, "swid": CRED["ayush_swid"], "name": "The Mike Daisy Sports IQ League"},
    ]

    all_matchups_df = pd.read_csv("all_matchups.csv")
    all_playoffs_df = pd.read_csv("all_playoff_dfs.csv")
    draft_grades_df = pd.read_csv("drafts/Draft_Grades_with_Standings.csv")
    missing_leagues = []
    for league_info in leagues:
        print(league_info['name'])
        for year in years:
            print("Year: " + str(year))
            try:
                # print(f"Pulling data for {league_info['name']} ({league_info['league_id']}) for year {year}")
                try:
                    league = League(league_id=league_info["league_id"], year=year, espn_s2=league_info["espn_s2"], swid=league_info["swid"])
                except Exception as e:
                    # print(f"NOTHING FOR LEAGUE THIS YEAR")
                    continue
                # print(league)
                settings = league.settings
                league_name = settings.name.replace(" 22/23", "")
                file_name = league_name + " " + str(year)
                file_path = f"leagues/{file_name}.xlsx"

                if not os.path.exists(file_path):
                    print(f"File {file_path} does not exist. BAD")
                else:
                    print(f"League File {file_path} found. GOOD")
                    # lpi = pd.read_excel(file_path, sheet_name='Louie Power Index')
                    # print(lpi)

                if year < 2025:
                    draft_file_path = f"drafts/{league_name} Draft Results {year}.csv"
                    if not os.path.exists(draft_file_path):
                        print(f"File {draft_file_path} does not exist. BAD")
                        missing_leagues.append([league, year])
                    # else:
                    #     print(f"Draft File {draft_file_path} found. GOOD")
                        # draft_df = pd.read_csv(draft_file_path)
                        # print(draft_df.head())

                    free_agent_file_path = f"drafts/{league_name} FreeAgent Results {year}.csv"
                    if not os.path.exists(free_agent_file_path):
                        print(f"File {free_agent_file_path} does not exist. BAD")
                    # else:
                    #     print(f"File {free_agent_file_path} found. GOOD")
                        # free_agent_df = pd.read_csv(free_agent_file_path)
                        # print(free_agent_df.head())

                    league_playoffs_df = all_playoffs_df[all_playoffs_df['File Name'] == file_path]
                    # print("Filtered Playofs Matchups DataFrame: " + str(len(league_playoffs_df)))
                    # print(league_playoffs_df.head())

                league_matchups_df = all_matchups_df[(all_matchups_df['League'] == league_name) & (all_matchups_df['Year'] == year)]
                # print("Exists in all matchups: " + str(len(league_matchups_df)))
                # print(league_matchups_df.head())

                league_draft_grade_df = draft_grades_df[(draft_grades_df['League Name'] == league_name) & (draft_grades_df['Year'] == year)]
                # print("Exists in DRAFT FILE: " + str(len(league_draft_grade_df)))
                # print(league_draft_grade_df.head())
                print("============================")

            except Exception as e:
                # print(f"league {league_info['name']} doesn't exist for year {year}: {e}")
                continue
    
    print("----------------------")
    print(missing_leagues)
    # if len(missing_leagues) > 0:
    #     for league_info in missing_leagues:
    #         league = league_info[0]
    #         year = league_info[1]
    #         pull_draft_data(league, year)

missing_info_checker()

print("--- %s seconds ---" % (time.time() - start_time))