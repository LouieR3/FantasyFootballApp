import pandas as pd
import numpy as np
from collections import defaultdict

def calculate_playoff_chances_by_week(teams, scores_df, reg_season_count, num_playoff_teams, current_week, num_simulations=1000):
    """
    Calculate each team's playoff chances week by week from week 1 to current week.
    
    Args:
        teams: List of team objects from ESPN API
        scores_df: DataFrame of team scores
        reg_season_count: Number of regular season games
        num_playoff_teams: Number of teams that make playoffs
        current_week: Current week number
        num_simulations: Number of Monte Carlo simulations per week
    
    Returns:
        pd.DataFrame: DataFrame with teams as index and weeks as columns showing playoff %
    """
    
    # Initialize results dictionary
    weekly_playoff_chances = defaultdict(dict)
    
    # Calculate for each week from 1 to current_week
    for week in range(1, current_week + 1):
        print(f"Calculating playoff odds for week {week}...")
        
        # Calculate team stats up to this week
        team_stats = calculate_team_stats_for_week(teams, scores_df, week, reg_season_count)
        
        # Run simulation from this week forward
        playoff_makes = simulate_from_week(
            teams, team_stats, week, reg_season_count, num_playoff_teams, num_simulations
        )
        
        # Calculate playoff percentage for each team
        for team_name in team_stats.keys():
            playoff_pct = (playoff_makes[team_name] / num_simulations) * 100
            weekly_playoff_chances[team_name][f'Week_{week}'] = playoff_pct
    
    # Convert to DataFrame
    playoff_df = pd.DataFrame(weekly_playoff_chances).T
    
    # Sort by current week's playoff chances
    last_week_col = f'Week_{current_week}'
    playoff_df = playoff_df.sort_values(last_week_col, ascending=False)
    
    return playoff_df


def calculate_team_stats_for_week(teams, scores_df, through_week, reg_season_count):
    """Calculate team stats through a specific week"""
    team_stats = {}
    
    # Determine how many regular season games have been completed through this week
    completed_reg_games = min(through_week, reg_season_count)
    
    for team_idx, team in enumerate(teams):
        # Only use regular season scores through this week
        reg_season_scores = [score for score in scores_df.iloc[team_idx, :completed_reg_games] if score > 0]
        
        # Calculate regular season record including ties
        reg_season_outcomes = team.outcomes[:completed_reg_games]
        wins = sum(1 for outcome in reg_season_outcomes if outcome == 'W')
        losses = sum(1 for outcome in reg_season_outcomes if outcome == 'L')
        ties = sum(1 for outcome in reg_season_outcomes if outcome == 'T')
        
        # Scoring statistics
        avg_score = np.mean(reg_season_scores) if reg_season_scores else 100.0
        score_std = np.std(reg_season_scores) if len(reg_season_scores) > 1 else 15.0
        
        # Adjust std dev based on sample size
        games_played = len(reg_season_scores)
        confidence_factor = max(0.5, 1 - (games_played / 40))
        adjusted_std = score_std * (1 + confidence_factor)
        
        team_stats[team.team_name] = {
            'team_obj': team,
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'avg_score': avg_score,
            'score_std': adjusted_std,
            'games_played': games_played,
            'total_points': sum(reg_season_scores)
        }
    
    return team_stats


