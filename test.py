import pandas as pd
from operator import itemgetter
import glob
pd.options.mode.chained_assignment = None
files = glob.glob('*.xlsx')
appended_data = []
for file in files:
    print(file.split(".xlsx")[0])
    df = pd.read_excel(file, sheet_name="Louie Power Index")
    appended_data.append(df)
dfFINAL = pd.concat(appended_data)
dfFINAL = dfFINAL.iloc[: , 1:]
dfFINAL.index += 1
df1 = dfFINAL.sort_values(by=['Louie Power Index (LPI)'], ascending=False)

# print(df1)