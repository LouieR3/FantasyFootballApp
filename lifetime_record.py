from espn_api.football import League
import pandas as pd
import time
from operator import itemgetter

start_time = time.time()

# Pennoni Younglings
# league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
espn_s2='AEB%2Bzu7FGxYPXt8rgNkQWTV8c4yxT2T3KNZZVkZUVKh9TOdH7iUalV08hSloqYJ5dDtxZVK6d4WC503CH3mH0UkNCPOgbTXYz44W3IJtXsplT%2BLoqNYCU8T7W1HU%2Fgh4PnasvHIkDZgTZFWkUFhcLA0eLkwH8AvYe2%2FCIlhdk7%2FdMeiM0ijsS8vhSYYB8LUhSrB0kuTXE2v85gSIrJQSbs3mPvP5p6pFr3w2OxWicVi9pe8p3eVDhSOLiPMYrPgpuL%2FLBZIGHxhKz5lzGRSL2uTA'
swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}'
# years = [2021, 2022, 2023]
# # EBC League
# league_id = 1118513122
# # Family League
# league_id = 1725372613
# years = [2022, 2023]
# Pennoni Younglings
league_id = 310334683
years = [2022, 2023, 2024]
team_name_to_filter = 'The Golden Receivers'


def lifetime_record(league_id, espn_s2, swid, years, team_name_to_filter):
    # List to store matchup statistics
    all_matchups = [] 
    owner_to_team_name = {}  # Mapping from owner ID to most recent team name
    for year in years:
        print(f"Processing year: {year}")
        
        # Instantiate the league object for the current year
        league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
        settings = league.settings
        reg_season_count = settings.reg_season_count  # Regular season weeks
        
        # Get teams' data
        teams = league.teams
        team_names = [team.team_name for team in teams]
        # team_owners = [team.owner[0] for team in teams]  # Use owner ID as unique identifier
        # print(team_owners)
        team_owners = [team.owners[0]['id'] for team in league.teams]
        # print()
        # print(team_owners)
        
        team_scores = [team.scores for team in teams]  # Each team's weekly scores
        # schedules = [[opponent.owner[0] for opponent in team.schedule] for team in teams]  # Use opponent owner ID
        # print(schedules_df)
        schedules = [[opponent.owners[0]['id'] for opponent in team.schedule] for team in teams]  # Use opponent owner ID
        # print()
        # print(schedules_df)
        # sfd
        
        # Track the most recent team name for each owner
        for owner, name in zip(team_owners, team_names):
            owner_to_team_name[owner] = name  # Always update with the most recent name

        # Convert scores and schedules to DataFrames using team_owner as index
        scores_df = pd.DataFrame(team_scores, index=team_owners)
        schedules_df = pd.DataFrame(schedules, index=team_owners)

        # Iterate through each team and week to determine head-to-head results
        for team_idx, team_owner in enumerate(team_owners):
            for week in range(reg_season_count):
                opponent_owner = schedules_df.iloc[team_idx, week]
                if opponent_owner == team_owner:
                    continue  # Skip self-matches if somehow the team faces itself
                
                # Get scores of the current team and the opponent for the week
                team_score = scores_df.iloc[team_idx, week]
                opponent_score = scores_df.loc[opponent_owner, week]

                # Get the most recent team names from owner_to_team_name
                team_1_name = owner_to_team_name[team_owner]
                team_2_name = owner_to_team_name[opponent_owner]

                # Determine winner and loser
                if team_score > opponent_score:
                    team_record = "1-0"
                    winner = team_1_name
                    loser = team_2_name
                elif team_score < opponent_score:
                    team_record = "0-1"
                    winner = team_2_name
                    loser = team_1_name
                else:
                    continue  # Skip ties for this example
                
                # Calculate points difference and trend
                points_scored = f"{team_score}-{opponent_score}"
                points_diff = abs(team_score - opponent_score)
                trend = f"{winner} W1"

                # Append the result to the matchups list
                all_matchups.append({
                    "Team 1 Owner": team_owner,
                    "Team 2 Owner": opponent_owner,
                    "Team 1": team_1_name,  # Add the most recent team name for Team 1
                    "Team 2": team_2_name,  # Add the most recent team name for Team 2
                    "Record": team_record,
                    "Points Scored": points_scored,
                    "Average Points Difference": points_diff,
                    "Trend": trend
                })

    # Convert the matchups data into a DataFrame
    matchups_df = pd.DataFrame(all_matchups)

    # Display or further process the matchups_df DataFrame as needed
    # print(matchups_df)

    # Create a consistent order for team pairs to avoid duplicates
    matchups_df['Team Pair'] = matchups_df.apply(lambda row: tuple(sorted([row['Team 1 Owner'], row['Team 2 Owner']])), axis=1)

    # # Drop duplicate rows based on 'Team Pair' to ensure only one instance of each pair is processed
    # matchups_df = matchups_df.drop_duplicates(subset=['Team Pair'])

    # filtered_matchups = matchups_df[matchups_df['Team 1'] == 'The Golden Receivers']
    # filtered_matchups = matchups_df[matchups_df['Team 1'] == 'Golden Receivers']
    # filtered_matchups = matchups_df[matchups_df['Team 1'] == 'The Hungry Dogs']
    # Function to get owner ID from the team name
    def get_owner_id_from_team_name(team_name_to_filter, owners_df):
        """
        Returns the owner ID for a given team name from the owners DataFrame.

        Parameters:
        - team_name_to_filter (str): The name of the team to filter.
        - owners_df (pd.DataFrame): DataFrame containing 'ID', 'Display Name', and 'Team Name'.

        Returns:
        - str: The owner ID if found, else 'ID not found'.
        """
        # Filter the DataFrame for the given team name
        filtered_df = owners_df[owners_df['Team Name'] == team_name_to_filter]
        
        if not filtered_df.empty:
            # Return the ID of the first match
            return filtered_df.iloc[0]['ID']
        else:
            return "ID not found"

    def owner_df_creation():
        team_owners = [team.owners for team in league.teams]
        team_names  = [team.team_name for team in league.teams]
        # team_owner = [team.owners[0]['id'] for team in league.teams]
        # team_dict   = dict(zip(team_names, team_owner))

        # Create a list of dictionaries for the DataFrame
        data = []
        count = 0
        for team in team_owners:
            team = team[0]
            team_name = team_names[count]
            data.append({
                "Display Name": team['firstName'] + " " + team['lastName'],
                "ID": team['id'],
                "Team Name": team_name
            })
            count += 1

        # Create the DataFrame
        df = pd.DataFrame(data)
        # print(df)
        # Reverse the team_dict to map IDs to team names
        # id_to_team_name = {id_: team_name for team_name, ids in team_dict.items() for id_ in ids}
        # print(id_to_team_name)
        # # Map team names to the DataFrame based on ID
        # df['Team Name'] = df['ID'].map(id_to_team_name)

        # Display the DataFrame
        return df

    owners_df = owner_df_creation()
    # print(owners_df)

    # Example team name to filter on
    # team_name_to_filter = 'The Golden Receivers'
    # team_name_to_filter = "Daddy's Home"
    # team_name_to_filter = 'The Hungry Dogs'
    # team_name_to_filter = 'Golden Receivers'

    # Get the owner ID corresponding to the given team name
    team_owner_id = get_owner_id_from_team_name(team_name_to_filter, owners_df)
    # print(team_owner_id)

    if team_owner_id:
        # filtered_matchups = matchups_df[matchups_df['Team 1'] == team_name_to_filter]
        # print(filtered_matchups[['Record', 'Points Scored', 'Average Points Difference', 'Team 1', 'Team 2']])

        filtered_matchups = matchups_df[matchups_df['Team 1 Owner'] == team_owner_id]
        # print(filtered_matchups[['Record', 'Points Scored', 'Average Points Difference', 'Team 1', 'Team 2']])

        def calculate_win_percentage(records):
            """
            Calculates and returns the win percentage as a three-decimal string.

            Parameters:
            - records (list of str): A list of strings representing game outcomes, e.g., '1-0' for wins and '0-1' for losses.

            Returns:
            - str: The win percentage formatted to three decimals (e.g., '.500', '.250').
            """
            total_games = len(records)
            if total_games == 0:
                return ".000"  # No games played

            # Count wins based on '1-0' outcomes
            wins = sum(1 for record in records if record == '1-0')

            # Calculate win percentage
            win_percentage = round(wins / total_games, 3)

            # Format the win percentage: keep leading '1' for 1.000, strip leading '0' for others
            if win_percentage == 1.0:
                return "1.000"
            else:
                return f"{win_percentage:.3f}"[1:]

        # Helper function to calculate the record for Team 1
        def calculate_record(records):
            wins = sum([1 for record in records if record == '1-0'])
            losses = len(records) - wins
            return f"{wins}-{losses}"

        # Helper function to calculate total points scored by both teams with rounding to avoid floating point issues
        def avg_points(points_list):
            num_matchups = len(points_list)  # Number of matchups
            team1_total_points = sum(round(float(points.split('-')[0]), 2) for points in points_list)
            team2_total_points = sum(round(float(points.split('-')[1]), 2) for points in points_list)

            # Calculate average for both teams
            team1_avg_points = round(team1_total_points / num_matchups, 2)
            team2_avg_points = round(team2_total_points / num_matchups, 2)
            
            return f"{team1_avg_points}-{team2_avg_points}"

        # Helper function to calculate the average point difference
        def avg_points_difference(points_list):
            num_matchups = len(points_list)  # Number of matchups
            team1_total_points = sum(round(float(points.split('-')[0]), 2) for points in points_list)
            team2_total_points = sum(round(float(points.split('-')[1]), 2) for points in points_list)

            # Calculate average for both teams
            team1_avg_points = round(team1_total_points / num_matchups, 2)
            team2_avg_points = round(team2_total_points / num_matchups, 2)
            return round((team1_avg_points - team2_avg_points), 2)

        # Helper function to update the trend correctly
        def determine_trend(trends):
            last_trend = trends.iloc[-1]
            winner = ' '.join(last_trend.split()[:-1])  # The winner should be the first word in the last trend
            streak = trends.str.contains(winner).sum()  # Count how many times that team appears in the trend list
            return f"{winner} W{streak}"

        # Assuming matchups_df is already generated with all matchups
        filtered_matchups['Team Pair'] = filtered_matchups.apply(lambda row: tuple(sorted([row['Team 1 Owner'], row['Team 2 Owner']])), axis=1)
        # print(filtered_matchups[['Team Pair']])

        # Group by the team pair
        grouped = filtered_matchups.groupby('Team Pair').agg({
            'Record': list,  # Aggregate records as a list to calculate later
            'Points Scored': list,  # Aggregate points scored as a list to sum later
            'Average Points Difference': list,  # Aggregate differences as a list to average later
            'Trend': list  # Aggregate trends as a list to analyze the last trend
        }).reset_index()

        # Process each group to calculate final values
        def process_group(group):
            records = calculate_record(group['Record'])
            win_percentage = calculate_win_percentage(group['Record'])
            points_scored = avg_points(group['Points Scored'])
            avg_diff = avg_points_difference(group['Points Scored'])
            trend = determine_trend(pd.Series(group['Trend']))
            return pd.Series([records, win_percentage, points_scored, avg_diff, trend])

        grouped[['Record', 'Win Percentage', 'Points Scored', 'Average Points Difference', 'Trend']] = grouped.apply(process_group, axis=1)

        # Split the 'Team Pair' back into 'Team 1 Owner' and 'Team 2 Owner'
        grouped[['Team 1 Owner', 'Team 2 Owner']] = pd.DataFrame(grouped['Team Pair'].tolist(), index=grouped.index)

        # Now replace the owner IDs with their most recent team names for display purposes
        grouped['Team 1'] = grouped['Team 1 Owner'].map(owner_to_team_name)
        grouped['Team 2'] = grouped['Team 2 Owner'].map(owner_to_team_name)

        # Drop the 'Team Pair' and 'Owner' columns as they're no longer needed
        grouped = grouped.drop(columns=['Team Pair', 'Team 1 Owner', 'Team 2 Owner'])

        # Ensure team_name_to_filter is always in the 'Team 1' position
        def reorder_teams(row):
            if row['Team 2'] == team_name_to_filter:
                # Swap Team 1 and Team 2
                row['Team 1'], row['Team 2'] = row['Team 2'], row['Team 1']
            return row

        # Apply the reordering function
        grouped = grouped.apply(reorder_teams, axis=1)

        # Convert 'Win Percentage' to float for sorting
        grouped['Win Percentage Float'] = grouped['Win Percentage'].astype(float)

        # Sort by 'Win Percentage'
        grouped = grouped.sort_values(
            by=['Win Percentage', 'Average Points Difference'],
            ascending=[False, False]  # Descending for both columns
        ).reset_index(drop=True)
        grouped = grouped.drop(columns=['Win Percentage Float'])


        # Display the final DataFrame
        # print(grouped)
        return grouped

df = lifetime_record(league_id, espn_s2, swid, years, team_name_to_filter)
print(df)