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

start_time = time.time()

# Pennoni Younglings
# league = League(league_id=310334683, year=2023, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',
#                 swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',
#                 swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
league = League(league_id=1118513122, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2021, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Pennoni Transportation
# league = League(league_id=1339704102, year=2022, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')

# Prahlad Friends League
# league = League(league_id=1781851, year=2022, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')


settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
fileName = leagueName + " 2023"
file = leagueName + ".xlsx"

team_owners = [team.owner for team in league.teams]
team_names = [team.team_name for team in league.teams]
team_scores = [team.scores for team in league.teams] 
schedules = []
for team in league.teams:
  schedule = [opponent.team_name for opponent in team.schedule]
  schedules.append(schedule)

# print(team_owners)
# print()
# print(team_names)
# print()
# print(team_scores)
# print()
# print(schedules)
# print()
# print(league.scoreboard(week=1))
# print()
# print(league.scoreboard(week=2))
# print()
# print(settings.reg_season_count)

# Precompute current week 
current_week = None
for week in range(1, settings.reg_season_count+1):
    scoreboard = league.scoreboard(week)
    if not any(matchup.home_score for matchup in scoreboard):
        current_week = week
        break 
# print()
# print(current_week)
if current_week is None:
    current_week = settings.reg_season_count
elif current_week != settings.reg_season_count:
  current_week -= 1
# print(current_week)

# Store data in DataFrames 
scores_df = pd.DataFrame(team_scores, index=team_names)
schedules_df = pd.DataFrame(schedules, index=team_names)
# print(scores_df)
# print(schedules_df)
# print()

# Precompute results 
# results = []
# for wk in range(1, current_week+1):
#     for matchup in league.scoreboard(wk):
#         res = {'week': wk}
#         res['team'] = matchup.home_team.team_name
#         res['opponent'] = matchup.away_team.team_name 
#         res['team_score'] = scores_df.loc[res['team'], wk-1]
#         res['opp_score'] = scores_df.loc[res['opponent'], wk-1]
#         results.append(res)
# results_df = pd.DataFrame(results)  
# print(results_df)

# Create empty dataframe  
records_df = pd.DataFrame(index=team_names, columns=team_names)

# Fill diagonal with team names
records_df.fillna('', inplace=True) 

# Initialize a DataFrame to store total wins for each team against all schedules
total_wins_df = pd.DataFrame(0, columns=team_names, index=team_names)

# Iterate through teams
for team in team_names:
  # Get team scores
  team_scores = scores_df.loc[team].tolist() 
  # Iterate through opponents
  for opp in team_names:
    
    # Compare scores
    wins = 0
    losses = 0
    ties = 0
    for i in range(current_week):
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
    
    # Update the total wins DataFrame
    total_wins_df.at[team, opp] = wins

# print(records_df)
# Calculate the total wins for each team
team_wins = total_wins_df.sum(axis=1)
avg_team_wins = team_wins / len(team_names)

# Calculate expected wins
expected_wins = total_wins_df.mean(axis=1)

# Calculate differences
differences = avg_team_wins - total_wins_df.values.diagonal()

# Calculate actual wins
actual_wins = records_df.values.diagonal()

# Calculate win percentages
win_percentages = team_wins / current_week

# Create a DataFrame for ranking
rank_df = pd.DataFrame({
    'Team': team_names,
    'Expected Wins': avg_team_wins,
    'Difference': differences,
    'Record': actual_wins,
})

# Create schedule_rank_df
schedule_rank_df = pd.DataFrame({
    'Teams': rank_df['Team'],
    'Wins Against Schedule': [sum(total_wins_df[team]) / len(team_names) for team in rank_df['Team']],
    'Record': rank_df['Record']
})

schedule_wins = [sum(total_wins_df[team]) for team in rank_df['Team']]
# Create the final DataFrame
lpi_df = pd.DataFrame({
    'Teams': rank_df['Team'],
    'Louie Power Index': team_wins - schedule_wins,
    'Record': rank_df['Record'],
    'Change From Last Week': 0,
})
# print()
lpi_df = lpi_df.sort_values(by=['Louie Power Index'], ascending=[False])
lpi_df.reset_index(drop=True, inplace=True)
lpi_df.index = lpi_df.index + 1 
print(lpi_df)


schedule_rank_df = schedule_rank_df.sort_values(by=['Wins Against Schedule'], ascending=[True])
schedule_rank_df.reset_index(drop=True, inplace=True)
schedule_rank_df.index = schedule_rank_df.index + 1 
# print(schedule_rank_df)


# Sort the DataFrame by total wins and difference
rank_df = rank_df.sort_values(by=['Expected Wins', 'Difference'], ascending=[False, True])
rank_df.reset_index(drop=True, inplace=True)
rank_df.index = rank_df.index + 1 
# Print the sorted rank DataFrame
# print(rank_df)

def oddsCalculator():
  team_scores = [team.scores for team in league.teams] 
  def standard_deviation(values):
      avg = sum(values) / len(values)
      square_diffs = [(value - avg) ** 2 for value in values]
      avg_square_diff = sum(square_diffs) / len(values)
      return math.sqrt(avg_square_diff)

  # Initialize a dictionary to store the results
  team_data = {}
  team_totals = [team.points_for for team in league.teams]

  # Calculate average score and standard deviation based on team totals
  for i in range(len(team_names)):
      team_name = team_names[i]
      total_points = team_totals[i]
      num_weeks_played = 14  # Assuming 14 weeks in the regular season
      
      # Calculate the average score (total points divided by weeks played)
      average_score = total_points / len(team_scores[0])
      
      # Calculate the standard deviation using the standard_deviation function
      std_dev_factor = 0.2  # Adjust this value based on your league's characteristics
      std_dev = standard_deviation([total_points] * num_weeks_played) * std_dev_factor
      
      team_data[team_name] = {'average_score': average_score, 'std_dev': std_dev}
  # print(team_data)
  # Initialize a dictionary to store the results
  results = {team: [0] * (len(team_names) + 1) for team in team_data}

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
      
      # Assign rankings to teams
      for rank, team in enumerate(sorted_teams):
          results[team][rank + 1] += 1

  # Calculate the odds of each team finishing in each position
  odds = {}
  for team, rank_counts in results.items():
      total_simulations = sum(rank_counts)
      odds[team] = [(count / total_simulations) * 100 for count in rank_counts]

  # # Print the odds for each team in each position
  # for team, team_odds in odds.items():
  #     print(f"Team: {team}")
  #     for rank, odds_percentage in enumerate(team_odds[1:], start=1):
  #         print(f"   Finish in Position {rank}: {odds_percentage:.2f}%")
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

  # Display the DataFrame
  # print(odds_df)
  # Get number of playoff teams 
  num_playoff_teams = settings.playoff_team_count  

  # Add new column 
  odds_df['Chance of making playoffs'] = 0

  # Sum the top # of finish places based on playoff teams
  for i, row in odds_df.iterrows():
      odds_df.at[i, 'Chance of making playoffs'] = row[:num_playoff_teams].sum()

  # Sort by 'Chance of making playoffs' column
#   sort_cols = ['Place 1', 'Place 2', 'Place 3', 'Place 4', 'Place 5', 'Place 6', 'Place 7', 'Place 8', 'Place 9', 'Place 10', 'Place 11', 'Place 12', 'Chance of making playoffs']
  sort_cols = ['Place 1', 'Place 2', 'Place 3', 'Place 4', 'Place 5', 'Place 6', 'Place 7', 'Place 8', 'Chance of making playoffs']

  odds_df = odds_df.sort_values(by=sort_cols, ascending=False)
  return odds_df

odds_df = oddsCalculator()
print(odds_df)

writer = pd.ExcelWriter(fileName + ".xlsx", engine='xlsxwriter')
records_df.to_excel(writer, sheet_name='Schedule Grid')
schedule_rank_df.to_excel(writer, sheet_name='Wins Against Schedule')
rank_df.to_excel(writer, sheet_name='Expected Wins')
odds_df.to_excel(writer, sheet_name='Playoff Odds')
lpi_df.to_excel(writer, sheet_name='Louie Power Index')
writer.save()

print("--- %s seconds ---" % (time.time() - start_time))