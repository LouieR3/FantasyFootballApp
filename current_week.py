import pandas as pd
import numpy as np
from espn_api.football import League
from collections import defaultdict

# ESPN API setup (using your provided data structure)
espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
year = 2025
# Pennoni Younglings
league = League(league_id=1118513122, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

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