"""Refresh final standings for every league-season.

`Finish` on the Lifetime page comes from `data/drafts/Draft_Grades_with_Standings.csv`,
which needs ESPN's `team.final_standing` and so cannot be rebuilt offline. That file
had stalled at 2024, leaving Finish blank for the whole of 2025.

The previous producer (`analysis/draft_analysis.py`) could not refresh it: its
`determine_final_standings(league_name, year)` reassigns `year = 2025` on the third
line, discarding the argument, then matches its league config on that year - so it
only ever resolves one season and silently returns an empty frame for any other.

This does the one job instead: one League init per league-season (~1 request), read
the standings, merge the current draft grades, write the file.

    python pipeline/refresh_standings.py                # 2019-current
    python pipeline/refresh_standings.py --years 2025
    python pipeline/refresh_standings.py --merge-only   # re-merge grades, no ESPN

Why not derive it from the data already on disk? Measured: reconstructing ESPN's
final standing from playoff brackets plus regular-season records matches on only
**62%** of team-seasons (champion 23/24, but the middle of the table diverges -
ESPN's consolation brackets and tiebreakers are not reproducible from what we
store). A number that is wrong for four teams in ten is worse than a blank.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import argparse
import datetime
import os

import pandas as pd

from credentials import CRED
from paths import AGGREGATED_DRAFT_GRADES, DRAFT_GRADES_WITH_STANDINGS
from ffapp.espn import transactions as tx          # for say(): league names carry emoji
from ffapp.metrics.owner_overrides import owner_id_for

EARLIEST_YEAR = 2019

# Same set the weekly update and the transaction backfill run over.
LEAGUES = [
    {"league_id": 310334683,  "s2": "louie_s2",   "swid": "louie_swid",   "name": "Pennoni Younglings"},
    {"league_id": 996930954,  "s2": "louie_s2",   "swid": "louie_swid",   "name": "Family Fantasy"},
    {"league_id": 1118513122, "s2": "louie_s2",   "swid": "louie_swid",   "name": "EBC League"},
    {"league_id": 1339704102, "s2": "prahlad_s2", "swid": "prahlad_swid", "name": "0755 Fantasy Football"},
    {"league_id": 1781851,    "s2": "prahlad_s2", "swid": "prahlad_swid", "name": "Game of Yards!"},
    {"league_id": 367134149,  "s2": "prahlad_s2", "swid": "prahlad_swid", "name": "Brown Munde"},
    {"league_id": 1049459,    "s2": "la_s2",      "swid": "la_swid",      "name": "THE BEST OF THE BEST"},
    {"league_id": 1399036372, "s2": "hannah_s2",  "swid": "hannah_swid",  "name": "The Girl's Room"},
    {"league_id": 417131856,  "s2": "ava_s2",     "swid": "ava_swid",     "name": "Philly Extra Special"},
    {"league_id": 261375772,  "s2": "matt_s2",    "swid": "matt_swid",    "name": "BP- Loudoun"},
    {"league_id": 1259693145, "s2": "elle_s2",    "swid": "elle_swid",    "name": "Operators Football League"},
    {"league_id": 1675186799, "s2": "dave_s2",    "swid": "dave_swid",    "name": "OnP Fantasy"},
    {"league_id": 1924463077, "s2": "dave_s2",    "swid": "dave_swid",    "name": "The Mike Daisy Sports IQ League"},
    {"league_id": 558148583,  "s2": "ayush_s2",   "swid": "ayush_swid",   "name": "Ross' Fantasy League"},
]

COLUMNS = ['Team', 'Draft Grade', 'Letter Grade', 'League Name', 'Standing',
           'Points For', 'Points Against', 'Record', 'Year', 'Owner ID']


def pull(years):
    """(league, year, team) standings rows straight from ESPN."""
    from espn_api.football import League

    rows, denied, absent = [], [], []
    for cfg in LEAGUES:
        for year in years:
            try:
                league = League(league_id=cfg['league_id'], year=year,
                                espn_s2=CRED[cfg['s2']], swid=CRED[cfg['swid']])
            except Exception as e:
                (denied if 'AccessDenied' in type(e).__name__ else absent
                 ).append((cfg['name'], year))
                continue
            try:
                name = league.settings.name.replace(" 22/23", "") or cfg['name']
                standings = league.standings()
            except Exception as e:
                tx.say(f"  {cfg['name']} {year}: standings failed "
                       f"({type(e).__name__}: {e})")
                continue
            # A season that exists on ESPN but has not been played yet reports
            # final_standing 0, standing 0 and 0-0-0 for everyone. Writing those
            # puts a Finish of 0 on the careers table for a season nobody played,
            # which reads as "finished first" at a glance.
            played = [t for t in standings
                      if (t.final_standing or t.standing or 0) > 0
                      or (t.wins or 0) + (t.losses or 0) + (t.ties or 0) > 0]
            if not played:
                tx.say(f"  {name} {year}: not played yet, skipped")
                continue

            for team in played:
                rows.append({
                    'Team': team.team_name,
                    'League Name': name,
                    'Year': year,
                    # final_standing is 0 until ESPN finalises a season; the
                    # regular-season standing is the honest stand-in mid-year
                    'Standing': team.final_standing or team.standing,
                    'Points For': round(float(team.points_for or 0), 2),
                    'Points Against': round(float(team.points_against or 0), 2),
                    'Record': f"{team.wins}-{team.losses}-{team.ties}",
                    'Owner ID': owner_id_for(league, team),
                })
            tx.say(f"  {name} {year}: {len(played)} teams")
    return pd.DataFrame(rows), denied, absent


def merge_grades(standings):
    """Attach the current draft grades. Grades are the source of truth in
    Aggregated_Draft_Grades.csv, which regrade_drafts rewrites in full."""
    if not os.path.exists(AGGREGATED_DRAFT_GRADES):
        standings['Draft Grade'] = pd.NA
        standings['Letter Grade'] = pd.NA
        return standings
    ag = pd.read_csv(AGGREGATED_DRAFT_GRADES)
    parts = ag['League Name'].str.rsplit(' ', n=1)
    ag['_league'] = parts.str[0].str.strip()
    ag['_year'] = pd.to_numeric(parts.str[1], errors='coerce')
    ag['_team'] = ag['Team'].astype(str).str.strip()
    lookup = {(l, y, t): (g, lg) for l, y, t, g, lg in
              zip(ag['_league'], ag['_year'], ag['_team'],
                  ag['Draft Grade'], ag['Letter Grade']) if pd.notna(y)}

    grades, letters = [], []
    for league, year, team in zip(standings['League Name'], standings['Year'],
                                  standings['Team']):
        hit = lookup.get((str(league).strip(), float(year), str(team).strip()))
        grades.append(hit[0] if hit else pd.NA)
        letters.append(hit[1] if hit else pd.NA)
    standings['Draft Grade'] = grades
    standings['Letter Grade'] = letters
    return standings


def main():
    current = datetime.date.today().year
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--years', type=int, nargs='+',
                    default=list(range(EARLIEST_YEAR, current + 1)))
    ap.add_argument('--merge-only', action='store_true',
                    help='re-merge draft grades into the existing file, no ESPN calls')
    args = ap.parse_args()

    if args.merge_only:
        if not os.path.exists(DRAFT_GRADES_WITH_STANDINGS):
            tx.say('nothing to merge into - run without --merge-only first')
            return
        df = merge_grades(pd.read_csv(DRAFT_GRADES_WITH_STANDINGS))
        df.to_csv(DRAFT_GRADES_WITH_STANDINGS, index=False)
        tx.say(f're-merged grades into {len(df)} rows')
        return

    years = [y for y in args.years if y >= EARLIEST_YEAR]
    tx.say(f'pulling standings for {len(LEAGUES)} leagues x {len(years)} seasons')
    standings, denied, absent = pull(years)
    if standings.empty:
        tx.say('no standings pulled - nothing written')
        return

    standings = merge_grades(standings)
    for col in COLUMNS:
        if col not in standings.columns:
            standings[col] = pd.NA
    standings = standings[COLUMNS].sort_values(['Year', 'League Name', 'Standing'])
    standings.to_csv(DRAFT_GRADES_WITH_STANDINGS, index=False)

    tx.say(f"\nwrote {len(standings)} rows to {os.path.basename(DRAFT_GRADES_WITH_STANDINGS)}")
    tx.say(f"  years: {sorted(standings['Year'].unique())}")
    tx.say(f"  leagues: {standings['League Name'].nunique()}")
    tx.say(f"  with a draft grade: {int(standings['Draft Grade'].notna().sum())}")
    if denied:
        tx.say(f"\n{len(denied)} refused by ESPN (cookie cannot read them):")
        for name, year in denied:
            tx.say(f"  {name} {year}")
    if absent:
        tx.say(f"\n{len(absent)} league-seasons do not exist (expected)")


if __name__ == '__main__':
    main()
