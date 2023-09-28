from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
import numpy as np
import math
import random
from copy import deepcopy
import openpyxl

start_time = time.time()

# Pennoni Younglings
# league = League(league_id=310334683, year=2023, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
league = League(league_id=1118513122, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2021, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
fileName = leagueName + " 2023"
file = leagueName + " 2023.xlsx"

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
# print(team_totals)
# print()

schedules = []
for team in league.teams:
  schedule = [opponent.team_name for opponent in team.schedule]
  schedules.append(schedule)

scores_df = pd.DataFrame(team_scores, index=team_names)
schedules_df = pd.DataFrame(schedules, index=team_names)

# print(scores_df)
# print(schedules_df)

settings = league.settings
reg_season = settings.reg_season_count

def standard_deviation(values):
    avg = sum(values) / len(values)
    square_diffs = [(value - avg) ** 2 for value in values]
    avg_square_diff = sum(square_diffs) / len(values)
    return math.sqrt(avg_square_diff)

# Initialize a dictionary to store the results
team_data = {}

# Set initial and maximum std_dev_factors
initial_std_dev_factor = 1  # Initial factor for week 1
min_std_dev_factor  = 0.2  # Maximum factor for later weeks

# # Calculate the dynamic std_dev_factor for the current week
# dynamic_std_dev_factor = calculate_dynamic_std_dev_factor(current_week, reg_season, initial_std_dev_factor, min_std_dev_factor)
def calculate_dynamic_std_dev_factor(current_week, total_weeks, initial_std_dev_factor, min_std_dev_factor, max_std_dev_factor, max_week):
    if current_week >= max_week:
        dynamic_std_dev_factor = max_std_dev_factor
    else:
        week_factor = current_week / total_weeks
        dynamic_std_dev_factor = initial_std_dev_factor - (initial_std_dev_factor - min_std_dev_factor) * week_factor
    return dynamic_std_dev_factor

# Set the maximum std_dev_factor and the week when it takes effect
max_std_dev_factor = 1.0  # Adjust this value as needed
max_week = 8  # Adjust this week as needed

# Calculate the dynamic std_dev_factor for the current week
dynamic_std_dev_factor = calculate_dynamic_std_dev_factor(current_week, reg_season, initial_std_dev_factor, min_std_dev_factor, max_std_dev_factor, max_week)
print(dynamic_std_dev_factor)

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
    std_dev = standard_deviation(non_zero_values) * dynamic_std_dev_factor
    
    team_data[team_name] = {'average_score': average_score, 'std_dev': std_dev}
# print(team_data)

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

# Calculate the number of wins for each team based on their schedule
team_records = {team: [] for team in team_data}

# Run Monte Carlo simulations
for _ in range(num_simulations):
    simulated_season = simulate_season(team_data, schedules_df)
    for i, team in enumerate(simulated_season):
        final_standings[team][i] += 1
        wins = i + 1  # Since teams are sorted by standings
        team_records[team].append(wins)
# print(final_standings)

# Calculate the average and most common record for each team
average_records = {}
most_common_records = {}

for team, records in team_records.items():
    average_wins = sum(records) / len(records)
    most_common_wins = max(set(records), key=records.count)
    average_records[team] = f"{int(average_wins)}-{14 - int(average_wins)}"
    most_common_records[team] = f"{most_common_wins}-{14 - most_common_wins}"

# Create DataFrames
average_records_df = pd.DataFrame(list(average_records.values()), columns=['Average Record'], index=average_records.keys())
most_common_records_df = pd.DataFrame(list(most_common_records.values()), columns=['Most Common Record'], index=most_common_records.keys())

# Sort DataFrames by the number of wins in the record
average_records_df['Wins'] = average_records_df['Average Record'].apply(lambda x: int(x.split('-')[0]))
most_common_records_df['Wins'] = most_common_records_df['Most Common Record'].apply(lambda x: int(x.split('-')[0]))

average_records_df = average_records_df.sort_values(by='Wins', ascending=False).drop(columns='Wins')
most_common_records_df = most_common_records_df.sort_values(by='Wins', ascending=False).drop(columns='Wins')

# Display sorted DataFrames
print("Average Records (Sorted by Wins):")
print(average_records_df)

print("\nMost Common Records (Sorted by Wins):")
print(most_common_records_df)


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
position_chances_df.index.name = 'Teams'

# Determine the maximum number of positions
max_positions = len(position_chances_df.columns)

# Rename the columns to represent the positions a team can finish
position_chances_df.columns = [f'Place {i}' for i in range(1, max_positions + 1)]

# Add a new column for the chance of making playoffs
num_playoff_teams = settings.playoff_team_count
position_chances_df['Chance of making playoffs'] = 0

# Sum the top # of finish places based on playoff teams
for team in position_chances_df.index:
    top_finishes = position_chances_df.iloc[position_chances_df.index.get_loc(team), :num_playoff_teams]
    position_chances_df.at[team, 'Chance of making playoffs'] = top_finishes.sum()

# Sort the DataFrame by 'Chance of making playoffs' column
sort_cols = [f'Place {i}' for i in range(1, max_positions + 1)] + ['Chance of making playoffs']
position_chances_df = position_chances_df.sort_values(by=sort_cols, ascending=False)

# Display the DataFrame
print(position_chances_df)

# writer = pd.ExcelWriter(fileName + ".xlsx", engine='xlsxwriter')
# position_chances_df.to_excel(writer, sheet_name='Playoff Odds')
# writer.save()

# Save the changes back to the Excel file
# wb.save(fileName + ".xlsx")
records_df = pd.read_excel(fileName + ".xlsx", sheet_name='Schedule Grid', index_col=0)
print(records_df)
schedule_rank_df = pd.read_excel(fileName + ".xlsx", sheet_name='Wins Against Schedule', index_col=0)
print(schedule_rank_df)
rank_df = pd.read_excel(fileName + ".xlsx", sheet_name='Expected Wins', index_col=0)
print(rank_df)
odds_df = pd.read_excel(fileName + ".xlsx", sheet_name='Playoff Odds', index_col=0)
print()
print(odds_df)
print(position_chances_df)
print()
lpi_df = pd.read_excel(fileName + ".xlsx", sheet_name='Louie Power Index', index_col=0)
print(lpi_df)

writer = pd.ExcelWriter(fileName + ".xlsx", engine='xlsxwriter')
records_df.to_excel(writer, sheet_name='Schedule Grid')
schedule_rank_df.to_excel(writer, sheet_name='Wins Against Schedule')
rank_df.to_excel(writer, sheet_name='Expected Wins')
position_chances_df.to_excel(writer, sheet_name='Playoff Odds')
lpi_df.to_excel(writer, sheet_name='Louie Power Index')
writer.save()

print("--- %s seconds ---" % (time.time() - start_time))