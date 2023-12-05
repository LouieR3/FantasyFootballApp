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
espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI'
swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}'
years = [2021, 2022, 2023]
# EBC League
league_id = 1118513122
# Family League
league_id = 1725372613
years = [2022, 2023]
# Pennoni Younglings
league_id = 310334683

all_matchups = []  # List to store matchup statistics

for year in years:
    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

    teams = {}  # Dictionary to store data for each year
    for team in league.teams:
        teams[team.team_name] = {'owner': team.owner, 'scores': team.scores}

    for team1_name, team1_data in teams.items():
        for team2_name, team2_data in teams.items():
            if team1_name != team2_name:
                team1_avg_points = sum(team1_data['scores']) / len(team1_data['scores'])
                team2_avg_points = sum(team2_data['scores']) / len(team2_data['scores'])
                avg_points_diff = abs(team1_avg_points - team2_avg_points)

                team1_wins = 0
                team2_wins = 0

                if sum(team1_data['scores']) > sum(team2_data['scores']):
                    team1_wins += 1
                else:
                    team2_wins += 1

                record = f"{team1_wins}-{team2_wins}"
                points_scored = f"{team1_avg_points:.2f}-{team2_avg_points:.2f}"
                avg_points = f"{team1_avg_points:.2f}-{team2_avg_points:.2f}"
                difference = f"{avg_points_diff:.2f}-{avg_points_diff:.2f}"
                trend = f"{team1_data['owner']} W3"  # Just an example for trend data

                matchup = {
                    'Team 1': team1_name,
                    'Team 2': team2_name,
                    'Record': record,
                    'Points Scored': points_scored,
                    'Average Points Scored': avg_points,
                    'Difference': difference,
                    'Trend': trend
                }

                all_matchups.append(matchup)

# Create DataFrame from matchup statistics
matchups_df = pd.DataFrame(all_matchups)

# Display or further process the matchups_df DataFrame as needed
print(matchups_df)