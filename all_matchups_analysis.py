import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Read the CSV file
all_matchups_df = pd.read_csv('all_matchups.csv')  # Replace with your actual file path
# pennoni_2023 = all_matchups_df[(all_matchups_df['League'] == "Pennoni Younglings") & (all_matchups_df['Year'] == 2023)]  # Filter out weeks greater than 15
# print(pennoni_2023)
# all_matchups_df = all_matchups_df[(all_matchups_df['Home Predicted Score'] > 40) & (all_matchups_df['Home Score'] != all_matchups_df['Home Predicted Score'])]  # Filter out weeks greater than 15
all_matchups_df = all_matchups_df[all_matchups_df['Home Predicted Score'] > 40]  # Filter out weeks greater than 15
# pennoni_2023 = pennoni_2023[(pennoni_2023['Home Predicted Score'] > 40) & (pennoni_2023['Home Score'] != pennoni_2023['Home Predicted Score'])]  # Filter out weeks greater than 15
# print(pennoni_2023)
# dhfg
print("Data loaded successfully!")
print(f"Shape: {all_matchups_df.shape}")
print("\nFirst few rows:")
print(all_matchups_df.head())

# Data preparation
def prepare_data(df):
    """Prepare data for analysis"""
    df = df.copy()
    
    # Create actual and predicted margin of victory
    df['Actual_MOV'] = df['Home Score'] - df['Away Score']
    df['Predicted_MOV'] = df['Home Predicted Score'] - df['Away Predicted Score']
    
    # Determine if prediction was correct
    df['Prediction_Correct'] = (df['Predicted Winner'] == df['Actual Winner'])
    
    # Create long format for team-level analysis
    home_games = df[['League', 'Year', 'Week', 'Home Team', 'Home Score', 'Home Predicted Score', 
                     'Away Team', 'Away Score', 'Away Predicted Score', 'Predicted Winner', 
                     'Actual Winner', 'Actual_MOV', 'Predicted_MOV', 'Prediction_Correct']].copy()
    home_games['Team'] = home_games['Home Team']
    home_games['Opponent'] = home_games['Away Team']
    home_games['Points_For'] = home_games['Home Score']
    home_games['Points_Against'] = home_games['Away Score']
    home_games['Predicted_Points_For'] = home_games['Home Predicted Score']
    home_games['Predicted_Points_Against'] = home_games['Away Predicted Score']
    home_games['Won'] = (home_games['Actual Winner'] == home_games['Home Team']).astype(int)
    home_games['Predicted_Win'] = (home_games['Predicted Winner'] == home_games['Home Team']).astype(int)
    home_games['Home_Away'] = 'Home'
    home_games['Team_MOV'] = home_games['Actual_MOV']
    home_games['Team_Predicted_MOV'] = home_games['Predicted_MOV']
    
    away_games = df[['League', 'Year', 'Week', 'Home Team', 'Home Score', 'Home Predicted Score', 
                     'Away Team', 'Away Score', 'Away Predicted Score', 'Predicted Winner', 
                     'Actual Winner', 'Actual_MOV', 'Predicted_MOV', 'Prediction_Correct']].copy()
    away_games['Team'] = away_games['Away Team']
    away_games['Opponent'] = away_games['Home Team']
    away_games['Points_For'] = away_games['Away Score']
    away_games['Points_Against'] = away_games['Home Score']
    away_games['Predicted_Points_For'] = away_games['Away Predicted Score']
    away_games['Predicted_Points_Against'] = away_games['Home Predicted Score']
    away_games['Won'] = (away_games['Actual Winner'] == away_games['Away Team']).astype(int)
    away_games['Predicted_Win'] = (away_games['Predicted Winner'] == away_games['Away Team']).astype(int)
    away_games['Home_Away'] = 'Away'
    away_games['Team_MOV'] = -away_games['Actual_MOV']  # Flip for away team perspective
    away_games['Team_Predicted_MOV'] = -away_games['Predicted_MOV']  # Flip for away team perspective
    
    # Combine home and away games
    team_games = pd.concat([
        home_games[['League', 'Year', 'Week', 'Team', 'Opponent', 'Points_For', 'Points_Against',
                   'Predicted_Points_For', 'Predicted_Points_Against', 'Won', 'Predicted_Win', 
                   'Home_Away', 'Team_MOV', 'Team_Predicted_MOV', 'Prediction_Correct']],
        away_games[['League', 'Year', 'Week', 'Team', 'Opponent', 'Points_For', 'Points_Against',
                   'Predicted_Points_For', 'Predicted_Points_Against', 'Won', 'Predicted_Win', 
                   'Home_Away', 'Team_MOV', 'Team_Predicted_MOV', 'Prediction_Correct']]
    ]).reset_index(drop=True)
    
    return df, team_games

