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

team_owners = [team.owner for team in league.teams]
team_names = [team.team_name for team in league.teams]
team_scores = [team.scores for team in league.teams] 
team_scores_x = [team.scores for team in league.teams] 
schedules = []
for team in league.teams:
  schedule = [opponent.team_name for opponent in team.schedule]
  schedules.append(schedule)

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
# current_week = 3

# Store data in DataFrames 
scores_df = pd.DataFrame(team_scores, index=team_names)
schedules_df = pd.DataFrame(schedules, index=team_names)

# Create empty dataframe  
records_df = pd.DataFrame(index=team_names, columns=team_names)

# Fill diagonal with team names
records_df.fillna('', inplace=True) 

# Initialize a DataFrame to store total wins for each team against all schedules
total_wins_weekly_df = pd.DataFrame(0, columns=team_names, index=team_names)

def oddsCalculator():
  team_totals = [team.points_for for team in league.teams]
  reg_season = settings.reg_season_count
  def standard_deviation(values):
    avg = sum(values) / len(values)
    square_diffs = [(value - avg) ** 2 for value in values]
    avg_square_diff = sum(square_diffs) / len(values)
    return math.sqrt(avg_square_diff)

  # Initialize a dictionary to store the results
  team_data = {}

  # Define a function to calculate the dynamic std_dev_factor based on the current week
  def calculate_dynamic_std_dev_factor(current_week, total_weeks, initial_std_dev_factor, min_std_dev_factor):
      # Calculate a factor that decreases as the season progresses
      week_factor = current_week / total_weeks
      # Use the factor to interpolate between initial and minimum std_dev_factors
      dynamic_std_dev_factor = initial_std_dev_factor - (initial_std_dev_factor - min_std_dev_factor) * week_factor
      return dynamic_std_dev_factor

  # Set initial and maximum std_dev_factors
  initial_std_dev_factor = 1  # Initial factor for week 1
  min_std_dev_factor  = 0.5  # Maximum factor for later weeks

  # Calculate the dynamic std_dev_factor for the current week
  dynamic_std_dev_factor = calculate_dynamic_std_dev_factor(current_week, reg_season, initial_std_dev_factor, min_std_dev_factor)
  # print(dynamic_std_dev_factor)

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
      average_score = total_points / current_week
      
      # Calculate the standard deviation using the standard_deviation function
      std_dev = standard_deviation(non_zero_values) * dynamic_std_dev_factor
      
      team_data[team_name] = {'average_score': average_score, 'std_dev': std_dev}

  # Define the number of Monte Carlo simulations
  num_simulations = 10000
  # Function to simulate a season
  def simulate_season(team_data, schedules_df):
      standings = {team: 0 for team in team_data}
      # Simulate each week's matchups
      for week in range(schedules_df.shape[1]):
          week_schedule = schedules_df[week].to_list()
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

      # Sort the standings by both total points and average score
      sorted_standings = sorted(standings.items(), key=lambda x: (-x[1], team_data[x[0]]['average_score']), reverse=True)
      return [team for team, _ in sorted_standings]

  # Dictionary to store the final standings for each simulation
  final_standings = {team: [0] * len(team_data) for team in team_data}

  # Run Monte Carlo simulations
  for _ in range(num_simulations):
      simulated_season = simulate_season(team_data, schedules_df)
      for i, team in enumerate(simulated_season):
          final_standings[team][i] += 1

  for team in final_standings:
      final_standings[team] = final_standings[team][::-1]
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
  # Determine the maximum number of positions
  max_positions = len(position_chances_df.columns)
  # Rename the columns to represent the positions a team can finish
  position_chances_df.columns = [f'Place {i}' for i in range(1, max_positions + 1)]
  # Add a new column for the chance of making playoffs
  num_playoff_teams = settings.playoff_team_count
  position_chances_df['Chance of making playoffs'] = 0.0
  # Sum the top # of finish places based on playoff teams
  for team in position_chances_df.index:
      top_finishes = position_chances_df.iloc[position_chances_df.index.get_loc(team), :num_playoff_teams]
      position_chances_df.at[team, 'Chance of making playoffs'] = top_finishes.sum()
  # Sort the DataFrame by 'Chance of making playoffs' column
  sort_cols = [f'Place {i}' for i in range(1, max_positions + 1)] + ['Chance of making playoffs']
  position_chances_df = position_chances_df.sort_values(by=sort_cols, ascending=False)
  return position_chances_df

