from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
import numpy as np
import math
import random
from copy import deepcopy

start_time = time.time()

# Pennoni Younglings
league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',
                swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

team_names = [team.team_name for team in league.teams]
# print(team_names)
# print()
# print()
record_total =int(league.teams[0].wins) + int(league.teams[0].losses)
print(str(record_total))
team_scores = [team.scores for team in league.teams] 
# print(team_scores)
# print()
# print(len(team_scores[0]))
# print()
team_totals = [team.points_for for team in league.teams]
# print(team_totals)
# print()

schedules = [team.schedule for team in league.teams]

settings = league.settings
reg_season = settings.reg_season_count

def standard_deviation(values):
    avg = sum(values) / len(values)
    square_diffs = [(value - avg) ** 2 for value in values]
    avg_square_diff = sum(square_diffs) / len(values)
    return math.sqrt(avg_square_diff)

# Initialize a dictionary to store the results
team_data = {}

# Calculate average score and standard deviation based on team totals
for i in range(len(team_names)):
    team_name = team_names[i]
    total_points = team_totals[i]
    num_weeks_played = 14  # Assuming 14 weeks in the regular season
    
    # Calculate the average score (total points divided by weeks played)
    average_score = total_points / len(team_scores[0])
    
    # Calculate the standard deviation using the standard_deviation function
    std_dev_factor = 0.2  # Adjust this value based on your league's characteristics
    std_dev = standard_deviation([total_points] * num_weeks_played) * std_dev_factor
    
    team_data[team_name] = {'average_score': average_score, 'std_dev': std_dev}
# print(team_data)
# Initialize a dictionary to store the results
results = {team: [0] * (len(team_names) + 1) for team in team_data}

# Number of simulations to run
num_simulations = 10000
# Run Monte Carlo simulations
for _ in range(num_simulations):
    # Simulate scores for each team based on normal distribution
    team_scores = {
        team: np.random.normal(data['average_score'], data['std_dev'])
        for team, data in team_data.items()
    }
    
    # Sort teams by their simulated scores
    sorted_teams = sorted(team_scores.keys(), key=lambda x: team_scores[x], reverse=True)
    
    # Assign rankings to teams
    for rank, team in enumerate(sorted_teams):
        results[team][rank + 1] += 1

# Calculate the odds of each team finishing in each position
odds = {}
for team, rank_counts in results.items():
    total_simulations = sum(rank_counts)
    odds[team] = [(count / total_simulations) * 100 for count in rank_counts]

# # Print the odds for each team in each position
# for team, team_odds in odds.items():
#     print(f"Team: {team}")
#     for rank, odds_percentage in enumerate(team_odds[1:], start=1):
#         print(f"   Finish in Position {rank}: {odds_percentage:.2f}%")
# Create a DataFrame
odds_df = pd.DataFrame(odds).T

# Add a column for the team names (optional)
odds_df.index.name = 'Team'

odds_df = odds_df.iloc[:, 1:]
# Determine the maximum number of positions
max_positions = max(len(odds_df.columns), max([len(team_odds) for team_odds in odds.values()]))

# Fill missing positions with 0
for team_odds in odds_df.columns:
    odds_df[team_odds] = odds_df[team_odds].fillna(0)

# Rename the columns to represent the positions a team can finish
odds_df.columns = [f'Place {i}' for i in range(1, max_positions)]

# Display the DataFrame
# print(odds_df)
# Get number of playoff teams 
num_playoff_teams = settings.playoff_team_count  

# Add new column 
odds_df['Chance of making playoffs'] = 0

# Sum the top # of finish places based on playoff teams
for i, row in odds_df.iterrows():
    odds_df.at[i, 'Chance of making playoffs'] = row[:num_playoff_teams].sum()

# Sort by 'Chance of making playoffs' column
sort_cols = ['Place 1', 'Place 2', 'Place 3', 'Place 4', 'Place 5', 'Place 6', 'Place 7', 'Place 8', 'Place 9', 'Place 10', 'Place 11', 'Place 12', 'Chance of making playoffs']

odds_df = odds_df.sort_values(by=sort_cols, ascending=False)

