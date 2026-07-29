import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
from credentials import CRED
from espn_api.football import League
import pandas as pd
import os
from openpyxl import load_workbook
from paths import DATA_DIR

def get_all_matchups(leagues, years):    
    # Initialize an empty list to store all playoff data
    combined_matchups_dfs = []

    # Loop through each league
    for league_config in leagues:
        league_id = league_config['league_id']
        espn_s2 = league_config['espn_s2']
        swid = league_config['swid']
        league_name = league_config['name']

        for year in years:
            print(f"Processing league: {league_name}, year: {year}")

            # Instantiate the league object for the current year
            try:
                league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
                league_name = league.settings.name
                print(league.settings)
            except Exception as e:
                print(f"Error initializing league {league_name} for year {year}: {e}")
                continue
            
            if year < 2025:
                weeks = league.current_week
            else:
                print("Getting weeks for current season")
                team_names = [team.team_name for team in league.teams]
                team_scores = [team.scores for team in league.teams] 
                scores_df = pd.DataFrame(team_scores, index=team_names)
                zero_week = (scores_df == 0.0).all(axis=0)
                if zero_week.any():
                    weeks = zero_week.idxmax()
                else:
                    weeks = scores_df.shape[1]
            print(weeks)
            for week in range(1, weeks + 1):
                try:
                    matchups = league.box_scores(week=week)
                except Exception as e:
                    # print(f"Error fetching box scores for league {league_name}, year {year}, week {week}: {e}")
                    continue
                print(f"Fetched {len(matchups)} matchups for week {week} of {league_name} ({year})")  
                # Prepare data for the current week's matchups
                matchup_data = []
                for matchup in matchups:
                    matchup_info = {
                        'League': league_name,
                        'Year': year,
                        'Week': week,
                        'Home Team': matchup.home_team.team_name if matchup.home_team else None,
                        'Home Score': matchup.home_score,
                        'Home Predicted Score': matchup.home_projected,
                        'Away Team': matchup.away_team.team_name if matchup.away_team else None,
                        'Away Score': matchup.away_score,
                        'Away Predicted Score': matchup.away_projected,
                    }
                    matchup_data.append(matchup_info)

                # Convert the current week's matchup data to a DataFrame
                week_df = pd.DataFrame(matchup_data)
                combined_matchups_dfs.append(week_df)
    # Concatenate all weekly DataFrames into a single DataFrame
    if combined_matchups_dfs:
        all_matchups_df = pd.concat(combined_matchups_dfs, ignore_index=True)
    else:
        all_matchups_df = pd.DataFrame()  # Return an empty DataFrame if no data was collected

    return all_matchups_df

def get_years_matchups(league, year):    
    # Initialize an empty list to store all playoff data
    combined_matchups_dfs = []
    settings = league.settings
    league_name = settings.name
    
    print(f"Processing league: {league_name}, year: {year}")

    # Instantiate the league object for the current year
    try:
        league_name = league.settings.name
        print(league.settings)
    except Exception as e:
        print(f"Error initializing league {league_name} for year {year}: {e}")
        return pd.DataFrame() # Return empty DataFrame on error
    
    if year < 2025:
        weeks = league.current_week
    else:
        print("Getting weeks for current season")
        team_names = [team.team_name for team in league.teams]
        team_scores = [team.scores for team in league.teams] 
        scores_df = pd.DataFrame(team_scores, index=team_names)
        zero_week = (scores_df == 0.0).all(axis=0)
        if zero_week.any():
            weeks = zero_week.idxmax()
        else:
            weeks = scores_df.shape[1]
    print(weeks)
    for week in range(1, weeks + 1):
        try:
            matchups = league.box_scores(week=week)
        except Exception as e:
            # print(f"Error fetching box scores for league {league_name}, year {year}, week {week}: {e}")
            continue
        print(f"Fetched {len(matchups)} matchups for week {week} of {league_name} ({year})")  
        # Prepare data for the current week's matchups
        matchup_data = []
        for matchup in matchups:
            matchup_info = {
                'League': league_name,
                'Year': year,
                'Week': week,
                'Home Team': matchup.home_team.team_name if matchup.home_team else None,
                'Home Score': matchup.home_score,
                'Home Predicted Score': matchup.home_projected,
                'Away Team': matchup.away_team.team_name if matchup.away_team else None,
                'Away Score': matchup.away_score,
                'Away Predicted Score': matchup.away_projected,
            }
            matchup_data.append(matchup_info)

        # Convert the current week's matchup data to a DataFrame
        week_df = pd.DataFrame(matchup_data)
        combined_matchups_dfs.append(week_df)
    # Concatenate all weekly DataFrames into a single DataFrame
    if combined_matchups_dfs:
        all_matchups_df = pd.concat(combined_matchups_dfs, ignore_index=True)
    else:
        all_matchups_df = pd.DataFrame()  # Return an empty DataFrame if no data was collected

    return all_matchups_df

