"""Does a weekly update actually reach the historical pages?

The weekly scripts write transaction data; the Transaction Analysis and Hall of
Fame pages read it. Nothing enforces that those two agree - the league name, the
file paths and the discovery glob all have to line up, and they are set in three
different files. This asserts the whole chain without touching ESPN.

    python tools/check_weekly_flow.py
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import os
import re

import pandas as pd

from paths import TRANSACTIONS_DIR, weekly_roster_file, moves_file
from ffapp.espn import transactions as tx
from ffapp.metrics import transaction_analysis as ta
from ffapp.metrics import transaction_hall_of_fame as thof

FAILURES = []


def check(label, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {label}: got {got!r}, want {want!r}")
    if not ok:
        FAILURES.append(label)


class FakeTeam:
    def __init__(self, tid, name, scores):
        self.team_id, self.team_name, self.scores = tid, name, scores
        self.owners = [{'id': f'{{OWNER-{tid}}}', 'firstName': f'Owner{tid}',
                        'lastName': 'Test'}]
        self.roster = []


class FakePlayer:
    def __init__(self, name, pos, slot, pts):
        self.name, self.position, self.slot_position = name, pos, slot
        self.points, self.projected_points = pts, pts


class FakeBox:
    def __init__(self, home, home_lineup, away, away_lineup):
        self.home_team, self.home_lineup = home, home_lineup
        self.away_team, self.away_lineup = away, away_lineup


class FakeSettings:
    name = 'Flow Test League'
    reg_season_count = 3
    playoff_team_count = 2
    team_count = 2
    roster = {'QB': 1, 'RB': 1, 'BE': 1}


class FakeLeague:
    """Two teams, three weeks. A free-agent add lands in week 2."""
    settings = FakeSettings()

    def __init__(self):
        self.teams = [FakeTeam(1, 'Alpha', [100.0] * 3),
                      FakeTeam(2, 'Bravo', [90.0] * 3)]
        self.current_week = 3

    def box_scores(self, week):
        a, b = self.teams
        a_line = [FakePlayer('Anna QB', 'QB', 'QB', 20.0),
                  FakePlayer('Andy RB', 'RB', 'RB', 10.0)]
        if week >= 2:                       # the add we expect to be detected
            a_line.append(FakePlayer('Late Bloomer', 'RB', 'BE', 30.0))
        b_line = [FakePlayer('Bob QB', 'QB', 'QB', 18.0),
                  FakePlayer('Ben RB', 'RB', 'RB', 4.0)]
        return [FakeBox(a, a_line, b, b_line)]

    def recent_activity(self, size=25, offset=0):
        raise RuntimeError('ESPNInvalidLeague: no feed in this test')


def main():
    league = FakeLeague()
    name, year = FakeSettings.name, 2099
    roster_path, move_path = weekly_roster_file(name, year), moves_file(name, year)
    for p in (roster_path, move_path):
        if os.path.exists(p):
            os.remove(p)

    print("\n[1. the weekly update writes]")
    # exactly what pipeline/ESPNWeeklyUpdateList.py calls
    rosters, moves, note = tx.build_season(league, name, year)
    check('roster file written where paths.py says', os.path.exists(roster_path), True)
    check('moves file written', os.path.exists(move_path), True)
    check('all 3 played weeks captured', sorted(rosters['Week'].unique()), [1, 2, 3])
    check('the week-2 add was detected',
          moves[moves['Type'] == tx.ADD]['Player'].tolist(), ['Late Bloomer'])
    check('missing feed degrades, does not raise', 'unavailable' in note, True)

    print("\n[2. the Transaction Analysis page discovers it]")
    found = tx.available_seasons()
    check('season appears in available_seasons()', (name, year) in found, True)
    scored = ta.load_and_score(name, year)
    check('page can score it', len(scored['owners']), 2)
    check('owner id survives the round trip',
          scored['owners']['Owner ID'].tolist(), ['{OWNER-1}', '{OWNER-2}'])

    print("\n[3. the Hall of Fame picks it up]")
    txn = thof.transaction_seasons()
    check('league-season reaches the HoF table',
          (txn['Season'] == f'{name} {year}').sum(), 2)
    adds, drops, trades = thof.all_moves()
    check('its adds reach the all-time list',
          'Late Bloomer' in set(adds['Player']), True)

    print("\n[4. re-running the same week is idempotent]")
    before = pd.read_csv(roster_path).shape
    tx.build_season(league, name, year)
    check('rerun does not duplicate rows', pd.read_csv(roster_path).shape, before)

    print("\n[5. naming agrees across the three files that set it]")
    # the weekly scripts derive the name this way; the backfill must match, or
    # the same league lands under two different filenames
    weekly_name = FakeSettings.name.replace(" 22/23", "")
    check('weekly-update name == backfill name', weekly_name, name)
    base = os.path.basename(weekly_roster_file(weekly_name, year))
    m = re.match(r'^(.+?) Weekly Rosters (\d{4})\.csv(\.gz)?$', base)
    check('discovery regex parses the written filename',
          (m.group(1), int(m.group(2))) if m else None, (name, year))

    for p in (roster_path, move_path):
        if os.path.exists(p):
            os.remove(p)

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED: {FAILURES}")
        raise SystemExit(1)
    print("weekly update flows into both historical pages")


if __name__ == '__main__':
    main()
