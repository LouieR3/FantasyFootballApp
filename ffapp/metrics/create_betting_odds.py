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
import random
import openpyxl
from ffapp.metrics.monte_carlo_odds import (
    calculate_team_stats, 
    simulate_remaining_season, 
    create_summary_dataframes,
    add_weekly_analysis_to_main,
    retrieve_odds_dfs
)
from paths import ODDS_DIR


start_time = time.time()

louie_s2 = CRED["louie_s2"]
prahlad_s2 = CRED["prahlad_s2"]
la_s2 = CRED["la_s2"]
hannah_s2 = CRED["hannah_s2"]
ava_s2 = CRED["ava_s2"]
matt_s2 = CRED["matt_s2"]
elle_s2 = CRED["elle_s2"]
dave_s2 = CRED["dave_s2"]
ayush_s2 = CRED["ayush_s2"]
nolan_s2 = CRED["nolan_s2"]
prahlad2_s2 = CRED["prahlad2_s2"]
# List of league configurations
year = 2026

from ffapp.leagues_config import get_leagues_for_year

leagues = get_leagues_for_year(year)

def create_betting_odds(leagues, year):
    # Loop through each league configuration
    for league_config in leagues:
        try:
            league = League(
                league_id=league_config["league_id"],
                year=league_config["year"],
                espn_s2=league_config["espn_s2"],
                swid=league_config["swid"],
            )
            print(f"Processing league: {league_config['name']}")
        
            settings = league.settings

            leagueName = settings.name.replace(" 22/23", "")
            fileName = leagueName + " " + str(year) + " Betting Odds"
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
                current_week = zero_week.idxmax() +1
            else:
                current_week = scores_df.shape[1]
            schedules_df = pd.DataFrame(schedules, index=team_names)
            records_df = pd.DataFrame(index=team_names, columns=team_names)

            # Fill diagonal with team names
            records_df.fillna('', inplace=True) 

            teams= league.teams
            reg_season_count = settings.reg_season_count
            num_playoff_teams = settings.playoff_team_count
            # Then use them step by step in your existing code
            team_stats = calculate_team_stats(teams, scores_df, current_week, reg_season_count)
            final_records, playoff_makes, last_place_finishes, seed_counts = simulate_remaining_season(
                teams, team_stats, current_week, reg_season_count, num_playoff_teams
            )
            summary_df, seed_df = create_summary_dataframes(
                team_stats, final_records, playoff_makes, last_place_finishes, seed_counts, num_playoff_teams, 1000, len(teams), reg_season_count
            )
            summary_df = (
                summary_df.sort_values('Playoff_Chance_Pct', ascending=False)
                .reset_index(drop=True)
                .set_index("Team")
            )
            num_teams = len(teams)

            make_playoff_odds_df, first_place_odds_df, last_place_odds_df = retrieve_odds_dfs(seed_df, num_teams, team_stats)

            writer = pd.ExcelWriter(f"{ODDS_DIR}/{fileName}.xlsx", engine='xlsxwriter')
            make_playoff_odds_df.to_excel(writer, sheet_name='Make Playoff Odds')
            first_place_odds_df.to_excel(writer, sheet_name='First Place Odds')
            last_place_odds_df.to_excel(writer, sheet_name='Last Place Odds')
            writer.close()
            # --------------------------------------------------------------------------------------
        except Exception as e:
            # Handle errors, such as the league not existing
            print(f"Error: League '{league_config['name']}' for year {league_config['year']} does not exist or could not be loaded.")
            print(f"Details: {str(e)}")
            continue  # Move to the next league

print("--- %s seconds ---" % (time.time() - start_time))