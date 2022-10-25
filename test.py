import pandas as pd
from operator import itemgetter
import glob
from espn_api.football import League
pd.options.mode.chained_assignment = None
import time

start_time = time.time()

# files = glob.glob('*.xlsx')
# appended_data = []
# for file in files:
#     print(file.split(".xlsx")[0])
#     df = pd.read_excel(file, sheet_name="Louie Power Index")
#     appended_data.append(df)
# dfFINAL = pd.concat(appended_data)
# dfFINAL = dfFINAL.iloc[: , 1:]
# dfFINAL.index += 1
# df1 = dfFINAL.sort_values(by=['Louie Power Index (LPI)'], ascending=False)

league = League(league_id=1118513122, year=2021, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
count = 0
check = True
settings = league.settings
for week in range(1, settings.reg_season_count + 1):
    scoreboard = league.scoreboard(week=week)
    # print(week)
    # print(scoreboard[0])
    if check:
        for sc in scoreboard:
            if (sc.home_score == 0 and sc.away_score == 0) or sc.away_team == 0:
                count = week
                check = False
    else:
        break

print(settings.reg_season_count)
print(settings = league.settings4)
print(count)


print("--- %s seconds ---" % (time.time() - start_time))