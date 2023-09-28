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
  print(dynamic_std_dev_factor)

  # Calculate average score and standard deviation based on team totals
  for i in range(len(team_names)):
      team_name = team_names[i]
      total_points = team_totals[i]
      team_score = team_scores[i]
      
      non_zero_values = []
      for score in team_score:
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
      for week in range(schedules_df.shape[1]):
          week_schedule = schedules_df[week].to_list()
          random.shuffle(week_schedule)
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
  position_chances_df['Chance of making playoffs'] = 0
  # Sum the top # of finish places based on playoff teams
  for team in position_chances_df.index:
      top_finishes = position_chances_df.iloc[position_chances_df.index.get_loc(team), :num_playoff_teams]
      position_chances_df.at[team, 'Chance of making playoffs'] = top_finishes.sum()
  # Sort the DataFrame by 'Chance of making playoffs' column
  sort_cols = [f'Place {i}' for i in range(1, max_positions + 1)] + ['Chance of making playoffs']
  position_chances_df = position_chances_df.sort_values(by=sort_cols, ascending=False)
  return position_chances_df