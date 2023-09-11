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
# leagueName = "EBC League 2021_test"
file = leagueName + ".xlsx"

scoresList = []
winsList = []
count = 0
keyList = []
for team in league.teams:
    scoresList.append(team.scores)
    winsList.append(team.schedule)
    keyList.append([count, team.team_name])
    count += 1

# print(league.teams)
# print(scoresList[5][0])
# print(scoresList[5])
# print(league.scoreboard(week=1))

# scoreboard1 = league.scoreboard(week=1)
# print(scoreboard1[4])
# print(scoreboard1[4].home_score)
# print(scoreboard1[4].home_team)
# print(scoreboard1[4].away_score)

tot = 1
win = 0
loss = 0
tie = 0
records = []
# df = pd.DataFrame(columns=namesIndex)
masterList = []
winsList = []
winsMaster = []

check = True
# count = 15
count = 0
# Find which week it currently is
for week in range(1, 18):
    scoreboard = league.scoreboard(week=week)
    if check:
        for sc in scoreboard:
            if sc.home_score == 0 and sc.away_score == 0:
                count = week
                check = False
    else:
        break

if count == 0:
    count = settings.reg_season_count + 1
# print(keyList)

team_owners = [team.owner for team in league.teams]
# print(team_owners)
# print()
team_names = [team.team_name for team in league.teams]
# print(team_names)
# print()
team_scores = [team.scores for team in league.teams] 
# print(team_scores)
# print()
schedules = []
for team in league.teams:
  schedule = [opponent.team_name for opponent in team.schedule]
  schedules.append(schedule)
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
# print(current_week)
# Store data in DataFrames 
scores_df = pd.DataFrame(team_scores, index=team_names)
schedules_df = pd.DataFrame(schedules, index=team_names)
print(scores_df)
print(schedules_df)
print()
# Team name -> index mapping
team_name_to_idx = {n: i for i, n in enumerate(team_names)}

# Precompute results 
results = []
for wk in range(1, current_week+1):
    for matchup in league.scoreboard(wk):
        res = {'week': wk}
        res['team'] = matchup.home_team.team_name
        res['opponent'] = matchup.away_team.team_name 
        res['team_score'] = scores_df.loc[res['team'], wk-1]
        res['opp_score'] = scores_df.loc[res['opponent'], wk-1]
        results.append(res)
results_df = pd.DataFrame(results)  
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
sdfsdfsdf
for i, team_i in enumerate(team_names):
    for j, team_j in enumerate(team_names):
      
        # Get matchup involving team_j
        matchup = None 
        for m in scoreboard:
            if m.home_team.name == team_j or m.away_team.name == team_j:
                matchup = m
                break
        
        # Get opponent 
        if matchup.home_team.name == team_j:
            opponent = matchup.away_team
        else:
            opponent = matchup.home_team
            
        # Get scores
        score_i = team_scores[i][scoreboard.index(matchup)]
        score_opp = team_scores[team_names.index(opponent.name)][scoreboard.index(matchup)]
        
        # Calculate record
        record = 1 if score_i > score_opp else 0
        
        # Fill dataframe
        df.at[team_i, team_j] = record
        
print(df)


league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',
                swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

settings = league.settings
team_owners = [team.owner for team in league.teams]
team_names = [team.team_name for team in league.teams]
team_scores = [team.scores for team in league.teams] 
schedules = [team.schedule for team in league.teams]
matchups = league.scoreboard(week=week+1)
def get_schedule_comparison(league):
  teams = league.teams

  team_names = [team.team_name for team in teams]
  team_scores = [team.scores for team in teams]
  schedules = [team.schedule for team in teams]

  # Initialize comparison
  comparison = []
  for team in teams:
    comparison.append({'team': team, 'weekly_results': [], 'schedule_comparison': []})  
  # Get weekly results
  for week in range(1, league.settings.reg_season_count+1):
    matchups = league.scoreboard(week=week)
    for matchup in matchups:
      team1 = matchup.home_team
      team2 = matchup.away_team

      team1_score = team_scores[team_names.index(team1.team_name)][week-1]
      team2_score = team_scores[team_names.index(team2.team_name)][week-1]

      # Update weekly results
      for team in comparison:
        if team['team'].team_name == team1.team_name:
          # Update team1 weekly results
          if team1_score > team2_score:
            team['weekly_results'].append({'wins': 1})
          # etc...
        if team['team'].team_name == team2.team_name:
          # Update team2 weekly results
          if team2_score > team1_score:
            team['weekly_results'].append({'losses': 1})
          # etc...

  # Populate schedule comparison
  for team in comparison:
    for opponent in comparison:
      if team == opponent:
        continue
        
      wins = 0 
      losses = 0
      ties = 0
      
      # Count results vs opponent schedule
      for i in range(len(team['weekly_results'])):
        if team['weekly_results'][i].get('wins'):
          if opponent['weekly_results'][i].get('losses'):
            wins += 1
        # Tally wins, losses, ties

      team['schedule_comparison'].append({'team': opponent['team'], 
                                         'wins': wins, 
                                         'losses': losses,
                                         'ties': ties}) 

  return comparison