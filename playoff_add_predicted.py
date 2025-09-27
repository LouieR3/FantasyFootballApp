from espn_api.football import League
import pandas as pd
import os
from openpyxl import load_workbook
import numpy as np

all_matchups = pd.read_csv("all_matchups.csv")

all_playoffs = pd.read_csv("all_playoff_dfs.csv")

# First, remove bye matchups and convert Score 2 to float
print("Removing bye matchups...")
all_playoffs = all_playoffs[all_playoffs['Team 2'] != 'Bye'].copy()

# Convert Score 2 to float (it might be stored as string)
all_playoffs['Score 2'] = pd.to_numeric(all_playoffs['Score 2'], errors='coerce')

print(f"Playoffs data after removing byes: {len(all_playoffs)} rows")

# Initialize the new predicted score columns
all_playoffs['Predicted Score 1'] = np.nan
all_playoffs['Predicted Score 2'] = np.nan

# Create a function to find predicted scores
def find_predicted_score(league, year, team, score, matchups_df):
    """
    Find predicted score for a team in a specific game
    """
    # Look for the team as home team
    home_match = matchups_df[
        (matchups_df['League'] == league) & 
        (matchups_df['Year'] == year) & 
        (matchups_df['Home Team'] == team) & 
        (matchups_df['Home Score'] == score)
    ]
    
    if not home_match.empty:
        return home_match.iloc[0]['Home Predicted Score']
    
    # Look for the team as away team
    away_match = matchups_df[
        (matchups_df['League'] == league) & 
        (matchups_df['Year'] == year) & 
        (matchups_df['Away Team'] == team) & 
        (matchups_df['Away Score'] == score)
    ]
    
    if not away_match.empty:
        return away_match.iloc[0]['Away Predicted Score']
    
    return np.nan

# Process each row in playoffs data
print("Matching predicted scores...")
for idx, row in all_playoffs.iterrows():
    league = row['League']
    year = row['Year']
    team1 = row['Team 1']
    score1 = row['Score 1']
    team2 = row['Team 2']
    score2 = row['Score 2']
    
    # Find predicted score for Team 1
    pred_score1 = find_predicted_score(league, year, team1, score1, all_matchups)
    all_playoffs.at[idx, 'Predicted Score 1'] = pred_score1
    
    # Find predicted score for Team 2
    pred_score2 = find_predicted_score(league, year, team2, score2, all_matchups)
    all_playoffs.at[idx, 'Predicted Score 2'] = pred_score2

# Check results
matched_1 = all_playoffs['Predicted Score 1'].notna().sum()
matched_2 = all_playoffs['Predicted Score 2'].notna().sum()
total_rows = len(all_playoffs)

print(f"\nResults:")
print(f"Total playoff rows (after removing byes): {total_rows}")
print(f"Predicted Score 1 matches found: {matched_1} ({matched_1/total_rows*100:.1f}%)")
print(f"Predicted Score 2 matches found: {matched_2} ({matched_2/total_rows*100:.1f}%)")

# Show some examples of matches found
print(f"\nFirst few rows with predicted scores:")
sample_cols = ['League', 'Year', 'Team 1', 'Score 1', 'Predicted Score 1', 
               'Team 2', 'Score 2', 'Predicted Score 2']
print(all_playoffs[sample_cols].head(10))

# Show rows where no predicted scores were found
no_pred_1 = all_playoffs[all_playoffs['Predicted Score 1'].isna()]
no_pred_2 = all_playoffs[all_playoffs['Predicted Score 2'].isna()]

if len(no_pred_1) > 0:
    print(f"\nRows with no Predicted Score 1 found ({len(no_pred_1)} rows):")
    print(no_pred_1[['League', 'Year', 'Team 1', 'Score 1']].head())

if len(no_pred_2) > 0:
    print(f"\nRows with no Predicted Score 2 found ({len(no_pred_2)} rows):")
    print(no_pred_2[['League', 'Year', 'Team 2', 'Score 2']].head())

# Save the updated playoffs data
all_playoffs.to_csv("all_playoffs_with_predictions.csv", index=False)
print(f"\nUpdated playoffs data saved to 'all_playoffs_with_predictions.csv'")

# Display final column structure
print(f"\nFinal columns in playoffs data:")
for i, col in enumerate(all_playoffs.columns):
    print(f"{i+1:2d}. {col}")