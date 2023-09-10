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

# league = "EBC League 2021"
# # league = "FamilyLeague"
# # league = "PennoniYounglings"
# file = league + ".xlsx"
# print(league)
# df1 = pd.read_excel(file, sheet_name="Schedule Grid")
# df = pd.read_excel(file, sheet_name="Louie Power Index")
# df = df.iloc[: , 1:]
# names = []
# for col in df1.columns:
#     if col != "Teams":
#         names.append(col)
# count = 0
# print(names)
# for team in names:
#     print(df.loc[df["Teams"] == team]["Louie Power Index (LPI)"])
#     count += 1
# print()
league = League(league_id=310334683, year=2023, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',
                swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

settings = league.settings
print(settings.reg_season_count)
# print(settings = league.settings4)
# print(count)


print("--- %s seconds ---" % (time.time() - start_time))