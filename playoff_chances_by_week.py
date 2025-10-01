import pandas as pd
from espn_api.football import League
from collections import defaultdict

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
    anomalies = []  # Track teams with good records that missed playoffs
    
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
                missed_playoffs = [team for team in teams_with_record if team not in playoff_teams]
                playoff_percentage = len(made_playoffs) / len(teams_with_record) * 100

                # Check for anomalies - teams with good records that missed playoffs
                wins = int(record.split('-')[0])
                if wins >= 9 and missed_playoffs:  # 9+ wins should almost always make playoffs
                    for team in missed_playoffs:
                        anomalies.append({
                            'Team': team,
                            'League': league_name,
                            'Year': year,
                            'Record': record,
                            'Week': target_week
                        })
                        print(f"🚨 ANOMALY: {team} went {record} in {league_name} ({year}) and MISSED playoffs!")

                # Append the result to the playoff chances list
                playoff_chances.append({
                    "League": league_name,
                    "Year": year,
                    "Week": target_week,
                    "Record": record,
                    "Total Teams": len(teams_with_record),
                    "Made Playoffs": len(made_playoffs),
                    "Missed Playoffs": len(missed_playoffs),
                    "Playoff Percentage": playoff_percentage,
                    "Teams": ', '.join(teams_with_record),
                    "Playoff Teams": ', '.join(made_playoffs),
                    "Missed Playoff Teams": ', '.join(missed_playoffs)
                })

    # Convert the playoff chances list to a DataFrame
    detailed_df = pd.DataFrame(playoff_chances)
    anomalies_df = pd.DataFrame(anomalies)
    
    if detailed_df.empty:
        print(f"No data found for week {target_week}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Print anomalies summary
    if not anomalies_df.empty:
        print(f"\n{'='*80}")
        print(f"ANOMALIES DETECTED - Teams with 9+ wins that missed playoffs:")
        print(f"{'='*80}")
        for record in sorted(anomalies_df['Record'].unique(), key=lambda x: int(x.split('-')[0]), reverse=True):
            record_anomalies = anomalies_df[anomalies_df['Record'] == record]
            print(f"\n{record} teams that missed playoffs ({len(record_anomalies)} total):")
            for _, row in record_anomalies.iterrows():
                print(f"  - {row['Team']} ({row['League']}, {row['Year']})")

    # Aggregate totals, made playoffs, and playoff percentage by record
    aggregated_df = detailed_df.groupby(['Record']).agg({
        'Total Teams': 'sum',
        'Made Playoffs': 'sum',
        'Missed Playoffs': 'sum'
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
    display_cols = ['Record', 'Total Teams', 'Made Playoffs', 'Missed Playoffs', 'Playoff Percentage']
    print(aggregated_df[display_cols].to_string(index=False, float_format='%.1f'))
    
    return aggregated_df, detailed_df, anomalies_df


def analyze_multiple_weeks_playoff_chances(leagues, years, weeks_to_analyze, all_playoff_dfs, output_filename='playoff_chances_by_week.xlsx'):
    """
    Analyze playoff chances for multiple weeks at once and save to Excel
    
    Args:
        leagues: List of league configurations
        years: List of years to analyze  
        weeks_to_analyze: List of weeks to analyze (e.g., [1, 2, 3, 4])
        all_playoff_dfs: DataFrame containing playoff data
        output_filename: Name of the Excel file to create (default: 'playoff_chances_by_week.xlsx')
        
    Returns:
        dict: Dictionary with week as key and (aggregated_df, detailed_df, anomalies_df) as values
    """
    
    results = {}
    
    # Create Excel writer
    with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
        
        for week in weeks_to_analyze:
            print(f"\n{'='*80}")
            print(f"ANALYZING WEEK {week}")
            print(f"{'='*80}")
            
            aggregated_df, detailed_df, anomalies_df = analyze_playoff_chances_by_record_at_week(
                leagues, years, week, all_playoff_dfs
            )
            
            results[week] = {
                'aggregated': aggregated_df,
                'detailed': detailed_df,
                'anomalies': anomalies_df
            }
            
            # Write aggregated data to Excel with sheet name like "Week_1", "Week_2", etc.
            if not aggregated_df.empty:
                sheet_name = f'Week_{week}'
                aggregated_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Auto-adjust column widths for better readability
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Create a summary sheet with all weeks side by side
        print(f"\n{'='*80}")
        print("CREATING SUMMARY SHEET")
        print(f"{'='*80}")
        
        summary_data = []
        for week in weeks_to_analyze:
            if results[week]['aggregated'].empty:
                continue
            
            week_df = results[week]['aggregated'][['Record', 'Playoff Percentage']].copy()
            week_df.columns = ['Record', f'Week {week} %']
            
            if not summary_data:
                summary_data = week_df
            else:
                summary_data = summary_data.merge(week_df, on='Record', how='outer')
        
        if not summary_data.empty:
            # Sort by record (best to worst)
            def sort_key(record):
                wins, losses = map(int, record.split('-'))
                return (-wins, losses)
            
            summary_data['sort_key'] = summary_data['Record'].apply(sort_key)
            summary_data = summary_data.sort_values('sort_key').drop('sort_key', axis=1).reset_index(drop=True)
            
            # Write summary to first sheet
            summary_data.to_excel(writer, sheet_name='Summary_All_Weeks', index=False)
            
            # Format summary sheet
            worksheet = writer.sheets['Summary_All_Weeks']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 20)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Create an anomalies sheet if there are any
        all_anomalies = []
        for week in weeks_to_analyze:
            if not results[week]['anomalies'].empty:
                all_anomalies.append(results[week]['anomalies'])
        
        if all_anomalies:
            anomalies_combined = pd.concat(all_anomalies, ignore_index=True)
            anomalies_combined = anomalies_combined.sort_values(['Week', 'Record', 'League', 'Year'])
            anomalies_combined.to_excel(writer, sheet_name='Anomalies', index=False)
            
            # Format anomalies sheet
            worksheet = writer.sheets['Anomalies']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"\n{'='*80}")
    print(f"✅ Excel file created: {output_filename}")
    print(f"{'='*80}")
    print(f"Sheets created:")
    print(f"  - Summary_All_Weeks: Playoff percentages for all weeks side-by-side")
    for week in weeks_to_analyze:
        if not results[week]['aggregated'].empty:
            print(f"  - Week_{week}: Detailed breakdown for week {week}")
    if all_anomalies:
        print(f"  - Anomalies: Teams with good records that missed playoffs")
    
    return results


def create_multi_week_analysis(leagues, years, all_playoff_dfs, output_filename='playoff_analysis_weeks_1_14.xlsx'):
    """
    Convenience function to analyze weeks 1-14 and create Excel file
    
    Args:
        leagues: List of league configurations
        years: List of years to analyze
        all_playoff_dfs: DataFrame containing playoff data
        output_filename: Name of the Excel file (default: 'playoff_analysis_weeks_1_14.xlsx')
        
    Returns:
        dict: Results dictionary with data for each week
    """
    
    weeks_to_analyze = list(range(1, 15))  # Weeks 1 through 14
    
    print(f"Analyzing playoff chances for weeks 1-14 across all leagues and years...")
    print(f"This may take a few minutes...\n")
    
    results = analyze_multiple_weeks_playoff_chances(
        leagues, 
        years, 
        weeks_to_analyze, 
        all_playoff_dfs,
        output_filename
    )
    
    return results

# Example usage function
def example_usage():
    """
    Example of how to use these functions
    """
    
    louie_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
    prahlad_s2 = "AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4"
    la_s2 = "AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D"
    hannah_s2 = "AEBy%2FXPWgz4DEVTKf5Z1y9k7Lco6fLP6tO80b1nl5a1p9CBOLF0Z0AlBcStZsywrAAdgHUABmm7G9Cy8l2IJCjgEAm%2BT5NHVNFPgtfDPjT0ei81RfEzwugF1UTbYc%2FlFrpWqK9xL%2FQvSoCW5TV9H4su6ILsqHLnI4b0xzH24CIDIGKInjez5Ivt8r1wlufknwMWo%2FQ2QaJfm6VPlcma3GJ0As048W4ujzwi68E9CWOtPT%2FwEQpfqN3g8WkKdWYCES0VdWmQvSeHnphAk8vlieiBTsh3BBegGULXInpew87nuqA%3D%3D"
    ava_s2 = "AEBL5xTPsfrhYhP04Dc%2FHGojCvZAK7pmvEtoKwm%2FDUFjM86FeGyFUfomgi6VkRTlpDC0bXAOQyOy9UfdWQm%2FAbZUPauwvbn%2Bfn9pkW4BTpHapwqDSJyXSMWoH7GJyQjI8Oq7AF4bkD8A5Vm31unAN0dn6ar5h2YdSy7USKAbm8vH%2BVmQ3yAoT8QQ23V4mCQM7ztjkA3hkEYf%2BFfyB1ASlVb%2B0286sPBoPaaESQv45qLuCUG6883kq4SXq7PUACFpAUICO7ahS%2F06pr1Gg%2BzhO79cea6jXKNJsgRYQLQmHea7Yw%3D%3D"
    matt_s2 = "AEApTMk4bKXLS%2ByFC85I7AlYVnFOTx28Qn8C5ElSPEEY3%2BV6Jn0RzRDIb1H39fmRU9ABSWxJBwDaxottGDrfteMllIgOnF6QDw%2Bv2v6ox%2FDJGV4DJav5ntyQn3oihvOstkQsXIvSGD5jFAQFTJcb6GOCe9jG0WuATob3%2BU5fi2fZdZJ%2Blpx65ty5SNBe8znFW3T52EfNFbEOrCFW13IHqmEUiO9%2BooinLTMwIhsD2Txzg7peD6bKhs%2BOQL7pqc2xE1x084MSLRZ33UZioi8aNJdJx%2FBO8BUaBy%2FB3VFUkB2S1CFUUnlY5S96e98QD9vgmLY%3D"
    elle_s2 = "AECfQX9GAenUR7mbrWgFnjVxXJJEz4u%2BKEZUVBlsfc%2FnRHEmQJhqDOvGAxCjq%2BpWobEwQaiNR2L2kFAZRcIxX9y3pWjZd%2BHuV4KL0gq495A4Ve%2Fnza1Ap%2BGM5hQwgIpHqKL%2BosHEXvXVBfUxUmmX%2BG7HkNIir0lAZIX3CS68XAO6KXX5aEl%2BjUsc8pYqNAiaEiCEyLdULrUimPcog39bHlbmIuwYHXf2LsMHWUdQ1RrDGP%2BOIpKXx257vQLxnW%2FI72Eg7W%2Fg6Htwx1TpG5U9eMXEwQp0UEKHanE0YSgnTTELIw%3D%3D"
    # List of league configurations
    year = 2025
    
    # Example league configurations (you would replace with your actual configs)
    leagues = [
        # Pennoni Younglings
        {"league_id": 310334683, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Pennoni Younglings"},
        # Family League
        {"league_id": 996930954, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Family League"},
        # EBC League
        {"league_id": 1118513122, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "EBC League"},
        # Pennoni Transportation
        {"league_id": 1339704102, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "0755 Fantasy Football"},
        # Game of Yards
        {"league_id": 1781851, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Game of Yards!"},
        # Brown Munde
        {"league_id": 367134149, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Brown Munde"},
        # Turf on Grade League
        {"league_id":1242265374, "year":year, "espn_s2":"AECbYb8WaMMCKHklAi740KXDsHbXHTaW5mI%2FLPUegrKbIb6MRovW0L4NPTBpsC%2Bc2%2Fn7UeX%2Bac0lk3KGEwyeI%2FgF9WynckxWNIfe8m8gh43s68UyfhDj5K187Fj5764WUA%2BTlCh1AF04x9xnKwwsneSvEng%2BfACneWjyu7hJy%2FOVWsHlEm3nfMbU7WbQRDBRfkPy7syz68C4pgMYN2XaU1kgd9BRj9rwrmXZCvybbezVEOEsApniBWRtx2lD3yhJnXYREAupVlIbRcd3TNBP%2F5Frfr6pnMMfUZrR9AP1m1OPGcQ0bFaZbJBoAKdWDk%2F6pJs%3D", "swid":'{4C1C5213-4BB5-4243-87AC-0BCB2D637264}', "name": "Turf On Grade 2.0"},
        # Las League
        {"league_id": 1049459, "year": year, "espn_s2": la_s2, "swid": "{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}", "name": "THE BEST OF THE BEST"},
        # Hannahs League
        {"league_id": 1399036372, "year": year, "espn_s2": hannah_s2, "swid": "{46993514-CB12-4CFA-9935-14CB122CFA5F}", "name": "Hannahs League"},
        # Avas League
        {"league_id": 417131856, "year": year, "espn_s2": ava_s2, "swid": "{9B611343-247D-458B-88C3-50BB33789365}", "name": "Avas League"},
        # Matts League
        {"league_id": 261375772, "year": year, "espn_s2": matt_s2, "swid": "{F8FBCEF4-616F-45CD-BBCE-F4616FE5CD64}", "name": "Matts League"},
        # Elles League
        {"league_id": 1259693145, "year": year, "espn_s2": elle_s2, "swid": "{B6F0817B-1DC0-4E29-B020-68B8E12B6931}", "name": "Matts League"},
    ]
    years = [2019, 2020, 2021, 2022, 2023, 2024]
    
    # Assuming you have all_playoff_dfs DataFrame available
    all_playoff_dfs = pd.read_csv('all_playoff_dfs.csv')  # Replace with your actual data source
    
    # Assuming you have all_playoff_dfs DataFrame available
    # all_playoff_dfs = your_playoff_dataframe
    
    # Analyze multiple weeks
    weeks_to_analyze = [1, 2, 3, 4, 5]
    weeks_to_analyze = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    multi_week_results = analyze_multiple_weeks_playoff_chances(
        leagues, years, weeks_to_analyze, all_playoff_dfs
    )
    
    return multi_week_results


if __name__ == "__main__":
    # Run example (you would call your specific function here)
    print("Example usage - replace with your actual data and function calls")
    example_usage()