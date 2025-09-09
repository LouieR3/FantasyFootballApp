import pandas as pd
from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
# import xlsxwriter
from itertools import combinations
import itertools
import math
import numpy as np
import random
import openpyxl

start_time = time.time()

louie_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
prahlad_s2 = "AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4"
la_s2 = "AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D"
hannah_s2 = "AEBy%2FXPWgz4DEVTKf5Z1y9k7Lco6fLP6tO80b1nl5a1p9CBOLF0Z0AlBcStZsywrAAdgHUABmm7G9Cy8l2IJCjgEAm%2BT5NHVNFPgtfDPjT0ei81RfEzwugF1UTbYc%2FlFrpWqK9xL%2FQvSoCW5TV9H4su6ILsqHLnI4b0xzH24CIDIGKInjez5Ivt8r1wlufknwMWo%2FQ2QaJfm6VPlcma3GJ0As048W4ujzwi68E9CWOtPT%2FwEQpfqN3g8WkKdWYCES0VdWmQvSeHnphAk8vlieiBTsh3BBegGULXInpew87nuqA%3D%3D"
ava_s2 = "AEBL5xTPsfrhYhP04Dc%2FHGojCvZAK7pmvEtoKwm%2FDUFjM86FeGyFUfomgi6VkRTlpDC0bXAOQyOy9UfdWQm%2FAbZUPauwvbn%2Bfn9pkW4BTpHapwqDSJyXSMWoH7GJyQjI8Oq7AF4bkD8A5Vm31unAN0dn6ar5h2YdSy7USKAbm8vH%2BVmQ3yAoT8QQ23V4mCQM7ztjkA3hkEYf%2BFfyB1ASlVb%2B0286sPBoPaaESQv45qLuCUG6883kq4SXq7PUACFpAUICO7ahS%2F06pr1Gg%2BzhO79cea6jXKNJsgRYQLQmHea7Yw%3D%3D"
matt_s2 = "AEApTMk4bKXLS%2ByFC85I7AlYVnFOTx28Qn8C5ElSPEEY3%2BV6Jn0RzRDIb1H39fmRU9ABSWxJBwDaxottGDrfteMllIgOnF6QDw%2Bv2v6ox%2FDJGV4DJav5ntyQn3oihvOstkQsXIvSGD5jFAQFTJcb6GOCe9jG0WuATob3%2BU5fi2fZdZJ%2Blpx65ty5SNBe8znFW3T52EfNFbEOrCFW13IHqmEUiO9%2BooinLTMwIhsD2Txzg7peD6bKhs%2BOQL7pqc2xE1x084MSLRZ33UZioi8aNJdJx%2FBO8BUaBy%2FB3VFUkB2S1CFUUnlY5S96e98QD9vgmLY%3D"
# List of league configurations
year = 2025
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
    # Other Prahlad League
    {"league_id":1242265374, "year":year, "espn_s2":"AECbYb8WaMMCKHklAi740KXDsHbXHTaW5mI%2FLPUegrKbIb6MRovW0L4NPTBpsC%2Bc2%2Fn7UeX%2Bac0lk3KGEwyeI%2FgF9WynckxWNIfe8m8gh43s68UyfhDj5K187Fj5764WUA%2BTlCh1AF04x9xnKwwsneSvEng%2BfACneWjyu7hJy%2FOVWsHlEm3nfMbU7WbQRDBRfkPy7syz68C4pgMYN2XaU1kgd9BRj9rwrmXZCvybbezVEOEsApniBWRtx2lD3yhJnXYREAupVlIbRcd3TNBP%2F5Frfr6pnMMfUZrR9AP1m1OPGcQ0bFaZbJBoAKdWDk%2F6pJs%3D", "swid":'{4C1C5213-4BB5-4243-87AC-0BCB2D637264}', "name": "Brown Munde"},
    # Las League
    {"league_id": 1049459, "year": year, "espn_s2": la_s2, "swid": "{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}", "name": "THE BEST OF THE BEST"},
    # Hannahs League
    {"league_id": 1399036372, "year": year, "espn_s2": hannah_s2, "swid": "{46993514-CB12-4CFA-9935-14CB122CFA5F}", "name": "Hannahs League"},
    # Avas League
    {"league_id": 417131856, "year": year, "espn_s2": ava_s2, "swid": "{9B611343-247D-458B-88C3-50BB33789365}", "name": "Avas League"},
    # Matts League
    {"league_id": 261375772, "year": year, "espn_s2": matt_s2, "swid": "{F8FBCEF4-616F-45CD-BBCE-F4616FE5CD64}", "name": "Matts League"},
]