# Prepare the data
matchups_df, team_games_df = prepare_data(all_matchups_df)

def analyze_luck(team_games_df):
    """Analyze team luck based on actual vs predicted performance"""
    
    team_stats = team_games_df.groupby(['League', 'Year', 'Team']).agg({
        'Won': 'sum',
        'Predicted_Win': 'sum',
        'Points_For': ['sum', 'mean'],
        'Points_Against': ['sum', 'mean'],
        'Predicted_Points_For': ['sum', 'mean'],
        'Predicted_Points_Against': ['sum', 'mean'],
        'Team_MOV': ['sum', 'mean', 'std'],
        'Team_Predicted_MOV': ['sum', 'mean', 'std'],
        'Week': 'count'
    }).round(2)
    
    # Flatten column names
    team_stats.columns = ['_'.join(col).strip() for col in team_stats.columns]
    team_stats = team_stats.reset_index()
    
    # Calculate luck metrics
    team_stats['Actual_Wins'] = team_stats['Won_sum']
    team_stats['Predicted_Wins'] = team_stats['Predicted_Win_sum']
    team_stats['Games_Played'] = team_stats['Week_count']
    team_stats['Win_Difference'] = team_stats['Actual_Wins'] - team_stats['Predicted_Wins']
    team_stats['Win_Pct'] = (team_stats['Actual_Wins'] / team_stats['Games_Played']).round(3)
    team_stats['Predicted_Win_Pct'] = (team_stats['Predicted_Wins'] / team_stats['Games_Played']).round(3)
    team_stats['Luck_Factor'] = team_stats['Win_Pct'] - team_stats['Predicted_Win_Pct']
    
    # Points luck
    team_stats['Points_Luck'] = team_stats['Points_For_sum'] - team_stats['Predicted_Points_For_sum']
    team_stats['Defense_Luck'] = team_stats['Predicted_Points_Against_sum'] - team_stats['Points_Against_sum']
    team_stats['Total_Point_Luck'] = team_stats['Points_Luck'] + team_stats['Defense_Luck']
    
    # MOV analysis
    team_stats['Actual_Total_MOV'] = team_stats['Team_MOV_sum']
    team_stats['Predicted_Total_MOV'] = team_stats['Team_Predicted_MOV_sum']
    team_stats['MOV_Difference'] = team_stats['Actual_Total_MOV'] - team_stats['Predicted_Total_MOV']
    
    return team_stats

def find_crazy_weeks(matchups_df):
    """Find the craziest weeks based on various metrics"""
    
    week_stats = matchups_df.groupby(['League', 'Year', 'Week']).agg({
        'Home Score': ['sum', 'mean', 'std', 'max', 'min'],
        'Away Score': ['sum', 'mean', 'std', 'max', 'min'],
        'Actual_MOV': ['mean', 'std', 'max', 'min'],
        'Predicted_MOV': ['mean', 'std'],
        'Prediction_Correct': ['sum', 'mean', 'count']
    }).round(2)
    
    week_stats.columns = ['_'.join(col).strip() for col in week_stats.columns]
    week_stats = week_stats.reset_index()
    
    # Calculate craziness metrics
    week_stats['Total_Points'] = week_stats['Home Score_sum'] + week_stats['Away Score_sum']
    week_stats['Avg_Points_Per_Team'] = week_stats['Total_Points'] / (week_stats['Prediction_Correct_count'] * 2)
    week_stats['Score_Variance'] = ((week_stats['Home Score_std']**2 + week_stats['Away Score_std']**2) / 2) ** 0.5
    week_stats['Blowout_Factor'] = week_stats['Actual_MOV_std']
    week_stats['Upset_Rate'] = 1 - week_stats['Prediction_Correct_mean']
    week_stats['Games_Count'] = week_stats['Prediction_Correct_count']
    
    # Highest scoring weeks
    highest_scoring = week_stats.nlargest(10, 'Total_Points')[['League', 'Year', 'Week', 'Total_Points', 'Avg_Points_Per_Team', 'Games_Count']]
    
    # Most unpredictable weeks (highest upset rate)
    most_unpredictable = week_stats.nlargest(10, 'Upset_Rate')[['League', 'Year', 'Week', 'Upset_Rate', 'Games_Count']]
    
    # Biggest blowout weeks
    biggest_blowouts = week_stats.nlargest(10, 'Blowout_Factor')[['League', 'Year', 'Week', 'Blowout_Factor', 'Actual_MOV_max', 'Actual_MOV_min']]
    
    # Most chaotic weeks (high variance in scores)
    most_chaotic = week_stats.nlargest(10, 'Score_Variance')[['League', 'Year', 'Week', 'Score_Variance', 'Total_Points']]
    
    return {
        'highest_scoring': highest_scoring,
        'most_unpredictable': most_unpredictable,
        'biggest_blowouts': biggest_blowouts,
        'most_chaotic': most_chaotic,
        'all_weeks': week_stats
    }

