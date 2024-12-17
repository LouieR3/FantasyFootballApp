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

player = league.player_info("Cowboys D/ST")
print(player)
print(player.stats)
games_played = 0
if player.stats:
    print(player)
    print(player.stats)
    for key, stat in player.stats.items():
        # Skip index 0 (season totals or projections)
        if key == 0:
            continue
        # Increment games_played if 'breakdown' is non-empty
        if stat.get('breakdown'):
            games_played += 1
print(games_played)
adf
league = League(league_id=310334683, year=2023, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

player = league.player_info(playerId=3918298)
print(player)
print(type(player))
# 3918298
league = League(league_id=310334683, year=2024, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

player = league.player_info(playerId=3918298)
print(player.playerId)
print(player)
asdf


team = league.teams[2]
print(team.roster[0])
player = league.player_info('Christian McCaffrey')
print(player)
player = league.player_info(3918298)
print(player)
print(player.stats[1]['points'])
print()
print(player.stats[0]['projected_points'])
print(player.stats[0]['projected_avg_points'])
print(player.stats[0]['points'])
print(player.stats[0]['avg_points'])