# Loop through each league configuration
for league_config in leagues:
    try:
        league = League(
            league_id=league_config["league_id"],
            year=league_config["year"],
            espn_s2=league_config["espn_s2"],
            swid=league_config["swid"],
        )
        print(f"Processing league: {league_config['name']}")
    
        settings = league.settings

        leagueName = settings.name.replace(" 22/23", "")
        fileName = leagueName + " "+str(year)
        file = leagueName + ".xlsx"

        # team_owners = [team.owners for team in league.teams]
        team_names = [team.team_name for team in league.teams]
        team_scores = [team.scores for team in league.teams] 
        team_scores_x = [team.scores for team in league.teams] 
        schedules = []
        for team in league.teams:
            schedule = [opponent.team_name for opponent in team.schedule]
            schedules.append(schedule)

        # Precompute current week 
        current_week = None
        for week in range(1, settings.reg_season_count+1):
            scoreboard = league.scoreboard(week)
            if not any(matchup.home_score for matchup in scoreboard):
                current_week = week
                break 
        # print()
        if current_week is None:
            current_week = settings.reg_season_count
        elif current_week != settings.reg_season_count:
            current_week -= 1
        # current_week = 17
        # print(current_week)
        # Store data in DataFrames 
        scores_df = pd.DataFrame(team_scores, index=team_names)
        schedules_df = pd.DataFrame(schedules, index=team_names)
        # print(scores_df)
        # print()
        # print(schedules_df)
        # Create empty dataframe  
        records_df = pd.DataFrame(index=team_names, columns=team_names)

        # Fill diagonal with team names
        records_df.fillna('', inplace=True) 

        # Initialize a DataFrame to store total wins for each team against all schedules
        total_wins_weekly_df = pd.DataFrame(0, columns=team_names, index=team_names)

        # Initialize an empty DataFrame to store LPI scores for each week
        lpi_weekly_df = pd.DataFrame()

        # Iterate through each week
        for week in range(1, current_week+1):
            # Initialize a DataFrame to store total wins for each team against all schedules for this week
            total_wins_weekly_df = pd.DataFrame(0, columns=team_names, index=team_names)

            # Iterate through teams (similar to your previous code)
            for team in team_names:
                # Get team scores
                team_scores = scores_df.loc[team].tolist() 
                # Iterate through opponents
                for opp in team_names:
                    
                    # Compare scores
                    wins = 0
                    losses = 0
                    ties = 0
                    for i in range(week):
                        # Get opponent schedule
                        opp_schedule = schedules_df.loc[opp].tolist()
                        
                        # Get opponent scores
                        opp_scores = [scores_df.loc[o][i] for i, o in enumerate(opp_schedule)]
                        if team == opp:
                            # Get team's opponent this week

                            opp_team = schedules_df.loc[team, i]
                            
                            # Get team and opponent score
                            team_score = scores_df.loc[team, i]
                            opp_score = scores_df.loc[opp_team, i]

                            if team_score > opp_score:
                                wins += 1
                            elif team_score < opp_score:
                                losses += 1
                            else:
                                ties += 1

                        else:
                            # Check if opponent is the same 
                            if opp == schedules_df.loc[team, i]:
                                # Opponent is the same, get correct scores
                                team_score = scores_df.loc[team, i]
                                opp_score = scores_df.loc[schedules_df.loc[team, i], i]

                            else:  
                                # Opponent is different
                                opp_schedule = schedules_df.loc[opp].tolist()
                                opp_scores = [scores_df.loc[o][i] for i, o in enumerate(opp_schedule)]
                                team_score = team_scores[i]
                                opp_score = opp_scores[i]

                            # Compare scores
                            if team_score > opp_score:
                                wins += 1
                            elif team_score < opp_score:
                                losses += 1
                            else:
                                ties += 1
                    
                    # Record result
                    record = f"{wins}-{losses}-{ties}"
                    records_df.at[team, opp] = record 
                    # Update the total wins DataFrame for this week
                    total_wins_weekly_df.at[team, opp] = wins  # Set wins for all opponents

            # Calculate LPI scores for this week
            team_wins = total_wins_weekly_df.sum(axis=1)
            schedule_wins = [sum(total_wins_weekly_df[team]) for team in team_names]
            num_teams_in_league = len(team_names)
            lpi_scores = ((team_wins - schedule_wins) * (12 / num_teams_in_league)).round().astype(int)
            week_name = "Week " + str(week)
            # Add LPI scores for this week to the weekly DataFrame
            lpi_weekly_df[week_name] = lpi_scores
            lpi_weekly_df = lpi_weekly_df.sort_values(by=[week_name], ascending=[False])
            # lpi_df.reset_index(drop=True, inplace=True)
        # Display the DataFrame with LPI scores for each week

        # Calculate actual wins
        actual_records = records_df.values.diagonal()
        # Calculate the total wins for each team
        team_wins = total_wins_weekly_df.sum(axis=1)
        avg_team_wins = team_wins / len(team_names)
        # Calculate expected wins
        expected_wins = total_wins_weekly_df.mean(axis=1)

        # Calculate differences
        differences = avg_team_wins - total_wins_weekly_df.values.diagonal()
        # Create a DataFrame for ranking
        rank_df = pd.DataFrame({
            'Team': team_names,
            'Expected Wins': avg_team_wins,
            'Difference': differences,
            'Record': actual_records,
        })
        # print(rank_df)
        # Create schedule_rank_df
        schedule_rank_df = pd.DataFrame({
            'Teams': rank_df['Team'],
            'Wins Against Schedule': [sum(total_wins_weekly_df[team]) / len(team_names) for team in rank_df['Team']],
            'Record': rank_df['Record']
        })
        # print(schedule_rank_df)


        # Function to format the change value
        def format_change(change):
            if change > 0:
                return f'↑{change}'
            elif change < 0:
                return f'↓{abs(change)}'
            else:
                return str(change)

        # lpi_weekly_df.insert(loc = 0, column = 'Teams', value = lpi_weekly_df.index)
        # lpi_weekly_df.reset_index(drop=True, inplace=True)

        if current_week > 1:
            # Calculate the "Change from last week" column
            lpi_weekly_df['Change From Last Week'] = lpi_weekly_df[week_name] - lpi_weekly_df['Week ' + str(week - 1)]
            # Apply the formatting function to the "Change from last week" column
            lpi_weekly_df['Change From Last Week'] = lpi_weekly_df['Change From Last Week'].apply(format_change)
        else:
            lpi_weekly_df['Change From Last Week'] = 0

        # Display the updated DataFrame
        print(lpi_weekly_df)
        lpi_df = lpi_weekly_df[[week_name, 'Change From Last Week']]
        lpi_df = lpi_df.rename(columns={week_name: "Louie Power Index (LPI)"})
        lpi_df.insert(loc = 0, column = 'Teams', value = lpi_df.index)
        lpi_df.reset_index(drop=True, inplace=True)
        lpi_df.index = lpi_df.index + 1 
        lpi_df.insert(loc = 2, column = 'Record', value = "")
        # Create a dictionary to map team names to records from rank_df
        team_to_record = dict(zip(rank_df['Team'], rank_df['Record']))

        # Map the records to lpi_df based on matching team names
        lpi_df['Record'] = lpi_df['Teams'].map(team_to_record)
        # team_dict = dict(zip(team_names, team_owners))

        # Apply dictionary mapping to Teams column
        # lpi_df.insert(1, "Owner", lpi_df['Teams'].map(team_dict))
        print(lpi_df)

        matchup_results = []
        # Iterate through each week's matchups
        for week in range(1, current_week + 1):
            matchups = league.scoreboard(week)
            for matchup in matchups:
                if matchup.home_score == 0 or matchup.away_score == 0:
                    # Skip this matchup
                    continue
                home_team = matchup.home_team.team_name
                away_team = matchup.away_team.team_name
                # Get LPI for home and away teams for this week
                home_lpi = lpi_weekly_df.at[home_team, 'Week ' + str(week)]
                away_lpi = lpi_weekly_df.at[away_team, 'Week ' + str(week)]
                # Calculate LPI difference
                higher_lpi = max(home_lpi, away_lpi)
                lower_lpi = min(home_lpi, away_lpi)
                lpi_difference = higher_lpi - lower_lpi
                # Determine the winner of the matchup
                winner = home_team if matchup.home_score > matchup.away_score else away_team
                # Record the matchup results and LPI differences
                matchup_result = {
                    'Week': week,
                    'Home Team': home_team,
                    'Away Team': away_team,
                    'Home LPI': home_lpi,
                    'Away LPI': away_lpi,
                    'LPI Difference': lpi_difference,
                    'Winner': winner
                }
                # Append the dictionary to the list
                matchup_results.append(matchup_result)
        # Convert the list of matchup results to a DataFrame
        matchup_results_df = pd.DataFrame(matchup_results)
        # Find the biggest upsets based on LPI difference
        biggest_upsets = matchup_results_df.nlargest(30, 'LPI Difference')
        # Filter for rows where the LPI_Difference is negative and the AwayTeam won
        upsets_df = biggest_upsets[((biggest_upsets['Winner'] == biggest_upsets['Away Team']) & (biggest_upsets['Home LPI'] > biggest_upsets['Away LPI'])) | ((biggest_upsets['Winner'] == biggest_upsets['Home Team']) & (biggest_upsets['Away LPI'] > biggest_upsets['Home LPI']))]
        upsets_df.reset_index(drop=True, inplace=True)

        schedule_rank_df = schedule_rank_df.sort_values(by=['Wins Against Schedule'], ascending=[True])
        schedule_rank_df.reset_index(drop=True, inplace=True)
        schedule_rank_df.index = schedule_rank_df.index + 1 
        # print(schedule_rank_df)

        # Sort the DataFrame by total wins and difference
        rank_df = rank_df.sort_values(by=['Expected Wins', 'Difference'], ascending=[False, True])
        rank_df.reset_index(drop=True, inplace=True)
        rank_df.index = rank_df.index + 1

        def oddsCalculator():
            team_totals = [team.points_for for team in league.teams]
            reg_season = settings.reg_season_count
            def standard_deviation(values):
                avg = sum(values) / len(values)
                square_diffs = [(value - avg) ** 2 for value in values]
                avg_square_diff = sum(square_diffs) / len(values)
                return math.sqrt(avg_square_diff)

            # Initialize a dictionary to store the results
            team_data = {}

            # Define a function to calculate the dynamic std_dev_factor based on the current week
            def calculate_dynamic_std_dev_factor(current_week, total_weeks, initial_std_dev_factor, min_std_dev_factor):
                # Calculate a factor that decreases as the season progresses
                week_factor = current_week / total_weeks
                # Use the factor to interpolate between initial and minimum std_dev_factors
                dynamic_std_dev_factor = initial_std_dev_factor - (initial_std_dev_factor - min_std_dev_factor) * week_factor
                return dynamic_std_dev_factor

            # Set initial and maximum std_dev_factors
            initial_std_dev_factor = 1  # Initial factor for week 1
            min_std_dev_factor  = 0.5  # Maximum factor for later weeks

            # Calculate the dynamic std_dev_factor for the current week
            dynamic_std_dev_factor = calculate_dynamic_std_dev_factor(current_week, reg_season, initial_std_dev_factor, min_std_dev_factor)
            # print(dynamic_std_dev_factor)

            # Calculate average score and standard deviation based on team totals
            for i in range(len(team_names)):
                team_name = team_names[i]
                total_points = team_totals[i]
                team_score_x = team_scores_x[i]
                
                non_zero_values = []
                for score in team_score_x:
                    if score != 0.0:
                        non_zero_values.append(score)
                    else:
                        break
                
                # Calculate the average score (total points divided by weeks played)
                average_score = total_points / current_week
                
                # Calculate the standard deviation using the standard_deviation function
                std_dev = standard_deviation(non_zero_values) * dynamic_std_dev_factor
                
                team_data[team_name] = {'average_score': average_score, 'std_dev': std_dev}
            # Define the number of Monte Carlo simulations
            num_simulations = 10000
            # Function to simulate a season
            def simulate_season(team_data, schedules_df):
                standings = {team: 0 for team in team_data}
                # Simulate each week's matchups
                for week in range(current_week, schedules_df.shape[1]):
                    week_schedule = schedules_df.iloc[:, week].to_list()
                    # print(week_schedule)
                    random.shuffle(week_schedule)
                    # print(week_schedule)
                    # print()
                    # Simulate each matchup
                    for i in range(0, len(week_schedule), 2):
                        team1 = week_schedule[i]
                        team2 = week_schedule[i + 1]
                        # Generate random scores based on team data
                        score1 = random.gauss(team_data[team1]['average_score'], team_data[team1]['std_dev'])
                        score2 = random.gauss(team_data[team2]['average_score'], team_data[team2]['std_dev'])
                        if score1 > score2:
                            standings[team1] += 2
                        elif score1 < score2:
                            standings[team2] += 2
                        else:
                            standings[team1] += 1
                            standings[team2] += 1

                # Sort the standings by both total points and average score
                sorted_standings = sorted(standings.items(), key=lambda x: (-x[1], team_data[x[0]]['average_score']), reverse=True)
                return [team for team, _ in sorted_standings]

            # Dictionary to store the final standings for each simulation
            final_standings = {team: [0] * len(team_data) for team in team_data}

            # Run Monte Carlo simulations
            for _ in range(num_simulations):
                simulated_season = simulate_season(team_data, schedules_df)
                for i, team in enumerate(simulated_season):
                    final_standings[team][i] += 1

            for team in final_standings:
                final_standings[team] = final_standings[team][::-1]
            # Calculate the percentage chance for each position
            position_chances = {i + 1: {} for i in range(len(team_data))}
            for position in range(1, len(team_data) + 1):
                for team in team_data:
                    team_index = list(team_data.keys()).index(team)
                    count = final_standings[team][position - 1]
                    position_chances[position][team] = (count / num_simulations) * 100

            # Create a DataFrame
            position_chances_df = pd.DataFrame(position_chances)
            # Add a column for the team names (optional)
            position_chances_df.index.name = 'Team'
            # Determine the maximum number of positions
            max_positions = len(position_chances_df.columns)
            # Rename the columns to represent the positions a team can finish
            position_chances_df.columns = [f'Place {i}' for i in range(1, max_positions + 1)]
            # Add a new column for the chance of making playoffs
            num_playoff_teams = settings.playoff_team_count
            position_chances_df['Chance of making playoffs'] = 0.0
            # Sum the top # of finish places based on playoff teams
            for team in position_chances_df.index:
                top_finishes = position_chances_df.iloc[position_chances_df.index.get_loc(team), :num_playoff_teams]
                position_chances_df.at[team, 'Chance of making playoffs'] = top_finishes.sum()
            # Sort the DataFrame by 'Chance of making playoffs' column
            sort_cols = [f'Place {i}' for i in range(1, max_positions + 1)] + ['Chance of making playoffs']
            position_chances_df = position_chances_df.sort_values(by=sort_cols, ascending=False)
            return position_chances_df

        odds_df = oddsCalculator()
        # print(odds_df)

        if current_week > settings.reg_season_count:
            fileName = leagueName + " " + str(year)
            fileName = f"leagues/{fileName}.xlsx"
            sheet_name = "LPI By Week"

            # Read the LPI data
            lpi_df = pd.read_excel(fileName, sheet_name=sheet_name, index_col=0)  # Team names as index
            lpi_df = lpi_df.drop(['Change From Last Week'], axis=1)

            # --------------------------------------------------------------------------------------
            # PLAYOFF RESULTS
            # --------------------------------------------------------------------------------------

            # team_owners = [team.owners for team in league.teams]
            team_names = [team.team_name for team in league.teams]
            team_scores = [team.scores for team in league.teams] 

            schedules = []
            for team in league.teams:
                schedule = [opponent.team_name for opponent in team.schedule]
                schedules.append(schedule)

            # Precompute current week 
            current_week = None
            for week in range(1, settings.reg_season_count+1):
                scoreboard = league.scoreboard(week)
                if not any(matchup.home_score for matchup in scoreboard):
                    current_week = week
                    break 

            if current_week is None:
                current_week = settings.reg_season_count
            elif current_week != settings.reg_season_count:
                current_week -= 1

            # Store data in DataFrames 
            scores_df = pd.DataFrame(team_scores, index=team_names)
            schedules_df = pd.DataFrame(schedules, index=team_names)
            # print(scores_df)
            last_column_name = scores_df.columns[-1]
            # print(schedules_df)

            # Playoff teams and seeds
            standings = [team.team_name for team in league.standings_weekly(settings.reg_season_count)]
            num_playoff_teams = settings.playoff_team_count
            playoff_teams = standings[:num_playoff_teams]  # Top teams in the playoffs
            reg_season_count = settings.reg_season_count
            # Initialize the results list
            playoff_results = []

            # Function to determine round name based on number of teams
            def get_round_name(num_teams):
                if num_teams >= 5:
                    return "Quarter Final"
                elif num_teams >= 3:
                    return "Semi Final"
                elif num_teams == 2:
                    return "Championship"
                else:
                    return "Final Team"  # Special case if there's one team left (shouldn't be used in matchups)

            # Iterate through playoff weeks
            last_column_name = scores_df.columns[-1]
            for week in range(reg_season_count, last_column_name+1):
                round_name = get_round_name(len(playoff_teams))
                # print(f"Processing Playoff Round {round_name} (Week {week + 1})")
                # print(playoff_teams)
                # print()
                advancing_teams = []  # Teams that win in the current week
                round_number = week - reg_season_count + 1
                teams_already_processed = set()  # Track teams already in a matchup

                # Matchups: process playoff teams
                for team in playoff_teams:
                    # Skip if this team has already been processed in a matchup
                    if team in teams_already_processed:
                        continue

                    opponent = schedules_df.loc[team, week]  # Get opponent for the current week

                    # Skip if the team has a bye (e.g., they face themselves)
                    if opponent == team:
                        playoff_results.append({
                            "Round": round_name,
                            "Team 1": team,
                            "Seed 1": standings.index(team) + 1,
                            "Score 1": scores_df.loc[team, week],
                            "Team 1 LPI": lpi_df.loc[team, f"Week {week + 1}"],  # Add LPI value
                            "Team 2": "Bye",
                            "Seed 2": "-",
                            "Score 2": "-",
                            "Team 2 LPI": "-",
                            "Winner": team
                        })
                        advancing_teams.append(team)  # Auto-advance the team
                        continue

                    # Skip if the opponent has already been processed
                    if opponent in teams_already_processed:
                        continue

                    # Retrieve team and opponent scores
                    score_1 = scores_df.loc[team, week]
                    score_2 = scores_df.loc[opponent, week]

                    # Retrieve LPI values
                    team_1_lpi = lpi_df.loc[team, f"Week {week + 1}"]
                    team_2_lpi = lpi_df.loc[opponent, f"Week {week + 1}"]

                    # Determine seeds
                    seed_1 = standings.index(team) + 1
                    seed_2 = standings.index(opponent) + 1

                    # Determine winner
                    if score_1 > score_2:
                        winner = team
                    elif score_2 > score_1:
                        winner = opponent
                    else:
                        winner = "Tie"  # Handle tie scenario if needed

                    # Append results to the playoff results list
                    playoff_results.append({
                        "Round": round_name,
                        "Team 1": team,
                        "Seed 1": seed_1,
                        "Score 1": score_1,
                        "Team 1 LPI": team_1_lpi,
                        "Team 2": opponent,
                        "Seed 2": seed_2,
                        "Score 2": score_2,
                        "Team 2 LPI": team_2_lpi,
                        "Winner": winner
                    })

                    # Add the winner to the advancing teams list
                    advancing_teams.append(winner)

                    # Mark both teams as processed
                    teams_already_processed.add(team)
                    teams_already_processed.add(opponent)

                # Update playoff_teams for the next round
                playoff_teams = advancing_teams
                round_number += 1

                # Break the loop if there is only one team left (champion)
                if len(playoff_teams) <= 1:
                    break

            # Convert results to DataFrame
            playoff_df = pd.DataFrame(playoff_results)

            # Display the DataFrame
            # print(playoff_df)

            # Open the workbook
            workbook = openpyxl.load_workbook(fileName)
            # Check if the sheet already exists
            if "Playoff Results" in workbook.sheetnames:
                # Remove the sheet
                del workbook["Playoff Results"]
            # Save the workbook after removing the sheet
            workbook.save(fileName)

            # Add playoff_df as a new sheet to the existing Excel file
            with pd.ExcelWriter(fileName, engine="openpyxl", mode="a") as writer:
                playoff_df.to_excel(writer, sheet_name="Playoff Results", index=False)

        writer = pd.ExcelWriter(f"leagues/{fileName}.xlsx", engine='xlsxwriter')
        records_df.to_excel(writer, sheet_name='Schedule Grid')
        schedule_rank_df.to_excel(writer, sheet_name='Wins Against Schedule')
        rank_df.to_excel(writer, sheet_name='Expected Wins')
        odds_df.to_excel(writer, sheet_name='Playoff Odds')
        lpi_df.to_excel(writer, sheet_name='Louie Power Index')
        lpi_weekly_df.to_excel(writer, sheet_name='LPI By Week')
        upsets_df.to_excel(writer, sheet_name='Biggest Upsets')
        writer.close()
        # --------------------------------------------------------------------------------------
    except Exception as e:
        # Handle errors, such as the league not existing
        print(f"Error: League '{league_config['name']}' for year {league_config['year']} does not exist or could not be loaded.")
        print(f"Details: {str(e)}")
        print(f"Details: {str(e)}")
        continue  # Move to the next league

print("--- %s seconds ---" % (time.time() - start_time))