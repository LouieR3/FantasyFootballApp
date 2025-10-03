import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

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
# Read the standings data
standings_df = pd.read_csv("drafts/Draft_Grades_with_Standings.csv")

# Initialize columns for pick data
standings_df['Pick Number'] = None
standings_df['First Pick Points'] = None
standings_df['Top Two Pick Points'] = None
standings_df['Top Four Pick Points'] = None

# Set up drafts folder
drafts_folder = "drafts"

# Dictionary to store team data by team name and year
team_pick_data = {}

# Process all draft files
for file in os.listdir(drafts_folder):
    if "Draft Results" in file and file.endswith(".csv"):
        file_path = os.path.join(drafts_folder, file)
        draft_df = pd.read_csv(file_path)
        
        print(f"\nProcessing: {file}")
        
        # Extract year from filename if possible (adjust pattern as needed)
        # Assumes format like "Draft Results 2024.csv"
        year = None
        if "2024" in file:
            year = 2024
        elif "2023" in file:
            year = 2023
        # Add more years as needed
        
        # Process each team's picks
        for team in draft_df['Team'].unique():
            team_picks = draft_df[draft_df['Team'] == team].copy()
            team_picks = team_picks.sort_values('Total Pick')
            
            if len(team_picks) > 0:
                # Extract pick number from first pick (e.g., "1 - 6" -> 6)
                first_pick_str = team_picks.iloc[0]['Pick']
                pick_number = int(first_pick_str.split(' - ')[1])
                
                # Get points for picks
                first_pick_points = team_picks.iloc[0]['Points']
                
                top_two_points = team_picks.iloc[:2]['Points'].sum() if len(team_picks) >= 2 else first_pick_points
                
                top_four_points = team_picks.iloc[:4]['Points'].sum() if len(team_picks) >= 4 else team_picks['Points'].sum()
                
                # Store data with team name and year as key
                key = (team, year) if year else team
                team_pick_data[key] = {
                    'Pick Number': pick_number,
                    'First Pick Points': first_pick_points,
                    'Top Two Pick Points': top_two_points,
                    'Top Four Pick Points': top_four_points
                }

# Update standings dataframe with pick data
for idx, row in standings_df.iterrows():
    team_name = row['Team']
    year = row['Year']
    
    # Try to match with year first, then without year
    key = (team_name, year)
    if key not in team_pick_data:
        key = team_name
    
    if key in team_pick_data:
        standings_df.at[idx, 'Pick Number'] = team_pick_data[key]['Pick Number']
        standings_df.at[idx, 'First Pick Points'] = team_pick_data[key]['First Pick Points']
        standings_df.at[idx, 'Top Two Pick Points'] = team_pick_data[key]['Top Two Pick Points']
        standings_df.at[idx, 'Top Four Pick Points'] = team_pick_data[key]['Top Four Pick Points']

# Save the enhanced CSV
output_file = "Draft_Grades_with_Standings_Enhanced.csv"
standings_df.to_csv(output_file, index=False)
print(f"\n✓ Enhanced CSV saved to: {output_file}")

# ===== ANALYSIS =====
print("\n" + "="*60)
print("DRAFT PICK PERFORMANCE ANALYSIS")
print("="*60)

# Remove rows with missing pick data for analysis
analysis_df = standings_df.dropna(subset=['Pick Number', 'First Pick Points'])