def get_weeks_matchups(leagues, year):  
    # Initialize an empty list to store all playoff data
    combined_matchups_dfs = []

    # Loop through each league
    for league_config in leagues:
        league_id = league_config['league_id']
        espn_s2 = league_config['espn_s2']
        swid = league_config['swid']
        league_name = league_config['name']

        # Instantiate the league object for the current year
        try:
            league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
            league_name = league.settings.name
            week = league.current_week - 1
            print(league.settings)
        except Exception as e:
            print(f"Error initializing league {league_name} for year {year}: {e}")
            continue
        
        print(f"Processing league: {league_name}, year: {year}, week: {week}")
        
        try:
            matchups = league.box_scores(week=week)
        except Exception as e:
            # print(f"Error fetching box scores for league {league_name}, year {year}, week {week}: {e}")
            return None
        print(f"Fetched {len(matchups)} matchups for week {week} of {league_name} ({year})")  
        # Prepare data for the current week's matchups
        matchup_data = []
        for matchup in matchups:
            matchup_info = {
                'League': league_name,
                'Year': year,
                'Week': week,
                'Home Team': matchup.home_team.team_name if matchup.home_team else None,
                'Home Score': matchup.home_score,
                'Home Predicted Score': matchup.home_projected,
                'Away Team': matchup.away_team.team_name if matchup.away_team else None,
                'Away Score': matchup.away_score,
                'Away Predicted Score': matchup.away_projected,
            }
            matchup_data.append(matchup_info)

        # Convert the current week's matchup data to a DataFrame
        week_df = pd.DataFrame(matchup_data)
        combined_matchups_dfs.append(week_df)
    # Concatenate all weekly DataFrames into a single DataFrame
    if combined_matchups_dfs:
        all_matchups_df = pd.concat(combined_matchups_dfs, ignore_index=True)
    else:
        all_matchups_df = pd.DataFrame()  # Return an empty DataFrame if no data was collected

    return all_matchups_df

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
year = 2025
leagues = [
    # Pennoni Younglings
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
    # Turf On Grade 2.0 League
    # {"league_id":1242265374, "year":year, "espn_s2":CRED["turf_s2"], "swid":CRED["prahlad_swid"], "name": "Turf On Grade 2.0"},
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
    # Dave Work League
    {"league_id": 1675186799, "year": year, "espn_s2": dave_s2, "swid": CRED["dave_swid"], "name": "OnP Fantasy"},
    # Dave Friend League
    {"league_id": 1924463077, "year": year, "espn_s2": dave_s2, "swid": CRED["dave_swid"], "name": "The Mike Daisy Sports IQ League"},
    # Ayush League
    {"league_id": 558148583, "year": year, "espn_s2": ayush_s2, "swid": CRED["ayush_swid"], "name": "Ross' Fantasy League"},
]

# years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
# years = [2019, 2020, 2021, 2022, 2023, 2024]
years = [2025]

# all_matchups_df = get_all_matchups(leagues, years)
# print(all_matchups_df)


# all_matchups_df = get_weeks_matchups(leagues, year)
# # Dave Friend League
# # league = League(league_id= 1924463077, year= year, espn_s2= dave_s2, swid= CRED["dave_swid"])
# # league = League(league_id=558148583, year=year, espn_s2=ayush_s2, swid=CRED["ayush_swid"])
# # all_matchups_df = get_years_matchups(league, year)
# print(all_matchups_df)
# try:
#     current_matchups = pd.read_csv(f"{DATA_DIR}/all_matchups.csv")
#     # print(current_matchups)
#     # current_matchups = current_matchups.drop_duplicates(
#     #     subset=["League","Year","Week","Home Team"]
#     # )
#     print(current_matchups)
#     # current_matchups.to_csv(f"{DATA_DIR}/all_matchups.csv", index=False)
#     all_matchups_df = pd.concat([current_matchups, all_matchups_df]).drop_duplicates().reset_index(drop=True)
#     print(all_matchups_df)
#     all_matchups_df["Home Predicted Score"] = all_matchups_df["Home Predicted Score"].round(2)
#     all_matchups_df["Away Predicted Score"] = all_matchups_df["Away Predicted Score"].round(2)
#     all_matchups_df["Predicted Winner"] = all_matchups_df.apply(lambda row: row["Home Team"] if row["Home Predicted Score"] > row["Away Predicted Score"] else (row["Away Team"] if row["Away Predicted Score"] > row["Home Predicted Score"] else "Tie"), axis=1)
#     all_matchups_df["Actual Winner"] = all_matchups_df.apply(lambda row: row["Home Team"] if row["Home Score"] > row["Away Score"] else (row["Away Team"] if row["Away Score"] > row["Home Score"] else "Tie"), axis=1)
#     print("Merged with existing all_matchups.csv")
#     print(all_matchups_df)
#     all_matchups_df.to_csv(f"{DATA_DIR}/all_matchups.csv", index=False)
# except FileNotFoundError:
#     print("No existing all_matchups.csv found, creating a new one.")

