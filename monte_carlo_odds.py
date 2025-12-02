import pandas as pd
import numpy as np
from espn_api.football import League
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

def create_results_dataframe(teams, scores_df, current_week):
    """Create a dataframe of completed matchup results"""
    results = []
    
    for week in range(current_week - 1):  # weeks completed
        for team_idx, team in enumerate(teams):
            opponent = team.schedule[week]
            team_score = scores_df.iloc[team_idx, week]
            
            # Find opponent index
            opponent_idx = next(i for i, t in enumerate(teams) if t == opponent)
            opponent_score = scores_df.iloc[opponent_idx, week]
            
            # Only add each matchup once (avoid duplicates)
            if team_idx < opponent_idx:
                winner = team.team_name if team_score > opponent_score else opponent.team_name
                results.append({
                    'week': week + 1,
                    'team1': team.team_name,
                    'team1_score': team_score,
                    'team2': opponent.team_name,
                    'team2_score': opponent_score,
                    'winner': winner
                })
    
    return pd.DataFrame(results)

def calculate_team_stats(teams, scores_df, current_week, reg_season_count):
    """Calculate current stats and scoring statistics for each team"""
    team_stats = {}
    
    # Determine how many regular season games have been completed
    completed_reg_games = min(current_week - 1, reg_season_count)
    
    for team_idx, team in enumerate(teams):
        # Only use regular season scores for statistics
        reg_season_scores = [score for score in scores_df.iloc[team_idx, :completed_reg_games] if score > 0]
        
        # Calculate regular season record including ties
        reg_season_outcomes = team.outcomes[:completed_reg_games]
        wins = sum(1 for outcome in reg_season_outcomes if outcome == 'W')
        losses = sum(1 for outcome in reg_season_outcomes if outcome == 'L')
        ties = sum(1 for outcome in reg_season_outcomes if outcome == 'T')
        
        # Scoring statistics based on regular season performance
        avg_score = np.mean(reg_season_scores) if reg_season_scores else 100.0
        score_std = np.std(reg_season_scores) if len(reg_season_scores) > 1 else 15.0
        
        # Adjust std dev based on sample size (more games = more confidence)
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

def simulate_remaining_season(teams, team_stats, current_week, reg_season_count, num_playoff_teams, num_simulations=1000):
    """Run Monte Carlo simulation for remaining REGULAR SEASON games only"""
    
    # Storage for simulation results
    final_records = defaultdict(list)
    playoff_makes = defaultdict(int)
    last_place_finishes = defaultdict(int)
    seed_counts = defaultdict(lambda: defaultdict(int))
    
    # Check if regular season is already complete
    remaining_reg_games = max(0, reg_season_count - (current_week - 1))
    
    for sim in range(num_simulations):
        # Initialize records for this simulation
        sim_records = {}
        
        for team_name, stats in team_stats.items():
            sim_records[team_name] = {
                'wins': stats['wins'], 
                'losses': stats['losses'],
                'ties': stats['ties'],
                'points_for': stats['total_points']
            }
        
        # Only simulate remaining REGULAR SEASON games
        for week in range(current_week, min(current_week + remaining_reg_games, reg_season_count + 1)):
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
                
                # Determine winner or tie (tie if within 0.5 points)
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
        
        # Determine final REGULAR SEASON standings
        teams_with_records = []
        for team_name, record in sim_records.items():
            # Calculate win percentage (ties count as 0.5 wins)
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
        
        # Sort by wins (descending), then by points_for as tiebreaker
        teams_with_records.sort(key=lambda x: (x['wins'] + 0.5 * x['ties'], x['points_for']), reverse=True)
        
        # Record final standings and playoff makes
        for idx, team_data in enumerate(teams_with_records):
            team_name = team_data['team']
            seed = idx + 1
            
            # Store final regular season record
            if team_data['ties'] > 0:
                final_record = f"{team_data['wins']}-{team_data['losses']}-{team_data['ties']}"
            else:
                final_record = f"{team_data['wins']}-{team_data['losses']}"
            final_records[team_name].append(final_record)
            
            # Count seed positions
            seed_counts[team_name][seed] += 1
            
            # Count playoff makes
            if seed <= num_playoff_teams:
                playoff_makes[team_name] += 1

            # Count last place finishes
            if seed == len(teams):
                last_place_finishes[team_name] += 1
    
    return final_records, playoff_makes, last_place_finishes, seed_counts

