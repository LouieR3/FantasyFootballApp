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
espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"

year = 2024
# Pennoni Younglings
# league = League(league_id=310334683, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=310334683, year=2023, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=310334683, year=2022, espn_s2=espn_s2,swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=996930954, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1725372613, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2021, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Pennoni Transportation
# league = League(league_id=1339704102, year=year, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')
# league = League(league_id=1339704102, year=2023, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')
# league = League(league_id=1339704102, year=2022, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Game of Yards
# league = League(league_id=1781851, year=year, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Brown Munde
# league = League(league_id=367134149, year=year, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Other Prahlad League
league = League(league_id=1242265374, year=year, espn_s2="AECbYb8WaMMCKHklAi740KXDsHbXHTaW5mI%2FLPUegrKbIb6MRovW0L4NPTBpsC%2Bc2%2Fn7UeX%2Bac0lk3KGEwyeI%2FgF9WynckxWNIfe8m8gh43s68UyfhDj5K187Fj5764WUA%2BTlCh1AF04x9xnKwwsneSvEng%2BfACneWjyu7hJy%2FOVWsHlEm3nfMbU7WbQRDBRfkPy7syz68C4pgMYN2XaU1kgd9BRj9rwrmXZCvybbezVEOEsApniBWRtx2lD3yhJnXYREAupVlIbRcd3TNBP%2F5Frfr6pnMMfUZrR9AP1m1OPGcQ0bFaZbJBoAKdWDk%2F6pJs%3D", swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Las League
# league = League(league_id=1049459, year=year, espn_s2='AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D', swid='{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}')

settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
fileName = leagueName + " " + str(year)
file = leagueName + ".xlsx"

# team_owners = [team.owners for team in league.teams]
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
current_week = 17
# print(current_week)
# Store data in DataFrames 
scores_df = pd.DataFrame(team_scores, index=team_names)
schedules_df = pd.DataFrame(schedules, index=team_names)
# print(scores_df)
# print()
print(schedules_df)
# Create empty dataframe  
records_df = pd.DataFrame(index=team_names, columns=team_names)

# Fill diagonal with team names
records_df.fillna('', inplace=True) 

# Initialize a DataFrame to store total wins for each team against all schedules
total_wins_weekly_df = pd.DataFrame(0, columns=team_names, index=team_names)

# Initialize an empty DataFrame to store LPI scores for each week
lpi_weekly_df = pd.DataFrame()

# Iterate through each week
for week in range(1, current_week+1):
    # Initialize a DataFrame to store total wins for each team against all schedules for this week
    total_wins_weekly_df = pd.DataFrame(0, columns=team_names, index=team_names)

    # Iterate through teams (similar to your previous code)
    for team in team_names:
      # Get team scores
      team_scores = scores_df.loc[team].tolist() 
      # Iterate through opponents
      for opp in team_names:
        
        # Compare scores
        wins = 0
        losses = 0
        ties = 0
        for i in range(week):
          # Get opponent schedule
          opp_schedule = schedules_df.loc[opp].tolist()
          
          # Get opponent scores
          opp_scores = [scores_df.loc[o][i] for i, o in enumerate(opp_schedule)]
          if team == opp:
            # Get team's opponent this week

            opp_team = schedules_df.loc[team, i]
            
            # Get team and opponent score
            team_score = scores_df.loc[team, i]
            opp_score = scores_df.loc[opp_team, i]

            if team_score > opp_score:
              wins += 1
            elif team_score < opp_score:
              losses += 1
            else:
              ties += 1

          else:
            # Check if opponent is the same 
            if opp == schedules_df.loc[team, i]:
              # Opponent is the same, get correct scores
              team_score = scores_df.loc[team, i]
              opp_score = scores_df.loc[schedules_df.loc[team, i], i]

            else:  
              # Opponent is different
              opp_schedule = schedules_df.loc[opp].tolist()
              opp_scores = [scores_df.loc[o][i] for i, o in enumerate(opp_schedule)]
              team_score = team_scores[i]
              opp_score = opp_scores[i]

            # Compare scores
            if team_score > opp_score:
              wins += 1
            elif team_score < opp_score:
              losses += 1
            else:
              ties += 1
        
        # Record result
        record = f"{wins}-{losses}-{ties}"
        records_df.at[team, opp] = record 
        # Update the total wins DataFrame for this week
        total_wins_weekly_df.at[team, opp] = wins  # Set wins for all opponents

    # Calculate LPI scores for this week
    team_wins = total_wins_weekly_df.sum(axis=1)
    schedule_wins = [sum(total_wins_weekly_df[team]) for team in team_names]
    num_teams_in_league = len(team_names)
    lpi_scores = ((team_wins - schedule_wins) * (12 / num_teams_in_league)).round().astype(int)
    week_name = "Week " + str(week)
    # Add LPI scores for this week to the weekly DataFrame
    lpi_weekly_df[week_name] = lpi_scores
    lpi_weekly_df = lpi_weekly_df.sort_values(by=[week_name], ascending=[False])
    # lpi_df.reset_index(drop=True, inplace=True)
# Display the DataFrame with LPI scores for each week

# Calculate actual wins
actual_records = records_df.values.diagonal()
# Calculate the total wins for each team
team_wins = total_wins_weekly_df.sum(axis=1)
avg_team_wins = team_wins / len(team_names)
# Calculate expected wins
expected_wins = total_wins_weekly_df.mean(axis=1)

# Calculate differences
differences = avg_team_wins - total_wins_weekly_df.values.diagonal()
# Create a DataFrame for ranking
rank_df = pd.DataFrame({
    'Team': team_names,
    'Expected Wins': avg_team_wins,
    'Difference': differences,
    'Record': actual_records,
})
# print(rank_df)
# Create schedule_rank_df
schedule_rank_df = pd.DataFrame({
    'Teams': rank_df['Team'],
    'Wins Against Schedule': [sum(total_wins_weekly_df[team]) / len(team_names) for team in rank_df['Team']],
    'Record': rank_df['Record']
})
# print(schedule_rank_df)


# Function to format the change value
def format_change(change):
    if change > 0:
        return f'↑{change}'
    elif change < 0:
        return f'↓{abs(change)}'
    else:
        return str(change)

# lpi_weekly_df.insert(loc = 0, column = 'Teams', value = lpi_weekly_df.index)
# lpi_weekly_df.reset_index(drop=True, inplace=True)

if current_week > 1:
  # Calculate the "Change from last week" column
  lpi_weekly_df['Change From Last Week'] = lpi_weekly_df[week_name] - lpi_weekly_df['Week ' + str(week - 1)]
  # Apply the formatting function to the "Change from last week" column
  lpi_weekly_df['Change From Last Week'] = lpi_weekly_df['Change From Last Week'].apply(format_change)
else:
   lpi_weekly_df['Change From Last Week'] = 0

# Display the updated DataFrame
print(lpi_weekly_df)
lpi_df = lpi_weekly_df[[week_name, 'Change From Last Week']]
lpi_df = lpi_df.rename(columns={week_name: "Louie Power Index (LPI)"})
lpi_df.insert(loc = 0, column = 'Teams', value = lpi_df.index)
lpi_df.reset_index(drop=True, inplace=True)
lpi_df.index = lpi_df.index + 1 
lpi_df.insert(loc = 2, column = 'Record', value = "")
# Create a dictionary to map team names to records from rank_df
team_to_record = dict(zip(rank_df['Team'], rank_df['Record']))

# Map the records to lpi_df based on matching team names
lpi_df['Record'] = lpi_df['Teams'].map(team_to_record)
# team_dict = dict(zip(team_names, team_owners))

# Apply dictionary mapping to Teams column
# lpi_df.insert(1, "Owner", lpi_df['Teams'].map(team_dict))
print(lpi_df)

matchup_results = []
# Iterate through each week's matchups
for week in range(1, current_week + 1):
    matchups = league.scoreboard(week)
    for matchup in matchups:
        if matchup.home_score == 0 or matchup.away_score == 0:
          # Skip this matchup
          continue
        home_team = matchup.home_team.team_name
        away_team = matchup.away_team.team_name
        # Get LPI for home and away teams for this week
        home_lpi = lpi_weekly_df.at[home_team, 'Week ' + str(week)]
        away_lpi = lpi_weekly_df.at[away_team, 'Week ' + str(week)]
        # Calculate LPI difference
        higher_lpi = max(home_lpi, away_lpi)
        lower_lpi = min(home_lpi, away_lpi)
        lpi_difference = higher_lpi - lower_lpi
        # Determine the winner of the matchup
        winner = home_team if matchup.home_score > matchup.away_score else away_team
        # Record the matchup results and LPI differences
        matchup_result = {
            'Week': week,
            'Home Team': home_team,
            'Away Team': away_team,
            'Home LPI': home_lpi,
            'Away LPI': away_lpi,
            'LPI Difference': lpi_difference,
            'Winner': winner
        }
        # Append the dictionary to the list
        matchup_results.append(matchup_result)
# Convert the list of matchup results to a DataFrame
matchup_results_df = pd.DataFrame(matchup_results)
# Find the biggest upsets based on LPI difference
biggest_upsets = matchup_results_df.nlargest(30, 'LPI Difference')
# Filter for rows where the LPI_Difference is negative and the AwayTeam won
upsets_df = biggest_upsets[((biggest_upsets['Winner'] == biggest_upsets['Away Team']) & (biggest_upsets['Home LPI'] > biggest_upsets['Away LPI'])) | ((biggest_upsets['Winner'] == biggest_upsets['Home Team']) & (biggest_upsets['Away LPI'] > biggest_upsets['Home LPI']))]
upsets_df.reset_index(drop=True, inplace=True)

schedule_rank_df = schedule_rank_df.sort_values(by=['Wins Against Schedule'], ascending=[True])
schedule_rank_df.reset_index(drop=True, inplace=True)
schedule_rank_df.index = schedule_rank_df.index + 1 
# print(schedule_rank_df)

# Sort the DataFrame by total wins and difference
rank_df = rank_df.sort_values(by=['Expected Wins', 'Difference'], ascending=[False, True])
rank_df.reset_index(drop=True, inplace=True)
rank_df.index = rank_df.index + 1

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
      for week in range(current_week, schedules_df.shape[1]):
        week_schedule = schedules_df.iloc[:, week].to_list()
        # print(week_schedule)
        random.shuffle(week_schedule)
        # print(week_schedule)
        # print()
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

odds_df = oddsCalculator()
# print(odds_df)

writer = pd.ExcelWriter(fileName + ".xlsx", engine='xlsxwriter')
records_df.to_excel(writer, sheet_name='Schedule Grid')
schedule_rank_df.to_excel(writer, sheet_name='Wins Against Schedule')
rank_df.to_excel(writer, sheet_name='Expected Wins')
odds_df.to_excel(writer, sheet_name='Playoff Odds')
lpi_df.to_excel(writer, sheet_name='Louie Power Index')
lpi_weekly_df.to_excel(writer, sheet_name='LPI By Week')
upsets_df.to_excel(writer, sheet_name='Biggest Upsets')
writer.close()

print("--- %s seconds ---" % (time.time() - start_time))