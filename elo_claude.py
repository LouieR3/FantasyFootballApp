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
league = League(league_id=310334683, year=2024, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1118513122, year=2021, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Pennoni Transportation
# league = League(league_id=1339704102, year=2022, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')

# Prahlad Friends League
# league = League(league_id=1781851, year=2022, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')
league = League(league_id=1049459, year=2024, espn_s2='AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D', swid='{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}')

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
print(current_week)
# current_week -= 1
# Store data in DataFrames 
scores_df = pd.DataFrame(team_scores, index=team_names)
print(scores_df)
schedules_df = pd.DataFrame(schedules, index=team_names)
print(schedules_df)

# Create empty dataframe  
records_df = pd.DataFrame(index=team_names, columns=team_names)

# Fill diagonal with team names
records_df.fillna('', inplace=True) 
print(records_df)

def calculate_elo_ratings(scores_df, schedules_df, current_week, k_factor=32, initial_elo=1500):
    """
    Calculate ELO ratings for fantasy football teams based on weekly matchups
    
    Parameters:
    - scores_df: DataFrame with team scores for each week
    - schedules_df: DataFrame with team schedules (opponents for each week)
    - current_week: Current week number (completed weeks)
    - k_factor: ELO K-factor (higher = more rating change per game)
    - initial_elo: Starting ELO rating for all teams
    
    Returns:
    - elo_history: DataFrame with ELO ratings after each week
    - final_rankings: DataFrame with final ELO rankings and stats
    """
    
    # Initialize ELO ratings
    teams = scores_df.index.tolist()
    elo_ratings = {team: initial_elo for team in teams}
    elo_history = pd.DataFrame(index=teams)
    elo_history[0] = initial_elo  # Starting ratings
    
    # Track additional stats
    team_stats = {team: {'wins': 0, 'losses': 0, 'points_for': 0, 'points_against': 0} 
                  for team in teams}
    
    # Process each completed week
    for week in range(current_week):
        week_results = []
        
        # Get all matchups for this week
        for team in teams:
            if week < len(schedules_df.columns):
                opponent = schedules_df.iloc[schedules_df.index.get_loc(team), week]
                team_score = scores_df.iloc[scores_df.index.get_loc(team), week]
                opponent_score = scores_df.iloc[scores_df.index.get_loc(opponent), week]
                
                # Store matchup info (avoid duplicates by only processing when team < opponent alphabetically)
                if team < opponent:
                    week_results.append({
                        'team1': team,
                        'team2': opponent,
                        'score1': team_score,
                        'score2': opponent_score
                    })
        
        # Calculate ELO changes for this week
        for matchup in week_results:
            team1, team2 = matchup['team1'], matchup['team2']
            score1, score2 = matchup['score1'], matchup['score2']
            
            # Current ELO ratings
            elo1 = elo_ratings[team1]
            elo2 = elo_ratings[team2]
            
            # Expected scores (probability of winning)
            expected1 = 1 / (1 + 10**((elo2 - elo1) / 400))
            expected2 = 1 / (1 + 10**((elo1 - elo2) / 400))
            
            # Actual results (1 for win, 0 for loss)
            if score1 > score2:
                actual1, actual2 = 1, 0
                team_stats[team1]['wins'] += 1
                team_stats[team2]['losses'] += 1
            elif score2 > score1:
                actual1, actual2 = 0, 1
                team_stats[team2]['wins'] += 1
                team_stats[team1]['losses'] += 1
            else:  # Tie (rare in fantasy)
                actual1, actual2 = 0.5, 0.5
            
            # Update stats
            team_stats[team1]['points_for'] += score1
            team_stats[team1]['points_against'] += score2
            team_stats[team2]['points_for'] += score2
            team_stats[team2]['points_against'] += score1
            
            # Calculate new ELO ratings
            new_elo1 = elo1 + k_factor * (actual1 - expected1)
            new_elo2 = elo2 + k_factor * (actual2 - expected2)
            
            # Update ELO ratings
            elo_ratings[team1] = new_elo1
            elo_ratings[team2] = new_elo2
        
        # Store ELO ratings after this week
        elo_history[week + 1] = [elo_ratings[team] for team in teams]
    
    # Create final rankings DataFrame
    final_rankings = pd.DataFrame({
        'Team': teams,
        'Final_ELO': [elo_ratings[team] for team in teams],
        'ELO_Change': [elo_ratings[team] - initial_elo for team in teams],
        'Wins': [team_stats[team]['wins'] for team in teams],
        'Losses': [team_stats[team]['losses'] for team in teams],
        'Win_Pct': [team_stats[team]['wins'] / (team_stats[team]['wins'] + team_stats[team]['losses']) 
                   if (team_stats[team]['wins'] + team_stats[team]['losses']) > 0 else 0 
                   for team in teams],
        'Points_For': [team_stats[team]['points_for'] for team in teams],
        'Points_Against': [team_stats[team]['points_against'] for team in teams],
        'Point_Diff': [team_stats[team]['points_for'] - team_stats[team]['points_against'] for team in teams]
    })
    
    # Sort by ELO rating (highest first)
    final_rankings = final_rankings.sort_values('Final_ELO', ascending=False).reset_index(drop=True)
    final_rankings['Rank'] = range(1, len(final_rankings) + 1)
    
    return elo_history, final_rankings

def print_elo_results(elo_history, final_rankings, league_name="Fantasy League"):
    """Print formatted ELO results"""
    
    print("="*80)
    print(f"ELO RATINGS ANALYSIS - {league_name}")
    print("="*80)
    
    print("\nFINAL ELO RANKINGS:")
    print("-" * 100)
    print(f"{'Rank':<4} {'Team':<30} {'ELO':<8} {'Change':<8} {'W-L':<8} {'Win%':<8} {'PF':<8} {'PA':<8} {'Diff':<8}")
    print("-" * 100)
    
    for _, row in final_rankings.iterrows():
        win_loss = f"{int(row['Wins'])}-{int(row['Losses'])}"
        win_pct = f"{row['Win_Pct']:.3f}"
        elo_change = f"{row['ELO_Change']:+.1f}"
        
        print(f"{row['Rank']:<4} {row['Team']:<30} {row['Final_ELO']:<8.1f} {elo_change:<8} {win_loss:<8} {win_pct:<8} {row['Points_For']:<8.1f} {row['Points_Against']:<8.1f} {row['Point_Diff']:<8.1f}")
    
    print("\nELO RATING PROGRESSION:")
    print("-" * 60)
    print("(Showing final 5 weeks)")
    
    # Show last 5 weeks of ELO progression
    recent_weeks = min(5, len(elo_history.columns) - 1)
    start_week = max(0, len(elo_history.columns) - recent_weeks - 1)
    
    week_cols = list(elo_history.columns)[start_week:]
    recent_elo = elo_history[week_cols].copy()
    
    # Sort by final ELO for display
    final_order = final_rankings['Team'].tolist()
    recent_elo_sorted = recent_elo.loc[final_order]
    
    print(f"{'Team':<30}", end="")
    for week in week_cols:
        if week == 0:
            print(f"{'Start':<8}", end="")
        else:
            print(f"{'Wk'+str(week):<8}", end="")
    print()
    
    print("-" * (30 + 8 * len(week_cols)))
    
    for team in final_order[:10]:  # Show top 10 teams
        print(f"{team:<30}", end="")
        for week in week_cols:
            elo_val = recent_elo_sorted.loc[team, week]
            print(f"{elo_val:<8.0f}", end="")
        print()
    
    # Statistical insights
    print("\nSTATISTICAL INSIGHTS:")
    print("-" * 40)
    
    highest_elo = final_rankings.iloc[0]
    lowest_elo = final_rankings.iloc[-1]
    biggest_riser = final_rankings.loc[final_rankings['ELO_Change'].idxmax()]
    biggest_faller = final_rankings.loc[final_rankings['ELO_Change'].idxmin()]
    
    print(f"Highest ELO: {highest_elo['Team']} ({highest_elo['Final_ELO']:.1f})")
    print(f"Lowest ELO:  {lowest_elo['Team']} ({lowest_elo['Final_ELO']:.1f})")
    print(f"Biggest Rise: {biggest_riser['Team']} ({biggest_riser['ELO_Change']:+.1f})")
    print(f"Biggest Fall: {biggest_faller['Team']} ({biggest_faller['ELO_Change']:+.1f})")
    
    # ELO vs Record correlation
    correlation = final_rankings['Final_ELO'].corr(final_rankings['Win_Pct'])
    print(f"ELO-Record Correlation: {correlation:.3f}")
    print()

# Calculate ELO ratings
print("Calculating ELO ratings...")
elo_history, final_rankings = calculate_elo_ratings(scores_df, schedules_df, current_week)

# Print results
print_elo_results(elo_history, final_rankings, leagueName)

# Optional: Save results to Excel if you want
# final_rankings.to_excel(f"{leagueName}_ELO_Rankings.xlsx", index=False)
# elo_history.to_excel(f"{leagueName}_ELO_History.xlsx")

print(f"\nProcessing completed in {time.time() - start_time:.2f} seconds")