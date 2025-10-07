import pandas as pd
import numpy as np

# Read the data
all_drafts_df = pd.read_csv("Master_Draft_Data.csv")

# Filter for Pennoni Younglings league
pennoni_df = all_drafts_df[all_drafts_df['League Name'] == 'EBC League'].copy()

# Get unique years
years = sorted(pennoni_df['Year'].unique())

print("=" * 80)
print("EBC League FANTASY FOOTBALL ANALYSIS")
print("=" * 80)

# ============================================================================
# PART 1: BEST POSSIBLE ROSTER BY ROUND
# ============================================================================
def get_best_roster_by_round(df_year):
    """
    Build the best roster by selecting the best available player 
    from each round that fills a needed position
    """
    
    # Define roster requirements
    roster_needs = {
        'QB': 1,
        'RB': 2,
        'WR': 2,
        'TE': 1,
        'D/ST': 1,
        'K': 1,
        'FLEX': 1  # RB, WR, or TE
    }
    
    filled_roster = {
        'QB': [],
        'RB': [],
        'WR': [],
        'TE': [],
        'D/ST': [],
        'K': [],
        'FLEX': None
    }
    
    # Extract round number from Pick column (e.g., "1 - 5" -> 1)
    df_year['Round'] = df_year['Pick'].str.split(' - ').str[0].astype(int)
    
    # Sort by round, then by points descending
    df_sorted = df_year.sort_values(['Round', 'Points'], ascending=[True, False])
    
    # Get unique rounds
    rounds = sorted(df_year['Round'].unique())
    
    # Go through each round
    for round_num in rounds:
        round_players = df_sorted[df_sorted['Round'] == round_num].copy()
        
        # Try to fill a needed position with the best player from this round
        best_pick = None
        best_value = -1
        position_to_fill = None
        
        for idx, player in round_players.iterrows():
            pos = player['Position']
            points = player['Points']
            
            # Check if this position is needed
            if pos in ['QB', 'D/ST', 'K']:
                if len(filled_roster[pos]) < roster_needs[pos]:
                    if points > best_value:
                        best_value = points
                        best_pick = player
                        position_to_fill = pos
            
            elif pos in ['RB', 'WR', 'TE']:
                # Check if needed for primary position
                if len(filled_roster[pos]) < roster_needs[pos]:
                    if points > best_value:
                        best_value = points
                        best_pick = player
                        position_to_fill = pos
                # Check if can be used for FLEX
                elif filled_roster['FLEX'] is None:
                    if points > best_value:
                        best_value = points
                        best_pick = player
                        position_to_fill = 'FLEX'
        
        # Add the best pick from this round
        if best_pick is not None:
            if position_to_fill == 'FLEX':
                filled_roster['FLEX'] = best_pick
            else:
                filled_roster[position_to_fill].append(best_pick)
    
    return filled_roster

