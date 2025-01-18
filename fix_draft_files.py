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


louie_espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
prahlad_espn_s2 = "AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4"
la_espn_s2 = "AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D"
year = 2024
leagues = [
    {"league_id": 310334683, "year": year, "espn_s2": louie_espn_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Pennoni Younglings"},
    {"league_id": 996930954, "year": year, "espn_s2": louie_espn_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Family League"},
    {"league_id": 1118513122, "year": year, "espn_s2": louie_espn_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "EBC League"},
    {"league_id": 1339704102, "year": year, "espn_s2": prahlad_espn_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Pennoni Transportation"},
    {"league_id": 1781851, "year": year, "espn_s2": prahlad_espn_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Game of Yards"},
    {"league_id": 367134149, "year": year, "espn_s2": prahlad_espn_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Brown Munde"},
    {"league_id": 1049459, "year": year, "espn_s2": la_espn_s2, "swid": "{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}", "name": "Las League"},
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