import pandas as pd
from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
# import xlsxwriter
from itertools import combinations
import itertools
import math
import numpy as np

start_time = time.time()

# Pennoni Younglings
# league = League(league_id=310334683, year=2023, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2021, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Pennoni Transportation
# league = League(league_id=1339704102, year=2022, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')

# Prahlad Friends League
# league = League(league_id=1781851, year=2022, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')

settings = league.settings

leagueName = settings.name.replace(" 22/23", "")
fileName = leagueName + " 2023"
file = leagueName + ".xlsx"

team_owners = [team.owner for team in league.teams]
team_names = [team.team_name for team in league.teams]
team_scores = [team.scores for team in league.teams] 
schedules = []
for team in league.teams:
  schedule = [opponent.team_name for opponent in team.schedule]
  schedules.append(schedule)

# Precompute current week 
current_week = None
for week in range(1, settings.reg_season_count+1):
    scoreboard = league.scoreboard(week)
    if not any(matchup.home_score for matchup in scoreboard):
        current_week = week
        break 
# print()
# print(current_week)
if current_week is None:
    current_week = settings.reg_season_count
elif current_week != settings.reg_season_count:
  current_week -= 1
# print(current_week)

# Store data in DataFrames 
scores_df = pd.DataFrame(team_scores, index=team_names)
schedules_df = pd.DataFrame(schedules, index=team_names)

# Create empty dataframe  
records_df = pd.DataFrame(index=team_names, columns=team_names)

# Fill diagonal with team names
records_df.fillna('', inplace=True) 

# Initialize a DataFrame to store total wins for each team against all schedules
total_wins_df = pd.DataFrame(0, columns=team_names, index=team_names)

# Initialize Elo ratings for each team
elo_ratings = {team: 1500 for team in team_names}

# K-factor for Elo rating adjustments (you can adjust this as needed)
k_factor = 15

# Iterate through teams
for team in team_names:
    # Get team scores and Elo rating
    team_scores = scores_df.loc[team].tolist()
    team_elo = elo_ratings[team]

    # Iterate through opponents
    for opp in team_names:
        # Compare scores
        wins = 0
        losses = 0
        ties = 0
        for i in range(current_week):
            # Get opponent schedule
            opp_schedule = schedules_df.loc[opp].tolist()
            # Get opponent scores
            opp_scores = [scores_df.loc[o][i] for i, o in enumerate(opp_schedule)]

            if team == opp:
                # Get team's opponent this week
                opp_team = schedules_df.loc[team, i]
                # Get team and opponent score
                team_score = scores_df.loc[team, i]
                opp_score = scores_df.loc[opp_team, i]
                if team_score > opp_score:
                    wins += 1
                elif team_score < opp_score:
                    losses += 1
                else:
                    ties += 1
            else:
                # Check if opponent is the same
                if opp == schedules_df.loc[team, i]:
                    # Opponent is the same, get correct scores
                    team_score = scores_df.loc[team, i]
                    opp_score = scores_df.loc[schedules_df.loc[team, i], i]
                else:
                    # Opponent is different
                    opp_schedule = schedules_df.loc[opp].tolist()
                    opp_scores = [scores_df.loc[o][i] for i, o in enumerate(opp_schedule)]
                    team_score = team_scores[i]
                    opp_score = opp_scores[i]
                # Compare scores
                if team_score > opp_score:
                    wins += 1
                elif team_score < opp_score:
                    losses += 1
                else:
                    ties += 1

        # Record result
        record = f"{wins}-{losses}-{ties}"
        records_df.at[team, opp] = record
        # Update the total wins DataFrame
        total_wins_df.at[team, opp] = wins
        # Calculate Elo rating adjustments
        expected_outcome = 1 / (1 + 10 ** ((elo_ratings[opp] - team_elo) / 400))
        elo_adjustment = k_factor * (wins - expected_outcome)
        elo_ratings[team] += elo_adjustment

# Rank teams by Elo ratings
ranked_teams = sorted(elo_ratings.keys(), key=lambda team: elo_ratings[team], reverse=True)

# Print ranked teams with their Elo ratings
print("Ranked Teams by Elo Ratings:")
elo_ratings_scores = []
for rank, team in enumerate(ranked_teams, start=1):
    elo_ratings_scores.append(elo_ratings[team])
    print(f"Rank {rank}: {team} | Elo Rating: {round(elo_ratings[team])} | {records_df.at[team, team]}")
# Calculate the sum of Elo ratings for all teams
sum_elo_ratings = sum(elo_ratings.values())
# avg_adjusted = (elo_ratings.values() * (12 / len(elo_ratings_scores))).round().astype(int)
# Calculate the average Elo rating
average_elo_rating = sum_elo_ratings / len(team_names)
print(average_elo_rating)
print()
# print(avg_adjusted)

# Calculate the sum of Elo ratings for each league
sum_elo_ratings_8_teams = 2300
sum_elo_ratings_10_teams = 2500
sum_elo_ratings_12_teams = 2700

# Print the sums
average_rating_8_teams = sum_elo_ratings_8_teams / 8
average_rating_10_teams = sum_elo_ratings_10_teams / 10
average_rating_12_teams = sum_elo_ratings_12_teams / 12
average_rating = sum(elo_ratings_scores) / len(elo_ratings_scores)
# Calculate scaling factors
scaling_factor_8_to_10 = average_rating_10_teams / average_rating_8_teams
scaling_factor_8_to_12 = average_rating_12_teams / average_rating_8_teams
scaling_factor = (sum(elo_ratings_scores) / len(elo_ratings_scores)) / average_rating_8_teams
# print(scaling_factor_8_to_10)
# print(scaling_factor_8_to_12)
# Normalize ratings for each league
# normalized_ratings_8_teams = [rating * scaling_factor_8_to_10 for rating in elo_ratings_8_teams]
# normalized_ratings_10_teams = elo_ratings_10_teams  # No scaling needed for the target league
# normalized_ratings_12_teams = [rating * scaling_factor_8_to_12 for rating in elo_ratings_12_teams]
normalized_ratings = [round(rating * scaling_factor) for rating in elo_ratings_scores]

print("Normalized Ratings for 8-Team League:", normalized_ratings)
print("Normalized Ratings for 8-Team League:", elo_ratings_scores)
# print("Normalized Ratings for 8-Team League:", normalized_ratings_8_teams)
# print("Normalized Ratings for 10-Team League:", normalized_ratings_10_teams)
# print("Normalized Ratings for 12-Team League:", normalized_ratings_12_teams)
print("--- %s seconds ---" % (time.time() - start_time))