def analyze_schedule_strength(team_games_df):
    """Analyze schedule strength based on opponent predicted scores"""
    
    # Calculate opponent strength metrics
    schedule_stats = team_games_df.groupby(['League', 'Year', 'Team']).agg({
        'Predicted_Points_Against': ['mean', 'sum'],  # Opponent predicted strength
        'Points_Against': ['mean', 'sum'],           # Actual opponent performance
        'Opponent': 'count',                         # Games played
        'Won': 'sum',                               # Actual wins
        'Predicted_Win': 'sum'                      # Predicted wins
    }).round(2)
    
    schedule_stats.columns = ['_'.join(col).strip() for col in schedule_stats.columns]
    schedule_stats = schedule_stats.reset_index()
    
    # Calculate schedule strength metrics
    schedule_stats['Games_Played'] = schedule_stats['Opponent_count']
    schedule_stats['Avg_Opponent_Predicted_Score'] = schedule_stats['Predicted_Points_Against_mean']
    schedule_stats['Total_Opponent_Predicted_Score'] = schedule_stats['Predicted_Points_Against_sum']
    schedule_stats['Avg_Opponent_Actual_Score'] = schedule_stats['Points_Against_mean']
    schedule_stats['Total_Opponent_Actual_Score'] = schedule_stats['Points_Against_sum']
    
    # Schedule difficulty based on predictions
    schedule_stats['Predicted_Schedule_Difficulty'] = schedule_stats['Avg_Opponent_Predicted_Score']
    
    # How much harder/easier was the actual schedule vs predicted
    schedule_stats['Schedule_Variance'] = schedule_stats['Avg_Opponent_Actual_Score'] - schedule_stats['Avg_Opponent_Predicted_Score']
    
    # Performance vs schedule strength
    schedule_stats['Actual_Wins'] = schedule_stats['Won_sum']
    schedule_stats['Predicted_Wins'] = schedule_stats['Predicted_Win_sum']
    schedule_stats['Win_Rate'] = schedule_stats['Actual_Wins'] / schedule_stats['Games_Played']
    schedule_stats['Expected_Win_Rate'] = schedule_stats['Predicted_Wins'] / schedule_stats['Games_Played']
    
    return schedule_stats

def analyze_opponent_strength_by_team(team_games_df):
    """Get detailed opponent analysis for each team"""
    
    # First, calculate each team's average predicted score as a measure of their strength
    team_strength = team_games_df.groupby(['League', 'Year', 'Team'])['Predicted_Points_For'].mean().reset_index()
    team_strength.columns = ['League', 'Year', 'Team', 'Team_Strength']
    
    # Merge this back to get opponent strengths
    opponent_data = team_games_df.merge(
        team_strength.rename(columns={'Team': 'Opponent', 'Team_Strength': 'Opponent_Strength'}),
        on=['League', 'Year', 'Opponent'],
        how='left'
    )
    
    # Calculate schedule metrics
    schedule_analysis = opponent_data.groupby(['League', 'Year', 'Team']).agg({
        'Opponent_Strength': ['mean', 'std', 'count'],
        'Won': 'sum',
        'Points_For': 'mean',
        'Predicted_Points_For': 'mean'
    }).round(2)
    
    schedule_analysis.columns = ['_'.join(col).strip() for col in schedule_analysis.columns]
    schedule_analysis = schedule_analysis.reset_index()
    
    schedule_analysis['Games_Played'] = schedule_analysis['Opponent_Strength_count']
    schedule_analysis['Avg_Opponent_Strength'] = schedule_analysis['Opponent_Strength_mean']
    schedule_analysis['Opponent_Strength_Variance'] = schedule_analysis['Opponent_Strength_std']
    schedule_analysis['Actual_Wins'] = schedule_analysis['Won_sum']
    
    return schedule_analysis
    """Analyze seasons for craziness and patterns"""
    
    season_stats = team_games_df.groupby(['League', 'Year']).agg({
        'Points_For': ['sum', 'mean', 'std'],
        'Won': 'sum',
        'Predicted_Win': 'sum',
        'Team_MOV': ['mean', 'std'],
        'Week': 'count'
    }).round(2)
    
    season_stats.columns = ['_'.join(col).strip() for col in season_stats.columns]
    season_stats = season_stats.reset_index()
    
    # Season-level metrics
    season_stats['Total_Games'] = season_stats['Week_count']
    season_stats['Avg_Points_Per_Game'] = season_stats['Points_For_sum'] / season_stats['Total_Games']
    season_stats['Score_Consistency'] = 1 / (season_stats['Points_For_std'] + 1)  # Higher = more consistent
    season_stats['Competitive_Balance'] = 1 / (season_stats['Team_MOV_std'] + 1)  # Higher = more balanced
    
    return season_stats