if len(analysis_df) > 0:
    # 1. First Pick Analysis
    print("\n1. FIRST ROUND PICK PERFORMANCE")
    print("-" * 60)
    
    for metric in ['Standing', 'Points For', 'LPI']:
        corr = analysis_df['First Pick Points'].corr(analysis_df[metric])
        # Note: negative correlation with Standing is good (lower standing = better)
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
    
    # 4. Summary statistics
    print("\n4. SUMMARY STATISTICS")
    print("-" * 60)
    
    print("\nFirst Pick Points by Final Standing:")
    standing_groups = analysis_df.groupby('Standing')['First Pick Points'].agg(['mean', 'median', 'count'])
    print(standing_groups)
    
    print("\nAverage Pick Number by Final Standing:")
    pick_by_standing = analysis_df.groupby('Standing')['Pick Number'].mean().sort_index()
    print(pick_by_standing)
    
    # 5. Create visualizations
    print("\n5. CREATING VISUALIZATIONS...")
    print("-" * 60)
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Fantasy Football Draft Pick Performance Analysis', fontsize=16)
    
    # First Pick vs Standing
    axes[0, 0].scatter(analysis_df['First Pick Points'], analysis_df['Standing'])
    axes[0, 0].set_xlabel('First Pick Points')
    axes[0, 0].set_ylabel('Final Standing (lower is better)')
    axes[0, 0].set_title('First Pick vs Standing')
    axes[0, 0].invert_yaxis()
    
    # First Pick vs Points For
    axes[0, 1].scatter(analysis_df['First Pick Points'], analysis_df['Points For'])
    axes[0, 1].set_xlabel('First Pick Points')
    axes[0, 1].set_ylabel('Points For')
    axes[0, 1].set_title('First Pick vs Points For')
    
    # First Pick vs LPI
    axes[0, 2].scatter(analysis_df['First Pick Points'], analysis_df['LPI'])
    axes[0, 2].set_xlabel('First Pick Points')
    axes[0, 2].set_ylabel('LPI')
    axes[0, 2].set_title('First Pick vs LPI')
    
    # Top Two vs Standing
    axes[1, 0].scatter(analysis_df['Top Two Pick Points'], analysis_df['Standing'])
    axes[1, 0].set_xlabel('Top Two Pick Points')
    axes[1, 0].set_ylabel('Final Standing (lower is better)')
    axes[1, 0].set_title('Top 2 Picks vs Standing')
    axes[1, 0].invert_yaxis()
    
    # Top Four vs Standing
    axes[1, 1].scatter(analysis_df['Top Four Pick Points'], analysis_df['Standing'])
    axes[1, 1].set_xlabel('Top Four Pick Points')
    axes[1, 1].set_ylabel('Final Standing (lower is better)')
    axes[1, 1].set_title('Top 4 Picks vs Standing')
    axes[1, 1].invert_yaxis()
    
    # Pick Number vs Standing
    axes[1, 2].scatter(analysis_df['Pick Number'], analysis_df['Standing'])
    axes[1, 2].set_xlabel('First Round Pick Number')
    axes[1, 2].set_ylabel('Final Standing (lower is better)')
    axes[1, 2].set_title('Pick Position vs Standing')
    axes[1, 2].invert_yaxis()
    
    plt.tight_layout()
    plt.savefig('draft_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Saved visualization to: draft_analysis.png")
    
    # 6. Key insights
    print("\n6. KEY INSIGHTS")
    print("-" * 60)
    
    # Best and worst first picks
    best_first = analysis_df.nlargest(3, 'First Pick Points')[['Team', 'First Pick Points', 'Standing']]
    worst_first = analysis_df.nsmallest(3, 'First Pick Points')[['Team', 'First Pick Points', 'Standing']]
    
    print("\nTop 3 First Round Picks by Points:")
    print(best_first.to_string(index=False))
    
    print("\nBottom 3 First Round Picks by Points:")
    print(worst_first.to_string(index=False))
    
    # Winners with top picks
    winners = analysis_df[analysis_df['Standing'] <= 3]
    print(f"\nTop 3 finishers' average first pick points: {winners['First Pick Points'].mean():.1f}")
    print(f"Top 3 finishers' average top 2 pick points: {winners['Top Two Pick Points'].mean():.1f}")
    print(f"Top 3 finishers' average top 4 pick points: {winners['Top Four Pick Points'].mean():.1f}")

else:
    print("\n⚠ No matching data found between standings and draft files.")
    print("Check that team names match exactly between the two data sources.")

print("\n" + "="*60)
print("Analysis complete!")
print("="*60)