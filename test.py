from espn_api.football import League
import pandas as pd
import time
import openpyxl

league = "EBCLeague2021"
file = league + ".xlsx"
# df = pd.read_excel(file, sheet_name="Schedule Grid")
# print(df)

file = league + ".xlsx"
print(league)
df = pd.read_excel(file, sheet_name="Schedule Grid")
df.index += 1 
pd.options.mode.chained_assignment = None
count = 14
top20 = round(count * 0.8)
bot20 = round(count * 0.2)
# def highlight_cellsGood(val):
#     val1 = str(val.split(" ")[0])
#     print(val)
#     val1 = int(val1)
#     color = 'blue' if val1 >= top20 else ''
#     print(val1 >= top20)
#     return 'background-color: {}'.format(color)
# def highlight_cellsBad(val):
#     color = 'red' if val <= bot20 else ''
#     return 'background-color: {}'.format(color)
# df.style.applymap(highlight_cellsGood)
# df3 = df.style.applymap(highlight_cellsBad)

def highlight_cells(val):
    print(val)
    color = 'yellow' if val == "8 - 6 - 0" else ''
    return 'background-color: {}'.format(color)

df.style.applymap(highlight_cells)

def highlight_cols(col):
    if col.name == 'Hungry Dogs':
        color = '#A79AFF' # Dark purple
    else:
        color = '#DCD3FF' # Light purple
    return ['background-color: {}'.format(color) for c in col]

df.style.apply(highlight_cols, axis=0)
print(df)