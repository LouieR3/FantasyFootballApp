"""Given raw ESPN credentials, what does that actually get you?

Walks every league in `leagues` below for the current year and reports, per
league, whether the credentials work and - if so - who owns each team. Meant
as a quick "what's broken right now" pass across all the leagues the pipeline
pulls, without touching any file under data/.

    python tools/check_league_access.py
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import sys

from credentials import CRED
from espn_api.football import League

# League/team names often carry emoji; Windows consoles default to cp1252 and
# raise UnicodeEncodeError on them instead of just showing '?'.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, 'reconfigure'):
        _stream.reconfigure(errors='replace')

louie_s2 = CRED["louie_s2"]
prahlad_s2 = CRED["prahlad_s2"]
la_s2 = CRED["la_s2"]
hannah_s2 = CRED["hannah_s2"]
ava_s2 = CRED["ava_s2"]
matt_s2 = CRED["matt_s2"]
ayush_s2 = CRED["ayush_s2"]

year = 2026
leagues = [
    # Pennoni Younglings
    {"league_id": 310334683, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "Pennoni Younglings"},
    # Family League
    {"league_id": 1343668602, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "Family League"},
    # EBC League
    {"league_id": 1118513122, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "EBC League"},
    # Game of Yards
    {"league_id": 1781851, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "Game of Yards!"},
    # Brown Munde
    {"league_id": 367134149, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "Brown Munde"},
    # Turf On Grade 2.0 League
    {"league_id": 1242265374, "year": year, "espn_s2": CRED["turf_s2"], "swid": CRED["prahlad_swid"], "name": "Turf On Grade 2.0"},
    # Las League
    {"league_id": 1049459, "year": year, "espn_s2": la_s2, "swid": CRED["la_swid"], "name": "THE BEST OF THE BEST"},
    # Hannahs League
    {"league_id": 1399036372, "year": year, "espn_s2": hannah_s2, "swid": CRED["hannah_swid"], "name": "The Girl's Room 💞🏈"},
    # Avas League
    {"league_id": 417131856, "year": year, "espn_s2": ava_s2, "swid": CRED["ava_swid"], "name": "Philly Extra Special"},
    # Matts League
    {"league_id": 29400230, "year": year, "espn_s2": matt_s2, "swid": CRED["matt_swid"], "name": "BP- Loudoun 2025"},
    # Ayush League
    {"league_id": 558148583, "year": year, "espn_s2": ayush_s2, "swid": CRED["ayush_swid"], "name": "Ross' Fantasy League"},
]


def check_league_access(league_config):
    league = League(
        league_id=league_config["league_id"],
        year=league_config["year"],
        espn_s2=league_config["espn_s2"],
        swid=league_config["swid"],
    )
    settings = league.settings
    print(f"League: {settings.name} ({league.year})")
    print(f"Teams ({len(league.teams)}):")
    for team in league.teams:
        owner = team.owners[0].get('firstName', '?') if team.owners else '?'
        print(f"  {team.team_id:>2}  {team.team_name}  (owner: {owner})")


results = []
for league_config in leagues:
    print(f"=== {league_config['name']} ({league_config['league_id']}) ===")
    try:
        check_league_access(league_config)
        results.append((league_config['name'], True, None))
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")
        results.append((league_config['name'], False, str(e)))
    print()

print("=== Summary ===")
for name, ok, err in results:
    status = "OK" if ok else f"FAILED - {err}"
    print(f"  {name:<30} {status}")