def create_summary_dataframes(team_stats, final_records, playoff_makes, last_place_finishes, seed_counts, num_playoff_teams, num_simulations, num_teams, reg_season_count):
    """Create summary dataframes with results (including ties)"""
    
    # Playoff chances and expected records
    summary_data = []
    for team_name, stats in team_stats.items():
        # Calculate most common final record
        record_counts = defaultdict(int)
        for record in final_records[team_name]:
            record_counts[record] += 1
        
        if stats['ties'] > 0:
            current_record = f"{stats['wins']}-{stats['losses']}-{stats['ties']}"
        else:
            current_record = f"{stats['wins']}-{stats['losses']}"
        
        most_common_record = max(record_counts.items(), key=lambda x: x[1])[0] if record_counts else current_record
        
        # Calculate average final record
        if final_records[team_name]:
            total_wins = 0
            total_ties = 0
            for record in final_records[team_name]:
                parts = record.split('-')
                total_wins += int(parts[0])
                if len(parts) == 3:  # Has ties
                    total_ties += int(parts[2])
            
            avg_wins = total_wins / len(final_records[team_name])
            avg_ties = total_ties / len(final_records[team_name])
        else:
            avg_wins = stats['wins']
            avg_ties = stats['ties']
        
        avg_losses = reg_season_count - avg_wins - avg_ties
        
        playoff_pct = (playoff_makes[team_name] / num_simulations) * 100
        last_chance_pct = (last_place_finishes[team_name] / num_simulations) * 100
        
        # Calculate win percentage (ties count as 0.5)
        current_games = stats['wins'] + stats['losses'] + stats['ties']
        current_win_pct = (stats['wins'] + 0.5 * stats['ties']) / current_games if current_games > 0 else 0
        
        # Format expected final record
        if avg_ties > 0.05:  # Show ties if average is significant
            expected_record = f"{avg_wins:.1f}-{avg_losses:.1f}-{avg_ties:.1f}"
        else:
            expected_record = f"{avg_wins:.1f}-{avg_losses:.1f}"
        
        summary_data.append({
            'Team': team_name,
            'Current_Record': current_record,
            'Current_Win_Pct': current_win_pct,
            'Avg_Score': stats['avg_score'],
            'Total_Points_For': stats['total_points'],
            'Playoff_Chance_Pct': playoff_pct,
            'Last_Place_Chance_Pct': last_chance_pct,
            'Expected_Final_Record': expected_record,
            'Most_Likely_Record': most_common_record
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Seed probability matrix
    seed_data = []
    for team_name in team_stats.keys():
        row = {'Team': team_name}
        
        for seed in range(1, num_teams + 1):
            seed_pct = (seed_counts[team_name][seed] / num_simulations) * 100
            place_suffix = get_ordinal_suffix(seed)
            row[f'{seed}{place_suffix} Place'] = round(seed_pct, 1)
        
        seed_data.append(row)
    
    seed_df = pd.DataFrame(seed_data)
    
    # Add playoff chance column
    # num_playoff_teams = settings.playoff_team_count
    playoff_places = [f'{i}{get_ordinal_suffix(i)} Place' for i in range(1, num_playoff_teams + 1)]
    seed_df['Chance of Making Playoffs'] = seed_df[playoff_places].sum(axis=1).round(1)
    
    return summary_df, seed_df

def get_ordinal_suffix(n):
    """Get ordinal suffix for numbers (1st, 2nd, 3rd, etc.)"""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return suffix

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
    remaining_reg_games = max(0, reg_season_count - start_week + 1)
    
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
    if current_week > reg_season_count:
        current_week = reg_season_count+1

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

def create_betting_odds_table(seed_df, team_stats):
    """
    Create a betting odds table from seed probability dataframe
    
    Args:
        seed_df: DataFrame with team seed probabilities and playoff chances
        team_stats: Dictionary of team statistics including records
    
    Returns:
        pd.DataFrame: DataFrame with betting odds in American format
    """
    betting_data = []
    
    for _, row in seed_df.iterrows():
        team = row['Team']
        playoff_prob = row['Chance of Making Playoffs']
        
        # Get team record
        stats = team_stats[team]
        if stats['ties'] > 0:
            record = f"{stats['wins']}-{stats['losses']}-{stats['ties']}"
        else:
            record = f"{stats['wins']}-{stats['losses']}"
        
        # Convert to odds
        odds = convert_probability_to_odds(playoff_prob)
        
        betting_data.append({
            'Team': team,
            'Record': record,
            'Playoff_Probability': f"{playoff_prob:.1f}%",
            'American_Odds': odds['American']
        })
    
    betting_df = pd.DataFrame(betting_data)
    return betting_df

def create_position_betting_odds(seed_df, num_teams, team_stats):
    """
    Create betting odds for finishing in each position
    
    Args:
        seed_df: DataFrame with team seed probabilities
        num_teams: Total number of teams
        team_stats: Dictionary of team statistics including records
    
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
            
            # Get team record
            stats = team_stats[team]
            if stats['ties'] > 0:
                record = f"{stats['wins']}-{stats['losses']}-{stats['ties']}"
            else:
                record = f"{stats['wins']}-{stats['losses']}"
            
            position_odds[col_name].append({
                'Team': team,
                'Record': record,
                'Probability': f"{prob:.1f}%",
                'American_Odds': odds['American']
            })
    
    # Convert to DataFrames
    position_dfs = {}
    for position, data in position_odds.items():
        df = pd.DataFrame(data)
        # Sort by probability descending
        df = df.sort_values('Probability', ascending=False).reset_index(drop=True)
        position_dfs[position] = df
    
    return position_dfs

def display_betting_odds(seed_df, num_teams, team_stats):
    """
    Display betting odds in a readable format
    
    Args:
        seed_df: DataFrame with seed probabilities
        num_teams: Total number of teams
        team_stats: Dictionary of team statistics including records
    """
    print("\n" + "="*80)
    print("BETTING ODDS - TO MAKE PLAYOFFS")
    print("="*80)
    
    betting_df = create_betting_odds_table(seed_df, team_stats)
    print(betting_df.to_string(index=False))
    
    print("\n" + "="*80)
    print("BETTING ODDS - TO FINISH 1ST PLACE")
    print("="*80)
    
    position_odds = create_position_betting_odds(seed_df, num_teams, team_stats)
    if '1st Place' in position_odds:
        print(position_odds['1st Place'].to_string(index=False))
    
    # Get last place column name
    last_place_suffix = get_ordinal_suffix(num_teams)
    last_place_col = f'{num_teams}{last_place_suffix} Place'
    
    print("\n" + "="*80)
    print("BETTING ODDS - TO FINISH LAST PLACE")
    print("="*80)
    
    if last_place_col in position_odds:
        print(position_odds[last_place_col].to_string(index=False))
    
    print("\n" + "="*80)
    print("BETTING ODDS EXPLANATION")
    print("="*80)
    print("American Odds: Negative = favorite (bet that amount to win $100)")
    print("               Positive = underdog (win that amount on $100 bet)")
    
    return betting_df, position_odds

def retrieve_odds_dfs(seed_df, num_teams, team_stats):
    """
    Create betting odds dataframes without printing
    
    Args:
        seed_df: DataFrame with seed probabilities
        num_teams: Total number of teams
        team_stats: Dictionary of team statistics including records
    
    Returns:
        tuple: (make_playoff_odds_df, first_place_odds_df, last_place_odds_df)
    """
    # Make Playoff Betting Odds
    make_playoff_odds_df = create_betting_odds_table(seed_df, team_stats)
    # Sort by probability descending
    make_playoff_odds_df['_prob_sort'] = make_playoff_odds_df['Playoff_Probability'].str.rstrip('%').astype(float)
    make_playoff_odds_df = make_playoff_odds_df.sort_values('_prob_sort', ascending=False).drop('_prob_sort', axis=1)
    make_playoff_odds_df = make_playoff_odds_df.set_index('Team')
    
    # Get position odds
    position_odds = create_position_betting_odds(seed_df, num_teams, team_stats)
    
    # First Place Betting Odds
    first_place_odds_df = position_odds.get('1st Place', pd.DataFrame())
    if not first_place_odds_df.empty:
        first_place_odds_df['_prob_sort'] = first_place_odds_df['Probability'].str.rstrip('%').astype(float)
        first_place_odds_df = first_place_odds_df.sort_values('_prob_sort', ascending=False).drop('_prob_sort', axis=1)
        first_place_odds_df = first_place_odds_df.set_index('Team')
    
    # Last Place Betting Odds
    last_place_suffix = get_ordinal_suffix(num_teams)
    last_place_col = f'{num_teams}{last_place_suffix} Place'
    last_place_odds_df = position_odds.get(last_place_col, pd.DataFrame())
    if not last_place_odds_df.empty:
        last_place_odds_df['_prob_sort'] = last_place_odds_df['Probability'].str.rstrip('%').astype(float)
        last_place_odds_df = last_place_odds_df.sort_values('_prob_sort', ascending=False).drop('_prob_sort', axis=1)
        last_place_odds_df = last_place_odds_df.set_index('Team')
    
    return make_playoff_odds_df, first_place_odds_df, last_place_odds_df

def calculate_remaining_schedule_difficulty(team_stats, schedules_df, lpi_df, current_week, reg_season_count):
    """
    Calculate the difficulty of remaining schedule for each team based on opponents' stats.
    
    Args:
        team_stats: Dictionary of team statistics including wins, losses, ties, total_points
        schedules_df: DataFrame with team schedules (team names as index, weeks as columns)
        lpi_df: DataFrame with LPI rankings (columns: Teams, Owners, Louie Power Index (LPI), Record, etc.)
        current_week: Current week number (first unplayed week)
        reg_season_count: Total number of regular season games
    
    Returns:
        pd.DataFrame: DataFrame with remaining schedule difficulty metrics
    """
    
    # Create LPI lookup dictionary
    lpi_dict = dict(zip(lpi_df['Teams'], lpi_df['Louie Power Index (LPI)']))
    
    # Create owner lookup dictionary
    owner_dict = dict(zip(lpi_df['Teams'], lpi_df['Owners']))
    
    schedule_data = []
    
    for team_name, stats in team_stats.items():
        # Calculate team's own stats
        total_games = stats['wins'] + stats['losses'] + stats['ties']
        team_record = f"{stats['wins']}-{stats['losses']}-{stats['ties']}"
        win_pct = (stats['wins'] + 0.5 * stats['ties']) / total_games if total_games > 0 else 0
        avg_points_for = stats['total_points'] / total_games if total_games > 0 else 0
        
        # Get remaining opponents (from current_week to end of regular season)
        remaining_weeks = range(current_week - 1, reg_season_count)  # -1 because schedules are 0-indexed
        
        if team_name in schedules_df.index:
            team_schedule = schedules_df.loc[team_name]
            remaining_opponents = [team_schedule[week] for week in remaining_weeks if week < len(team_schedule)]
        else:
            remaining_opponents = []
        
        # Calculate opponent averages
        if remaining_opponents:
            opp_points_list = []
            opp_win_pct_list = []
            opp_lpi_list = []
            
            for opponent in remaining_opponents:
                if opponent in team_stats:
                    opp_stats = team_stats[opponent]
                    opp_total_games = opp_stats['wins'] + opp_stats['losses'] + opp_stats['ties']
                    
                    # Opponent points for
                    opp_avg_points = opp_stats['total_points'] / opp_total_games if opp_total_games > 0 else 0
                    opp_points_list.append(opp_avg_points)
                    
                    # Opponent win percentage
                    opp_win_pct = (opp_stats['wins'] + 0.5 * opp_stats['ties']) / opp_total_games if opp_total_games > 0 else 0
                    opp_win_pct_list.append(opp_win_pct)
                    
                    # Opponent LPI
                    if opponent in lpi_dict:
                        opp_lpi_list.append(lpi_dict[opponent])
            
            avg_opp_points = np.mean(opp_points_list) if opp_points_list else 0
            avg_opp_win_pct = np.mean(opp_win_pct_list) if opp_win_pct_list else 0
            avg_opp_lpi = np.mean(opp_lpi_list) if opp_lpi_list else 0
        else:
            avg_opp_points = 0
            avg_opp_win_pct = 0
            avg_opp_lpi = 0
        
        # Get owner name
        owner = owner_dict.get(team_name, "Unknown")
        
        schedule_data.append({
            'Team': team_name,
            'Owner': owner,
            'Avg_Points_For': round(avg_points_for, 2),
            'Team_Record': team_record,
            'Avg_Opp_Points_For': round(avg_opp_points, 2),
            'Avg_Opp_Win_Pct': round(avg_opp_win_pct, 3),
            'Avg_Opp_LPI': round(avg_opp_lpi, 1),
            'Games_Remaining': len(remaining_opponents) if remaining_opponents else 0
        })
    
    # Create DataFrame
    schedule_df = pd.DataFrame(schedule_data)
    
    # Sort by average opponent difficulty (combination of metrics)
    # Higher opponent stats = harder schedule, so sort descending
    schedule_df = schedule_df.sort_values('Avg_Opp_LPI', ascending=False).reset_index(drop=True)
    
    return schedule_df

def display_remaining_schedule_difficulty(schedule_df):
    """
    Display the remaining schedule difficulty with formatted output.
    
    Args:
        schedule_df: DataFrame from calculate_remaining_schedule_difficulty
    """
    print("\n" + "="*100)
    print("REMAINING SCHEDULE DIFFICULTY")
    print("="*100)
    print("\nTeam's Own Stats vs. Remaining Opponents' Average Stats")
    print("-"*100)
    
    display_cols = ['Team', 'Owner', 'Avg_Points_For', 'Win_Pct', 
                    'Avg_Opp_Points_For', 'Avg_Opp_Win_Pct', 'Avg_Opp_LPI', 'Games_Remaining']
    
    print(schedule_df[display_cols].to_string(index=False))
    
# Example usage function
def analyze_remaining_schedule(team_stats, schedules_df, lpi_df, current_week, reg_season_count):
    """
    Convenience function to calculate and display remaining schedule difficulty.
    
    Args:
        team_stats: Dictionary of team statistics
        schedules_df: DataFrame with team schedules
        lpi_df: DataFrame with LPI rankings
        current_week: Current week number
        reg_season_count: Total regular season games
    
    Returns:
        pd.DataFrame: Schedule difficulty DataFrame
    """
    schedule_df = calculate_remaining_schedule_difficulty(
        team_stats, schedules_df, lpi_df, current_week, reg_season_count
    )
    
    display_remaining_schedule_difficulty(schedule_df)
    
    return schedule_df

def main():
    # ESPN API setup (using your provided data structure)
    espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
    year = 2025
    # Pennoni Younglings
    # league = League(league_id=1118513122, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
    league = League(league_id=310334683, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
    # hannah_s2 = "AEBy%2FXPWgz4DEVTKf5Z1y9k7Lco6fLP6tO80b1nl5a1p9CBOLF0Z0AlBcStZsywrAAdgHUABmm7G9Cy8l2IJCjgEAm%2BT5NHVNFPgtfDPjT0ei81RfEzwugF1UTbYc%2FlFrpWqK9xL%2FQvSoCW5TV9H4su6ILsqHLnI4b0xzH24CIDIGKInjez5Ivt8r1wlufknwMWo%2FQ2QaJfm6VPlcma3GJ0As048W4ujzwi68E9CWOtPT%2FwEQpfqN3g8WkKdWYCES0VdWmQvSeHnphAk8vlieiBTsh3BBegGULXInpew87nuqA%3D%3D"
    # league = League(league_id=1399036372, year=2025, espn_s2=hannah_s2, swid='{46993514-CB12-4CFA-9935-14CB122CFA5F}')

    # League settings
    settings = league.settings
    reg_season_count = settings.reg_season_count
    num_playoff_teams = settings.playoff_team_count
    
    # Get teams and data
    teams = league.teams
    team_scores = [team.scores for team in teams]
    team_owners = [team.owners[0]['id'] for team in teams]
    team_names = [team.team_name for team in league.teams]
    
    # Create scores DataFrame
    scores_df = pd.DataFrame(team_scores, index=team_owners)
    
    # Calculate current week
    zero_week = (scores_df == 0.0).all(axis=0)
    if zero_week.any():
        current_week = zero_week.idxmax() +1
    else:
        current_week = scores_df.shape[1]
    
    print(f"Current week: {current_week}")
    print(f"Regular season games: {reg_season_count}")
    print(f"Playoff teams: {num_playoff_teams}")
    print(f"Total teams: {len(teams)}")
    
    # Calculate team statistics
    team_stats = calculate_team_stats(teams, scores_df, current_week, reg_season_count)
    
    # Determine how many regular season games remain
    completed_reg_games = min(current_week - 1, reg_season_count)
    remaining_reg_games = max(0, reg_season_count - completed_reg_games)
    
    print(f"Regular season games completed: {completed_reg_games}")
    print(f"Regular season games remaining: {remaining_reg_games}")
    
    # Run Monte Carlo simulation
    print("Running Monte Carlo simulation for remaining regular season...")
    final_records, playoff_makes, last_place_finishes, seed_counts = simulate_remaining_season(
        teams, team_stats, current_week, reg_season_count, num_playoff_teams, num_simulations=1000
    )
    
    # Create summary dataframes
    summary_df, seed_df = create_summary_dataframes(
        team_stats, final_records, playoff_makes, last_place_finishes, seed_counts, num_playoff_teams, 1000, len(teams), reg_season_count
    )
    
    # Sort by playoff chances
    summary_df = summary_df.sort_values('Playoff_Chance_Pct', ascending=False).reset_index(drop=True)
    
    # Sort seed_df by playoff chances (using the new column)
    seed_df = seed_df.sort_values('Chance of Making Playoffs', ascending=False).reset_index(drop=True)
    
    # Display results
    print("\n" + "="*80)
    print("FANTASY FOOTBALL PLAYOFF PREDICTIONS")
    print("="*80)
    
    print(f"\nSUMMARY - Regular Season Playoff Predictions:")
    print("(Based on regular season performance only)")
    display_cols = ['Team', 'Current_Record', 'Current_Win_Pct', 'Total_Points_For', 'Playoff_Chance_Pct', 'Last_Place_Chance_Pct', 'Expected_Final_Record', 'Most_Likely_Record']
    print(summary_df[display_cols].to_string(index=False, float_format='%.1f'))
    
    print(f"\nSEED PROBABILITIES (All positions and playoff chances):")
    print("(Values represent percentage chance of finishing in each position)")
    
    # Show first 8 place columns plus playoff chance column
    display_cols = ['Team']
    for i in range(1, min(9, len(teams) + 1)):
        place_suffix = get_ordinal_suffix(i)
        display_cols.append(f'{i}{place_suffix} Place')
    display_cols.append('Chance of Making Playoffs')
    
    available_cols = [col for col in display_cols if col in seed_df.columns]
    print(seed_df[available_cols].to_string(index=False, float_format='%.1f'))

    # After getting your league data
    weekly_playoff_df = calculate_playoff_chances_by_week(
        teams, scores_df, reg_season_count, num_playoff_teams, current_week
    )
    print("\nWeekly Playoff Chances:")
    print(weekly_playoff_df)

    # Or use the integrated function for full output
    weekly_df = add_weekly_analysis_to_main(
        teams, scores_df, reg_season_count, num_playoff_teams, current_week
    )
    print()
    print(weekly_df)

    num_teams = len(teams)

    schedules = []
    for team in league.teams:
        schedule = [opponent.team_name for opponent in team.schedule]
        schedules.append(schedule)
    # print(current_week)
    schedules_df = pd.DataFrame(schedules, index=team_names)

    leagueName = league.settings.name
    fileName = leagueName + " " + str(year)
    fileName = f"leagues/{fileName}.xlsx"
    lpi_df = pd.read_excel(fileName, sheet_name="Louie Power Index", index_col=0)  # Team names as index

    analyze_remaining_schedule(team_stats, schedules_df, lpi_df, current_week, reg_season_count)

    # schedule_df = calculate_remaining_schedule_difficulty(team_stats, schedules_df, lpi_df, current_week, reg_season_count)
    # print(schedule_df)

    # display_betting_odds(seed_df, num_teams, team_stats)
    # Save to Excel if desired
    # try:
    #     with pd.ExcelWriter('fantasy_predictions.xlsx') as writer:
    #         summary_df.to_excel(writer, sheet_name='Summary', index=False)
    #         seed_df.to_excel(writer, sheet_name='Seed_Probabilities', index=False)
    #     print(f"\nResults saved to 'fantasy_predictions.xlsx'")
    # except:
    #     print(f"\nCould not save Excel file - results displayed above")
    # summary_df = (
    #     summary_df.sort_values('Playoff_Chance_Pct', ascending=False)
    #             .reset_index(drop=True)
    #             .set_index("Team")
    # )

    # seed_df = (
    #     seed_df.sort_values('Chance of Making Playoffs', ascending=False)
    #         .reset_index(drop=True)
    #         .set_index("Team")
    # )
    
    return summary_df, seed_df

# Global variables for settings
reg_season_count = 17  # Default, will be updated from API
num_playoff_teams = 6  # Default, will be updated from API

def run_simulation_with_data(teams, scores_df, reg_season_count, num_playoff_teams, current_week=None, num_simulations=1000):
    """
    Run simulation with pre-loaded data (for importing into other scripts)
    
    Args:
        teams: List of team objects from ESPN API
        scores_df: DataFrame of team scores
        reg_season_count: Number of regular season games
        num_playoff_teams: Number of teams that make playoffs
        current_week: Current week (will calculate if None)
        num_simulations: Number of Monte Carlo simulations
    
    Returns:
        tuple: (summary_df, seed_df)
    """
    
    # Calculate current week if not provided
    if current_week is None:
        current_week = scores_df.apply(lambda row: row[row != 0.0].last_valid_index(), axis=1).max() + 1
    
    # Calculate team statistics
    team_stats = calculate_team_stats(teams, scores_df, current_week, reg_season_count)
    
    # Run Monte Carlo simulation
    final_records, playoff_makes, last_place_finishes, seed_counts = simulate_remaining_season(
        teams, team_stats, current_week, reg_season_count, num_playoff_teams, num_simulations
    )
    
    # Create summary dataframes
    summary_df, seed_df = create_summary_dataframes(
        team_stats, final_records, playoff_makes, last_place_finishes, seed_counts, num_playoff_teams, num_simulations, len(teams), reg_season_count
    )
    
    # Sort results
    summary_df = summary_df.sort_values('Playoff_Chance_Pct', ascending=False).reset_index(drop=True)
    seed_df = seed_df.sort_values('Chance of Making Playoffs', ascending=False).reset_index(drop=True)
    # print(summary_df)
    
    return summary_df, seed_df

if __name__ == "__main__":
    summary_df, seed_df = main()