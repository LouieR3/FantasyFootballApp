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

league = "EBC League 2021"
# league = "FamilyLeague"
# league = "PennoniYounglings"
file = league + ".xlsx"
print(league)
df = pd.read_excel(file, sheet_name="Schedule Grid")

names = []
for col in df.columns:
    if col != "Teams":
        names.append(col)
count = 0
for team in names:
    print(df[team][count])
    count += 1
# print()

# print(settings.reg_season_count)
# print(settings = league.settings4)
# print(count)


print("--- %s seconds ---" % (time.time() - start_time))