from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
from calcPercent import percent
import random

start_time = time.time()

# Pennoni Younglings
# league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

settings = league.settings
team_owners = [team.owner for team in league.teams]
team_names = [team.team_name for team in league.teams]
team_scores = [team.scores for team in league.teams] 

# Assuming you already have data for regular season records and points
# Create a DataFrame with regular season data
data = {
    'Team': team_names,
    'Wins': [team.wins for team in league.teams],
    'Losses': [team.losses for team in league.teams],
    'Points For': [team.points_for for team in league.teams]
}
regular_season_df = pd.DataFrame(data)

# Sort the DataFrame by Wins, then Points For (as a tiebreaker)
regular_season_df = regular_season_df.sort_values(by=['Wins', 'Points For'], ascending=False)

# Identify playoff teams based on the league's playoff settings
playoff_team_count = settings.playoff_team_count

# Define the number of byes for the top seeds
num_byes = 2

# If there are more teams with byes than playoff spots, adjust the number of byes
if num_byes > playoff_team_count:
    num_byes = playoff_team_count

# Get teams with byes
bye_teams = regular_season_df.head(num_byes)

# Get remaining teams to fill the remaining playoff spots
remaining_teams = regular_season_df.iloc[num_byes:playoff_team_count]

# Print the standings
print("Regular Season Standings:")
print(regular_season_df)

# Print the playoff teams
print("\nPlayoff Teams:")
print(remaining_teams)  # Print only the teams competing in the first round

# Print the teams with byes
print("\nTeams with First-Round Byes:")
print(bye_teams)

# Determine and print playoff matchups for the remaining teams
# For simplicity, assuming playoff matchups are fixed (e.g., 3 vs. 6, 4 vs. 5, etc.)
playoff_matchups = []
for i in range(num_byes):
    matchup = f"Matchup {i + 1}: {remaining_teams.iloc[i]['Team']} vs. {remaining_teams.iloc[playoff_team_count - num_byes - i - 1]['Team']}"
    playoff_matchups.append(matchup)

print("\nFirst Round Playoff Matchups:")
for matchup in playoff_matchups:
    print(matchup)

def calculate_playoff_odds(odds_df, num_playoff_teams):
    # Assuming num_playoff_teams is either 6 or 8
    if num_playoff_teams == 6:
        # First round matchups
        first_round_matchups = [('Place 3', 'Place 6'), ('Place 4', 'Place 5')]

    elif num_playoff_teams == 8:
        # First round matchups
        first_round_matchups = [('Place 1', 'Place 8'), ('Place 2', 'Place 7'), ('Place 3', 'Place 6'), ('Place 4', 'Place 5')]

    # Initialize a dictionary to store playoff matchup odds
    playoff_matchup_odds = {}

    # Calculate odds for first round matchups
    for matchup in first_round_matchups:
        team1, team2 = matchup
        odds_team1 = odds_df.at[team1, 'Chance of making playoffs']
        odds_team2 = odds_df.at[team2, 'Chance of making playoffs']

        # Probability of team1 winning the matchup
        prob_team1_wins = (odds_team1 / 100) * (odds_team2 / 100)

        # Probability of team2 winning the matchup
        prob_team2_wins = (odds_team2 / 100) * (odds_team1 / 100)

        playoff_matchup_odds[matchup] = {
            team1: prob_team1_wins * 100,
            team2: prob_team2_wins * 100,
        }

    # Assuming 1 vs. 4 (or 5) in the next round
    # Calculate odds for the next round
    next_round_matchup = ('Place 1', 'Place 4')  # You can change 4 to 5 if 5th place can also make it

    team1, team2 = next_round_matchup
    odds_team1 = odds_df.at[team1, 'Chance of making playoffs']
    odds_team2 = odds_df.at[team2, 'Chance of making playoffs']

    # Probability of team1 winning the matchup
    prob_team1_wins = (odds_team1 / 100) * (odds_team2 / 100)

    # Probability of team2 winning the matchup
    prob_team2_wins = (odds_team2 / 100) * (odds_team1 / 100)

    playoff_matchup_odds[next_round_matchup] = {
        team1: prob_team1_wins * 100,
        team2: prob_team2_wins * 100,
    }

    return playoff_matchup_odds

# Calculate playoff odds for 6-team playoffs
playoff_odds_6 = calculate_playoff_odds(odds_df, num_playoff_teams=6)
print("Playoff Odds for 6-Team Playoffs:")
print(playoff_odds_6)

# Calculate playoff odds for 8-team playoffs
# playoff_odds_8 = calculate_playoff_odds(odds_df, num_playoff_teams=8)
# print("\nPlayoff Odds for 8-Team Playoffs:")
# print(playoff_odds_8)