import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Set up drafts folder
drafts_folder = "drafts"

# Initialize an empty list to store dataframes
dataframes = []

# Process all draft files
for file in os.listdir(drafts_folder):
    if "Draft Results" in file and file.endswith(".csv"):
        file_path = os.path.join(drafts_folder, file)
        league_name = file.split(" Draft")[0]
        year = file.split("Results ")[1].split(".csv")[0]
        draft_df = pd.read_csv(file_path)
        draft_df = draft_df.drop(columns=["Owner ID"])
        draft_df["League Name"] = league_name
        draft_df["Year"] = year
        
        print(f"\nProcessing: {file}")
        print()
        # Append the dataframe to the list
        dataframes.append(draft_df)

# Combine all dataframes into a single dataframe
all_drafts_df = pd.concat(dataframes, ignore_index=True)

# Save the master draft data
all_drafts_df.to_csv("Master_Draft_Data.csv", index=False)
print(f"✓ Master draft data saved to: Master_Draft_Data.csv")
print(f"  Total picks: {len(all_drafts_df)}")
print(f"  Leagues: {all_drafts_df['League Name'].nunique()}")
print(f"  Years: {all_drafts_df['Year'].nunique()}")

# ===== CALCULATE TEAM-LEVEL STATISTICS =====
print("\n" + "="*60)
print("CALCULATING TEAM DRAFT METRICS")
print("="*60)

# Group by Team, League Name, and Year to calculate metrics
team_metrics = []

for (team, league, year), group in all_drafts_df.groupby(['Team', 'League Name', 'Year']):
    # Sort by Total Pick to ensure correct order
    group = group.sort_values('Total Pick')
    
    # Extract pick number from first pick (e.g., "1 - 6" -> 6)
    first_pick_str = group.iloc[0]['Pick']
    pick_number = int(first_pick_str.split(' - ')[1])
    
    # Top Pick Points
    top_pick_points = group.iloc[0]['Points'] if len(group) > 0 else None
    
    # Top Two Pick Points
    top_two_points = group.iloc[:2]['Points'].sum() if len(group) >= 2 else top_pick_points
    
    # Top Four Pick Points
    top_four_points = group.iloc[:4]['Points'].sum() if len(group) >= 4 else group['Points'].sum()
    
    # Best Pick (highest points from any pick)
    best_pick_idx = group['Points'].idxmax()
    best_pick_points = group.loc[best_pick_idx, 'Points']
    best_pick_player = group.loc[best_pick_idx, 'Player']
    best_pick_round = group.loc[best_pick_idx, 'Pick']
    
    # Top Pick Grade
    top_pick_grade = group.iloc[0]['Draft Grade'] if len(group) > 0 else None
    
    # Top Four Pick Grade (average of top 4 picks)
    top_four_grade = group.iloc[:4]['Draft Grade'].mean() if len(group) >= 4 else group['Draft Grade'].mean()
    
    team_metrics.append({
        'Team': team,
        'League Name': league,
        'Year': year,
        'Pick Number': pick_number,
        'Top Pick Points': top_pick_points,
        'Top Two Pick Points': top_two_points,
        'Top Four Pick Points': top_four_points,
        'Best Pick Points': best_pick_points,
        'Best Pick Player': best_pick_player,
        'Best Pick Round': best_pick_round,
        'Top Pick Grade': top_pick_grade,
        'Top Four Pick Grade': top_four_grade
    })

# Create team metrics dataframe
team_metrics_df = pd.DataFrame(team_metrics)


# Read standings data to add Final Place
standings_df = pd.read_csv("drafts/Draft_Grades_with_Standings.csv")
team_metrics_df["Year"] = team_metrics_df["Year"].astype(int)
standings_df["Year"] = standings_df["Year"].astype(int)
# Merge to add Standing (renamed to Final Place)
team_metrics_df = team_metrics_df.merge(
    standings_df[['Team', 'League Name', 'Year', 'Standing']],
    on=['Team', 'League Name', 'Year'],
    how='left'
)

# Rename Standing to Final Place
team_metrics_df = team_metrics_df.rename(columns={'Standing': 'Final Place'})

# Round Top Four Pick Points and Top Four Pick Grade to 2 decimal places
team_metrics_df['Top Four Pick Points'] = team_metrics_df['Top Four Pick Points'].round(2)
team_metrics_df['Top Four Pick Grade'] = team_metrics_df['Top Four Pick Grade'].round(2)

# Reorder columns to put Final Place near the beginning
cols = ['Team', 'League Name', 'Year', 'Final Place'] + [col for col in team_metrics_df.columns if col not in ['Team', 'League Name', 'Year', 'Final Place']]
team_metrics_df = team_metrics_df[cols]

