from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
import xlsxwriter

start_time = time.time()

# Pennoni Younglings
# league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

scoresList = []
schedList = []
count = 0
keyList = []
for team in league.teams:
    scoresList.append(team.scores)
    schedList.append(team.schedule)
    keyList.append([count, team.team_name])
    count += 1

print(schedList[5][0])
# print(scoresList[5][0])
# print(scoresList[5])
# print(league.scoreboard(week=1))

# scoreboard1 = league.scoreboard(week=1)
# print(scoreboard1[4])
# print(scoreboard1[4].home_score)
# print(scoreboard1[4].home_team)
# print(scoreboard1[4].away_score)

names = []
for k in keyList:
    names.append(k[1])

tot = 1
win = 0
loss = 0
tie = 0
records = []
names.insert(0, "Teams")
# df = pd.DataFrame(columns=namesIndex)
masterList = []
schedList = []
schedMaster = []
for i in range(len(keyList)):
    for team in keyList:
        checkTeam = team[1]
        while tot < 6:
            scoreboard = league.scoreboard(week=tot)
            myTeam = keyList[i][1]
            for sc in scoreboard:
                myScore = scoresList[i][tot-1]
                if sc.home_team.team_name == checkTeam:
                    if myScore > sc.away_score:
                        win += 1
                    elif myScore < sc.away_score:
                        loss += 1
                    else:
                        if myTeam == sc.away_team.team_name:
                            if myScore > sc.home_score:
                                win += 1
                            elif myScore < sc.home_score:
                                loss += 1
                        else:
                            tie += 1
                elif sc.away_team.team_name == checkTeam:
                    if myScore > sc.home_score:
                        win += 1
                    elif myScore < sc.home_score:
                        loss += 1
                    else:
                        if myTeam == sc.home_team.team_name:
                            if myScore > sc.away_score:
                                win += 1
                            elif myScore < sc.away_score:
                                loss += 1
                        else:
                            tie += 1
            tot += 1
        record = str(win) + " - " + str(loss) + " - " + str(tie)
        records.append(record)
        schedList.append(win)
        tot = 1
        win = 0
        loss = 0
        tie = 0
    records.insert(0, myTeam)
    schedList.insert(0, myTeam)
    masterList.append(records)
    schedMaster.append(schedList)
    schedList = []
    records = []
    
df = pd.DataFrame(masterList, columns = names)
df1 = pd.DataFrame(masterList, columns = names)
df1 = df1.set_index("Teams")

df2 = pd.DataFrame(schedMaster, columns = names)
df2 = df2.set_index("Teams")

schedRank = []
for k in keyList:
    team = k[1]
    tot = sum(df2[team])
    actualWins = df1[team][team]
    schedRank.append([team, tot, actualWins])

rankList = []
for i in range(len(df2)):
    team = df.iloc[i]["Teams"]
    tot = sum(df2.iloc[i])
    actualWins = df1[team][team]
    rankList.append([team, tot, actualWins])

# print(df)
sortList = sorted(schedRank, key=itemgetter(1))


sortList2 = sorted(rankList, key=itemgetter(1), reverse=True)


s1 = sorted(schedRank, key=itemgetter(0))
s2 = sorted(rankList, key=itemgetter(0))
powerRank = []
for t in range(len(s1)):
    ranking = (s2[t][1] - s1[t][1]) 
    actualWins = df1[keyList[t][1]][keyList[t][1]]
    powerRank.append([s1[t][0], ranking, actualWins])
sortFinal = sorted(powerRank, key=itemgetter(1), reverse=True)

for s in range(len(sortList)):
    num = sortList[s][1] / len(keyList)
    sortList[s][1] = num
# print(tabulate(sortList, headers=["Teams", "Avg Wins Against Schedule"]))

for s in range(len(sortList2)):
    num = sortList2[s][1] / len(keyList)
    sortList2[s][1] = num
# print(tabulate(sortList2, headers=["Teams", "Expected Wins"]))

# WHAT IF YOU ARE 5-0 AGAINST ALL BUT EVERYONE IS 5-0 AGAINST YOUR SCHEDULE

# print(tabulate(sortFinal, headers=["Teams", "Louie Power Index (LPI)"]))

dfSched = pd.DataFrame(sortList, columns = ["Teams", "Avg Wins Against Schedule", "Record"])
dfRank = pd.DataFrame(sortList2, columns = ["Teams", "Expected Wins", "Record"])
dfPowerRank = pd.DataFrame(sortFinal, columns = ["Teams", "Louie Power Index (LPI)", "Record"])
writer = pd.ExcelWriter("FamilyLeague.xlsx", engine = 'xlsxwriter')
df1.to_excel(writer, sheet_name = 'Schedule Grid')
dfSched.to_excel(writer, sheet_name = 'Wins Against Schedule')
dfRank.to_excel(writer, sheet_name = 'Expected Wins')
dfPowerRank.to_excel(writer, sheet_name = 'Louie Power Index')
writer.save()
writer.close()

print("--- %s seconds ---" % (time.time() - start_time))