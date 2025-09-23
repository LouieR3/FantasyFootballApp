from espn_api.football import League
import pandas as pd
import time
from operator import itemgetter
import inflect
import os

start_time = time.time()

# Pennoni Younglings
# league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
espn_s2='AEB%2Bzu7FGxYPXt8rgNkQWTV8c4yxT2T3KNZZVkZUVKh9TOdH7iUalV08hSloqYJ5dDtxZVK6d4WC503CH3mH0UkNCPOgbTXYz44W3IJtXsplT%2BLoqNYCU8T7W1HU%2Fgh4PnasvHIkDZgTZFWkUFhcLA0eLkwH8AvYe2%2FCIlhdk7%2FdMeiM0ijsS8vhSYYB8LUhSrB0kuTXE2v85gSIrJQSbs3mPvP5p6pFr3w2OxWicVi9pe8p3eVDhSOLiPMYrPgpuL%2FLBZIGHxhKz5lzGRSL2uTA'
swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}'
p = inflect.engine()

def lifetime_record_owner(league_id, espn_s2, swid, years, owner_name_to_filter):
    """
    Calculates the lifetime record for a given owner across all seasons they appear in the league.

    Parameters:
    - league_id (int): The league ID.
    - espn_s2 (str): ESPN S2 authentication token.
    - swid (str): SWID authentication token.
    - years (list): List of years to analyze.
    - owner_name_to_filter (str): The Display Name of the owner to filter.

    Returns:
    - pd.DataFrame: A DataFrame summarizing the lifetime record for the owner.
    """
    def grade_to_letter(grade):
        if grade >= 97: return "A+"
        elif grade >= 93: return "A"
        elif grade >= 90: return "A-"
        elif grade >= 87: return "B+"
        elif grade >= 83: return "B"
        elif grade >= 80: return "B-"
        elif grade >= 77: return "C+"
        elif grade >= 73: return "C"
        elif grade >= 70: return "C-"
        elif grade >= 67: return "D+"
        elif grade >= 63: return "D"
        elif grade >= 60: return "D-"
        else: return "F-"
    def owner_df_creation(league):
        """
        Creates a DataFrame mapping owner IDs to Display Names and Team Names for a given league.

        Parameters:
        - league (League): The league object.

        Returns:
        - pd.DataFrame: A DataFrame with columns 'Display Name', 'ID', and 'Team Name'.
        """
        team_owners = [team.owners for team in league.teams]
        team_names = [team.team_name for team in league.teams]

        # Create a list of dictionaries for the DataFrame
        data = []
        for team, team_name in zip(team_owners, team_names):
            team = team[0]
            data.append({
                "Display Name": team['firstName'] + " " + team['lastName'],
                "ID": team['id'],
                "Team Name": team_name.strip()
            })

        # Create the DataFrame
        return pd.DataFrame(data)

    # List to store matchup statistics
    all_matchups = []
    yearly_stats = []

    for year in years:
        print(f"Processing year: {year}")
        league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
        owners_df = owner_df_creation(league)
        # print(f"Owners DataFrame for year {year}:\n{owners_df}")

        # Get the owner ID for the given Display Name
        filtered_owner = owners_df[owners_df['Display Name'] == owner_name_to_filter]
        if filtered_owner.empty:
            print(f"Owner '{owner_name_to_filter}' not found in year {year}. Skipping this year.")
            continue

        owner_id = filtered_owner.iloc[0]['ID']
        team_name = filtered_owner.iloc[0]['Team Name']

        print(f"Found owner '{owner_name_to_filter}' with ID '{owner_id}' and team '{team_name}' for year {year}.")

        # Get teams' data
        teams = league.teams
        team_names = [team.team_name for team in teams]
        team_owners = [team.owners[0]['id'] for team in league.teams]

        team_scores = [team.scores for team in teams]
        schedules = [[opponent.owners[0]['id'] for opponent in team.schedule] for team in teams]

        scores_df = pd.DataFrame(team_scores, index=team_owners)
        schedules_df = pd.DataFrame(schedules, index=team_owners)

        # Matchup data for the year
        year_matchups = []

        for week in range(league.settings.reg_season_count):
            opponent_id = schedules_df.loc[owner_id, week]
            if opponent_id == owner_id:
                continue

            team_score = scores_df.loc[owner_id, week]
            opponent_score = scores_df.loc[opponent_id, week]

            opponent_team_name = owners_df[owners_df['ID'] == opponent_id]['Team Name'].values[0]
            team_2_owner = owners_df[owners_df['Team Name'] == opponent_team_name]['Display Name'].values[0]

            if team_score > opponent_score:
                record = "1-0"
                winner = owner_name_to_filter
                loser = team_2_owner
            elif team_score < opponent_score:
                record = "0-1"
                winner = team_2_owner
                loser = owner_name_to_filter
            else:
                continue

            points_scored = f"{team_score}-{opponent_score}"
            points_diff = abs(team_score - opponent_score)

            trend = f"{winner} W1"  # Default trend for the first game

            year_matchups.append({
                "Year": year,
                "Week": week + 1,
                "Team 1": team_name,
                "Team 1 Owner": owner_name_to_filter,
                "Team 2": opponent_team_name,
                "Team 2 Owner": team_2_owner,
                "Record": record,
                "Points Scored": points_scored,
                "Points Difference": points_diff,
                "Trend": trend,
                "Winner": winner,
                "Loser": loser
            })

        all_matchups.extend(year_matchups)

        # Calculate yearly stats
        wins = sum(1 for matchup in year_matchups if matchup['Record'] == "1-0")
        losses = sum(1 for matchup in year_matchups if matchup['Record'] == "0-1")
        points_scored = sum(float(matchup['Points Scored'].split('-')[0]) for matchup in year_matchups)
        points_against = sum(float(matchup['Points Scored'].split('-')[1]) for matchup in year_matchups)

        # Process draft grade
        league_name = league.settings.name.replace(" 22/23", "")
        file_draft = f"drafts/{league_name} Draft Results {year}.csv"

        if os.path.exists(file_draft):
            draft_df = pd.read_csv(file_draft)
            team_draft = draft_df[draft_df["Team"].str.strip() == team_name]
            avg_draft_grade = team_draft["Draft Grade"].mean().round(2) if not team_draft.empty else None
        else:
            avg_draft_grade = None

        # Get final and regular season standings
        standings = [team.team_name.strip() for team in league.standings()]

        current_week = scores_df.apply(lambda row: row[row != 0.0].last_valid_index(), axis=1).max() + 1

        print(f"Current Week: {current_week}")
        if current_week > 14:
            final_place = standings.index(team_name) + 1
            final_place_ordinal = p.ordinal(final_place)
        else:
            final_place_ordinal = "N/A"

        reg_standings = [team.team_name.strip() for team in league.standings_weekly(14)]
        reg_season_place = reg_standings.index(team_name) + 1
        # Calculate places
        reg_season_place = reg_standings.index(team_name) + 1

        # Convert to ordinal (e.g., 1st, 2nd)
        # final_place_ordinal = p.ordinal(final_place)
        reg_season_place_ordinal = p.ordinal(reg_season_place)

        # Update the DataFrame
        # grouped.at[index, "Regular Season Place"] = reg_season_place_ordinal
        # grouped.at[index, "Final Place"] = final_place_ordinal

        yearly_stats.append({
            "Year": year,
            "Wins": wins,
            "Losses": losses,
            "Points Scored": points_scored,
            "Points Against": points_against,
            "Regular Season Place": reg_season_place_ordinal,
            "Final Place": final_place_ordinal,
            "Draft Grade": avg_draft_grade,
            "Letter Grade": grade_to_letter(avg_draft_grade) if avg_draft_grade else None
        })

    # Create yearly stats DataFrame
    year_df = pd.DataFrame(yearly_stats)

    # Add "All Time" row
    all_time_stats = {
        "Year": "All Time",
        "Wins": year_df["Wins"].sum(),
        "Losses": year_df["Losses"].sum(),
        "Points Scored": year_df["Points Scored"].sum(),
        "Points Against": year_df["Points Against"].sum(),
        "Regular Season Place": "",
        "Final Place": "",
        "Draft Grade": year_df["Draft Grade"].mean().round(2),
        "Letter Grade": grade_to_letter(year_df["Draft Grade"].mean().round(2))
    }
    year_df = pd.concat([year_df, pd.DataFrame([all_time_stats])], ignore_index=True)

    # Convert matchups to DataFrame
    matchups_df = pd.DataFrame(all_matchups)

    
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
        # trends is a Series of strings like ["Louis Rodriguez W1", "Jackson Jansorn W1", ...]
        last_trend = trends.iloc[-1]
        winner = ' '.join(last_trend.split()[:-1])  # extract winner name
        streak = 0

        # walk backwards and count only consecutive wins for the last winner
        for t in reversed(trends):
            if t.startswith(winner):
                streak += 1
            else:
                break

        return f"{winner} W{streak}"

    filtered_matchups = matchups_df[matchups_df['Team 1 Owner'] == owner_name_to_filter]
    filtered_matchups['Team Pair'] = filtered_matchups.apply(lambda row: tuple(sorted([row['Team 1 Owner'], row['Team 2 Owner']])), axis=1)
    print(filtered_matchups[['Team 1 Owner', 'Team 2 Owner', 'Trend']])
    # Group by the team pair
    grouped_records = filtered_matchups.groupby('Team Pair').agg({
        'Record': list,  # Aggregate records as a list to calculate later
        'Points Scored': list,  # Aggregate points scored as a list to sum later
        'Points Difference': list,  # Aggregate differences as a list to average later
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

    grouped_records[['Record', 'Win Percentage', 'Points Scored', 'Points Difference', 'Trend']] = grouped_records.apply(process_group, axis=1)

    # Split the 'Team Pair' back into 'Team 1 Owner' and 'Team 2 Owner'
    grouped_records[['Team 1 Owner', 'Team 2 Owner']] = pd.DataFrame(grouped_records['Team Pair'].tolist(), index=grouped_records.index)
    # Replace 'Lou Rod' with 'Ethyn' in both owner columns
    grouped_records['Team 1 Owner'] = grouped_records['Team 1 Owner'].replace('Lou Rod', 'Ethyn')
    grouped_records['Team 2 Owner'] = grouped_records['Team 2 Owner'].replace('Lou Rod', 'Ethyn')

    # Create a mapping from owner display names to their most recent team names
    owner_to_team_name = {}
    if not matchups_df.empty:
        # Get the most recent year for each owner
        latest_teams = matchups_df.sort_values('Year').drop_duplicates('Team 1 Owner', keep='last')
        for _, row in latest_teams.iterrows():
            owner_to_team_name[row['Team 1 Owner']] = row['Team 1']
        latest_teams2 = matchups_df.sort_values('Year').drop_duplicates('Team 2 Owner', keep='last')
        for _, row in latest_teams2.iterrows():
            owner_to_team_name[row['Team 2 Owner']] = row['Team 2']

    # Now replace the owner display names with their most recent team names for display purposes
    # grouped_records['Team 1'] = grouped_records['Team 1 Owner'].map(owner_to_team_name)
    # grouped_records['Team 2'] = grouped_records['Team 2 Owner'].map(owner_to_team_name)

    # Drop the 'Team Pair' and 'Owner' columns as they're no longer needed
    grouped_records = grouped_records.drop(columns=['Team Pair'])
    # grouped_records = grouped_records.drop(columns=['Team Pair', 'Team 1 Owner', 'Team 2 Owner'])

    # Ensure team_name_to_filter is always in the 'Team 1' position
    def reorder_teams(row):
        if row['Team 2 Owner'] == owner_name_to_filter:
            # Swap Team 1 and Team 2
            row['Team 1 Owner'], row['Team 2 Owner'] = row['Team 2 Owner'], row['Team 1 Owner']
        return row

    # Apply the reordering function
    grouped_records = grouped_records.apply(reorder_teams, axis=1)

    # Convert 'Win Percentage' to float for sorting
    grouped_records['Win Percentage Float'] = grouped_records['Win Percentage'].astype(float)

    # Sort by 'Win Percentage'
    grouped_records = grouped_records.sort_values(
        by=['Win Percentage', 'Points Difference'],
        ascending=[False, False]  # Descending for both columns
    ).reset_index(drop=True)
    grouped_records = grouped_records.drop(columns=['Win Percentage Float'])

    return grouped_records, year_df, matchups_df

def convert_to_int_list(original_list):
    """
    Converts all elements in a list to integers.

    Parameters:
    - original_list (list): A list of elements that can be converted to integers.

    Returns:
    - list: A new list with all elements as integers.
    """
    return [int(item) for item in original_list]

# league_id = 310334683
# league_id = 1118513122
# espn_s2='AEB%2Bzu7FGxYPXt8rgNkQWTV8c4yxT2T3KNZZVkZUVKh9TOdH7iUalV08hSloqYJ5dDtxZVK6d4WC503CH3mH0UkNCPOgbTXYz44W3IJtXsplT%2BLoqNYCU8T7W1HU%2Fgh4PnasvHIkDZgTZFWkUFhcLA0eLkwH8AvYe2%2FCIlhdk7%2FdMeiM0ijsS8vhSYYB8LUhSrB0kuTXE2v85gSIrJQSbs3mPvP5p6pFr3w2OxWicVi9pe8p3eVDhSOLiPMYrPgpuL%2FLBZIGHxhKz5lzGRSL2uTA'
# swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}'

# # Initialize the dropdown for year selection
# year_options = ['2021', '2022', '2023', '2024', '2025']
# # # Convert to integers
# years = convert_to_int_list(year_options)
# # lifetime_record_df, year_df, all_matchups_df = lifetime_record(league_id, espn_s2, swid, years, 'The Golden Receivers')
# owner_name = 'Louis Rodriguez'
# grouped_records, summary, matchups = lifetime_record_owner(league_id, espn_s2, swid, years, owner_name)
# # print(summary)
# print(grouped_records)
# print()
# print(matchups)