print(odds_df)
def random_value():
    u = 0
    v = 0
    while u == 0:
        u = random.random()  # Converting [0, 1) to (0, 1)
    while v == 0:
        v = random.random()
    return math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)

def simulate_rest_of_season(league, playoff_odds_teams):
    for week in league['remainingSchedule']:
        for matchup in week['matchups']:
            home_team = next(team for team in playoff_odds_teams if team['teamName'] == matchup['homeTeamName'])
            away_team = next(team for team in playoff_odds_teams if team['teamName'] == matchup['awayTeamName'])

            home_team_score = home_team['averageScore'] + random_value() * home_team['standardDeviation']
            away_team_score = away_team['averageScore'] + random_value() * away_team['standardDeviation']

            home_team['pointsFor'] += home_team_score
            home_team['pointsAgainst'] += away_team_score
            away_team['pointsFor'] += away_team_score
            away_team['pointsAgainst'] += home_team_score

            if home_team_score > away_team_score:
                set_matchup(matchup, False, False, True, league, playoff_odds_teams)
            elif away_team_score > home_team_score:
                set_matchup(matchup, True, False, False, league, playoff_odds_teams)
            else:  # Tie
                set_matchup(matchup, False, True, False, league, playoff_odds_teams)

    order_standings(league)

def run_playoff_odds_calculation(league, teams, iterations):
    league_copy = deepcopy(league)
    league_to_use = deepcopy(league)
    teams_copy = deepcopy(teams)
    teams_to_use = deepcopy(teams)

    for _ in range(iterations):
        simulate_rest_of_season(league_to_use, teams_to_use)

        # Based on results, update the simulatedPlacements for each team with passed-in teams object
        for team in teams:
            # Find the team in the league with the same teamName
            matched_team = next((t for t in league_to_use['teams'] if t['teamName'] == team['teamName']), None)
            if matched_team:
                team['simulatedPlacements'][matched_team['overallRank'] - 1] += 1.0 / iterations * 100

        # Reset league and teams for the next iteration
        league_to_use = deepcopy(league_copy)
        teams_to_use = deepcopy(teams_copy)

def order_standings(league):
    if league is None:
        return []

    unranked_teams = []
    division_winners = []
    ranks_remaining = list(range(1, len(league['teams']) + 1))
    tiebreaker_id = get_tiebreaker_id_from_id(league['leagueSettings']['playoffTiebreakerID'])

    all_matchups = []
    for week in league['completedSchedule']:
        all_matchups.extend(week['matchups'])
    for week in league['remainingSchedule']:
        all_matchups.extend(week['matchups'])

    for team in league['teams']:
        team['winPercentage'] = (team['wins'] + 0.5 * team['ties']) / max((team['wins'] + team['losses'] + team['ties']), 1)
        team['divisionWinPercentage'] = (team['divisionWins'] + 0.5 * team['divisionTies']) / max((team['divisionWins'] + team['divisionLosses'] + team['divisionTies']), 1)
        team['tiebreakers'] = []
        unranked_teams.append(team)

    # Find division winners
    for division in league['leagueSettings']['divisions']:
        division_teams = [team for team in unranked_teams if team['teamName'] in [each_team['teamName'] for each_team in division['teams']]]
        division_winner = determine_division_winner(sort_by_win_percentage(division_teams), tiebreaker_id, all_matchups)
        if division_winner:
            division_winners.append(division_winner)

    # Remove division winners from overall ranks
    unranked_teams = [team for team in unranked_teams if team['teamName'] not in [each_team['teamName'] for each_team in division_winners]]

    # Sort division winners
    sorted_division_winners = sort_teams(division_winners, tiebreaker_id, all_matchups)

    # Apply Ranking
    set_team_ranking(ranks_remaining, sorted_division_winners)

    # Sort all the rest
    sorted_teams = sort_teams(unranked_teams, tiebreaker_id, all_matchups)

    set_team_ranking(ranks_remaining, sorted_teams)