# Run all analyses
print("\n" + "="*50)
print("RUNNING COMPREHENSIVE FANTASY FOOTBALL ANALYSIS")
print("="*50)

# Team luck analysis
print("\n📊 Analyzing Team Luck...")
team_luck = analyze_luck(team_games_df)

# Filter teams with sufficient games (at least 8 games for meaningful luck analysis)
team_luck_filtered = team_luck[team_luck['Games_Played'] >= 8].copy()

print(f"Total teams analyzed: {len(team_luck)}")
print(f"Teams with 8+ games: {len(team_luck_filtered)}")

# Sort by luck factor (filtered for teams with enough games)
luckiest_teams = team_luck_filtered.nlargest(10, 'Luck_Factor')[['League', 'Year', 'Team', 'Actual_Wins', 'Predicted_Wins', 'Win_Difference', 'Luck_Factor', 'Games_Played']]
unluckiest_teams = team_luck_filtered.nsmallest(10, 'Luck_Factor')[['League', 'Year', 'Team', 'Actual_Wins', 'Predicted_Wins', 'Win_Difference', 'Luck_Factor', 'Games_Played']]

print("\n🍀 TOP 10 LUCKIEST TEAMS:")
print("="*40)
print(luckiest_teams.to_string(index=False))

print("\n😩 TOP 10 UNLUCKIEST TEAMS:")
print("="*40)
print(unluckiest_teams.to_string(index=False))

# Point luck analysis (also filter for sufficient games)
best_point_luck = team_luck_filtered.nlargest(10, 'Total_Point_Luck')[['League', 'Year', 'Team', 'Points_Luck', 'Defense_Luck', 'Total_Point_Luck', 'Games_Played']]
worst_point_luck = team_luck_filtered.nsmallest(10, 'Total_Point_Luck')[['League', 'Year', 'Team', 'Points_Luck', 'Defense_Luck', 'Total_Point_Luck', 'Games_Played']]

print("\n🛡️ DEFENSE LUCK EXPLANATION:")
print("="*50)
print("Defense Luck = Predicted Points Against - Actual Points Against")
print("Positive Defense Luck = Opponents scored LESS than predicted (good luck)")
print("Negative Defense Luck = Opponents scored MORE than predicted (bad luck)")
print("="*50)

print("\n📈 BIGGEST OVERPERFORMERS (Scored more than predicted):")
print("="*50)
print(best_point_luck.to_string(index=False))

print("\n📉 BIGGEST UNDERPERFORMERS (Scored less than predicted):")
print("="*50)
print(worst_point_luck.to_string(index=False))

# Margin of Victory analysis (also filter for sufficient games)
best_mov_luck = team_luck_filtered.nlargest(10, 'MOV_Difference')[['League', 'Year', 'Team', 'Actual_Total_MOV', 'Predicted_Total_MOV', 'MOV_Difference', 'Games_Played']]
worst_mov_luck = team_luck_filtered.nsmallest(10, 'MOV_Difference')[['League', 'Year', 'Team', 'Actual_Total_MOV', 'Predicted_Total_MOV', 'MOV_Difference', 'Games_Played']]

print("\n💪 BEST MARGIN OF VICTORY LUCK:")
print("="*40)
print(best_mov_luck.to_string(index=False))

print("\n💔 WORST MARGIN OF VICTORY LUCK:")
print("="*40)
print(worst_mov_luck.to_string(index=False))

# Schedule Strength Analysis
print("\n💪 Analyzing Schedule Strength...")
schedule_strength = analyze_schedule_strength(team_games_df)
opponent_strength_analysis = analyze_opponent_strength_by_team(team_games_df)

