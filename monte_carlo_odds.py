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
        
        # Calculate regular season record only
        reg_season_outcomes = team.outcomes[:completed_reg_games]
        wins = sum(1 for outcome in reg_season_outcomes if outcome == 'W')
        losses = sum(1 for outcome in reg_season_outcomes if outcome == 'L')
        
        # Scoring statistics based on regular season performance
        avg_score = np.mean(reg_season_scores) if reg_season_scores else 100.0
        score_std = np.std(reg_season_scores) if len(reg_season_scores) > 1 else 15.0
        
        # Adjust std dev based on sample size (more games = more confidence)
        games_played = len(reg_season_scores)
        confidence_factor = max(0.5, 1 - (games_played / 20))  # Gets tighter with more games
        adjusted_std = score_std * (1 + confidence_factor)
        
        team_stats[team.team_name] = {
            'team_obj': team,
            'wins': wins,
            'losses': losses,
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
                'points_for': stats['total_points']
            }
        
        # Only simulate remaining REGULAR SEASON games (up to reg_season_count)
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
                
                # Generate random scores based on normal distribution
                team1_score = max(0, np.random.normal(team1_stats['avg_score'], team1_stats['score_std']))
                team2_score = max(0, np.random.normal(team2_stats['avg_score'], team2_stats['score_std']))
                
                # Determine winner and update records
                if team1_score > team2_score:
                    sim_records[team1_name]['wins'] += 1
                    sim_records[team2_name]['losses'] += 1
                else:
                    sim_records[team2_name]['wins'] += 1
                    sim_records[team1_name]['losses'] += 1
                
                # Update points
                sim_records[team1_name]['points_for'] += team1_score
                sim_records[team2_name]['points_for'] += team2_score
        
        # Determine final REGULAR SEASON standings and playoff seeding
        teams_with_records = []
        for team_name, record in sim_records.items():
            teams_with_records.append({
                'team': team_name,
                'wins': record['wins'],
                'losses': record['losses'],
                'points_for': record['points_for'],
                'win_pct': record['wins'] / (record['wins'] + record['losses']) if (record['wins'] + record['losses']) > 0 else 0
            })
        
        # Sort by wins (descending), then by points_for as tiebreaker (descending)
        teams_with_records.sort(key=lambda x: (x['wins'], x['points_for']), reverse=True)
        
        # Record final standings and playoff makes
        for idx, team_data in enumerate(teams_with_records):
            team_name = team_data['team']
            seed = idx + 1
            
            # Store final regular season record for this simulation
            final_record = f"{team_data['wins']}-{team_data['losses']}"
            final_records[team_name].append(final_record)
            
            # Count seed positions (overall standings)
            seed_counts[team_name][seed] += 1
            
            # Count playoff makes (top N teams make playoffs based on regular season)
            if seed <= num_playoff_teams:
                playoff_makes[team_name] += 1
    
    return final_records, playoff_makes, seed_counts

def create_summary_dataframes(team_stats, final_records, playoff_makes, seed_counts, num_simulations, num_teams, reg_season_count):
    """Create summary dataframes with results"""
    
    # Playoff chances and expected records
    summary_data = []
    for team_name, stats in team_stats.items():
        # Calculate most common final record
        record_counts = defaultdict(int)
        for record in final_records[team_name]:
            record_counts[record] += 1
        
        most_common_record = max(record_counts.items(), key=lambda x: x[1])[0] if record_counts else f"{stats['wins']}-{stats['losses']}"
        
        # Calculate average final record
        if final_records[team_name]:
            total_wins = sum(int(record.split('-')[0]) for record in final_records[team_name])
            avg_wins = total_wins / len(final_records[team_name])
        else:
            # If no simulations (regular season complete), use current record
            avg_wins = stats['wins']
        
        avg_losses = reg_season_count - avg_wins
        
        playoff_pct = (playoff_makes[team_name] / num_simulations) * 100
        
        # Handle division by zero for win percentage
        current_games = stats['wins'] + stats['losses']
        current_win_pct = stats['wins'] / current_games if current_games > 0 else 0
        
        summary_data.append({
            'Team': team_name,
            'Current_Record': f"{stats['wins']}-{stats['losses']}",
            'Current_Win_Pct': current_win_pct,
            'Avg_Score': stats['avg_score'],
            'Total_Points_For': stats['total_points'],
            'Playoff_Chance_Pct': playoff_pct,
            'Expected_Final_Record': f"{avg_wins:.1f}-{avg_losses:.1f}",
            'Most_Likely_Record': most_common_record
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Seed probability matrix
    seed_data = []
    for team_name in team_stats.keys():
        row = {'Team': team_name}
        
        # Add place columns (1st Place, 2nd Place, etc.)
        for seed in range(1, num_teams + 1):
            seed_pct = (seed_counts[team_name][seed] / num_simulations) * 100
            place_suffix = get_ordinal_suffix(seed)
            row[f'{seed}{place_suffix} Place'] = round(seed_pct, 1)
        
        seed_data.append(row)
    
    seed_df = pd.DataFrame(seed_data)
    
    # Add playoff chance column (sum of top N places)
    playoff_places = [f'{i}{get_ordinal_suffix(i)} Place' for i in range(1, num_playoff_teams + 1)]
    seed_df['Chance of Making Playoffs'] = seed_df[playoff_places].sum(axis=1).round(1)
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

def get_ordinal_suffix(n):
    """Get ordinal suffix for numbers (1st, 2nd, 3rd, etc.)"""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return suffix
    
    return summary_df, seed_df

def main():
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
    final_records, playoff_makes, seed_counts = simulate_remaining_season(
        teams, team_stats, current_week, reg_season_count, num_playoff_teams, num_simulations=1000
    )
    
    # Create summary dataframes
    summary_df, seed_df = create_summary_dataframes(
        team_stats, final_records, playoff_makes, seed_counts, 1000, len(teams), reg_season_count
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
    display_cols = ['Team', 'Current_Record', 'Current_Win_Pct', 'Total_Points_For', 'Playoff_Chance_Pct', 'Expected_Final_Record', 'Most_Likely_Record']
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
    final_records, playoff_makes, seed_counts = simulate_remaining_season(
        teams, team_stats, current_week, reg_season_count, num_playoff_teams, num_simulations
    )
    
    # Create summary dataframes
    summary_df, seed_df = create_summary_dataframes(
        team_stats, final_records, playoff_makes, seed_counts, num_simulations, len(teams), reg_season_count
    )
    
    # Sort results
    summary_df = summary_df.sort_values('Playoff_Chance_Pct', ascending=False).reset_index(drop=True)
    seed_df = seed_df.sort_values('Chance of Making Playoffs', ascending=False).reset_index(drop=True)
    
    return summary_df, seed_df

if __name__ == "__main__":
    summary_df, seed_df = main()