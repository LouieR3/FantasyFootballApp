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
                    
                print(pick)
                print(player)
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
        
        # Extract the round from the 'Pick' column
        draft_df['Round'] = draft_df['Pick'].str.split(' - ').str[0].astype(int)

        # Compute average `Avg Points` by draft round
        average_points_by_round = draft_df.groupby('Round')['Avg Points'].mean().to_dict()

        # Add Round Value column to the DataFrame
        draft_df['Round Value'] = draft_df.apply(
            lambda row: row['Avg Points'] / average_points_by_round[row['Round']], axis=1
        )

        # Constants to weigh the different factors
        W1 = 0.4  # Weight for points vs. projected points
        W2 = 0.3  # Weight for avg points vs. projected avg points
        W3 = 0.2  # Weight for games played
        W4 = 0.4  # Weight for draft position (steals)
        W5 = 0.5  # Weight for position value (new metric)
        W6 = 0.7  # Weight for total points
        W8 = 0.5  # Weight for avg points
        W7 = 0.5  # Weight for round value (new metric)

        # Get the maximum points scored by any player
        max_points = draft_df['Points'].max()
        max_avg_points = draft_df['Avg Points'].max()

        # Add a column for Draft Grade
        max_games = 14  # Maximum possible games (e.g., full NFL season)

        # Get the maximum pick number
        max_pick = draft_df['Total Pick'].max()

        # Compute average points by position
        average_points_by_position = draft_df.groupby('Position')['Points'].mean().to_dict()

        # Add Position Value column to the DataFrame
        draft_df['Position Value'] = draft_df.apply(
            lambda row: row['Points'] / average_points_by_position[row['Position']], axis=1
        )

        # Recalculate Draft Grade
        if year == 2024:
            draft_df['Draft Grade'] = (
                (draft_df['Points'] / draft_df['Projected Points']) * W1 +
                (draft_df['Avg Points'] / draft_df['Projected Avg Points']) * W2 +
                (draft_df['Games Played'] / max_games) * W3 +
                (draft_df['Total Pick'] - 1) / (max_pick - 1) * W4 + 
                (draft_df['Position Value']) * W5 +
                (draft_df['Points'] / max_points) * W6  +
                (draft_df['Avg Points'] / max_avg_points) * W8
                # + (draft_df['Round Value']) * W7
            )
            # draft_df['Points Grade'] = (draft_df['Points'] / draft_df['Projected Points']) * W1
            # draft_df['Avg Grade'] = (draft_df['Avg Points'] / draft_df['Projected Avg Points']) * W2
            # draft_df['GamesPlay Grade'] = (draft_df['Games Played'] / max_games) * W3
            # draft_df['Pick Grade'] = (draft_df['Total Pick'] - 1) / (max_pick - 1) * W4
            # draft_df['Position Grade'] = (draft_df['Position Value']) * W5
            # draft_df['Points MAX Grade'] = (draft_df['Points'] / max_points) * W6
            # draft_df['Avg MAX Grade'] = (draft_df['Avg Points'] / max_avg_points) * W8
        else:
            W1 = 0.7  # Weight for points
            W2 = 0.5  # Weight for avg points
            W3 = 0.2  # Weight for games played
            W4 = 0.4  # Weight for draft position (steals)
            W5 = 0.5  # Weight for position value (new metric)
            W7 = 0.5  # Weight for round value (new metric)
            max_avg_points = draft_df['Avg Points'].max()
            draft_df['Draft Grade'] = (
                (draft_df['Points'] / max_points) * W1 +
                (draft_df['Avg Points'] / max_avg_points) * W2 +
                (draft_df['Games Played'] / max_games) * W3 +
                ((max_pick - draft_df['Total Pick']) / max_pick) * W4 + 
                (draft_df['Position Value']) * W5  +
                (draft_df['Round Value']) * W7
            )

        # Sort by Draft Grade to see best values
        draft_df = draft_df.sort_values(by='Draft Grade', ascending=False)
        # print(draft_df.head(20))

        # Get the min and max of the Draft Grade column
        min_grade = draft_df['Draft Grade'].min()
        max_grade = draft_df['Draft Grade'].max()

        # Apply min-max scaling to convert to a 1-100 scale
        draft_df['Draft Grade'] = 1 + ((draft_df['Draft Grade'] - min_grade) / (max_grade - min_grade)) * 99

        # Apply square root transformation to Draft Grade (normalize to 1-100 first)
        draft_df['Draft Grade'] = 10 * (draft_df['Draft Grade'] ** 0.51)
        # Cap Draft Grade at 100 if it exceeds the maximum
        draft_df['Draft Grade'] = draft_df['Draft Grade'].clip(upper=100)

        # Define a function to map numeric grades to letter grades
        def grade_to_letter(grade):
            if grade >= 97: return "A+"
            elif grade >= 93: return "A"
            elif grade >= 90: return "A-"
            elif grade >= 87: return "B+"
            elif grade >= 83: return "B"
            elif grade >= 80: return "B-"
            elif grade >= 77: return "C+"
            elif grade >= 73: return "C"
            elif grade >= 70: return "C-"
            elif grade >= 67: return "D+"
            elif grade >= 63: return "D"
            elif grade >= 60: return "D-"
            else: return "F-"

        # Apply the function to create a new column for letter grades
        draft_df['Letter Grade'] = draft_df['Draft Grade'].apply(grade_to_letter)
        draft_df = draft_df.drop(['Position Value', 'Round', 'Round Value'], axis=1)
        # Display the DataFrame
        draft_df['Draft Grade'] = draft_df['Draft Grade'].round(2)

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

            # Add Position Value column to the DataFrame
            additions_df['Position Value'] = additions_df.apply(
                lambda row: row['Points'] / average_points_by_position[row['Position']], axis=1
            )

            # Recalculate Draft Grade
            if year == 2024:
                additions_df['Performance Grade'] = (
                    (additions_df['Points'] / draft_df['Projected Points']) * W1 +
                    (additions_df['Avg Points'] / draft_df['Projected Avg Points']) * W2 +
                    (additions_df['Games Played'] / max_games) * W3 +
                    (additions_df['Position Value']) * W5+
                    (additions_df['Points'] / max_points) * W6 
                )
            else:
                W1 = 0.6  # Weight for points
                W2 = 0.3  # Weight for avg points
                W3 = 0.2  # Weight for games played
                W4 = 0.2  # Weight for draft position (steals)
                W5 = 0.5  # Weight for position value (new metric)
                W7 = 0.5  # Weight for round value (new metric)
                max_avg_points = draft_df['Avg Points'].max()
                additions_df['Performance Grade'] = (
                    (draft_df['Points'] / max_points) * W1 +
                    (draft_df['Avg Points'] / max_avg_points) * W2 +
                    (additions_df['Games Played'] / max_games) * W3 +
                    (additions_df['Position Value']) * W5
                )

            # Get the min and max of the Draft Grade column
            min_grade = additions_df['Performance Grade'].min()
            max_grade = additions_df['Performance Grade'].max()

            # Apply min-max scaling to convert to a 1-100 scale
            additions_df['Performance Grade'] = 1 + ((additions_df['Performance Grade'] - min_grade) / (max_grade - min_grade)) * 99
            # Apply square root transformation to Draft Grade (normalize to 1-100 first)
            additions_df['Performance Grade'] = 10 * (additions_df['Performance Grade'] ** 0.5)
            # Sort by Draft Grade to see best values
            additions_df = additions_df.sort_values(by='Performance Grade', ascending=False)

            # Define a function to map numeric grades to letter grades
            def grade_to_letter(grade):
                if grade >= 97: return "A+"
                elif grade >= 93: return "A"
                elif grade >= 90: return "A-"
                elif grade >= 87: return "B+"
                elif grade >= 83: return "B"
                elif grade >= 80: return "B-"
                elif grade >= 77: return "C+"
                elif grade >= 73: return "C"
                elif grade >= 70: return "C-"
                elif grade >= 67: return "D+"
                elif grade >= 63: return "D"
                elif grade >= 60: return "D-"
                else: return "F-"

            # Apply the function to create a new column for letter grades
            additions_df['Letter Grade'] = additions_df['Performance Grade'].apply(grade_to_letter)
            additions_df['Performance Grade'] = additions_df['Performance Grade'].round(2)

            additions_df = additions_df.drop(['Position Value'], axis=1)
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

espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
# Pennoni Younglings
league = League(league_id=310334683, year=2024, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# print(league.settings)
# gfds
# league = League(league_id=310334683, year=2023, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=310334683, year=2022, espn_s2=espn_s2,swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=996930954, year=2024, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1725372613, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=2024, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2021, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Pennoni Transportation
# league = League(league_id=1339704102, year=2024, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')
# league = League(league_id=1339704102, year=2023, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')
# league = League(league_id=1339704102, year=2022, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Game of Yards
# league = League(league_id=1781851, year=2024, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')
# league = League(league_id=1781851, year=2022, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Brown Munde
# league = League(league_id=367134149, year=2024, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Las League
# league = League(league_id=1049459, year=2024, espn_s2='AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D', swid='{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}')

# louie_espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
# prahlad_espn_s2 = "AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4"
# la_espn_s2 = "AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D"
# year = 2020
# # List of league configurations
# leagues = [
#     # {"league_id": 310334683, "year": year, "espn_s2": louie_espn_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Pennoni Younglings"},
#     # {"league_id": 996930954, "year": year, "espn_s2": louie_espn_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Family League"},
#     # {"league_id": 1118513122, "year": year, "espn_s2": louie_espn_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "EBC League"},
#     # {"league_id": 1339704102, "year": year, "espn_s2": prahlad_espn_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Pennoni Transportation"},
#     {"league_id": 1781851, "year": year, "espn_s2": prahlad_espn_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Game of Yards!"},
#     # {"league_id":1242265374, "year":year, "espn_s2":"AECbYb8WaMMCKHklAi740KXDsHbXHTaW5mI%2FLPUegrKbIb6MRovW0L4NPTBpsC%2Bc2%2Fn7UeX%2Bac0lk3KGEwyeI%2FgF9WynckxWNIfe8m8gh43s68UyfhDj5K187Fj5764WUA%2BTlCh1AF04x9xnKwwsneSvEng%2BfACneWjyu7hJy%2FOVWsHlEm3nfMbU7WbQRDBRfkPy7syz68C4pgMYN2XaU1kgd9BRj9rwrmXZCvybbezVEOEsApniBWRtx2lD3yhJnXYREAupVlIbRcd3TNBP%2F5Frfr6pnMMfUZrR9AP1m1OPGcQ0bFaZbJBoAKdWDk%2F6pJs%3D", "swid":'{4C1C5213-4BB5-4243-87AC-0BCB2D637264}', "name": "Turf On Grade 2.0"},
#     # {"league_id": 367134149, "year": year, "espn_s2": prahlad_espn_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Brown Munde"},
#     # {"league_id": 1049459, "year": year, "espn_s2": la_espn_s2, "swid": "{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}", "name": "Las League"},
# ]

# # Loop through each league configuration
# for league_config in leagues:
#     try:
        
#         league = League(
#             league_id=league_config["league_id"],
#             year=league_config["year"],
#             espn_s2=league_config["espn_s2"],
#             swid=league_config["swid"],
#         )
#         pull_draft_data(league, year)
#     except Exception as e:
#         print(f"Failed to process league: {league_config['name']}. Error: {str(e)}")
#         continue

# team = league.teams[2]
# print(team.roster[0])

# player = league.player_info('Christian McCaffrey')
# print(player.stats[1]['points'])
# print()
# print(player.stats[0]['projected_points'])
# print(player.stats[0]['projected_avg_points'])
# print(player.stats[0]['points'])
# print(player.stats[0]['avg_points'])