# Filter for teams with sufficient games
schedule_filtered = schedule_strength[schedule_strength['Games_Played'] >= 8].copy()
opponent_filtered = opponent_strength_analysis[opponent_strength_analysis['Games_Played'] >= 8].copy()

# Toughest schedules (highest average opponent predicted scores)
toughest_schedules = schedule_filtered.nlargest(10, 'Predicted_Schedule_Difficulty')[
    ['League', 'Year', 'Team', 'Predicted_Schedule_Difficulty', 'Avg_Opponent_Actual_Score', 
     'Schedule_Variance', 'Win_Rate', 'Games_Played']
].sort_values('Predicted_Schedule_Difficulty', ascending=False)

# Easiest schedules (lowest average opponent predicted scores)  
easiest_schedules = schedule_filtered.nsmallest(10, 'Predicted_Schedule_Difficulty')[
    ['League', 'Year', 'Team', 'Predicted_Schedule_Difficulty', 'Avg_Opponent_Actual_Score', 
     'Schedule_Variance', 'Win_Rate', 'Games_Played']
].sort_values('Predicted_Schedule_Difficulty', ascending=True)

# Alternative method using opponent team strength
toughest_by_strength = opponent_filtered.nlargest(10, 'Avg_Opponent_Strength')[
    ['League', 'Year', 'Team', 'Avg_Opponent_Strength', 'Opponent_Strength_Variance', 
     'Actual_Wins', 'Games_Played']
].sort_values('Avg_Opponent_Strength', ascending=False)

easiest_by_strength = opponent_filtered.nsmallest(10, 'Avg_Opponent_Strength')[
    ['League', 'Year', 'Team', 'Avg_Opponent_Strength', 'Opponent_Strength_Variance', 
     'Actual_Wins', 'Games_Played']
].sort_values('Avg_Opponent_Strength', ascending=True)

print("\n⚔️ TOUGHEST SCHEDULES (Based on Opponent Predicted Scores):")
print("="*55)
print(toughest_schedules.to_string(index=False))

print("\n😌 EASIEST SCHEDULES (Based on Opponent Predicted Scores):")
print("="*54)
print(easiest_schedules.to_string(index=False))

print("\n🔥 TOUGHEST SCHEDULES (Based on Opponent Team Strength):")
print("="*52)
print(toughest_by_strength.to_string(index=False))

print("\n🎯 EASIEST SCHEDULES (Based on Opponent Team Strength):")
print("="*51)
print(easiest_by_strength.to_string(index=False))

# Teams that had schedules turn out harder/easier than expected
schedule_surprises_harder = schedule_filtered.nlargest(10, 'Schedule_Variance')[
    ['League', 'Year', 'Team', 'Predicted_Schedule_Difficulty', 'Avg_Opponent_Actual_Score', 
     'Schedule_Variance', 'Win_Rate']
]

schedule_surprises_easier = schedule_filtered.nsmallest(10, 'Schedule_Variance')[
    ['League', 'Year', 'Team', 'Predicted_Schedule_Difficulty', 'Avg_Opponent_Actual_Score', 
     'Schedule_Variance', 'Win_Rate']
]

print("\n📈 SCHEDULES THAT GOT HARDER THAN EXPECTED:")
print("="*44)
print("(Opponents scored more than their predictions)")
print(schedule_surprises_harder.to_string(index=False))

print("\n📉 SCHEDULES THAT GOT EASIER THAN EXPECTED:")
print("="*45)
print("(Opponents scored less than their predictions)")
print(schedule_surprises_easier.to_string(index=False))

# Weekly analysis
print("\n🎢 Analyzing Crazy Weeks...")
crazy_weeks = find_crazy_weeks(matchups_df)

print("\n🔥 HIGHEST SCORING WEEKS:")
print("="*30)
print(crazy_weeks['highest_scoring'].to_string(index=False))

print("\n😱 MOST UNPREDICTABLE WEEKS (Most Upsets):")
print("="*45)
print(crazy_weeks['most_unpredictable'].to_string(index=False))

print("\n💥 BIGGEST BLOWOUT WEEKS:")
print("="*25)
print(crazy_weeks['biggest_blowouts'].to_string(index=False))

print("\n🌪️ MOST CHAOTIC WEEKS (Score Variance):")
print("="*35)
print(crazy_weeks['most_chaotic'].to_string(index=False))

