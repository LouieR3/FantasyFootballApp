from espn_api.football import League
import pandas as pd
import time
import openpyxl

league = "EBCLeague2021"
file = league + ".xlsx"
# df = pd.read_excel(file, sheet_name="Schedule Grid")
# print(df)

# league = "EBCLeague2021"
# # league = "FamilyLeague"
# # league = "PennoniYounglings"
# file = league + ".xlsx"
# print(league)
# df = pd.read_excel(file, sheet_name="Schedule Grid")
# df.index += 1 
# pd.options.mode.chained_assignment = None
# count = 14
# top20 = round(count * 0.8)
# bot20 = round(count * 0.2)
# def highlight_cells(val):
#     val1 = str(val.split(" ")[0])
#     print(val)
#     val1 = int(val1)
#     color = 'blue' if val1 >= top20 else ''
#     print(val1 >= top20)
#     return 'background-color: {}'.format(color)
# def highlight_cellsBad(val):
#     color = 'red' if val <= bot20 else ''
#     return 'background-color: {}'.format(color)
# df.style.applymap(highlight_cells)
# print(df)
# df3 = df.style.applymap(highlight_cellsBad)
df = pd.read_excel(file, sheet_name="Schedule Grid")
# df = pd.read_excel(file, sheet_name="Wins Against Schedule")
df = df.iloc[: , 1:]
df.index += 1 
pd.options.mode.chained_assignment = None
df3 = df.style.background_gradient(subset=['Avg Wins Against Schedule'])
print(df["Hungry Dogs"][3].split(" "))
print(int(df["Hungry Dogs"][3].split(" ")[0]) + int(df["Hungry Dogs"][3].split(" ")[2]) + int(df["Hungry Dogs"][3].split(" ")[4]))

# print(type(df["Hungry Dogs"][3]))
# print(df)