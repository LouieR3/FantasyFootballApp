from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
from calcPercent import percent
# import xlsxwriter

start_time = time.time()

# Pennoni Younglings
league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
file = leagueName + ".xlsx"

df = pd.read_excel(file, sheet_name="Expected Wins")
df = df.iloc[: , 1:]

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
print(remainingWeeks)
multiplier = regCount / count
print(multiplier)

total = 0
winList = []
for name in names:
    team = league.teams[0]
    for t in teams:
        if t.team_name == name:
            team = t
    wins = team.wins
    winPercent = round(wins / count, 3)
    xdf = df.loc[df["Teams"] == name]
    expectWins = xdf["Expected Wins"].item()
    diff = xdf["Difference"].item()
    expWinPercent = round(expectWins / count, 3)
    totalWins = (expectWins + diff) + wins
    magicNumber = (expWinPercent * 2) - winPercent
    roundWins = round(totalWins)
    losses = regCount - roundWins
    total += roundWins
    record = str(roundWins) + " - " + str(losses) + " - 0"
    winList.append([name, magicNumber, record])

df = pd.DataFrame(winList, columns=['Team', 'Percent', 'Record'])
print(df)
testList = []
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
        oppo = team.schedule[cnt].team_name
        xdf = df.loc[df["Team"] == oppo]
        oppoPrcnt = round(xdf["Percent"].item(), 3) * 1000

        print(name + " vs " + oppo)
        testList.append(name)
        testList.append(oppo)
        tot = oppoPrcnt + prcnt
        myPERCENT = round(((prcnt / tot) * 100), 1)
        oppoPERCENT = round(((oppoPrcnt / tot) * 100), 1)
        print(str(myPERCENT) + "% vs " + str(oppoPERCENT) + "%")
        print("======================")

print()
print(regCount * (len(teams) / 2))
print(total)