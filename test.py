from espn_api.football import League
import pandas as pd
import time
import openpyxl

league = "PennoniYounglings"
file = league + ".xlsx"
df = pd.read_excel(file, sheet_name="Schedule Grid")
print(df)