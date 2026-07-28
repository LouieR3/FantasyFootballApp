import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from credentials import CRED
import pandas as pd
from espn_api.football import League
from collections import defaultdict
import time

start_time = time.time()

def analyze_playoff_chances_by_record_at_week(leagues, years, target_week, all_playoff_dfs):
    """
    Analyze playoff chances for teams with different records at a specific week
    
    Args:
        leagues: List of league configurations with league_id, espn_s2, swid, name
        years: List of years to analyze
        target_week: The specific week to analyze (e.g., 2 for week 2)
        all_playoff_dfs: DataFrame containing playoff data for all leagues/years
    
    Returns:
        tuple: (aggregated_df, detailed_df)
            - aggregated_df: Overall playoff percentages by record across all leagues/years
            - detailed_df: Detailed breakdown by league and year
    """
    
    playoff_chances = []
    
    for league_config in leagues:
        league_id = league_config['league_id']
        espn_s2 = league_config['espn_s2']
        swid = league_config['swid']
        league_name = league_config['name']

        for year in years:
            try:
                league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
            except Exception as e:
                # print(f"Error initializing league {league_name} for year {year}: {e}")
                continue

            if league_name == "Game of Yards!" and year > 2022:
                print(f"Skipping {league_name} for year {year} due to known issues")
                continue
            # else:
            #     print(f"Analyzing league: {league_name}, year: {year}")
            
            if league_name == "Family League":
                league_name = "Family Fantasy"

            # Filter the playoff DataFrame for the current year and league
            year_playoff_df = all_playoff_dfs[
                (all_playoff_dfs['Year'] == year) & (all_playoff_dfs['League'] == league_name)
            ]
            # print(f"Year playoff df:\n{year_playoff_df}")

            # Combine Team 1 and Team 2 columns to get all teams that participated in the playoffs
            playoff_teams = pd.concat([year_playoff_df['Team 1'], year_playoff_df['Team 2']])
            playoff_teams = playoff_teams[playoff_teams != 'Bye'].unique()

            # print(f"Analyzing week {target_week} for league: {league_name}, year {year}")
            # print(f"Playoff teams: {playoff_teams}")

            # Group teams by their record at the target week
            record_groups = defaultdict(list)
            
            for team in league.teams:
                # Check if team has played enough games to evaluate at target_week
                if len(team.outcomes) >= target_week:
                    wins = team.outcomes[:target_week].count('W')
                    losses = team.outcomes[:target_week].count('L')
                    
                    # Only include if they've actually played target_week games
                    if wins + losses == target_week:
                        record_key = f"{wins}-{losses}"
                        record_groups[record_key].append(team.team_name)

            # Analyze playoff chances for each record
            for record, teams_with_record in record_groups.items():
                if not teams_with_record:  # Skip if no teams have this record
                    continue
                
                # print(f"Teams with record {record} after week {target_week}: {teams_with_record}")
                
                # Calculate how many of these teams made the playoffs
                made_playoffs = [team for team in teams_with_record if team in playoff_teams]
                playoff_percentage = len(made_playoffs) / len(teams_with_record) * 100

                # Append the result to the playoff chances list
                playoff_chances.append({
                    "League": league_name,
                    "Year": year,
                    "Week": target_week,
                    "Record": record,
                    "Total Teams": len(teams_with_record),
                    "Made Playoffs": len(made_playoffs),
                    "Playoff Percentage": playoff_percentage,
                    "Teams": ', '.join(teams_with_record),
                    "Playoff Teams": ', '.join(made_playoffs)
                })

    # Convert the playoff chances list to a DataFrame
    detailed_df = pd.DataFrame(playoff_chances)
    
    if detailed_df.empty:
        print(f"No data found for week {target_week}")
        return pd.DataFrame(), pd.DataFrame()

    # Aggregate totals, made playoffs, and playoff percentage by record
    aggregated_df = detailed_df.groupby(['Record']).agg({
        'Total Teams': 'sum',
        'Made Playoffs': 'sum'
    }).reset_index()

    # Calculate the aggregated playoff percentage
    aggregated_df['Playoff Percentage'] = (aggregated_df['Made Playoffs'] / aggregated_df['Total Teams']) * 100
    
    # Sort by wins (descending), then by losses (ascending)
    def sort_key(record):
        wins, losses = map(int, record.split('-'))
        return (-wins, losses)  # Negative wins for descending, positive losses for ascending
    
    aggregated_df['sort_key'] = aggregated_df['Record'].apply(sort_key)
    aggregated_df = aggregated_df.sort_values('sort_key').drop('sort_key', axis=1).reset_index(drop=True)
    
    # Also sort detailed_df by record
    detailed_df['sort_key'] = detailed_df['Record'].apply(sort_key)
    detailed_df = detailed_df.sort_values(['sort_key', 'League', 'Year']).drop('sort_key', axis=1).reset_index(drop=True)

    # Add some summary statistics
    print(f"\n{'='*80}")
    print(f"PLAYOFF CHANCES BY RECORD AFTER WEEK {target_week}")
    print(f"{'='*80}")
    
    print(f"\nAGGREGATED RESULTS ACROSS ALL LEAGUES/YEARS:")
    print(aggregated_df[['Record', 'Total Teams', 'Made Playoffs', 'Playoff Percentage']].to_string(index=False, float_format='%.1f'))
    
    return aggregated_df, detailed_df


