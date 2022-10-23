import pandas as pd
from operator import itemgetter
import glob
pd.options.mode.chained_assignment = None
files = glob.glob('*.xlsx')
dfFINAL = pd.DataFrame()
for file in files:
    df = pd.read_excel(file, sheet_name="Louie Power Index")
    dfFINAL.append(df)

dfFINAL = dfFINAL.iloc[: , 1:]
dfFINAL.index += 1 
print(dfFINAL)