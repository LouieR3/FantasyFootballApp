import pandas as pd
import numpy as np
from espn_api.football import League

def monte_carlo_simulation(league_id, year, espn_s2, swid, num_simulations=1000):
    # Initialize the league
    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    teams = league.teams
    settings = league.settings

    # Extract data
    team_names = [team.team_name for team in teams]
    team_owners = [team.owners[0]['id'] for team in teams]
    team_scores = [team.scores for team in teams]
    team_outcomes = [team.outcomes for team in teams]
    schedules = [[opponent.owners[0]['id'] for opponent in team.schedule] for team in teams]

    # Create a DataFrame for scores
    scores_df = pd.DataFrame(team_scores, index=team_owners)

    # Calculate current week
    current_week = scores_df.apply(lambda row: row[row != 0.0].last_valid_index(), axis=1).max() + 1

    # Regular season and playoff settings
    reg_season_weeks = settings.reg_season_count
    num_playoff_teams = settings.playoff_team_count

    # Initialize results storage
    standings_simulation = {team.team_name: [0] * len(teams) for team in teams}
    expected_records = {team.team_name: [0, 0] for team in teams}  # [wins, losses]

    # Monte Carlo simulation
    for _ in range(num_simulations):
        simulated_records = {team.team_name: [team.outcomes.count('W'), team.outcomes.count('L')] for team in teams}

        for week in range(current_week, reg_season_weeks + 1):
            for team, schedule in zip(teams, schedules):
                opponent_id = schedule[week - 1].owners[0]['id']
                opponent = next(t for t in teams if t.owners[0]['id'] == opponent_id)

                # Simulate scores based on historical performance
                team_score = np.random.normal(np.mean(team.scores[:current_week]), np.std(team.scores[:current_week]))
                opponent_score = np.random.normal(np.mean(opponent.scores[:current_week]), np.std(opponent.scores[:current_week]))

                # Determine winner
                if team_score > opponent_score:
                    simulated_records[team.team_name][0] += 1  # Increment wins
                    simulated_records[opponent.team_name][1] += 1  # Increment losses
                else:
                    simulated_records[team.team_name][1] += 1  # Increment losses
                    simulated_records[opponent.team_name][0] += 1  # Increment wins

        # Sort teams by simulated records
        sorted_teams = sorted(simulated_records.items(), key=lambda x: (-x[1][0], x[1][1]))  # Sort by wins, then losses
        for rank, (team_name, record) in enumerate(sorted_teams):
            standings_simulation[team_name][rank] += 1
            expected_records[team_name][0] += record[0]
            expected_records[team_name][1] += record[1]

    # Calculate percentages for standings
    standings_df = pd.DataFrame(standings_simulation)
    standings_df = standings_df.div(num_simulations).mul(100)  # Convert to percentages
    standings_df.index = [f"Seed {i + 1}" for i in range(len(teams))]

    # Calculate expected records
    expected_records_df = pd.DataFrame.from_dict(expected_records, orient='index', columns=['Expected Wins', 'Expected Losses'])
    expected_records_df['Expected Wins'] = expected_records_df['Expected Wins'] / num_simulations
    expected_records_df['Expected Losses'] = expected_records_df['Expected Losses'] / num_simulations

    return standings_df, expected_records_df


# Example usage
league_id = 310334683
year = 2024
swid = '{4656A2AD-A939-460B-96A2-ADA939760B8B}'

# ESPN API setup (using your provided data structure)
espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
year = 2024
# Pennoni Younglings
league = League(league_id=310334683, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

standings_df, expected_records_df = monte_carlo_simulation(league_id, year, espn_s2, swid)

print("Standings Simulation:")
print(standings_df)

print("\nExpected Records:")
print(expected_records_df)