import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
from credentials import CRED
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

louie_espn_s2 = CRED["louie_s2"]
prahlad_espn_s2 = CRED["prahlad_s2"]
la_espn_s2 = CRED["la_s2"]
year = 2024
# List of league configurations
leagues = [
    {"league_id": 310334683, "year": year, "espn_s2": louie_espn_s2, "swid": CRED["louie_swid"], "name": "Pennoni Younglings"},
    {"league_id": 996930954, "year": year, "espn_s2": louie_espn_s2, "swid": CRED["louie_swid"], "name": "Family League"},
    {"league_id": 1118513122, "year": year, "espn_s2": louie_espn_s2, "swid": CRED["louie_swid"], "name": "EBC League"},
    {"league_id": 1339704102, "year": year, "espn_s2": prahlad_espn_s2, "swid": CRED["prahlad_swid"], "name": "Pennoni Transportation"},
    {"league_id": 1781851, "year": year, "espn_s2": prahlad_espn_s2, "swid": CRED["prahlad_swid"], "name": "Game of Yards"},
    {"league_id": 367134149, "year": year, "espn_s2": prahlad_espn_s2, "swid": CRED["prahlad_swid"], "name": "Brown Munde"},
    {"league_id": 1049459, "year": year, "espn_s2": la_espn_s2, "swid": CRED["la_swid"], "name": "Las League"},
]

for league_config in leagues:
    try:
        league = League(
            league_id=league_config["league_id"],
            year=league_config["year"],
            espn_s2=league_config["espn_s2"],
            swid=league_config["swid"],
        )
        print(league.settings)
        print(f"Processing league: {league_config['name']}")

        settings = league.settings

        leagueName = settings.name.replace(" 22/23", "")
        # pr = league.power_rankings(week=17)
        pr = league.standings()
        table = [
            [
                team.team_name,
                round(team.points_for, 2),
                team.points_against,
                team.wins,
                team.losses,
                team.trades,
                team.final_standing
            ]
            for team in pr
        ]
        headers = ["Team Name", "Points For", "Points Against", "Wins", "Losses", "Trades", "Final Standing"]
        print(tabulate(table, headers=headers, tablefmt="pretty"))
        # pr = league.standings_weekly(week=17)
        # print(tabulate(pr, headers="keys", tablefmt="pretty", showindex="always"))
    except Exception as e:
        print(f"Error processing league {league_config['name']}: {e}")
        continue