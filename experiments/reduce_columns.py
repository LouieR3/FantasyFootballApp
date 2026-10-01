import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import pandas as pd
from credentials import CRED
from ffapp.ui.data_loader import load_sheet, load_csv, load_owner_df, get_league, sheet_names
import streamlit as st

from paths import LEAGUES_DIR


league_id = 250835749
espn_s2 = CRED["ayush_league2_s2"]
swid = CRED["ayush_league2_swid"]
    
league_name = "Ketkar Fantasy Football 2026"
league = f"{league_name} 2026"
file = f"{LEAGUES_DIR}/" + league + ".xlsx"

# Read the Excel sheet
df = load_sheet(file, "Remaining Schedule Difficulty")

# Process the DataFrame
df = df.iloc[:, 1:]
df.index += 1
print(file)
print(file)
# Remove Owners column for Ketkar Fantasy Football league
if "Ketkar Fantasy Football" in file and "Owner" in df.columns:
    df = df.drop(columns=["Owner"])

# Format specific columns
columns_to_format = ['Avg_Points_For', 'Avg_Opp_Points_For', 'Avg_Opp_LPI']
df[columns_to_format] = df[columns_to_format].applymap(lambda x: f"{x:.1f}")  # Format to 1 decimal place
# df = df.drop('Win_Pct', axis=1)
# df['Win_Pct'] = df['Win_Pct'].apply(lambda x: f"{x:.3f}")  # Format to 3 decimal places
df['Avg_Opp_Win_Pct'] = df['Avg_Opp_Win_Pct'].apply(lambda x: f"{x:.3f}")  # Format to 3 decimal places

# df['Avg LPI of Remaining Opponents'] = (df['Avg LPI of Remaining Opponents']
#                                       .round(2))
df.columns = df.columns.str.replace('_', ' ')

print(df)