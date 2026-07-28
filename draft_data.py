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

start_time = time.time()

def pull_draft_data(league, year):
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
    
    try:
        # league = League(
        #     league_id=league_config["league_id"],
        #     year=league_config["year"],
        #     espn_s2=league_config["espn_s2"],
        #     swid=league_config["swid"],
        # )
        print(league.settings)
        print(f"Processing league: {league.settings.name}")

        settings = league.settings

        leagueName = settings.name.replace(" 22/23", "")
        fileName = leagueName + " " + str(year)

        # --------------------------------------------------------------------------------------
        # DRAFT RESULTS CSV CREATION
        # --------------------------------------------------------------------------------------
        def draft_results():
            # Extract the data from the draft
            data = []
            print(league.draft)
            for pick in league.draft:
                pick_number = f"{pick.round_num} - {pick.round_pick}"  # Combine round_num and round_pick
                player_name = pick.playerName  # Player's name
                team = pick.team.team_name  # Team
                
                # Get player stats
                if player_name == "Josh Allen":
                    player = league.player_info(playerId=3918298)
                elif player_name == 'A.J. Green':
                    player = league.player_info(playerId=13983)
                else:
                    player = league.player_info(player_name)
                    
                # print(pick)
                # print(player)
                # if player_name == "Lamar Jackson":
                #     position = 'QB'
                #     projected_points = 303.83
                #     projected_avg_points = 20.26
                #     points = 430.38
                #     avg_points = 25.32
                #     games_played = 17
                # else:
                position = player.position
            
                stats = player.stats[0] if player.stats else {}  # Handle cases with no stats

                # Extract required stats, using 0 if stats are unavailable
                projected_points = stats.get('projected_points', 0)
                projected_avg_points = stats.get('projected_avg_points', 0)
                points = stats.get('points', 0)
                avg_points = stats.get('avg_points', 0)

                # Calculate Games Played
                games_played = 0
                if player.stats:
                    for key, stat in player.stats.items():
                        # Skip index 0 (season totals or projections)
                        if key == 0:
                            continue
                        # Increment games_played if 'breakdown' is non-empty
                        if stat.get('breakdown'):
                            games_played += 1

                # Append data for this pick
                data.append({
                    "Pick": pick_number,
                    "Player": player_name,
                    "Position": position,
                    "Team": team,
                    "Projected Points": projected_points,
                    "Projected Avg Points": projected_avg_points,
                    "Points": points,
                    "Avg Points": avg_points,
                    "Games Played": games_played
                })

            draft_df = pd.DataFrame(data)
            return draft_df

        fileDraft = "drafts/" +leagueName + " Draft Results" + " " + str(year) + ".csv"
        # Create a DataFrame
        draft_df = draft_results()
        # draft_df = pd.read_csv(fileDraft)

        # draft_df['Total Pick'] = draft_df.index + 1
        draft_df.insert(loc = 1,
                column = 'Total Pick',
                value = draft_df.index + 1)
        
        # Grades are computed by draft_grading.regrade_all() after all pulls,
        # pooled across every league-year so they are comparable. Placeholders here.
        import numpy as np
        draft_df['Draft Grade'] = np.nan
        draft_df['Letter Grade'] = ""

        print(draft_df[["Total Pick", "Player", "Projected Points", "Points", "Avg Points", "Games Played", "Draft Grade", "Letter Grade"]].head(20))
        # print(draft_df[["Player", "Position", "Projected Points", "Points", "Avg Points", "Draft Grade", "Points Grade", "Avg Grade", "GamesPlay Grade", "Pick Grade", "Position Grade", "Points MAX Grade", "Avg MAX Grade", "Letter Grade"]])
        team_draft = draft_df[draft_df["Team"].str.strip() == "The Golden Receivers"]
        print(team_draft[["Total Pick", "Player", "Projected Points", "Points", "Avg Points", "Games Played", "Draft Grade", "Letter Grade"]])
        # print(team_draft[["Player", "Position", "Projected Points", "Points", "Avg Points", "Draft Grade", "Points Grade", "Avg Grade", "GamesPlay Grade", "Pick Grade", "Position Grade", "Points MAX Grade", "Avg MAX Grade", "Letter Grade"]])
        # test = draft_df[["Player", "Position", "Projected Points", "Points", "Avg Points", "Draft Grade", "Points Grade", "Avg Grade", "GamesPlay Grade", "Pick Grade", "Position Grade", "Points MAX Grade", "Avg MAX Grade", "Letter Grade"]]

        owners_df = owner_df_creation()
        # Create a dictionary for efficient lookup from owner_df
        owner_mapping = dict(zip(owners_df["Team Name"], owners_df["ID"]))

        # Add Owner ID column to draft_df
        draft_df["Owner ID"] = draft_df["Team"].map(owner_mapping)

        draft_df.to_csv(fileDraft, index=False)
        # --------------------------------------------------------------------------------------

        # --------------------------------------------------------------------------------------
        # FREE AGENT RESULTS CSV
        # --------------------------------------------------------------------------------------
        def freeAgentResults():
            # Create a set of drafted player names for quick lookup
            drafted_players = set(draft_df['Player'])

            # Prepare data for additions_df
            additions_data = []

            # Iterate over each team in the league
            for team in league.teams:
                team_name = team.team_name  # Team's name
                
                # Extract roster as a list of player objects
                roster = team.roster  # List of Player objects
                
                for player in roster:
                    player_name = player.name  # Extract player's name
                    position = player.position
                    
                    # Skip players already in the draft
                    if player_name in drafted_players:
                        continue
                    
                    # Get player stats
                    player_info = league.player_info(player_name)
                    stats = player_info.stats[0] if player_info.stats else {}

                    # Extract required stats, with defaults for missing values
                    projected_points = stats.get('projected_points', 0)
                    projected_avg_points = stats.get('projected_avg_points', 0)
                    points = stats.get('points', 0)
                    avg_points = stats.get('avg_points', 0)
                    
                    games_played = 0
                    if player_info.stats:
                        for key, stat in player_info.stats.items():
                            # Skip index 0 (season totals or projections)
                            if key == 0:
                                continue
                            # Increment games_played if 'breakdown' is non-empty
                            if stat.get('breakdown'):
                                games_played += 1

                    # Append data for this player
                    additions_data.append({
                        "Player": player_name,
                        "Position": position,
                        "Team": team_name,
                        "Projected Points": projected_points,
                        "Projected Avg Points": projected_avg_points,
                        "Points": points,
                        "Avg Points": avg_points,
                        "Games Played": games_played
                    })

            # Create the additions_df DataFrame
            additions_df = pd.DataFrame(additions_data)

            # Graded by draft_grading.regrade_all() after all pulls (placeholders).
            additions_df['Performance Grade'] = np.nan
            additions_df['Letter Grade'] = ""

            # Display the DataFrame
            print(additions_df)
            fileFreeAgent = "drafts/" +leagueName + " FreeAgent Results" + " " + str(year) + ".csv"
            # Add Owner ID column to free_agent_df
            additions_df["Owner ID"] = additions_df["Team"].map(owner_mapping)

            additions_df.to_csv(fileFreeAgent, index=False)
        freeAgentResults()
        print("=======")
        # --------------------------------------------------------------------------------------
    except Exception as e:
        # Handle errors, such as the league not existing
        print(f"Error: League '{league}' for year {year} does not exist or could not be loaded.")
        print(f"Details: {str(e)}")
        print(f"Details: {str(e)}")