# Save team metrics
team_metrics_df.to_csv("Team_Draft_Metrics.csv", index=False)
print(f"\n✓ Team draft metrics saved to: Team_Draft_Metrics.csv")

# Display sample
print("\nSample Team Metrics:")
print(team_metrics_df.head(10).to_string(index=False))

# ===== MERGE WITH STANDINGS DATA =====
print("\n" + "="*60)
print("MERGING WITH STANDINGS DATA")
print("="*60)

# Read the standings data
standings_df = pd.read_csv("drafts/Draft_Grades_with_Standings.csv")

team_metrics_df["Year"] = team_metrics_df["Year"].astype(int)
standings_df["Year"] = standings_df["Year"].astype(int)
# Merge standings with team metrics
merged_df = standings_df.merge(
    team_metrics_df,
    on=['Team', 'League Name', 'Year'],
    how='left'
)

# Save the enhanced standings
merged_df.to_csv("Draft_Grades_with_Standings_Enhanced.csv", index=False)
print(f"✓ Enhanced standings saved to: Draft_Grades_with_Standings_Enhanced.csv")

# ===== ANALYSIS =====
print("\n" + "="*60)
print("DRAFT PICK PERFORMANCE ANALYSIS")
print("="*60)

# Remove rows with missing pick data for analysis
analysis_df = merged_df.dropna(subset=['Pick Number', 'Top Pick Points'])

