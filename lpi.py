import pandas as pd
import streamlit as st
from calcPercent import percent
from playoffNum import playoff_num
from espn_api.football import League
import os


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

file = "leagues/EBC League 2025.xlsx"
espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
league = League(league_id=1118513122, year=2025, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

df = pd.read_excel(file, sheet_name="Louie Power Index")
    
df = df.iloc[: , 1:]
df.index += 1

# Extract year from file name, e.g., '0755 Fantasy Football 2022.xlsx'
base_name = os.path.basename(file)
# Remove extension
name_no_ext = base_name.rsplit('.', 1)[0]
# Split by spaces and get the second to last part (the year)
year_str = name_no_ext.split()[-1]
year = int(year_str)

owner_df = owner_df_creation(league)
print(owner_df)

# Map Team Name to Display Name
team_to_owner = dict(zip(owner_df["Team Name"], owner_df["Display Name"]))

# Insert Owners column next to Teams
if "Teams" in df.columns:
    owners = df["Teams"].map(team_to_owner)
    df.insert(1, "Owners", owners)
else:
    # If Teams is index, try to use index
    owners = df.index.map(team_to_owner)
    df.insert(0, "Owners", owners)

print(df)