def analyze_multiple_weeks_playoff_chances(leagues, years, weeks_to_analyze, all_playoff_dfs):
    """
    Analyze playoff chances for multiple weeks at once
    
    Args:
        leagues: List of league configurations
        years: List of years to analyze  
        weeks_to_analyze: List of weeks to analyze (e.g., [1, 2, 3, 4])
        all_playoff_dfs: DataFrame containing playoff data
        
    Returns:
        dict: Dictionary with week as key and (aggregated_df, detailed_df) as values
    """
    
    results = {}
    
    for week in weeks_to_analyze:
        print(f"\n{'='*50}")
        print(f"ANALYZING WEEK {week}")
        print(f"{'='*50}")
        
        aggregated_df, detailed_df = analyze_playoff_chances_by_record_at_week(
            leagues, years, week, all_playoff_dfs
        )
        
        results[week] = {
            'aggregated': aggregated_df,
            'detailed': detailed_df
        }
    
    return results


def diagnose_playoff_data_issues(leagues, years, all_playoff_dfs):
    """
    Diagnose potential issues with playoff data
    """
    print("DIAGNOSING POTENTIAL PLAYOFF DATA ISSUES...")
    print("="*60)
    
    issues = []
    
    for league_config in leagues:
        league_name = league_config['name']
        
        for year in years:
            print(f"\nChecking league: {league_name}, year: {year}")
            # Check playoff data for this league/year
            year_playoff_df = all_playoff_dfs[
                (all_playoff_dfs['Year'] == year) & (all_playoff_dfs['League'] == league_name)
            ]
            
            if year_playoff_df.empty:
                # issues.append(f"❌ No playoff data found for {league_name} ({year})")
                continue
            
            # Get unique playoff teams
            playoff_teams = pd.concat([year_playoff_df['Team 1'], year_playoff_df['Team 2']])
            playoff_teams = playoff_teams[playoff_teams != 'Bye'].unique()
            
            print(f"\n{league_name} ({year}):")
            print(f"  - Playoff teams in data: {len(playoff_teams)}")
            print(f"  - Teams: {list(playoff_teams)}")
            
            # Try to get league data
            try:
                league = League(league_id=league_config['league_id'], 
                              year=year, 
                              espn_s2=league_config['espn_s2'], 
                              swid=league_config['swid'])
                
                print(f"  - Total teams in league: {len(league.teams)}")
                print(f"  - Playoff team count setting: {league.settings.playoff_team_count}")
                
                # Check if playoff team count matches
                expected_playoff_teams = league.settings.playoff_team_count
                if len(playoff_teams) != expected_playoff_teams:
                    issues.append(f"⚠️  {league_name} ({year}): Expected {expected_playoff_teams} playoff teams, found {len(playoff_teams)}")
                
                # Check for team name mismatches
                league_team_names = [team.team_name for team in league.teams]
                for playoff_team in playoff_teams:
                    if playoff_team not in league_team_names:
                        issues.append(f"⚠️  {league_name} ({year}): Playoff team '{playoff_team}' not found in league team names")
                        print(f"    Available team names: {league_team_names}")
                
            except Exception as e:
                issues.append(f"❌ Could not load league data for {league_name} ({year}): {e}")
    
    if issues:
        print(f"\n{'='*60}")
        print("ISSUES FOUND:")
        print("="*60)
        for issue in issues:
            print(issue)
    else:
        print(f"\n✅ No obvious data issues detected!")
    
    return issues


def create_playoff_heatmap_data(leagues, years, max_week, all_playoff_dfs):
    """
    Create data suitable for a heatmap showing playoff chances by record and week
    
    Args:
        leagues: List of league configurations
        years: List of years to analyze
        max_week: Maximum week to analyze
        all_playoff_dfs: DataFrame containing playoff data
        
    Returns:
        pd.DataFrame: DataFrame with Record as index, Week as columns, and playoff percentages as values
    """
    
    heatmap_data = []
    
    for week in range(1, max_week + 1):
        aggregated_df, _ = analyze_playoff_chances_by_record_at_week(
            leagues, years, week, all_playoff_dfs
        )
        
        for _, row in aggregated_df.iterrows():
            heatmap_data.append({
                'Week': week,
                'Record': row['Record'],
                'Playoff_Percentage': row['Playoff Percentage'],
                'Total_Teams': row['Total Teams'],
                'Made_Playoffs': row['Made Playoffs']
            })
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    if heatmap_df.empty:
        return pd.DataFrame()
    
    # Pivot to create heatmap format
    pivot_df = heatmap_df.pivot(index='Record', columns='Week', values='Playoff_Percentage')
    pivot_df = pivot_df.fillna(0)  # Fill missing values with 0
    
    return pivot_df


