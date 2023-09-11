import pandas as pd
from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
# import xlsxwriter
from itertools import combinations
import itertools

start_time = time.time()

# Pennoni Younglings
league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',
                swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
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
# print(settings.reg_season_count)

# Precompute current week 
current_week = None
for week in range(1, settings.reg_season_count+1):
    scoreboard = league.scoreboard(week)
    if not any(matchup.home_score for matchup in scoreboard):
        current_week = week
        break 

if current_week is None:
    current_week = settings.reg_season_count

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

print(records_df)
print("--- %s seconds ---" % (time.time() - start_time))