def sort_teams(teams, tiebreaker_id, all_matchups):
    ordered_teams = []
    sorted_teams = sort_by_win_percentage(teams)
    
    while sorted_teams:
        top_teams = [team for team in sorted_teams if team['winPercentage'] == sorted_teams[0]['winPercentage']]

        while len(top_teams) > 1:
            tiebreaker = generate_tiebreaker_object(top_teams)
            top_team = determine_tiebreakers_winner(top_teams, tiebreaker, tiebreaker_id, all_matchups)
            
            if not top_team:
                return []

            index = sorted_teams.index(top_team)
            if index > -1:
                sorted_teams.pop(index)

            index = top_teams.index(top_team)
            if index > -1:
                top_teams.pop(index)

            ordered_teams.append(top_team)

        temp = top_teams.pop()
        if temp:
            index = sorted_teams.index(temp)
            if index > -1:
                sorted_teams.pop(index)

            ordered_teams.append(temp)

    return ordered_teams

def set_team_ranking(remaining_rankings, sorted_teams):
    while sorted_teams:
        team = sorted_teams.pop(0)
        if team:
            team['overallRank'] = remaining_rankings.pop(0) if remaining_rankings else 100

def determine_division_winner(sorted_teams, tiebreaker_id, all_matchups):
    top_teams = [team for team in sorted_teams if team['winPercentage'] == sorted_teams[0]['winPercentage']]

    if len(top_teams) == 1:
        return top_teams[0]

    tiebreaker = generate_tiebreaker_object(top_teams)

    return determine_tiebreakers_winner(top_teams, tiebreaker, tiebreaker_id, all_matchups)

def determine_tiebreakers_winner(sorted_teams, tiebreaker, tiebreaker_id, all_matchups):
    if tiebreaker_id == PlayoffTiebreakerID.HeadToHead:
        winner = head_to_head_tiebreaker(sorted_teams, tiebreaker, tiebreaker_id, all_matchups)
        if winner:
            return winner

        winner = points_for_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner

        winner = intra_division_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner

        winner = points_against_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner
    elif tiebreaker_id == PlayoffTiebreakerID.TotalPointsScored:
        winner = points_for_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner

        winner = head_to_head_tiebreaker(sorted_teams, tiebreaker, tiebreaker_id, all_matchups)
        if winner:
            return winner

        winner = intra_division_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner

        winner = points_against_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner
    elif tiebreaker_id == PlayoffTiebreakerID.IntraDivisionRecord:
        winner = intra_division_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner

        winner = head_to_head_tiebreaker(sorted_teams, tiebreaker, tiebreaker_id, all_matchups)
        if winner:
            return winner

        winner = points_for_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner

        winner = points_against_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner
    elif tiebreaker_id == PlayoffTiebreakerID.TotalPointsAgainst:
        winner = points_against_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner

        winner = head_to_head_tiebreaker(sorted_teams, tiebreaker, tiebreaker_id, all_matchups)
        if winner:
            return winner

        winner = points_for_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner

        winner = intra_division_tiebreaker(sorted_teams, tiebreaker)
        if winner:
            return winner

    return coin_flip_tiebreaker(sorted_teams, tiebreaker)

def coin_flip_tiebreaker(sorted_teams, tiebreaker):
    winning_team = sorted_teams.pop(0)
    if winning_team:
        for team in sorted_teams:
            add_tiebreaker_to_team(team, tiebreaker, "Lost coin flip tiebreaker to " + (winning_team['teamName'] or ''))

        add_tiebreaker_to_team(winning_team, tiebreaker, "Won coin flip tiebreaker")
        return winning_team