# Example usage function
def example_usage():
    """
    Example of how to use these functions
    """
    louie_s2 = CRED["louie_s2"]
    prahlad_s2 = CRED["prahlad_s2"]
    la_s2 = CRED["la_s2"]
    hannah_s2 = CRED["hannah_s2"]
    ava_s2 = CRED["ava_s2"]
    matt_s2 = CRED["matt_s2"]
    elle_s2 = CRED["elle_s2"]
    # List of league configurations
    year = 2025
    
    # Example league configurations (you would replace with your actual configs)
    leagues = [
        # Pennoni Younglings
        {"league_id": 310334683, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "Pennoni Younglings"},
        # Family League
        {"league_id": 996930954, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "Family League"},
        # EBC League
        {"league_id": 1118513122, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "EBC League"},
        # Pennoni Transportation
        {"league_id": 1339704102, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "0755 Fantasy Football"},
        # Game of Yards
        {"league_id": 1781851, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "Game of Yards!"},
        # Brown Munde
        {"league_id": 367134149, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "Brown Munde"},
        # Turf on Grade League
        {"league_id":1242265374, "year":year, "espn_s2":CRED["turf_s2"], "swid":CRED["prahlad_swid"], "name": "Turf On Grade 2.0"},
        # Las League
        {"league_id": 1049459, "year": year, "espn_s2": la_s2, "swid": CRED["la_swid"], "name": "THE BEST OF THE BEST"},
        # Hannahs League
        {"league_id": 1399036372, "year": year, "espn_s2": hannah_s2, "swid": CRED["hannah_swid"], "name": "Hannahs League"},
        # Avas League
        {"league_id": 417131856, "year": year, "espn_s2": ava_s2, "swid": CRED["ava_swid"], "name": "Avas League"},
        # Matts League
        {"league_id": 261375772, "year": year, "espn_s2": matt_s2, "swid": CRED["matt_swid"], "name": "Matts League"},
        # Elles League
        {"league_id": 1259693145, "year": year, "espn_s2": elle_s2, "swid": CRED["elle_swid"], "name": "Matts League"},
    ]

    years = [2019, 2020, 2021, 2022, 2023, 2024]
    # years = [2021, 2022, 2023, 2024]
    
    # Assuming you have all_playoff_dfs DataFrame available
    all_playoff_dfs = pd.read_csv('all_playoff_dfs.csv')  # Replace with your actual data source
    
    # Analyze a specific week
    # target_week = 14
    # aggregated_df, detailed_df = analyze_playoff_chances_by_record_at_week(
    #     leagues, years, target_week, all_playoff_dfs
    # )

    # First, run the diagnostic
    # issues = diagnose_playoff_data_issues(leagues, years, all_playoff_dfs)
    # print(f"Issues found: {issues}")
    
    # Analyze multiple weeks
    weeks_to_analyze = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # weeks_to_analyze = [3, 4, 5, 6, 7]
    # weeks_to_analyze = [1, 2, 3, 4,/ 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    multi_week_results = analyze_multiple_weeks_playoff_chances(
        leagues, years, weeks_to_analyze, all_playoff_dfs
    )
    
    # print(f"Multi-week Results:\n{multi_week_results}")
    # # Create heatmap data
    # heatmap_df = create_playoff_heatmap_data(
    #     leagues, years, max_week=8, all_playoff_dfs=all_playoff_dfs
    # )
    
    # print("\nHEATMAP DATA (Playoff % by Record and Week):")
    # print(heatmap_df.round(1))
    
    return multi_week_results
    return aggregated_df, detailed_df, multi_week_results, heatmap_df


if __name__ == "__main__":
    # Run example (you would call your specific function here)
    print("Example usage - replace with your actual data and function calls")
    aggregated_df, detailed_df, multi_week_results, heatmap_df = example_usage()
    # print("\nScript execution completed.")
    # print(f"Aggregated DataFrame:\n{aggregated_df}")
    # print(f"Detailed DataFrame:\n{detailed_df}")
    print(f"Multi-week Results:\n{multi_week_results}")
    # print(f"Heatmap DataFrame:\n{heatmap_df}")
    # print()
    print("--- %s seconds ---" % (time.time() - start_time))