# Season analysis
print("\n📅 Analyzing Seasons...")
def analyze_seasons(team_games_df):
    """Analyze seasons for craziness and patterns"""
    
    season_stats = team_games_df.groupby(['League', 'Year']).agg({
        'Points_For': ['sum', 'mean', 'std'],
        'Won': 'sum',
        'Predicted_Win': 'sum',
        'Team_MOV': ['mean', 'std'],
        'Week': 'count'
    }).round(2)
    
    season_stats.columns = ['_'.join(col).strip() for col in season_stats.columns]
    season_stats = season_stats.reset_index()
    
    # Season-level metrics
    season_stats['Total_Games'] = season_stats['Week_count']
    season_stats['Avg_Points_Per_Game'] = season_stats['Points_For_sum'] / season_stats['Total_Games']
    season_stats['Score_Consistency'] = 1 / (season_stats['Points_For_std'] + 1)  # Higher = more consistent
    season_stats['Competitive_Balance'] = 1 / (season_stats['Team_MOV_std'] + 1)  # Higher = more balanced
    
    return season_stats
season_analysis = analyze_seasons(team_games_df)

# Most competitive seasons
most_competitive = season_analysis.nlargest(5, 'Competitive_Balance')[['League', 'Year', 'Competitive_Balance', 'Avg_Points_Per_Game']]
print("\n⚖️ MOST COMPETITIVE SEASONS:")
print("="*30)
print(most_competitive.to_string(index=False))

# Highest scoring seasons
highest_scoring_seasons = season_analysis.nlargest(5, 'Avg_Points_Per_Game')[['League', 'Year', 'Avg_Points_Per_Game', 'Points_For_std']]
print("\n🚀 HIGHEST SCORING SEASONS:")
print("="*27)
print(highest_scoring_seasons.to_string(index=False))

# Additional insights
print("\n" + "="*50)
print("ADDITIONAL INSIGHTS")
print("="*50)

# Overall prediction accuracy
overall_accuracy = matchups_df['Prediction_Correct'].mean()
print(f"\n🎯 Overall Prediction Accuracy: {overall_accuracy:.1%}")

print(matchups_df)
asfd

# Teams that consistently outperform predictions (filter for multiple seasons and sufficient games)
team_luck_multi_season = team_luck_filtered.copy()
consistent_overperformers = team_luck_multi_season[team_luck_multi_season['Luck_Factor'] > 0].groupby('Team').agg({
    'Luck_Factor': ['count', 'mean'],
    'League': 'first',
    'Year': lambda x: ', '.join(map(str, sorted(x)))
}).round(3)

consistent_overperformers.columns = ['Seasons', 'Avg_Luck_Factor', 'League', 'Years']
consistent_overperformers = consistent_overperformers[consistent_overperformers['Seasons'] >= 1].sort_values('Avg_Luck_Factor', ascending=False).head(10).reset_index()

print("\n⭐ MOST CONSISTENT OVERPERFORMERS:")
print("="*35)
print(consistent_overperformers.to_string(index=False))

# Teams that consistently underperform predictions (filter for multiple seasons and sufficient games)
consistent_underperformers = team_luck_multi_season[team_luck_multi_season['Luck_Factor'] < 0].groupby('Team').agg({
    'Luck_Factor': ['count', 'mean'],
    'League': 'first',
    'Year': lambda x: ', '.join(map(str, sorted(x)))
}).round(3)

consistent_underperformers.columns = ['Seasons', 'Avg_Luck_Factor', 'League', 'Years']
consistent_underperformers = consistent_underperformers[consistent_underperformers['Seasons'] >= 1].sort_values('Avg_Luck_Factor').head(10).reset_index()

print("\n😔 MOST CONSISTENT UNDERPERFORMERS:")
print("="*37)
print(consistent_underperformers.to_string(index=False))

# Biggest single-game upsets (where predicted loser won by a lot)
matchups_df['Upset_Magnitude'] = np.where(
    matchups_df['Prediction_Correct'] == False,
    abs(matchups_df['Actual_MOV']),
    0
)
biggest_upsets = matchups_df.nlargest(10, 'Upset_Magnitude')[['League', 'Year', 'Week', 'Home Team', 'Away Team', 'Predicted Winner', 'Actual Winner', 'Actual_MOV', 'Upset_Magnitude']]
print("\n🎊 BIGGEST SINGLE-GAME UPSETS:")
print("="*32)
print(biggest_upsets.to_string(index=False))

print("\n" + "="*50)
print("ANALYSIS COMPLETE! 🏆")
print("="*50)