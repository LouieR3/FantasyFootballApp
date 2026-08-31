"""Given raw ESPN credentials, what does that actually get you?

Before wiring a new league into the app, it's worth checking the credentials
work at all and seeing what ESPN hands back: how many prior seasons it will
serve, the current season's settings, and the team names - all without
touching any file under data/.

Swap the active `league = League(...)` line below for the league you want to
check, same as archive/test.py.

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

year = 2025

# Pennoni Younglings
# league = League(league_id=310334683, year=year, espn_s2=CRED["louie_s2"], swid=CRED["louie_swid"])

# Family League
# league = League(league_id=996930954, year=year, espn_s2=CRED["louie_s2"], swid=CRED["louie_swid"])

# EBC League
# league = League(league_id=1118513122, year=year, espn_s2=CRED["louie_s2"], swid=CRED["louie_swid"])

# Pennoni Transportation
# league = League(league_id=1339704102, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Game of Yards
league = League(league_id=1616305229, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Brown Munde
# league = League(league_id=367134149, year=2022, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Turf On Grade League
# league = League(league_id=1242265374, year=2024, espn_s2=CRED["turf_s2"], swid=CRED["prahlad_swid"])

# Las League
# league = League(league_id=1049459, year=2025, espn_s2=CRED["la_s2"], swid=CRED["la_swid"])

# Hannahs League
# league = League(league_id=1399036372, year=year, espn_s2=CRED["hannah_s2"], swid=CRED["hannah_swid"])

# Avas League
# league = League(league_id=417131856, year=2025, espn_s2=CRED["ava_s2"], swid=CRED["ava_swid"])

# Matts League
# league = League(league_id=261375772, year=2024, espn_s2=CRED["matt_s2"], swid=CRED["matt_swid"])

# Elles League
# league = League(league_id=1259693145, year=2025, espn_s2=CRED["elle_s2"], swid=CRED["elle_swid"])

# Dave Work League
# league = League(league_id=1675186799, year=2025, espn_s2=CRED["dave_s2"], swid=CRED["dave_swid"])


def check_league_access(league):
    seasons = sorted(set(league.previousSeasons) | {league.year})
    print(f"Seasons available: {len(seasons)}")
    print(f"  {seasons}")
    print()

    settings = league.settings
    print(f"League: {settings.name} ({league.year})")
    print(f"  Team count:          {settings.team_count}")
    print(f"  Regular season wks:  {settings.reg_season_count}")
    print(f"  Playoff teams:       {settings.playoff_team_count}")
    print(f"  Tie rule:            {settings.tie_rule}")
    print(f"  Roster:              {settings.position_slot_counts}")
    print()

    print(f"Teams ({len(league.teams)}):")
    for team in league.teams:
        owner = team.owners[0].get('firstName', '?') if team.owners else '?'
        print(f"  {team.team_id:>2}  {team.team_name}  (owner: {owner})")


check_league_access(league)
