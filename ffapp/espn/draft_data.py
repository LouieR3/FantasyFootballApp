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
import os

from ffapp import league_registry as registry
from ffapp.metrics.owner_overrides import resolve_owner
from ffapp.espn import league_settings
from paths import DRAFTS_DIR

start_time = time.time()

def pull_draft_data(league, year):
    def owner_df_creation():
        # Co-owned teams resolve to their canonical owner (owner_overrides.py)
        data = []
        for team in league.teams:
            owner = resolve_owner(league, team)
            data.append({
                "Display Name": f"{owner.get('firstName', '')} {owner.get('lastName', '')}".strip(),
                "ID": owner.get('id'),
                "Team Name": team.team_name
            })

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

        # Canonical, not raw: ESPN renames leagues, and filing under the new
        # name silently forks a league's history into two (see league_registry).
        leagueName = registry.canonical(settings.name.replace(" 22/23", ""))
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
                
                # Look up by player id, not name. Name lookup is ambiguous -
                # hence the old hardcoded cases for Josh Allen and A.J. Green -
                # and returns None for anything it cannot resolve, which used to
                # crash the entire league on `player.position` below. The pick
                # object carries the id, so use it.
                player = None
                if getattr(pick, 'playerId', None):
                    player = league.player_info(playerId=pick.playerId)
                if player is None:                      # last resort
                    player = league.player_info(player_name)
                if player is None or getattr(player, 'position', None) is None:
                    # One unresolvable pick must not lose the other 191. Recorded
                    # with an unknown position and no stats so the row still
                    # exists and the gap is visible rather than silent.
                    print(f"  WARNING: could not resolve {player_name!r} "
                          f"(id={getattr(pick, 'playerId', None)}) - "
                          f"recording with no stats")
                    data.append({
                        "Pick": pick_number, "Player": player_name,
                        "Position": "UNK", "Team": team,
                        "Projected Points": 0, "Projected Avg Points": 0,
                        "Points": 0, "Avg Points": 0, "Games Played": 0,
                    })
                    continue
                    
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

        fileDraft = f"{DRAFTS_DIR}/" +leagueName + " Draft Results" + " " + str(year) + ".csv"
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

        # Record this league-season's lineup settings (starting slots, flex,
        # bench size). Needed to know what a legal lineup is - see
        # ffapp/metrics/draft_analysis.py's best-possible-lineup work.
        league_settings.save_settings(leagueName, year, settings)

        draft_df.to_csv(fileDraft, index=False)
        # --------------------------------------------------------------------------------------

        # --------------------------------------------------------------------------------------
        # FINAL ROSTER CSV
        # Who each team actually finished the season with. The free agent file
        # only lists players nobody drafted, so on its own it cannot say how much
        # of a team's own draft survived - that needs the roster itself. Powers
        # the draft-retention view in ffapp/metrics/draft_analysis.py.
        # --------------------------------------------------------------------------------------
        def finalRosterResults():
            rows = []
            for team in league.teams:
                for player in team.roster:
                    rows.append({
                        "Team": team.team_name,
                        "Player": player.name,
                        "Position": player.position,
                    })
            roster_df = pd.DataFrame(rows)
            roster_df["Owner ID"] = roster_df["Team"].map(owner_mapping)
            fileRoster = f"{DRAFTS_DIR}/" + leagueName + " Final Roster" + " " + str(year) + ".csv"
            roster_df.to_csv(fileRoster, index=False)
            print(f"final rosters: {len(roster_df)} players across {roster_df['Team'].nunique()} teams")
        finalRosterResults()

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
            fileFreeAgent = f"{DRAFTS_DIR}/" +leagueName + " FreeAgent Results" + " " + str(year) + ".csv"
            # Add Owner ID column to free_agent_df
            additions_df["Owner ID"] = additions_df["Team"].map(owner_mapping)

            additions_df.to_csv(fileFreeAgent, index=False)
        freeAgentResults()
        print("=======")
        # --------------------------------------------------------------------------------------
    except Exception as e:
        # Was previously reported as "league does not exist", which sent debugging
        # in the wrong direction when the real failure was a single player lookup.
        import traceback
        print(f"Error pulling draft data for '{league}' {year}: "
              f"{type(e).__name__}: {e}")
        traceback.print_exc()


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

import argparse
import datetime
current_year = datetime.date.today().year
parser = argparse.ArgumentParser()
parser.add_argument('--years', type=int, nargs='+', default=[current_year],
                    help='Pull draft data for these years (default: current year)')
args = parser.parse_args()

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
    {"league_id": 261375772, "year": year, "espn_s2": matt_s2, "swid": CRED["matt_swid"], "name": "BP- Loudoun 2025"},
    # Elles League
    {"league_id": 1259693145, "year": year, "espn_s2": elle_s2, "swid": CRED["elle_swid"], "name": "Operators Football League"},
    # Dave Work League
    {"league_id": 1675186799, "year": year, "espn_s2": dave_s2, "swid": CRED["dave_swid"], "name": "OnP Fantasy"},
    # Dave Friend League
    {"league_id": 1924463077, "year": year, "espn_s2": dave_s2, "swid": CRED["dave_swid"], "name": "The Mike Daisy Sports IQ League"},
    # Ayush League
    {"league_id": 558148583, "year": year, "espn_s2": ayush_s2, "swid": CRED["ayush_swid"], "name": "Ross' Fantasy League"},
    # Goofy Goobers (2026)
    {"league_id": 1616305229, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "The Goofy Goobers"},
    # Campers and Skiers and Prahlad (2026)
    {"league_id": 47829282, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "Campers and Skiers and Prahlad"},
    # Board Fantasy Football (Nolan)
    {"league_id": 496646254, "year": year, "espn_s2": CRED["nolan_s2"], "swid": CRED["nolan_swid"], "name": "Board Fantasy Football"},
]

if __name__ == "__main__":
    # Pull raw draft + free agent data for every league, then regrade all
    # seasons together so grades stay comparable across leagues and years.
    for year in args.years:
        for league_config in leagues:
            # Update league_config year for this iteration
            league_config_copy = league_config.copy()
            league_config_copy["year"] = year
            try:
                _lid = (registry.league_id_for(league_config["name"], year)
                        or league_config["league_id"])
                league = League(
                    league_id=_lid,
                    year=year,
                    espn_s2=league_config["espn_s2"],
                    swid=league_config["swid"],
                )
                pull_draft_data(league, year)
            except Exception as e:
                print(f"Failed to process {league_config['name']} {year}. Error: {str(e)}")
                continue

    from ffapp.metrics.draft_grading import regrade_all
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