def simulate_from_week(teams, team_stats, start_week, reg_season_count, num_playoff_teams, num_simulations):
    """Simulate remaining season from a specific week forward"""
    
    playoff_makes = defaultdict(int)
    remaining_reg_games = max(0, reg_season_count - (start_week - 1))
    
    # If regular season is complete, determine actual playoff teams
    if remaining_reg_games == 0:
        # Season is complete, determine final standings
        teams_with_records = []
        for team_name, stats in team_stats.items():
            total_games = stats['wins'] + stats['losses'] + stats['ties']
            win_pct = (stats['wins'] + 0.5 * stats['ties']) / total_games if total_games > 0 else 0
            
            teams_with_records.append({
                'team': team_name,
                'wins': stats['wins'],
                'losses': stats['losses'],
                'ties': stats['ties'],
                'points_for': stats['total_points'],
                'win_pct': win_pct
            })
        
        # Sort by wins + ties, then points
        teams_with_records.sort(key=lambda x: (x['wins'] + 0.5 * x['ties'], x['points_for']), reverse=True)
        
        # Award playoff spots - no simulation needed
        for idx, team_data in enumerate(teams_with_records):
            seed = idx + 1
            if seed <= num_playoff_teams:
                playoff_makes[team_data['team']] = num_simulations  # 100%
            else:
                playoff_makes[team_data['team']] = 0  # 0%
        
        return playoff_makes
    
    for sim in range(num_simulations):
        # Initialize records
        sim_records = {}
        for team_name, stats in team_stats.items():
            sim_records[team_name] = {
                'wins': stats['wins'], 
                'losses': stats['losses'],
                'ties': stats['ties'],
                'points_for': stats['total_points']
            }
        
        # Simulate remaining regular season games
        for week in range(start_week, min(start_week + remaining_reg_games, reg_season_count + 1)):
            week_matchups = []
            used_teams = set()
            
            # Create matchups for this week
            for team_idx, team in enumerate(teams):
                if team.team_name in used_teams:
                    continue
                    
                if week - 1 < len(team.schedule):
                    opponent = team.schedule[week - 1]
                    if opponent.team_name not in used_teams:
                        week_matchups.append((team.team_name, opponent.team_name))
                        used_teams.add(team.team_name)
                        used_teams.add(opponent.team_name)
            
            # Simulate each matchup
            for team1_name, team2_name in week_matchups:
                team1_stats = team_stats[team1_name]
                team2_stats = team_stats[team2_name]
                
                # Generate random scores
                team1_score = max(0, np.random.normal(team1_stats['avg_score'], team1_stats['score_std']))
                team2_score = max(0, np.random.normal(team2_stats['avg_score'], team2_stats['score_std']))
                
                # Determine winner or tie
                if abs(team1_score - team2_score) < 0.5:
                    sim_records[team1_name]['ties'] += 1
                    sim_records[team2_name]['ties'] += 1
                elif team1_score > team2_score:
                    sim_records[team1_name]['wins'] += 1
                    sim_records[team2_name]['losses'] += 1
                else:
                    sim_records[team2_name]['wins'] += 1
                    sim_records[team1_name]['losses'] += 1
                
                # Update points
                sim_records[team1_name]['points_for'] += team1_score
                sim_records[team2_name]['points_for'] += team2_score
        
        # Determine standings
        teams_with_records = []
        for team_name, record in sim_records.items():
            total_games = record['wins'] + record['losses'] + record['ties']
            win_pct = (record['wins'] + 0.5 * record['ties']) / total_games if total_games > 0 else 0
            
            teams_with_records.append({
                'team': team_name,
                'wins': record['wins'],
                'losses': record['losses'],
                'ties': record['ties'],
                'points_for': record['points_for'],
                'win_pct': win_pct
            })
        
        # Sort by wins + ties, then points
        teams_with_records.sort(key=lambda x: (x['wins'] + 0.5 * x['ties'], x['points_for']), reverse=True)
        
        # Count playoff makes
        for idx, team_data in enumerate(teams_with_records):
            seed = idx + 1
            if seed <= num_playoff_teams:
                playoff_makes[team_data['team']] += 1
    
    return playoff_makes


# Example usage function to integrate with existing code
def add_weekly_analysis_to_main(teams, scores_df, reg_season_count, num_playoff_teams, current_week):
    """
    Function to add to your main script to show weekly playoff progression
    """
    print("\n" + "="*80)
    print("PLAYOFF CHANCES BY WEEK")
    print("="*80)
    
    # Calculate weekly playoff chances
    weekly_df = calculate_playoff_chances_by_week(
        teams, scores_df, reg_season_count, num_playoff_teams, current_week, num_simulations=1000
    )
    
    # Display results
    print("\nPlayoff Chances (%) by Week:")
    print(weekly_df.round(1).to_string())
    
    # Optional: Show change from previous week
    print("\n" + "="*80)
    print("WEEK-OVER-WEEK CHANGE IN PLAYOFF ODDS")
    print("="*80)
    
    change_df = weekly_df.copy()
    for i in range(2, current_week + 1):
        prev_col = f'Week_{i-1}'
        curr_col = f'Week_{i}'
        change_df[f'Δ_Week_{i}'] = change_df[curr_col] - change_df[prev_col]
    
    # Show only the change columns
    change_cols = [col for col in change_df.columns if col.startswith('Δ_')]
    if change_cols:
        print("\nChange in Playoff Odds by Week (percentage points):")
        print(change_df[change_cols].round(1).to_string())
    
    return weekly_df


