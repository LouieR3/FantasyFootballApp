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

start_time = time.time()

# Pennoni Younglings
league = League(league_id=310334683, year=2023, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2021, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Pennoni Transportation
# league = League(league_id=1339704102, year=2023, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')
# league = League(league_id=1339704102, year=2022, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Game of Yards
# league = League(league_id=1781851, year=2023, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')
# league = League(league_id=1781851, year=2022, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Brown Munde
# league = League(league_id=367134149, year=2023, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
fileName = leagueName + " 2023"
file = leagueName + ".xlsx"

# Precompute current week 
current_week = None
for week in range(1, settings.reg_season_count+1):
    scoreboard = league.scoreboard(week)
    if not any(matchup.home_score for matchup in scoreboard):
        current_week = week
        break 
# print()
if current_week is None:
    current_week = settings.reg_season_count
elif current_week != settings.reg_season_count:
  current_week -= 1

team_owners = [team.owner for team in league.teams]
team_names = [team.team_name for team in league.teams]

schedules = []
for team in league.teams:
    schedule = [opponent.team_name for opponent in team.schedule]
schedules.append(schedule)

col_list = [f'Week {i} Chances' for i in range(1, current_week + 1)]
final_df = pd.DataFrame(0, columns=col_list, index=team_names)
final_df.index.name = 'Team'
position_chances_dfs = {}
for week in range(1, current_week+1):
    team_scores = [team.scores for team in league.teams]
    team_scores_x = [team.scores for team in league.teams] 
    for i, team in enumerate(team_names):
        team_scores[i] = team_scores[i][:week]
    for i, team in enumerate(team_names):
        team_scores_x[i] = team_scores_x[i][:week]
    team_totals = []
    for team_data in team_scores_x:
        team_total = sum(team_data)
        team_totals.append(team_total)

    # Store data in DataFrames 
    scores_df = pd.DataFrame(team_scores, index=team_names)
    schedules_df = pd.DataFrame(schedules, index=team_names)

    # Create empty dataframe  
    records_df = pd.DataFrame(index=team_names, columns=team_names)

    # Fill diagonal with team names
    records_df.fillna('', inplace=True) 

    # Initialize a DataFrame to store total wins for each team against all schedules
    total_wins_weekly_df = pd.DataFrame(0, columns=team_names, index=team_names)

    def standard_deviation(values):
        avg = sum(values) / len(values)
        square_diffs = [(value - avg) ** 2 for value in values]
        avg_square_diff = sum(square_diffs) / len(values)
        return math.sqrt(avg_square_diff)

    # Initialize a dictionary to store the results
    team_data = {}

    # Calculate average score and standard deviation based on team totals
    for i in range(len(team_names)):
        team_name = team_names[i]
        total_points = team_totals[i]
        team_score_x = team_scores_x[i]
        
        non_zero_values = []
        for score in team_score_x:
            if score != 0.0:
                non_zero_values.append(score)
            else:
                break
        
        # Calculate the average score (total points divided by weeks played)
        average_score = total_points / week
        
        # Calculate the standard deviation using the standard_deviation function
        std_dev = standard_deviation(non_zero_values)
        
        team_data[team_name] = {'average_score': average_score, 'std_dev': std_dev}

    # Define the number of Monte Carlo simulations
    num_simulations = 10000

    # Function to simulate a season
    def simulate_season(team_data, schedules_df, week):
        schedules_df = schedules_df.iloc[:, :week]
        standings = {team: 0 for team in team_data}
        # Simulate each week's matchups
        for week_use in range(schedules_df.shape[1]):
            week_schedule = schedules_df[week_use].to_list()
            random.shuffle(week_schedule)
            # Simulate each matchup
            for i in range(0, len(week_schedule), 2):
                team1 = week_schedule[i]
                team2 = week_schedule[i + 1]
                # Generate random scores based on team data
                score1 = random.gauss(team_data[team1]['average_score'], team_data[team1]['std_dev'])
                score2 = random.gauss(team_data[team2]['average_score'], team_data[team2]['std_dev'])
                if score1 > score2:
                    standings[team1] += 2
                elif score1 < score2:
                    standings[team2] += 2
                else:
                    standings[team1] += 1
                    standings[team2] += 1
            print(standings)

        # Sort the standings by both total points and average score
        sorted_standings = sorted(standings.items(), key=lambda x: (-x[1], team_data[x[0]]['average_score']), reverse=True)
        return [team for team, _ in sorted_standings]

    # Dictionary to store the final standings for each simulation
    final_standings = {team: [0] * len(team_data) for team in team_data}
    print(team_data)
    # Run Monte Carlo simulations
    for _ in range(num_simulations):
        simulated_season = simulate_season(team_data, schedules_df, week)
        for i, team in enumerate(simulated_season):
            final_standings[team][i] += 1

    for team in final_standings:
        final_standings[team] = final_standings[team][::-1]
    
    print(final_standings)
    # Calculate the percentage chance for each position
    position_chances = {i + 1: {} for i in range(len(team_data))}
    for position in range(1, len(team_data) + 1):
        for team in team_data:
            team_index = list(team_data.keys()).index(team)
            count = final_standings[team][position - 1]
            position_chances[position][team] = (count / num_simulations) * 100

    # Create a DataFrame
    position_chances_df = pd.DataFrame(position_chances)
    # Add a column for the team names (optional)
    position_chances_df.index.name = 'Team'
    # Add a new column for the chance of making playoffs
    num_playoff_teams = settings.playoff_team_count
    position_chances_df[f'Week {week} Chances'] = 0.0
    # Sum the top # of finish places based on playoff teams
    for team in position_chances_df.index:
        top_finishes = position_chances_df.iloc[position_chances_df.index.get_loc(team), :num_playoff_teams]
        position_chances_df.at[team, f'Week {week} Chances'] = top_finishes.sum()
    position_chances_dfs[week] = position_chances_df

    # final_df[f'Week {week} Chances'] = position_chances_df[[f'Week {week} Chances']]
    # final_df = position_chances_df.sort_values(by=f'Week {week} Chances', ascending=False)
    # print(final_df)

# final_df = pd.DataFrame(index=team_names, columns=col_list)
for week in position_chances_dfs:
    final_df[f'Week {week} Chances'] = position_chances_dfs[week][f'Week {week} Chances']

# odds_df = oddsCalculator()
print(final_df)