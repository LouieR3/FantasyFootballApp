from credentials import CRED
from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
# import xlsxwriter

start_time = time.time()

# Pennoni Younglings
# league = League(league_id=310334683, year=2022, espn_s2=CRED["legacy_s2_a"], swid=CRED["louie_swid"])

# Family League
# league = League(league_id=1725372613, year=2022, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])

# EBC League
league = League(league_id=1118513122, year=2021, espn_s2=CRED["legacy_s2_b"], swid=CRED["louie_swid"])

scoresList = []
schedList = []
count = 0
keyList = []
for team in league.teams:
    scoresList.append(team.scores)
    schedList.append(team.schedule)
    keyList.append([count, team.team_name])
    count += 1

scoreboard1 = league.scoreboard(week=15)
print(scoreboard1)