espn_s2 = CRED["louie_s2"]

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

# List of league configurations

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
    {"league_id": 1399036372, "year": year, "espn_s2": hannah_s2, "swid": CRED["hannah_swid"], "name": "The Girl's Room 💞🏈"},
    # Avas League
    {"league_id": 417131856, "year": year, "espn_s2": ava_s2, "swid": CRED["ava_swid"], "name": "Philly Extra Special"},
    # Matts League
    # {"league_id": 261375772, "year": year, "espn_s2": matt_s2, "swid": CRED["matt_swid"], "name": "BP- Loudoun 2025"},
    # Elles League
    {"league_id": 1259693145, "year": year, "espn_s2": elle_s2, "swid": CRED["elle_swid"], "name": "Operators Football League"},
    # Dave Work League
    {"league_id": 1675186799, "year": year, "espn_s2": dave_s2, "swid": CRED["dave_swid"], "name": "OnP Fantasy"},
    # Dave Friend League
    {"league_id": 1924463077, "year": year, "espn_s2": dave_s2, "swid": CRED["dave_swid"], "name": "The Mike Daisy Sports IQ League"},
    # Ayush League
    {"league_id": 558148583, "year": year, "espn_s2": ayush_s2, "swid": CRED["ayush_swid"], "name": "Ross' Fantasy League"},
]

if __name__ == "__main__":
    # Pull raw draft + free agent data for every league, then regrade all
    # seasons together so grades stay comparable across leagues and years.
    for league_config in leagues:
        try:
            league = League(
                league_id=league_config["league_id"],
                year=league_config["year"],
                espn_s2=league_config["espn_s2"],
                swid=league_config["swid"],
            )
            pull_draft_data(league, year)
        except Exception as e:
            print(f"Failed to process league: {league_config['name']}. Error: {str(e)}")
            continue

    from draft_grading import regrade_all
    regrade_all()

# team = league.teams[2]
# print(team.roster[0])

# player = league.player_info('Christian McCaffrey')
# print(player.stats[1]['points'])
# print()
# print(player.stats[0]['projected_points'])
# print(player.stats[0]['projected_avg_points'])
# print(player.stats[0]['points'])
# print(player.stats[0]['avg_points'])
