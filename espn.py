from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
import xlsxwriter

start_time = time.time()

leagueName = "PrahladFriendsLeague"

# Pennoni Younglings
# league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBCLeague
# league = League(league_id=1118513122, year=2021, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# PennoniTransportation
# league = League(league_id=1339704102, year=2022, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')

# PrahladFriendsLeague
league = League(league_id=1781851, year=2022, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')

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

# teamToUse = "The Golden Receivers"
# teamToUse = "PAI Athletic Director"
# teamToUse = "Girth Brooks"

# teamToUse = "Golden Receivers"
# teamToUse = "Team Janstrong"
# teamToUse = "Lockett inma pockett"
# teamToUse = "DadBod 69ers"
# teamToUse = "Kuppcakes  ."

# teamToUse = "The Hungry Dogs"
# teamToUse = "Abyss Diamond Eyes"
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

check = True
count = 1
for week in range(1, 17):
    scoreboard = league.scoreboard(week=week)
    if check:
        for sc in scoreboard:
            if sc.home_score == 0 and sc.away_score == 0:
                count = week
                check = False
    else:
        break

for i in range(len(keyList)):
    for team in keyList:
        checkTeam = team[1]
        while tot < count:
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
    seasonWins = df2.iloc[i][team]
    difference = (tot / len(keyList)) - seasonWins
    actualWins = df1[team][team]
    rankList.append([team, tot, difference, actualWins])

# print(df)
sortList = sorted(schedRank, key=itemgetter(1))


sortList2 = sorted(rankList, key=itemgetter(1), reverse=True)


s1 = sorted(schedRank, key=itemgetter(0))
s2 = sorted(rankList, key=itemgetter(0))
powerRank = []
for t in range(len(s1)):
    ranking = (s2[t][1] - s1[t][1]) 
    actualWins = df1[s1[t][0]][s1[t][0]]
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
dfRank = pd.DataFrame(sortList2, columns = ["Teams", "Expected Wins", "Difference", "Record"])
dfPowerRank = pd.DataFrame(sortFinal, columns = ["Teams", "Louie Power Index (LPI)", "Record"])
# writer = pd.ExcelWriter("FamilyLeague.xlsx", engine = 'xlsxwriter')
# writer = pd.ExcelWriter("EBCLeague.xlsx", engine = 'xlsxwriter')
writer = pd.ExcelWriter(leagueName + ".xlsx", engine = 'xlsxwriter')
df1.to_excel(writer, sheet_name = 'Schedule Grid')
dfSched.to_excel(writer, sheet_name = 'Wins Against Schedule')
dfRank.to_excel(writer, sheet_name = 'Expected Wins')
dfPowerRank.to_excel(writer, sheet_name = 'Louie Power Index')
writer.save()
writer.close()

print("--- %s seconds ---" % (time.time() - start_time))