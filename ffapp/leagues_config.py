"""Centralized league configuration for all scripts.

Instead of hardcoding league lists in draft_data.py, create_betting_odds.py,
ESPNWeeklyUpdateList.py, etc., all scripts should import from here.

Usage:
    from ffapp.leagues_config import get_leagues_for_year

    leagues = get_leagues_for_year(2026)
    for league in leagues:
        print(league['name'], league['league_id'], league['espn_s2'])
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

from credentials import CRED
from ffapp import league_registry as registry

# Credential shortcuts
louie_s2 = CRED["louie_s2"]
louie_s2_pages = CRED["louie_s2_pages"]
prahlad_s2 = CRED["prahlad_s2"]
la_s2 = CRED["la_s2"]
hannah_s2 = CRED["hannah_s2"]
ava_s2 = CRED["ava_s2"]
matt_s2 = CRED["matt_s2"]
elle_s2 = CRED["elle_s2"]
dave_s2 = CRED["dave_s2"]
ayush_s2 = CRED["ayush_s2"]
nolan_s2 = CRED["nolan_s2"]

# Define league metadata once - no hardcoding league IDs per year
LEAGUES_METADATA = [
    {"name": "Pennoni Younglings", "s2_key": "louie_s2_pages", "swid_key": "louie_swid"},
    {"name": "Family Fantasy", "s2_key": "louie_s2_pages", "swid_key": "louie_swid"},
    {"name": "EBC League", "s2_key": "louie_s2_pages", "swid_key": "louie_swid"},
    {"name": "0755 Fantasy Football", "s2_key": "prahlad_s2", "swid_key": "prahlad_swid"},
    {"name": "Game of Yards!", "s2_key": "prahlad_s2", "swid_key": "prahlad_swid"},
    {"name": "Brown Munde", "s2_key": "prahlad_s2", "swid_key": "prahlad_swid"},
    {"name": "Turf On Grade 2.0", "s2_key": "turf_s2", "swid_key": "prahlad_swid"},
    {"name": "THE BEST OF THE BEST", "s2_key": "la_s2", "swid_key": "la_swid"},
    {"name": "The Girl's Room 💞🏈", "s2_key": "hannah_s2", "swid_key": "hannah_swid"},
    {"name": "Operators Football League", "s2_key": "elle_s2", "swid_key": "elle_swid"},
    {"name": "Philly Extra Special", "s2_key": "ava_s2", "swid_key": "ava_swid"},
    {"name": "OnP Fantasy", "s2_key": "dave_s2", "swid_key": "dave_swid"},
    {"name": "The Mike Daisy Sports IQ League", "s2_key": "dave_s2", "swid_key": "dave_swid"},
    {"name": "BP- Loudoun 2025", "s2_key": "matt_s2", "swid_key": "matt_swid"},
    {"name": "Ross' Fantasy League", "s2_key": "ayush_s2", "swid_key": "ayush_swid"},
    {"name": "Board Fantasy Football", "s2_key": "nolan_s2", "swid_key": "nolan_swid"},
    {"name": "The Goofy Goobers", "s2_key": "louie_s2", "swid_key": "louie_swid"},
    {"name": "Campers and Skiers and Prahlad", "s2_key": "louie_s2", "swid_key": "louie_swid"},
]

def get_leagues_for_year(year):
    """
    Get list of all leagues with correct league IDs for the given year.

    The league ID is looked up from the registry, which knows about IDs
    that change per year (e.g., Family Fantasy 2026 uses a different ID).

    Args:
        year (int): The fantasy football season year

    Returns:
        list: List of dicts with keys: league_id, year, espn_s2, swid, name
    """
    leagues = []

    for meta in LEAGUES_METADATA:
        league_id = registry.league_id_for(meta["name"], year)
        if league_id is None:
            # Skip leagues that don't have data for this year
            continue

        # Resolve S2 and SWID from CRED
        s2_key = meta["s2_key"]
        swid_key = meta["swid_key"]

        # Handle special case: turf_s2 might not exist in CRED
        try:
            espn_s2 = CRED[s2_key]
            swid = CRED[swid_key]
        except KeyError:
            print(f"Warning: Credentials not found for {meta['name']} ({s2_key}/{swid_key})")
            continue

        leagues.append({
            "league_id": league_id,
            "year": year,
            "espn_s2": espn_s2,
            "swid": swid,
            "name": meta["name"],
        })

    return leagues


if __name__ == "__main__":
    # Test: print leagues for current and past years
    for year in [2024, 2025, 2026]:
        print(f"\n=== {year} ===")
        leagues = get_leagues_for_year(year)
        for lg in leagues:
            print(f"  {lg['name']}: {lg['league_id']}")