if len(analysis_df) > 0:
    # 1. First Pick Analysis
    print("\n1. FIRST ROUND PICK PERFORMANCE")
    print("-" * 60)
    
    for metric in ['Standing', 'Points For', 'LPI']:
        corr = analysis_df['Top Pick Points'].corr(analysis_df[metric])
        print(f"Correlation with {metric}: {corr:.3f}")
    
    # 2. Top Two Picks Analysis
    print("\n2. TOP TWO PICKS PERFORMANCE")
    print("-" * 60)
    
    for metric in ['Standing', 'Points For', 'LPI']:
        corr = analysis_df['Top Two Pick Points'].corr(analysis_df[metric])
        print(f"Correlation with {metric}: {corr:.3f}")
    
    # 3. Top Four Picks Analysis
    print("\n3. TOP FOUR PICKS PERFORMANCE")
    print("-" * 60)
    
    for metric in ['Standing', 'Points For', 'LPI']:
        corr = analysis_df['Top Four Pick Points'].corr(analysis_df[metric])
        print(f"Correlation with {metric}: {corr:.3f}")
    
    # 4. Draft Grade Analysis
    print("\n4. DRAFT GRADE ANALYSIS")
    print("-" * 60)
    
    print("\nTop Pick Grade correlation with Standing:", 
          analysis_df['Top Pick Grade'].corr(analysis_df['Standing']))
    print("Top Four Pick Grade correlation with Standing:", 
          analysis_df['Top Four Pick Grade'].corr(analysis_df['Standing']))
    
    # 5. Summary statistics
    print("\n5. SUMMARY STATISTICS")
    print("-" * 60)
    
    print("\nTop Pick Points by Final Standing:")
    standing_groups = analysis_df.groupby('Standing').agg({
        'Top Pick Points': ['mean', 'median'],
        'Top Two Pick Points': 'mean',
        'Top Four Pick Points': 'mean',
        'Pick Number': 'mean'
    }).round(2)
    print(standing_groups)
    
    
    # 7. Create visualizations
    print("\n7. CREATING VISUALIZATIONS...")
    print("-" * 60)
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Fantasy Football Draft Pick Performance Analysis', fontsize=16)
    
    # First Pick vs Standing
    axes[0, 0].scatter(analysis_df['Top Pick Points'], analysis_df['Standing'], alpha=0.6)
    axes[0, 0].set_xlabel('First Pick Points')
    axes[0, 0].set_ylabel('Final Standing (lower is better)')
    axes[0, 0].set_title('First Pick vs Standing')
    axes[0, 0].invert_yaxis()
    
    # First Pick vs Points For
    axes[0, 1].scatter(analysis_df['Top Pick Points'], analysis_df['Points For'], alpha=0.6)
    axes[0, 1].set_xlabel('First Pick Points')
    axes[0, 1].set_ylabel('Points For')
    axes[0, 1].set_title('First Pick vs Points For')
    
    # Top Four vs Standing
    axes[0, 2].scatter(analysis_df['Top Four Pick Points'], analysis_df['Standing'], alpha=0.6)
    axes[0, 2].set_xlabel('Top Four Pick Points')
    axes[0, 2].set_ylabel('Final Standing (lower is better)')
    axes[0, 2].set_title('Top 4 Picks vs Standing')
    axes[0, 2].invert_yaxis()
    
    # Top Pick Grade vs Standing
    axes[1, 0].scatter(analysis_df['Top Pick Grade'], analysis_df['Standing'], alpha=0.6)
    axes[1, 0].set_xlabel('Top Pick Draft Grade')
    axes[1, 0].set_ylabel('Final Standing (lower is better)')
    axes[1, 0].set_title('Top Pick Grade vs Standing')
    axes[1, 0].invert_yaxis()
    
    # Pick Number vs Standing
    axes[1, 1].scatter(analysis_df['Pick Number'], analysis_df['Standing'], alpha=0.6)
    axes[1, 1].set_xlabel('First Round Pick Number')
    axes[1, 1].set_ylabel('Final Standing (lower is better)')
    axes[1, 1].set_title('Pick Position vs Standing')
    axes[1, 1].invert_yaxis()
    
    # Best Pick vs Standing
    axes[1, 2].scatter(analysis_df['Best Pick Points'], analysis_df['Standing'], alpha=0.6)
    axes[1, 2].set_xlabel('Best Pick Points')
    axes[1, 2].set_ylabel('Final Standing (lower is better)')
    axes[1, 2].set_title('Best Pick vs Standing')
    axes[1, 2].invert_yaxis()
    
    plt.tight_layout()
    plt.savefig('draft_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Saved visualization to: draft_analysis.png")
    
    # 8. Key insights
    print("\n8. KEY INSIGHTS")
    print("-" * 60)
    
    # Winners analysis
    winners = analysis_df[analysis_df['Standing'] <= 3]
    top_two = winners['Top Two Pick Points'].mean() / 2
    top_four = winners['Top Four Pick Points'].mean() / 4
    print(f"\nTop 3 finishers' average first pick points: {winners['Top Pick Points'].mean():.1f}")
    print(f"Top 3 finishers' average top 2 pick points: {top_two:.1f}")
    print(f"Top 3 finishers' average top 4 pick points: {top_four:.1f}")
    print(f"Top 3 finishers' average best pick points: {winners['Best Pick Points'].mean():.1f}")
    print(f"Top 3 finishers' average points for: {winners['Points For'].mean():.1f}")
    print(f"Top 3 finishers' average points against: {winners['Points Against'].mean():.1f}")
    
    # Compare to bottom finishers
    losers = analysis_df[analysis_df['Standing'] >= analysis_df['Standing'].max() - 2]
    bot_two = losers['Top Two Pick Points'].mean() / 2
    bot_four = losers['Top Four Pick Points'].mean() / 4
    print(f"\nBottom 3 finishers' average first pick points: {losers['Top Pick Points'].mean():.1f}")
    print(f"Bottom 3 finishers' average top 2 pick points: {bot_two:.1f}")
    print(f"Bottom 3 finishers' average top 4 pick points: {bot_four:.1f}")
    print(f"Bottom 3 finishers' average best pick points: {losers['Best Pick Points'].mean():.1f}")
    print(f"Bottom 3 finishers' average points for: {losers['Points For'].mean():.1f}")
    print(f"Bottom 3 finishers' average points against: {losers['Points Against'].mean():.1f}")
    

    bot_first_pick = losers['Top Pick Points'].mean()
    top_first_pick = winners['Top Pick Points'].mean()
    first_pick_diff = top_first_pick - bot_first_pick

    top_two_diff = top_two - bot_two
    top_four_diff = top_four - bot_four

    best_pick_diff = winners['Best Pick Points'].mean() - losers['Best Pick Points'].mean()
    points_for_diff = winners['Points For'].mean() - losers['Points For'].mean()
    points_against_diff = winners['Points Against'].mean() - losers['Points Against'].mean()
    
    print(f"\nDifference Between Top and Bot average first pick points: {first_pick_diff:.1f}")
    print(f"Difference Between Top and Bot average top 2 pick points: {top_two_diff:.1f}")
    print(f"Difference Between Top and Bot average top 4 pick points: {top_four_diff:.1f}")
    print(f"Difference Between Top and Bot average best pick points: {best_pick_diff:.1f}")
    print(f"Difference Between Top and Bot average points for: {best_pick_diff:.1f}")
    print(f"Difference Between Top and Bot average points against: {best_pick_diff:.1f}")
    # 9. Champions and Runners-Up Analysis
    print("\n9. CHAMPIONS & RUNNERS-UP ANALYSIS")
    print("-" * 60)
    
    # Get teams that finished 1st or 2nd
    champions_df = team_metrics_df[team_metrics_df['Final Place'].isin([1, 2])].copy()
    
    # Analyze by year
    for year in sorted(champions_df['Year'].unique()):
        year_champs = champions_df[champions_df['Year'] == year]
        
        print(f"\n{year} Champions & Runners-Up:")
        print("-" * 40)
        
        # for _, team_row in year_champs.iterrows():
        #     print(f"\n{team_row['Team']} ({team_row['League Name']}) - Place {int(team_row['Final Place'])}")
        #     print(f"  Pick Number: {int(team_row['Pick Number'])}")
        
        # Calculate median and mean pick number for 1st and 2nd place
        pick_numbers = year_champs['Pick Number'].dropna()
        if len(pick_numbers) > 0:
            print(f"\nPick Number Stats for 1st & 2nd place teams in {year}:")
            print(f"  Mean: {pick_numbers.mean():.2f}")
            print(f"  Median: {pick_numbers.median():.1f}")
    
    # 10. Most Drafted Players by Champions
    print("\n10. MOST DRAFTED PLAYERS BY CHAMPIONS & RUNNERS-UP")
    print("-" * 60)
    
    # Strip whitespace from all relevant columns
    all_drafts_df['Team'] = all_drafts_df['Team'].str.strip()
    all_drafts_df['League Name'] = all_drafts_df['League Name'].str.strip()
    champions_df['Team'] = champions_df['Team'].str.strip()
    champions_df['League Name'] = champions_df['League Name'].str.strip()
    champions_df['Year'] = champions_df['Year'].astype(int)
    all_drafts_df['Year'] = all_drafts_df['Year'].astype(int)
    
    # Get all picks by teams that finished 1st or 2nd using merge
    champion_picks = all_drafts_df.merge(
        champions_df[['Team', 'League Name', 'Year']],
        on=['Team', 'League Name', 'Year'],
        how='inner'
    )
    
    # Count player occurrences
    player_counts = champion_picks['Player'].value_counts()
    print(player_counts)
    
    # Filter players drafted more than twice
    frequent_players = player_counts[player_counts > 4]
    
    if len(frequent_players) > 0:
        print("\nPlayers drafted more than twice by 1st/2nd place teams:")
        for player, count in frequent_players.items():
            print(f"  {player}: {count} times")
            
            # Show details for each occurrence
            player_details = champion_picks[champion_picks['Player'] == player][
                ['Team', 'League Name', 'Year', 'Pick', 'Position', 'Points']
            ].sort_values('Year')
            
            for _, detail in player_details.iterrows():
                print(f"    - {detail['Year']} | {detail['Team']} ({detail['League Name']}) | "
                      f"Pick {detail['Pick']} | {detail['Position']} | {detail['Points']:.1f} pts")
    else:
        print("\nNo players were drafted more than twice by 1st/2nd place teams.")
    
    # Additional analysis: By year
    print("\n" + "-" * 60)
    print("Players drafted by champions/runners-up by year:")
    for year in sorted(champion_picks['Year'].unique()):
        year_picks = champion_picks[champion_picks['Year'] == year]
        year_player_counts = year_picks['Player'].value_counts()
        
        # Count total leagues for this year (from champions only)
        total_leagues_year = champions_df[champions_df['Year'] == year]['League Name'].nunique()
        
        # Determine threshold based on number of leagues
        if total_leagues_year >= 7:
            threshold = 3
        elif total_leagues_year >= 6:
            threshold = 2
        else:
            threshold = 2
        
        frequent_in_year = year_player_counts[year_player_counts >= threshold]
        
        if len(frequent_in_year) > 0:
            print(f"\n{year} - Players drafted by multiple 1st/2nd place teams ({total_leagues_year} leagues):")
            for player, count in frequent_in_year.items():
                # Get player stats
                player_data = year_picks[year_picks['Player'] == player]
                avg_points = player_data['Points'].mean()
                avg_pick = player_data['Total Pick'].mean()
                avg_grade = player_data['Draft Grade'].mean()
                
                teams_str = ", ".join(player_data['Team'].unique())
                print(f"  {player}: {count} teams ({teams_str})")
                print(f"    Avg Points: {avg_points:.1f} | Avg Pick: {avg_pick:.1f} | Avg Grade: {avg_grade:.1f}")
        else:
            print(f"\n{year} - No players drafted by {threshold}+ 1st/2nd place teams ({total_leagues_year} leagues)")


else:
    print("\n⚠ No matching data found between standings and draft files.")
    print("Check that team names match exactly between the two data sources.")

print("\n" + "="*60)
print("Analysis complete!")
print("="*60)
print("\nFiles created:")
print("  1. Master_Draft_Data.csv - All draft picks combined")
print("  2. Team_Draft_Metrics.csv - Team-level draft metrics")
print("  3. Draft_Grades_with_Standings_Enhanced.csv - Standings with draft metrics")
print("  4. draft_analysis.png - Visualization of key relationships")