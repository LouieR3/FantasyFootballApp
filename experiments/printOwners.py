import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
from credentials import CRED
import pandas as pd
from operator import itemgetter
import glob
from espn_api.football import League
from ffapp.metrics.owner_overrides import resolve_owner, owner_id_for
from paths import LEAGUES_DIR

files = glob.glob('*.xlsx')

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

# league = League(league_id=1339704102, year=2024, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])
ava_s2 = CRED["ava_s2"]
# league = League(league_id=310334683, year=2025, espn_s2=CRED["legacy_s2_a"],swid=CRED["louie_swid"])
league = League(league_id=417131856, year=2025, espn_s2=ava_s2, swid=CRED["ava_swid"])


# league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
owner_df = owner_df_creation(league)
file = f"{LEAGUES_DIR}/Philly Extra Special 2025.xlsx"
# Map Team Name to Display Name
team_to_owner = dict(zip(owner_df["Team Name"], owner_df["Display Name"]))
print(team_to_owner)
df = pd.read_excel(file, sheet_name="Louie Power Index")

df = df.iloc[: , 1:]
df.index += 1

# Insert Owners column next to Teams
if "Teams" in df.columns:
    print("Teams is a column")
    owners = df["Teams"].map(team_to_owner)
    df.insert(1, "Owners", owners)
else:
    # If Teams is index, try to use index
    print("NO")
    owners = df.index.map(team_to_owner)

print(owners)
sdf
louie_s2 = CRED["louie_s2"]
prahlad_s2 = CRED["prahlad_s2"]
la_s2 = CRED["la_s2"]
hannah_s2 = CRED["hannah_s2"]
ava_s2 = CRED["ava_s2"]
matt_s2 = CRED["matt_s2"]
elle_s2 = CRED["elle_s2"]
# List of league configurations
year = 2025
years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
leagues = [
    # Pennoni Youn  glings
    {"league_id": 310334683, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "Pennoni Younglings"},
    # Family League
    {"league_id": 996930954, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "Family League"},
    # EBC League
    {"league_id": 1118513122, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "EBC League"},
    # Pennoni Transportation
    {"league_id": 1339704102, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "0755 Fantasy Football"},
    # Game of Yards
    {"league_id": 1781851, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "Game of Yards!"},
    # Brown Munde
    {"league_id": 367134149, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "Brown Munde"},
    # Other Prahlad League
    {"league_id":1242265374, "year":year, "espn_s2":CRED["turf_s2"], "swid":CRED["prahlad_swid"], "name": "Brown Munde"},
    # Las League
    {"league_id": 1049459, "year": year, "espn_s2": la_s2, "swid": CRED["la_swid"], "name": "THE BEST OF THE BEST"},
    # Hannahs League
    {"league_id": 1399036372, "year": year, "espn_s2": hannah_s2, "swid": CRED["hannah_swid"], "name": "Hannahs League"},
    # Avas League
    {"league_id": 417131856, "year": year, "espn_s2": ava_s2, "swid": CRED["ava_swid"], "name": "Avas League"},
    # Matts League
    {"league_id": 261375772, "year": year, "espn_s2": matt_s2, "swid": CRED["matt_swid"], "name": "Matts League"},
    # Elles League
    {"league_id": 1259693145, "year": year, "espn_s2": elle_s2, "swid": CRED["elle_swid"], "name": "Elles League"},
]

for league_config in leagues:
    for year in years:
        try:
            league = League(
                league_id=league_config["league_id"],
                year=year,
                espn_s2=league_config["espn_s2"],
                swid=league_config["swid"],
            )

            team_owner = [team.owner for team in league.teams]
            team_owners = [team.owners for team in league.teams]
            team_names  = [team.team_name for team in league.teams]
            team_dict   = dict(zip(team_names, team_owner))

            # Create a list of dictionaries for the DataFrame
            data = []
            for team in team_owners:
                team = team[0]
                data.append({
                    "Display Name": team['firstName'] + " " + team['lastName'],
                    "ID": team['id']
                })

            # Create the DataFrame
            df = pd.DataFrame(data)

            # Reverse the team_dict to map IDs to team names
            id_to_team_name = {id_: team_name for team_name, ids in team_dict.items() for id_ in ids}

            # Map team names to the DataFrame based on ID
            df['Team Name'] = df['ID'].map(id_to_team_name)
            
            settings = league.settings

            leagueName = settings.name
            df['League'] = leagueName + " " + str(year)

            # Display the DataFrame
            # print(league_config["name"])
            print(leagueName)
            print(df)
            print()
        except Exception as e:
            print(f"Error initializing league {league_config['name']} for year {year}: {e}")
            continue
    print("-----")