def head_to_head_tiebreaker(teams, tiebreaker, tiebreaker_id, all_matchups):
    head_to_head_teams = []
    total_teams = len(teams)

    for i in range(total_teams):
        selected_team = teams[i]
        other_teams = [team for team in teams if team['teamName'] != selected_team['teamName']]
        team_wins = 0
        team_losses = 0
        team_ties = 0

        for j in range(total_teams):
            matchup = all_matchups[j]

            if matchup['awayTeamName'] == selected_team['teamName'] and any(team['teamName'] == matchup['homeTeamName'] for team in other_teams):
                if matchup['awayTeamWon']:
                    team_wins += 1
                elif matchup['homeTeamWon']:
                    team_losses += 1
                elif matchup['tie']:
                    team_ties += 1
            elif matchup['homeTeamName'] == selected_team['teamName'] and any(team['teamName'] == matchup['awayTeamName'] for team in other_teams):
                if matchup['homeTeamWon']:
                    team_wins += 1
                elif matchup['awayTeamWon']:
                    team_losses += 1
                elif matchup['tie']:
                    team_ties += 1

        total_games = team_wins + team_losses + team_ties
        head_to_head_team = {
            'team': selected_team,
            'totalGames': total_games,
            'winPercentage': (team_wins + 0.5 * team_ties) / max(total_games, 1),
            'wins': team_wins,
            'losses': team_losses,
            'ties': team_ties
        }
        head_to_head_teams.append(head_to_head_team)

    teams_with_matching_games = [team for team in head_to_head_teams if team['totalGames'] == head_to_head_teams[0]['totalGames']]

    if len(teams_with_matching_games) != len(head_to_head_teams):
        tiebreaker.append("Head to head tiebreaker cannot be used as all teams don't have the same amount of games against each other")
        return None

    best_record_win_percentage = max([team['winPercentage'] for team in head_to_head_teams])
    teams_with_matching_win_percentage = [team for team in head_to_head_teams if team['winPercentage'] == best_record_win_percentage]
    teams_without_matching_win_percentage = [team for team in head_to_head_teams if team['winPercentage'] != best_record_win_percentage]

    if len(teams_with_matching_win_percentage) > 1:
        for team in teams_without_matching_win_percentage:
            add_tiebreaker_to_team(team['team'], tiebreaker, "Lost head to head tiebreaker due to multiple teams being " + teams_with_matching_win_percentage[0]['wins'] + "-" + teams_with_matching_win_percentage[0]['losses'] + "-" + teams_with_matching_win_percentage[0]['ties'] + " compared to " + team['wins'] + "-" + team['losses'] + "-" + team['ties'])

            index = teams.index(team)
            if index > -1:
                teams.pop(index)

        remaining_team_names = [team['team']['teamName'] for team in teams]

        remaining_text = ""
        if total_teams > 2 and total_teams != len(teams):
            remaining_text = " Teams remaining: " + ', '.join(remaining_team_names) + ". Remaining teams will restart the tiebreaking process"
            tiebreaker.append(remaining_text)
            return determine_tiebreakers_winner(teams, tiebreaker, tiebreaker_id, all_matchups)

        tiebreaker.append("Head to head tiebreaker could not break the tie because multiple teams have the same head to head record." + remaining_text)
        return None

    best_record_team = teams_with_matching_win_percentage[0]['team']
    loser_strings = [team['team']['teamName'] + ": " + str(team['wins']) + "-" + str(team['losses']) + "-" + str(team['ties']) for team in teams_without_matching_win_percentage]

    for team in teams_without_matching_win_percentage:
        add_tiebreaker_to_team(team['team'], tiebreaker, "Lost head to head tiebreaker to " + best_record_team['teamName'] + " with " + str(best_record_team['wins']) + "-" + str(best_record_team['losses']) + "-" + str(best_record_team['ties']) + " record compared to " + str(team['wins']) + "-" + str(team['losses']) + "-" + str(team['ties']))

    add_tiebreaker_to_team(best_record_team, tiebreaker, "Won points for by having more points for than the specified team(s): " + ', '.join(loser_strings))
    return best_record_team

def points_for_tiebreaker(teams, tiebreaker):
    max_points_for = max([team['pointsFor'] for team in teams])

    teams_with_point_value = [team for team in teams if team['pointsFor'] == max_points_for]

    if len(teams_with_point_value) == 1:
        losers = [team for team in teams if team['teamName'] != teams_with_point_value[0]['teamName']]
        loser_strings = [team['teamName'] + ": " + str(teams_with_point_value[0]['pointsFor'] - team['pointsFor']) for team in losers]

        for team in losers:
            points_for_diff = str(teams_with_point_value[0]['pointsFor'] - team['pointsFor'])
            add_tiebreaker_to_team(team['team'], tiebreaker, "Lost points for tiebreaker to " + teams_with_point_value[0]['teamName'] + " by " + points_for_diff + " points")

        add_tiebreaker_to_team(teams_with_point_value[0]['team'], tiebreaker, "Won points for by having more points for than the specified team(s): " + ', '.join(loser_strings))
        return teams_with_point_value[0]

    tiebreaker.append("Points for tiebreaker could not break the tie because multiple teams have the same points for.")
    return None

