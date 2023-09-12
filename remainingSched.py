from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
from calcPercent import percent
import random

start_time = time.time()

# Pennoni Younglings
league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',
                swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
file = leagueName + "PLAYOFFS.xlsx"

df = pd.read_excel(file, sheet_name="Expected Wins")
df = df.iloc[:, 1:]

df2 = pd.read_excel(file, sheet_name="Schedule Grid")

names = []
for col in df2.columns:
    if col != "Teams":
        names.append(col)
percentList = percent(file)
count = percentList[0]
top25 = percentList[1]
bot25 = percentList[2]
top10 = percentList[3]
bot10 = percentList[4]

regCount = settings.reg_season_count
teams = league.teams

remainingWeeks = regCount - count
multiplier = regCount / count

winList = []
recordList = []
for name in names:
    team = league.teams[0]
    for t in teams:
        if t.team_name == name:
            team = t
    wins = team.wins
    loss1 = team.losses
    winPercent = round(wins / count, 3)
    xdf = df.loc[df["Teams"] == name]
    expectWins = xdf["Expected Wins"].item()
    diff = xdf["Difference"].item()
    expWinPercent = round(expectWins / count, 3)
    totalWins = round((expectWins + diff) + wins)
    magicNumber = (expWinPercent * 2) - winPercent
    losses = regCount - totalWins
    record = str(wins) + " - " + str(loss1) + " - 0"
    winList.append([name, magicNumber, record])
    recordList.append([name, wins, loss1])

df = pd.DataFrame(winList, columns=['Team', 'Percent', 'Record'])
print(winList)
# dfRecord = pd.DataFrame(recordList, columns=['Team', 'Wins', 'Losses'])

# testList = []
# for i in range(count, regCount):
#     print("Week " + str(i+1))
#     for x in winList:
#         name = x[0]
#         prcnt = round(x[1], 3) * 1000
#         record = x[2]
#         if name not in testList:
#             team = league.teams[0]
#             for t in teams:
#                 if t.team_name == name:
#                     team = t
#             cnt = count
#             oppo = team.schedule[i].team_name
#             xdf = df.loc[df["Team"] == oppo]
#             oppoPrcnt = round(xdf["Percent"].item(), 3) * 1000

#             testList.append(name)
#             testList.append(oppo)
#             tot = oppoPrcnt + prcnt
#             myPERCENT = round(((prcnt / tot) * 100), 1)
#             oppoPERCENT = round(((oppoPrcnt / tot) * 100), 1)
#             picker = random.randint(-prcnt, oppoPrcnt)
#             winner = ""
#             if picker > 0:
#                 winner = oppo
#                 # xdf = dfRecord.loc[dfRecord["Team"] == winner]
#                 # ldf = dfRecord.loc[dfRecord["Team"] == name]
#                 # dfRecord.loc[dfRecord.Team == winner, 'Wins'] = xdf["Wins"].item() + 1
#                 # dfRecord.loc[dfRecord.Team == name, 'Losses'] = ldf["Losses"].item() + 1
#             else:
#                 winner = name
#                 # xdf = dfRecord.loc[df["Team"] == winner]
#                 # ldf = dfRecord.loc[df["Team"] == oppo]
#                 # dfRecord.loc[dfRecord.Team == winner, 'Wins'] = xdf["Wins"].item() + 1
#                 # dfRecord.loc[dfRecord.Team == oppo, 'Losses'] = ldf["Losses"].item() + 1
#             print("======================")
#             print(name + " vs " + oppo)
#             print(str(myPERCENT) + "% vs " + str(oppoPERCENT) + "%")
#             print("Winner is: " + winner)
#     print()
#     print()
#     testList = []
#     print()

testList = []
print("Week " + str(15))
i = 0
while i < 10:
    for x in winList:
        name = x[0]
        prcnt = round(x[1], 3) * 1000
        record = x[2]
        if name not in testList:
            team = league.teams[0]
            for t in teams:
                if t.team_name == name:
                    team = t
            cnt = count
            oppo = team.schedule[16].team_name
            xdf = df.loc[df["Team"] == oppo]
            oppoPrcnt = round(xdf["Percent"].item(), 3) * 1000

            testList.append(name)
            testList.append(oppo)
            tot = oppoPrcnt + prcnt
            myPERCENT = round(((prcnt / tot) * 100), 1)
            oppoPERCENT = round(((oppoPrcnt / tot) * 100), 1)
            picker = random.randint(-prcnt, oppoPrcnt)
            winner = ""
            if picker > 0:
                winner = oppo
                # xdf = dfRecord.loc[dfRecord["Team"] == winner]
                # ldf = dfRecord.loc[dfRecord["Team"] == name]
                # dfRecord.loc[dfRecord.Team == winner, 'Wins'] = xdf["Wins"].item() + 1
                # dfRecord.loc[dfRecord.Team == name, 'Losses'] = ldf["Losses"].item() + 1
            else:
                winner = name
                # xdf = dfRecord.loc[df["Team"] == winner]
                # ldf = dfRecord.loc[df["Team"] == oppo]
                # dfRecord.loc[dfRecord.Team == winner, 'Wins'] = xdf["Wins"].item() + 1
                # dfRecord.loc[dfRecord.Team == oppo, 'Losses'] = ldf["Losses"].item() + 1
            print("======================")
            print(name + " vs " + oppo)
            print(str(myPERCENT) + "% vs " + str(oppoPERCENT) + "%")
            # print("Winner is: " + winner)
    i += 1


# dfRecord = dfRecord.sort_values(by=['Wins'], ascending=False, ignore_index=True)
# dfRecord.index += 1
# print(dfRecord)

# print(settings.playoff_team_count)

print("--- %s seconds ---" % (time.time() - start_time))