def convert_probability_to_odds(probability_pct):
    """
    Convert probability percentage to betting odds formats
    
    Args:
        probability_pct: Probability as percentage (0-100)
    
    Returns:
        dict: Dictionary with American, Decimal, and Fractional odds
    """
    if probability_pct <= 0:
        return {'American': '+∞', 'Decimal': '∞', 'Fractional': '∞/1', 'Implied_Prob': '0.0%'}
    if probability_pct >= 100:
        return {'American': '-∞', 'Decimal': '1.00', 'Fractional': '0/1', 'Implied_Prob': '100.0%'}
    
    prob = probability_pct / 100.0
    
    # Decimal odds
    decimal_odds = 1 / prob
    
    # American odds
    if prob >= 0.5:
        american_odds = -(prob / (1 - prob)) * 100
        american_str = f"{american_odds:.0f}"
    else:
        american_odds = ((1 - prob) / prob) * 100
        american_str = f"+{american_odds:.0f}"
    
    # Fractional odds (simplified)
    if prob < 0.5:
        numerator = (1 - prob) * 100
        denominator = prob * 100
    else:
        numerator = prob * 100
        denominator = (1 - prob) * 100
    
    # Simplify fraction
    from math import gcd
    g = gcd(int(numerator), int(denominator))
    if prob < 0.5:
        frac_str = f"{int(numerator/g)}/{int(denominator/g)}"
    else:
        frac_str = f"{int(denominator/g)}/{int(numerator/g)}"
    
    return {
        'American': american_str,
        'Decimal': f"{decimal_odds:.2f}",
        'Fractional': frac_str,
        'Implied_Prob': f"{probability_pct:.1f}%"
    }


def create_betting_odds_table(seed_df):
    """
    Create a betting odds table from seed probability dataframe
    
    Args:
        seed_df: DataFrame with team seed probabilities and playoff chances
    
    Returns:
        pd.DataFrame: DataFrame with betting odds in multiple formats
    """
    betting_data = []
    
    for _, row in seed_df.iterrows():
        team = row['Team']
        playoff_prob = row['Chance of Making Playoffs']
        
        # Convert to odds
        odds = convert_probability_to_odds(playoff_prob)
        
        betting_data.append({
            'Team': team,
            'Playoff_Probability': f"{playoff_prob:.1f}%",
            'American_Odds': odds['American'],
            'Decimal_Odds': odds['Decimal'],
            'Fractional_Odds': odds['Fractional']
        })
    
    betting_df = pd.DataFrame(betting_data)
    return betting_df


def create_position_betting_odds(seed_df, num_teams):
    """
    Create betting odds for finishing in each position
    
    Args:
        seed_df: DataFrame with team seed probabilities
        num_teams: Total number of teams
    
    Returns:
        dict: Dictionary of DataFrames, one for each position
    """
    from collections import defaultdict
    
    position_odds = defaultdict(list)
    
    for position in range(1, num_teams + 1):
        place_suffix = get_ordinal_suffix(position)
        col_name = f'{position}{place_suffix} Place'
        
        if col_name not in seed_df.columns:
            continue
        
        for _, row in seed_df.iterrows():
            team = row['Team']
            prob = row[col_name]
            odds = convert_probability_to_odds(prob)
            
            position_odds[col_name].append({
                'Team': team,
                'Probability': f"{prob:.1f}%",
                'American_Odds': odds['American'],
                'Decimal_Odds': odds['Decimal']
            })
    
    # Convert to DataFrames
    position_dfs = {}
    for position, data in position_odds.items():
        df = pd.DataFrame(data)
        # Sort by probability descending
        df = df.sort_values('Probability', ascending=False).reset_index(drop=True)
        position_dfs[position] = df
    
    return position_dfs


def display_betting_odds(seed_df, num_teams):
    """
    Display betting odds in a readable format
    
    Args:
        seed_df: DataFrame with seed probabilities
        num_teams: Total number of teams
    """
    print("\n" + "="*80)
    print("BETTING ODDS - TO MAKE PLAYOFFS")
    print("="*80)
    
    betting_df = create_betting_odds_table(seed_df)
    print(betting_df.to_string(index=False))
    
    print("\n" + "="*80)
    print("BETTING ODDS EXPLANATION")
    print("="*80)
    print("American Odds: Negative = favorite (bet that amount to win $100)")
    print("               Positive = underdog (win that amount on $100 bet)")
    print("Decimal Odds:  Multiply your stake by this number to get total return")
    print("Fractional Odds: Traditional format (profit/stake)")
    
    # Optional: Show odds for specific positions
    print("\n" + "="*80)
    print("BETTING ODDS - TO FINISH 1ST PLACE")
    print("="*80)
    
    position_odds = create_position_betting_odds(seed_df, num_teams)
    if '1st Place' in position_odds:
        print(position_odds['1st Place'].to_string(index=False))
    
    return betting_df, position_odds