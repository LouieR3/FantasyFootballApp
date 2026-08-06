"""Backfill weekly roster snapshots and reconstructed moves for past seasons.

    python pipeline/backfill_transactions.py                 # every league, 2019-current
    python pipeline/backfill_transactions.py --years 2024 2025
    python pipeline/backfill_transactions.py --league "EBC League"
    python pipeline/backfill_transactions.py --skip-existing  # resume a part-done run

Roughly 14 ESPN requests per league-season (one per week), so a full sweep of
~15 leagues over 7 seasons is on the order of 1,000 requests. That is a one-time
cost and far cheaper than the draft pull, which fires one request *per player*.

2019 is a hard floor: `box_scores` raises before that. Seasons a league did not
play simply fail to initialise and are skipped.

The activity feed is only fetched for the current season - ESPN 404s it for every
completed one - so backfilled moves carry ``Source='snapshot'`` and cannot
distinguish a trade from a same-week drop-and-claim. See ffapp/espn/transactions.py.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import argparse
import os

from credentials import CRED
from paths import TRANSACTIONS_DIR, weekly_roster_file
from ffapp.espn import transactions as tx

EARLIEST_YEAR = 2019          # box_scores / recent_activity both refuse earlier

# Same league set the weekly update runs over. Names are the ESPN league name,
# which is what every other data file on disk is keyed by.
LEAGUES = [
    {"league_id": 310334683,  "s2": "louie_s2",   "swid": "louie_swid",   "name": "Pennoni Younglings"},
    {"league_id": 996930954,  "s2": "louie_s2",   "swid": "louie_swid",   "name": "Family Fantasy"},
    {"league_id": 1118513122, "s2": "louie_s2",   "swid": "louie_swid",   "name": "EBC League"},
    {"league_id": 1339704102, "s2": "prahlad_s2", "swid": "prahlad_swid", "name": "0755 Fantasy Football"},
    {"league_id": 1781851,    "s2": "prahlad_s2", "swid": "prahlad_swid", "name": "Game of Yards!"},
    {"league_id": 367134149,  "s2": "prahlad_s2", "swid": "prahlad_swid", "name": "Brown Munde"},
    {"league_id": 1049459,    "s2": "la_s2",      "swid": "la_swid",      "name": "THE BEST OF THE BEST"},
    {"league_id": 1399036372, "s2": "hannah_s2",  "swid": "hannah_swid",  "name": "The Girl's Room 💞🏈"},
    {"league_id": 417131856,  "s2": "ava_s2",     "swid": "ava_swid",     "name": "Philly Extra Special"},
    {"league_id": 1259693145, "s2": "elle_s2",    "swid": "elle_swid",    "name": "Operators Football League"},
    {"league_id": 1675186799, "s2": "dave_s2",    "swid": "dave_swid",    "name": "OnP Fantasy"},
    {"league_id": 558148583,  "s2": "ayush_s2",   "swid": "ayush_swid",   "name": "Ross' Fantasy League"},
]


def _already_built(league_name, year):
    """True if this league-season is on disk, compressed or not.

    Checked against the name in LEAGUES below. Files are written under the name
    ESPN reports, so if a league was renamed on ESPN this returns False and the
    season is pulled again under its new name - wasteful but not wrong. Keep
    LEAGUES in step with ESPN to avoid it.
    """
    path = weekly_roster_file(league_name, year)
    return os.path.exists(path) or os.path.exists(path[:-3])


def run(years, only_league=None, skip_existing=False):
    from espn_api.football import League

    os.makedirs(TRANSACTIONS_DIR, exist_ok=True)
    done, skipped, failed = 0, 0, []

    for cfg in LEAGUES:
        if only_league and cfg['name'] != only_league:
            continue
        for year in years:
            if skip_existing and _already_built(cfg['name'], year):
                skipped += 1
                continue
            try:
                league = League(league_id=cfg['league_id'], year=year,
                                espn_s2=CRED[cfg['s2']], swid=CRED[cfg['swid']])
            except Exception as e:
                # a league that did not exist that year is expected, not an error
                failed.append((cfg['name'], year, type(e).__name__, str(e)))
                continue
            try:
                # ESPN reports the league's own name; prefer it so files line up
                # with the rest of data/ rather than with this script's label
                name = league.settings.name.replace(" 22/23", "") or cfg['name']
                tx.build_season(league, name, year)
                done += 1
            except Exception as e:
                failed.append((cfg['name'], year, type(e).__name__, str(e)))

    tx.say(f"\nbuilt {done} league-seasons"
           + (f", skipped {skipped} already on disk" if skipped else ""))
    if not failed:
        return

    # Separate the two very different reasons a season is missing. Lumping them
    # together hid that three THE BEST OF THE BEST seasons were a credential
    # problem, not a league that never existed.
    absent = [f for f in failed if f[2] == 'ESPNInvalidLeague']
    denied = [f for f in failed if f[2] == 'ESPNAccessDenied']
    other = [f for f in failed if f[2] not in ('ESPNInvalidLeague', 'ESPNAccessDenied')]

    if absent:
        tx.say(f"\n{len(absent)} league-season(s) do not exist on ESPN (expected - "
               f"the league had not started yet):")
        for name, year, _, _ in absent:
            tx.say(f"  {name} {year}")
    if denied:
        tx.say(f"\n⚠ {len(denied)} league-season(s) REFUSED - the stored cookie cannot "
               f"read them. These are real gaps, not missing leagues:")
        for name, year, _, _ in denied:
            tx.say(f"  {name} {year}")
    if other:
        tx.say(f"\n⚠ {len(other)} league-season(s) failed unexpectedly:")
        for name, year, kind, msg in other:
            tx.say(f"  {name} {year}: {kind}: {msg}")


def main():
    import datetime
    current = datetime.date.today().year
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--years', type=int, nargs='+',
                    default=list(range(EARLIEST_YEAR, current + 1)))
    ap.add_argument('--league', default=None, help='only this ESPN league name')
    ap.add_argument('--skip-existing', action='store_true',
                    help='leave league-seasons that already have a roster file')
    args = ap.parse_args()

    years = [y for y in args.years if y >= EARLIEST_YEAR]
    if len(years) != len(args.years):
        print(f"ignoring years before {EARLIEST_YEAR} (ESPN has no box scores)")
    run(years, args.league, args.skip_existing)


if __name__ == '__main__':
    main()