# odds_df = oddsCalculator()
# print(odds_df)

# Define a function to calculate the dynamic std_dev_factor based on the current week
def calculate_dynamic_std_dev_factor(current_week, total_weeks, initial_std_dev_factor, min_std_dev_factor):
    # Calculate a factor that decreases as the season progresses
    week_factor = current_week / total_weeks
    # Use the factor to interpolate between initial and minimum std_dev_factors
    dynamic_std_dev_factor = initial_std_dev_factor - (initial_std_dev_factor - min_std_dev_factor) * week_factor
    return dynamic_std_dev_factor
# Define a function to calculate playoff odds for each week
reg_season = settings.reg_season_count
# Set initial and maximum std_dev_factors
initial_std_dev_factor = 1  # Initial factor for week 1
min_std_dev_factor  = 0.5  # Maximum factor for later weeks

def calculate_weekly_playoff_odds(team_data, schedules_df, num_simulations=10000):
    # Initialize a dictionary to store the results
    weekly_playoff_odds = {}

    for week in range(1, current_week + 1):
        # Update dynamic_std_dev_factor for the current week
        dynamic_std_dev_factor = calculate_dynamic_std_dev_factor(week, reg_season, initial_std_dev_factor, min_std_dev_factor)

        # Run simulations for the current week
        team_weekly_odds = simulate_weekly_playoffs(team_data, schedules_df, num_simulations, week, dynamic_std_dev_factor)

        # Calculate the percentage chance for each position
        position_chances = {i + 1: {} for i in range(len(team_data))}
        for position in range(1, len(team_data) + 1):
            for team in team_data:
                team_index = list(team_data.keys()).index(team)
                count = team_weekly_odds[team][position - 1]
                position_chances[position][team] = (count / num_simulations) * 100
        
        if len(team_owners) == 12 or len(team_owners) == 11:
            num_playoff_teams = 8
        elif len(team_owners) == 10 or len(team_owners) == 8:
            num_playoff_teams = 6

        # Create a DataFrame for the weekly playoff odds
        weekly_odds_df = pd.DataFrame(position_chances)
        weekly_odds_df.index.name = 'Team'
        weekly_odds_df.columns = [f'Week {week} Place {i}' for i in range(1, len(team_owners) + 1)]
        weekly_odds_df[f'Week {week} Chance of making playoffs'] = weekly_odds_df.iloc[:, :num_playoff_teams].sum(axis=1)
        weekly_playoff_odds[week] = weekly_odds_df

    return weekly_playoff_odds

# Function to simulate a season
def simulate_season(team_data, schedules_df):
    standings = {team: 0 for team in team_data}
    # Simulate each week's matchups
    for week in range(schedules_df.shape[1]):
        week_schedule = schedules_df[week].to_list()
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


# Define a function to simulate playoff matchups for the current week
def simulate_weekly_playoffs(team_data, schedules_df, num_simulations, current_week, dynamic_std_dev_factor):
    weekly_standings = {team: [0] * len(team_data) for team in team_data}

    for _ in range(num_simulations):
        simulated_season = simulate_season(team_data, schedules_df, current_week, dynamic_std_dev_factor)
        for i, team in enumerate(simulated_season):
            weekly_standings[team][i] += 1

    for team in weekly_standings:
        weekly_standings[team] = weekly_standings[team][::-1]

    return weekly_standings

# Calculate weekly playoff odds
weekly_playoff_odds = calculate_weekly_playoff_odds(team_data, schedules_df)
for week, weekly_odds_df in weekly_playoff_odds.items():
    print(f"Week {week} Playoff Odds:")
    print(weekly_odds_df)