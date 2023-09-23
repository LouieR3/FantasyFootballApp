from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
import numpy as np
import math
import random
from copy import deepcopy

start_time = time.time()

# Pennoni Younglings
league = League(league_id=310334683, year=2023, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',
                swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

team_names = [team.team_name for team in league.teams]
settings = league.settings
# Calculate the chance of getting each place in the league
current_week = None

for week in range(1, settings.reg_season_count + 1):
    scoreboard = league.scoreboard(week)
    if not any(matchup.home_score for matchup in scoreboard):
        current_week = week
        break

if current_week is None:
    current_week = settings.reg_season_count
elif current_week != settings.reg_season_count:
    current_week -= 1

record_total =int(league.teams[0].wins) + int(league.teams[0].losses)
print(str(record_total))
team_scores = [team.scores for team in league.teams] 
# print(team_scores)
# print()
# print(len(team_scores[0]))
# print()
team_totals = [team.points_for for team in league.teams]
print(team_totals)
# print()

schedules = [team.schedule for team in league.teams]

settings = league.settings
reg_season = settings.reg_season_count

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
    team_score = team_scores[i]
    num_weeks_played = 14  # Assuming 14 weeks in the regular season
    # print(team_score)
    
    non_zero_values = []
    for score in team_score:
        if score != 0.0:
            non_zero_values.append(score)
        else:
            break
    
    # Calculate the average score (total points divided by weeks played)
    average_score = total_points / current_week
    
    # Calculate the standard deviation using the standard_deviation function
    std_dev_factor = 0.4  # Adjust this value based on your league's characteristics
    std_dev = standard_deviation(non_zero_values) * std_dev_factor
    
    team_data[team_name] = {'average_score': average_score, 'std_dev': std_dev}
print(team_data)

# Initialize a dictionary to store the results
results = {team: [0] * (len(team_names) + 1) for team in team_data}
# print(results)
# Number of simulations to run
num_simulations = 10000
# Run Monte Carlo simulations
for _ in range(num_simulations):
    # Simulate scores for each team based on normal distribution
    team_scores = {
        team: np.random.normal(data['average_score'], data['std_dev'])
        for team, data in team_data.items()
    }

    # Sort teams by their simulated scores
    sorted_teams = sorted(team_scores.keys(), key=lambda x: team_scores[x], reverse=True)

    # Assign rankings to teams based on the current week
    for rank, team in enumerate(sorted_teams):
        if rank < current_week:
            results[team][rank + 1] += 1
        else:
            results[team][current_week] += 1
print()
print(results)

# Calculate the odds of each team finishing in each position
odds = {}
for team, rank_counts in results.items():
    total_simulations = sum(rank_counts)
    odds[team] = [(count / total_simulations) * 100 for count in rank_counts]

# Create a DataFrame
odds_df = pd.DataFrame(odds).T

# Add a column for the team names (optional)
odds_df.index.name = 'Team'

odds_df = odds_df.iloc[:, 1:]
# Determine the maximum number of positions
max_positions = max(len(odds_df.columns), max([len(team_odds) for team_odds in odds.values()]))

# Fill missing positions with 0
for team_odds in odds_df.columns:
    odds_df[team_odds] = odds_df[team_odds].fillna(0)

# Rename the columns to represent the positions a team can finish
odds_df.columns = [f'Place {i}' for i in range(1, max_positions)]

# Add new column 
odds_df['Chance of making playoffs'] = 0

num_playoff_teams = settings.playoff_team_count  
# Sum the top # of finish places based on playoff teams
for i, row in odds_df.iterrows():
    odds_df.at[i, 'Chance of making playoffs'] = row[:num_playoff_teams].sum()

# Sort by 'Chance of making playoffs' column
sort_cols = ['Place 1', 'Place 2', 'Place 3', 'Place 4', 'Place 5', 'Place 6', 'Place 7', 'Place 8', 'Place 9', 'Place 10', 'Place 11', 'Place 12', 'Chance of making playoffs']

odds_df = odds_df.sort_values(by=sort_cols, ascending=False)

# Display the DataFrame
print(odds_df)