for year in years:
    print(f"\n{'=' * 80}")
    print(f"YEAR: {year}")
    print(f"{'=' * 80}")
    
    year_df = pennoni_df[pennoni_df['Year'] == year].copy()
    
    # Best Possible Roster by Round
    print(f"\n--- BEST POSSIBLE ROSTER BY ROUND ({year}) ---")
    print("(Selecting best player from each round that fills a roster need)")
    print()
    
    best_roster = get_best_roster_by_round(year_df)
    
    total_points = 0
    
    # Display QB
    if best_roster['QB']:
        player = best_roster['QB'][0]
        print(f"QB     | {player['Player']:25} | Round {player['Round']:2} | {player['Points']:6.1f} pts")
        total_points += player['Points']
    
    # Display RBs
    for i, player in enumerate(best_roster['RB'], 1):
        print(f"RB{i}    | {player['Player']:25} | Round {player['Round']:2} | {player['Points']:6.1f} pts")
        total_points += player['Points']
    
    # Display WRs
    for i, player in enumerate(best_roster['WR'], 1):
        print(f"WR{i}    | {player['Player']:25} | Round {player['Round']:2} | {player['Points']:6.1f} pts")
        total_points += player['Points']
    
    # Display TE
    if best_roster['TE']:
        player = best_roster['TE'][0]
        print(f"TE     | {player['Player']:25} | Round {player['Round']:2} | {player['Points']:6.1f} pts")
        total_points += player['Points']
    
    # Display FLEX
    if best_roster['FLEX'] is not None:
        player = best_roster['FLEX']
        print(f"FLEX   | {player['Player']:25} ({player['Position']}) | Round {player['Round']:2} | {player['Points']:6.1f} pts")
        total_points += player['Points']
    
    # Display D/ST
    if best_roster['D/ST']:
        player = best_roster['D/ST'][0]
        print(f"D/ST   | {player['Player']:25} | Round {player['Round']:2} | {player['Points']:6.1f} pts")
        total_points += player['Points']
    
    # Display K
    if best_roster['K']:
        player = best_roster['K'][0]
        print(f"K      | {player['Player']:25} | Round {player['Round']:2} | {player['Points']:6.1f} pts")
        total_points += player['Points']
    
    print(f"\nTOTAL POINTS: {total_points:.1f}")
    
    # Top 5 at each position
    print(f"\n--- TOP 5 BY POSITION ({year}) ---")
    
    positions = ['QB', 'RB', 'WR', 'TE', 'D/ST', 'K']
    for pos in positions:
        print(f"\n{pos}:")
        pos_df = year_df[year_df['Position'] == pos].nlargest(5, 'Points')
        for idx, row in pos_df.iterrows():
            round_num = row['Pick'].split(' - ')[0]
            print(f"  {row['Player']:25} | {row['Points']:6.1f} pts | Round {round_num}, Pick {row['Total Pick']}")
qwre
# ============================================================================
# PART 2: DRAFT PICK ANALYSIS (1st ROUND)
# ============================================================================
print(f"\n\n{'=' * 80}")
print("DRAFT PICK OPTIMIZATION ANALYSIS (1st ROUND)")
print(f"{'=' * 80}")

for year in years:
    print(f"\n{'=' * 80}")
    print(f"YEAR: {year}")
    print(f"{'=' * 80}")
    
    year_df = pennoni_df[pennoni_df['Year'] == year].copy()
    year_df = year_df.sort_values('Total Pick')
    
    # Determine number of teams (assuming snake draft)
    max_pick_in_round_1 = year_df[year_df['Pick'].str.startswith('1 -')]['Total Pick'].max()
    num_teams = max_pick_in_round_1
    
    print(f"\nNumber of teams: {num_teams}")
    
    # Analyze each 1st round pick
    first_round_picks = year_df[year_df['Pick'].str.startswith('1 -')].copy()
    
    for idx, first_pick in first_round_picks.iterrows():
        pick_num = first_pick['Total Pick']
        team_name = first_pick['Team']
        
        print(f"\n--- PICK #{pick_num} ({team_name}) ---")
        
        # Get actual picks for this team
        actual_team = year_df[year_df['Team'] == team_name].copy()
        actual_points = actual_team['Points'].sum()
        
        print(f"Actual 1st round pick: {first_pick['Player']} ({first_pick['Position']}) - {first_pick['Points']:.1f} pts")
        print(f"Actual team total: {actual_points:.1f} pts")
        
        # Find best alternative 1st round pick
        available_first_round = year_df[year_df['Total Pick'] <= max_pick_in_round_1].copy()
        
        best_alt_points = actual_points
        best_alt_player = None
        
        for alt_idx, alt_player in available_first_round.iterrows():
            if alt_player['Total Pick'] == pick_num:
                continue
            
            # Calculate points: remove actual 1st pick, add alternative
            alt_total = actual_points - first_pick['Points'] + alt_player['Points']
            
            if alt_total > best_alt_points:
                best_alt_points = alt_total
                best_alt_player = alt_player
        
        if best_alt_player is not None:
            print(f"\nBest alternative: {best_alt_player['Player']} ({best_alt_player['Position']}) - {best_alt_player['Points']:.1f} pts")
            print(f"Optimized team total: {best_alt_points:.1f} pts")
            print(f"Points gained: +{best_alt_points - actual_points:.1f} pts")
        else:
            print("\nNo better 1st round alternative found")

print(f"\n{'=' * 80}")
print("ANALYSIS COMPLETE")
print(f"{'=' * 80}")