def points_against_tiebreaker(teams, tiebreaker):
    max_points_against = max([team['pointsAgainst'] for team in teams])

    teams_with_point_value = [team for team in teams if team['pointsAgainst'] == max_points_against]

    if len(teams_with_point_value) == 1:
        losers = [team for team in teams if team['teamName'] != teams_with_point_value[0]['teamName']]
        loser_strings = [team['teamName'] + ": " + str(teams_with_point_value[0]['pointsAgainst'] - team['pointsAgainst']) for team in losers]

        for team in losers:
            points_against_diff = str(teams_with_point_value[0]['pointsAgainst'] - team['pointsAgainst'])
            add_tiebreaker_to_team(team['team'], tiebreaker, "Lost points against tiebreaker to " + teams_with_point_value[0]['teamName'] + " by " + points_against_diff + " points againsts")

        add_tiebreaker_to_team(teams_with_point_value[0]['team'], tiebreaker, "Won points against by having more points against than the specified team(s): " + ', '.join(loser_strings))
        return teams_with_point_value[0]

    tiebreaker.append("Points against tiebreaker could not break the tie because multiple teams have the same points against.")
    return None

def intra_division_tiebreaker(teams, tiebreaker):
    sorted_teams = sort_by_division_win_percentage(teams)

    top_teams = [team for team in sorted_teams if team['divisionWinPercentage'] == sorted_teams[0]['divisionWinPercentage']]

    if len(top_teams) == 1:
        losers = [team for team in teams if team['teamName'] != top_teams[0]['teamName']]
        loser_strings = [team['teamName'] + ": " + str(team['divisionWins']) + "-" + str(team['divisionLosses']) + "-" + str(team['divisionTies']) for team in losers]

        for team in losers:
            add_tiebreaker_to_team(team['team'], tiebreaker, "Lost intradivision tiebreaker to " + top_teams[0]['teamName'] + " " + str(top_teams[0]['divisionWins']) + "-" + str(top_teams[0]['divisionLosses']) + "-" + str(top_teams[0]['divisionTies']) + " record compared to " + str(team['divisionWins']) + "-" + str(team['divisionLosses']) + "-" + str(team['divisionTies']))

        add_tiebreaker_to_team(top_teams[0]['team'], tiebreaker, "Won intradivision tiebreaker by having a " + str(top_teams[0]['divisionWins']) + "-" + str(top_teams[0]['divisionLosses']) + "-" + str(top_teams[0]['divisionTies']) + " record compared to " + ', '.join(loser_strings))
        return top_teams[0]

    tiebreaker.append("Intra division record could not break the tie because multiple teams have the same record.")
    return None

def sort_by_win_percentage(teams):
    teams.sort(key=lambda x: x['winPercentage'], reverse=True)
    return teams

def sort_by_division_win_percentage(teams):
    teams.sort(key=lambda x: x['divisionWinPercentage'], reverse=True)
    return teams

def generate_tiebreaker_object(teams):
    tiebreaker = ["Tiebreaker between " + ', '.join([team['teamName'] for team in teams])]
    return tiebreaker

def get_tiebreaker_id_from_id(tiebreaker_id):
    if tiebreaker_id == 0:
        return PlayoffTiebreakerID.HeadToHead
    if tiebreaker_id == 1:
        return PlayoffTiebreakerID.TotalPointsScored
    if tiebreaker_id == 2:
        return PlayoffTiebreakerID.IntraDivisionRecord
    if tiebreaker_id == 3:
        return PlayoffTiebreakerID.TotalPointsAgainst
    return PlayoffTiebreakerID.TotalPointsScored

def add_tiebreaker_to_team(team, tiebreaker, tiebreaker_to_add):
    if tiebreaker and team:
        tiebreaker_copy = tiebreaker.copy()
        tiebreaker_copy.append(tiebreaker_to_add)

        if 'tiebreakers' not in team:
            team['tiebreakers'] = []

        team['tiebreakers'].append(tiebreaker_copy)
print("--- %s seconds ---" % (time.time() - start_time))

print()
print(settings.playoff_team_count)
print(settings.team_count)