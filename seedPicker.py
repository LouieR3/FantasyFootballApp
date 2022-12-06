from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
from calcPercent import percent
import random

start_time = time.time()

# Pennoni Younglings
league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

settings = league.settings

# print(league.teams)

print(settings.reg_season_count)
print(settings.playoff_team_count)

teams = league.teams

leagueName = "Pennoni Younglings"
file = leagueName + ".xlsx"
lpiDF = pd.read_excel(file, sheet_name="Louie Power Index")
lpiDF = lpiDF.iloc[: , 1:]

teamList = []
for team in teams:
    teamName = team.team_name
    wins = team.wins
    losses = team.losses
    points = team.points_for
    lpi = lpiDF.loc[lpiDF["Teams"] == teamName]["Louie Power Index (LPI)"].item()
    teamList.append([teamName, wins, losses, points, lpi])

df = pd.DataFrame(teamList, columns = ["Teams", "Wins", "Losses", "Points", "LPI"])
df.sort_values(by=['Wins','Points'], inplace=True,
               ascending = [False, False])
df = df.reset_index(drop=True)
df.index += 1
# print(df)

playoffs = df.head(settings.playoff_team_count)
print(playoffs)

check = True
count = 0
for week in range(1, 18):
    scoreboard = league.scoreboard(week=week)
    if check:
        print(week)
        print(scoreboard[0].home_score)
        if scoreboard[0].home_score == 0 and scoreboard[0].away_score == 0:
            count = week -1
            check = False
    else:
        break
if count == 0:
    count = settings.reg_season_count + 1

regCount = settings.reg_season_count
remainingWeeks = regCount - count
print()
print(len(playoffs))
print(remainingWeeks)

print("--- %s seconds ---" % (time.time() - start_time))