from credentials import CRED
import pandas as pd
import numpy as np
from espn_api.football import League
from collections import defaultdict

# ESPN API setup (using your provided data structure)
espn_s2 = CRED["louie_s2"]
year = 2025
# Pennoni Younglings
league = League(league_id=1118513122, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])

# League settings
settings = league.settings
reg_season_count = settings.reg_season_count
num_playoff_teams = settings.playoff_team_count

# Get teams and data
teams = league.teams
team_scores = [team.scores for team in teams]
team_owners = [team.owners[0]['id'] for team in teams]

# Create scores DataFrame
scores_df = pd.DataFrame(team_scores, index=team_owners)
print(scores_df)
# Calculate current week
# Find the first week where all scores are 0.0 (i.e., games haven't been played yet)
zero_week = (scores_df == 0.0).all(axis=0)
if zero_week.any():
	current_week = zero_week.idxmax() +1
else:
	current_week = scores_df.shape[1]

print(f"Current week: {current_week}")