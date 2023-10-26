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
# league = League(league_id=310334683, year=2023, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
league = League(league_id=1118513122, year=2021, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

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
fileName = leagueName + " 2021"
file = leagueName + ".xlsx"

team_owners = [team.owner for team in league.teams]
team_names = [team.team_name for team in league.teams]
team_scores = [team.scores for team in league.teams] 
team_scores_x = [team.scores for team in league.teams] 
schedules = []
for team in league.teams:
  schedule = [opponent.team_name for opponent in team.schedule]
  schedules.append(schedule)
# print(league.scoreboard(17))
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

# Store data in DataFrames 
scores_df = pd.DataFrame(team_scores, index=team_names)
schedules_df = pd.DataFrame(schedules, index=team_names)

# Create empty dataframe  
records_df = pd.DataFrame(index=team_names, columns=team_names)

# Fill diagonal with team names
records_df.fillna('', inplace=True) 

# Initialize a DataFrame to store total wins for each team against all schedules
total_wins_weekly_df = pd.DataFrame(0, columns=team_names, index=team_names)

# Initialize an empty DataFrame to store LPI scores for each week
lpi_weekly_df = pd.DataFrame()
matchup_results_df = pd.DataFrame(columns=['Week', 'HomeTeam', 'AwayTeam', 'HomeLPI', 'AwayLPI', 'LPI_Difference', 'Winner'])

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

# Calculate the "Change from last week" column
lpi_weekly_df['Change From Last Week'] = lpi_weekly_df[week_name] - lpi_weekly_df['Week ' + str(week - 1)]

# Function to format the change value
def format_change(change):
    if change > 0:
        return f'↑{change}'
    elif change < 0:
        return f'↓{abs(change)}'
    else:
        return str(change)

# Apply the formatting function to the "Change from last week" column
lpi_weekly_df['Change From Last Week'] = lpi_weekly_df['Change From Last Week'].apply(format_change)
# lpi_weekly_df.insert(loc = 0, column = 'Teams', value = lpi_weekly_df.index)
# lpi_weekly_df.reset_index(drop=True, inplace=True)

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
team_dict = dict(zip(team_names, team_owners))

# Apply dictionary mapping to Teams column
lpi_df.insert(1, "Owner", lpi_df['Teams'].map(team_dict))
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
            'HomeTeam': home_team,
            'AwayTeam': away_team,
            'HomeLPI': home_lpi,
            'AwayLPI': away_lpi,
            'LPI_Difference': lpi_difference,
            'Winner': winner
        }
        
        # Append the dictionary to the list
        matchup_results.append(matchup_result)

# Convert the list of matchup results to a DataFrame
matchup_results_df = pd.DataFrame(matchup_results)

# Find the biggest upsets based on LPI difference
biggest_upsets = matchup_results_df.nlargest(30, 'LPI_Difference')
print("Biggest Upsets of the Year:")
# Filter for rows where the LPI_Difference is negative and the AwayTeam won
upsets_df = biggest_upsets[((biggest_upsets['Winner'] == biggest_upsets['AwayTeam']) & (biggest_upsets['HomeLPI'] > biggest_upsets['AwayLPI'])) | ((biggest_upsets['Winner'] == biggest_upsets['HomeTeam']) & (biggest_upsets['AwayLPI'] > biggest_upsets['HomeLPI']))]
# Print the resulting DataFrame
upsets_df.reset_index(drop=True, inplace=True)
print(upsets_df)

schedule_rank_df = schedule_rank_df.sort_values(by=['Wins Against Schedule'], ascending=[True])
schedule_rank_df.reset_index(drop=True, inplace=True)
schedule_rank_df.index = schedule_rank_df.index + 1 
# Sort the DataFrame by total wins and difference
rank_df = rank_df.sort_values(by=['Expected Wins', 'Difference'], ascending=[False, True])
rank_df.reset_index(drop=True, inplace=True)
rank_df.index = rank_df.index + 1



print("--- %s seconds ---" % (time.time() - start_time))