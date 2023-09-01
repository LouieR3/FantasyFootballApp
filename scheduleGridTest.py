import pandas as pd
from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
# import xlsxwriter

start_time = time.time()

# Pennoni Younglings
league = League(league_id=310334683, year=2023, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',
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

print(league.teams)
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
print(keyList)

team_names = [team.team_name for team in league.teams]
team_scores = [team.scores for team in league.teams] 
schedules = [team.schedule for team in league.teams]

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