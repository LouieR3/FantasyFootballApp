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
import os

start_time = time.time()

espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
# Pennoni Younglings
league = League(league_id=310334683, year=2024, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

def test_league_data(league):
    print(league.settings)
    print(league.current_week)

    # print(league.free_agents())
    # print(league.least_scored_week())
    # print(league.least_scorer())
    # print(league.load_roster_week(2))
    # print(league.most_points_against())
    # print(league.player_info(4036212))
    # print(league.previousSeasons)
    print(league.recent_activity())

# test_league_data(league)

def test_matchup_data(league):
    playoff_round_1 = league.box_scores(week=1)
    for match in playoff_round_1:
        print(match)
        print(match.home_lineup)
        print(match.home_team)
        print(match.home_projected)
        print(match.home_score)
        print(match.away_team)
        print(match.away_projected)
        print(match.away_score)
        # print(match.matchup_type)
        print()
test_matchup_data(league)

playoff_round_1 = league.box_scores(week=15)[0]
playoff_round_1.matchup_type
# player = playoff_round_1[0].home_lineup[0]
# print(player.points_breakdown)
def test_player_data(league):
    playoff_round_1 = league.box_scores(week=15)
    player = playoff_round_1[0].home_lineup[0]
    print(player.playerId)
    print(player.name)
    print(player.position)
    print(player.proTeam)
    print(player.injuryStatus)
    print(player.projected_points)
    print(player.points)
    print(player.points_breakdown)
    print(player.acquisitionType)
    print(player.stats)
    print(player.avg_points)
    print(player.posRank)
    print()
    print(playoff_round_1[0].home_lineup)

    player_name = player.name
    player_stat = league.player_info(player_name)
    player_stats = player_stat.stats
    print(player_stats)
# test_player_data(league)

def test_team_data(league):
    team_names = [team.team_name for team in league.teams]
    print(team_names)

    team_owners = [team.owners[0]['id'] for team in league.teams]
    # print(team_owners)

    team_scores = [team.scores for team in league.teams] 
    # print(team_scores)

    teams = league.teams
    schedules = [[opponent.owners[0]['id'] for opponent in team.schedule] for team in teams]
    schedules = [team.schedule for team in teams]
    # print(schedules)
    scores_df = pd.DataFrame(team_scores, index=team_owners)

    current_week = scores_df.apply(lambda row: row[row != 0.0].last_valid_index(), axis=1).max() + 1
    print(current_week)

    team = teams[5]

    print(team.team_name)
    print(team.outcomes)
    print(team.acquisitions)

# test_team_data(league)