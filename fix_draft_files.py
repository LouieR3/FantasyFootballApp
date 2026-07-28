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
import os


louie_espn_s2 = CRED["louie_s2"]
prahlad_espn_s2 = CRED["prahlad_s2"]
la_espn_s2 = CRED["la_s2"]
year = 2024
leagues = [
    {"league_id": 310334683, "year": year, "espn_s2": louie_espn_s2, "swid": CRED["louie_swid"], "name": "Pennoni Younglings"},
    {"league_id": 996930954, "year": year, "espn_s2": louie_espn_s2, "swid": CRED["louie_swid"], "name": "Family League"},
    {"league_id": 1118513122, "year": year, "espn_s2": louie_espn_s2, "swid": CRED["louie_swid"], "name": "EBC League"},
    {"league_id": 1339704102, "year": year, "espn_s2": prahlad_espn_s2, "swid": CRED["prahlad_swid"], "name": "Pennoni Transportation"},
    {"league_id": 1781851, "year": year, "espn_s2": prahlad_espn_s2, "swid": CRED["prahlad_swid"], "name": "Game of Yards"},
    {"league_id": 367134149, "year": year, "espn_s2": prahlad_espn_s2, "swid": CRED["prahlad_swid"], "name": "Brown Munde"},
    {"league_id": 1049459, "year": year, "espn_s2": la_espn_s2, "swid": CRED["la_swid"], "name": "Las League"},
]

def owner_df_creation():
    team_owners = [team.owners for team in league.teams]
    team_names  = [team.team_name for team in league.teams]

    # Create a list of dictionaries for the DataFrame
    data = []
    count = 0
    for team in team_owners:
        team = team[0]
        team_name = team_names[count]
        data.append({
            "Display Name": team['firstName'] + " " + team['lastName'],
            "ID": team['id'],
            "Team Name": team_name
        })
        count += 1

    # Create the DataFrame
    df = pd.DataFrame(data)

    # Display the DataFrame
    return df


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
        
        owners_df = owner_df_creation()
        # Create a dictionary for efficient lookup from owner_df
        owner_mapping = dict(zip(owners_df["Team Name"], owners_df["ID"]))

        leagueName = settings.name.replace(" 22/23", "") 
        fileDraft = leagueName + " Draft Results" + " " + str(year) + ".csv"
        fileFreeAgent = leagueName + " FreeAgent Results" + " " + str(year) + ".csv"

        draft_df = pd.read_csv(fileDraft)
        free_agent_df = pd.read_csv(fileFreeAgent)

        # Add Owner ID column to draft_df
        draft_df["Owner ID"] = draft_df["Team"].map(owner_mapping)
        # Add Owner ID column to free_agent_df
        free_agent_df["Owner ID"] = free_agent_df["Team"].map(owner_mapping)
        # Verify the results
        # print(draft_df.head())
        # print(free_agent_df.head())
        
        draft_df.to_csv(fileDraft, index=False)
        free_agent_df.to_csv(fileFreeAgent, index=False)
    except Exception as e:
        # Handle errors, such as the league not existing
        print(f"Error: League '{league_config['name']}' for year {league_config['year']} does not exist or could not be loaded.")
        print(f"Details: {str(e)}")
        print(f"Details: {str(e)}")
        continue  # Move to the next league