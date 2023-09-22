import math

team_names = ["Team A", "Team B", "Team C", "Team D"]
team_totals = [[30, 35, 32, 33], [25, 22, 27, 26], [40, 38, 42, 139], [28, 28, 28, 28]]

std_dev_factor = 0.2

team_data = {}
def standard_deviation(values):
    avg = sum(values) / len(values)
    square_diffs = [(value - avg) ** 2 for value in values]
    avg_square_diff = sum(square_diffs) / len(values)
    return math.sqrt(avg_square_diff)

for i in range(len(team_names)):
    team_name = team_names[i]
    total_points = team_totals[i]
    num_weeks_played = 4  # 4 weeks in this example
    
    # Calculate the average score
    average_score = sum(total_points) / num_weeks_played
    
    # Calculate the standard deviation
    std_dev = standard_deviation(total_points) * std_dev_factor
    
    team_data[team_name] = {'average_score': average_score, 'std_dev': std_dev}
print(team_data)