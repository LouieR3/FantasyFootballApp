"""Correctness and validity checks for the transaction analysis.

Two halves:

**Correctness** - synthetic rosters with a known answer, so the stint/SPAR
arithmetic is checked against a hand-computed result rather than eyeballed.

**Validity** - the honest questions about the metric itself, measured over every
backfilled league-season: does SPAR just measure how many moves you made, and
does it relate to actually winning games?

    python tools/check_transactions.py
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import os

import numpy as np
import pandas as pd

from paths import ALL_MATCHUPS
from ffapp.espn import transactions as tx
from ffapp.metrics import transaction_analysis as ta

FAILURES = []


def check(label, got, want):
    ok = got == want if not isinstance(want, float) else abs(got - want) < 1e-6
    print(f"  {'PASS' if ok else 'FAIL'}  {label}: got {got!r}, want {want!r}")
    if not ok:
        FAILURES.append(label)


def _roster_rows(spec, league='L', year=2024):
    """spec: list of (week, team, player, position, slot, points)."""
    return pd.DataFrame(
        [{'League': league, 'Year': year, 'Week': w, 'Team': t, 'Owner ID': f'own-{t}',
          'Player': p, 'Position': pos, 'Slot': s, 'Started': s not in tx.BENCH_SLOTS,
          'Points': pts, 'Projected': 0.0}
         for (w, t, p, pos, s, pts) in spec],
        columns=tx.ROSTER_COLUMNS)


# ---------------------------------------------------------------------------
def test_reconstruction():
    print("\n[reconstruction]")
    # A: on team1 the whole time. B: team1 -> team2 in wk2 (with a return leg,
    # so it is a trade). C: team2 -> team1 in wk2 (the return leg).
    # D: appears wk2 from nobody (ADD). E: on team1 wk1 then gone (DROP).
    spec = []
    for w in (1, 2, 3):
        spec.append((w, 'team1', 'A', 'RB', 'RB', 10.0))
    spec += [(1, 'team1', 'B', 'WR', 'WR', 5.0),
             (2, 'team2', 'B', 'WR', 'WR', 5.0),
             (3, 'team2', 'B', 'WR', 'WR', 5.0),
             (1, 'team2', 'C', 'WR', 'WR', 7.0),
             (2, 'team1', 'C', 'WR', 'WR', 7.0),
             (3, 'team1', 'C', 'WR', 'WR', 7.0),
             (2, 'team2', 'D', 'TE', 'TE', 9.0),
             (3, 'team2', 'D', 'TE', 'TE', 9.0),
             (1, 'team1', 'E', 'QB', 'QB', 3.0)]
    moves = tx.reconstruct_moves(_roster_rows(spec))
    kinds = moves['Type'].value_counts().to_dict()
    check('trade legs detected', kinds.get(tx.TRADE, 0), 2)
    check('adds detected', kinds.get(tx.ADD, 0), 1)
    check('drops detected', kinds.get(tx.DROP, 0), 1)
    check('no spurious team->team', kinds.get(tx.TEAM_TO_TEAM, 0), 0)

    # Without a return leg the same movement must NOT be called a trade.
    spec2 = [(1, 'team1', 'B', 'WR', 'WR', 5.0),
             (2, 'team2', 'B', 'WR', 'WR', 5.0)]
    m2 = tx.reconstruct_moves(_roster_rows(spec2))
    check('one-way move stays ambiguous',
          m2['Type'].tolist(), [tx.TEAM_TO_TEAM])


def test_stints_and_spar():
    print("\n[stints + SPAR]")
    # One position, one week, four rostered RBs scoring 0/4/8/20.
    # 25th percentile of [0,4,8,20] -> 3.0, but the pool is < MIN_POOL(4)? it is
    # exactly 4, so the quantile applies.
    spec = [(1, 't1', 'p0', 'RB', 'RB', 0.0),
            (1, 't2', 'p1', 'RB', 'RB', 4.0),
            (1, 't3', 'p2', 'RB', 'RB', 8.0),
            (1, 't4', 'p3', 'RB', 'RB', 20.0)]
    rosters = _roster_rows(spec)
    levels = ta.replacement_levels(rosters)
    check('replacement = 25th pctile', levels[(1, 'RB')], 3.0)

    st = ta.stints(rosters).set_index('Player')
    check('SPAR of the 20-pt back', float(st.loc['p3', 'SPAR']), 17.0)
    check('SPAR of the 0-pt back', float(st.loc['p0', 'SPAR']), -3.0)

    # a benched week contributes no SPAR and no started points
    spec3 = [(1, 't1', 'x', 'RB', 'RB', 10.0), (2, 't1', 'x', 'RB', 'BE', 30.0),
             (1, 't2', 'y', 'RB', 'RB', 0.0), (2, 't2', 'y', 'RB', 'RB', 0.0)]
    st3 = ta.stints(_roster_rows(spec3)).set_index('Player')
    check('benched points excluded from started', float(st3.loc['x', 'Points Started']), 10.0)
    check('benched points tracked separately', float(st3.loc['x', 'Points Benched']), 30.0)
    check('weeks started counts lineup weeks only', int(st3.loc['x', 'Weeks Started']), 1)

    # a re-acquisition is two stints, not one
    spec4 = [(1, 't1', 'z', 'RB', 'RB', 1.0), (2, 't2', 'z', 'RB', 'RB', 1.0),
             (3, 't1', 'z', 'RB', 'RB', 1.0)]
    st4 = ta.stints(_roster_rows(spec4))
    check('re-acquisition splits into stints', len(st4), 3)


def test_move_impacts():
    print("\n[move impacts]")
    # y is added by t1 in week 2 and started for 2 weeks at 10 pts.
    spec = [(1, 't1', 'a', 'RB', 'RB', 5.0), (2, 't1', 'a', 'RB', 'RB', 5.0),
            (3, 't1', 'a', 'RB', 'RB', 5.0),
            (2, 't1', 'y', 'RB', 'RB', 10.0), (3, 't1', 'y', 'RB', 'RB', 10.0),
            (1, 't2', 'b', 'RB', 'RB', 0.0), (2, 't2', 'b', 'RB', 'RB', 0.0),
            (3, 't2', 'b', 'RB', 'RB', 0.0)]
    rosters = _roster_rows(spec)
    moves = tx.reconstruct_moves(rosters)
    imp = ta.move_impacts(rosters, moves)
    check('one acquisition scored', len(imp), 1)
    row = imp.iloc[0]
    check('credited to the acquiring team', row['Team'], 't1')
    check('started points over the stint', float(row['Points Started']), 20.0)
    check('weeks started', int(row['Weeks Started']), 2)


def test_drop_costs():
    print("\n[drop regret]")
    # t1 drops 'star' after week 1; t2 picks them up and starts them for 20/wk.
    spec = [(1, 't1', 'star', 'WR', 'WR', 1.0),
            (2, 't2', 'star', 'WR', 'WR', 20.0), (3, 't2', 'star', 'WR', 'WR', 20.0),
            (1, 't1', 'filler', 'WR', 'WR', 1.0), (2, 't1', 'filler', 'WR', 'WR', 1.0),
            (3, 't1', 'filler', 'WR', 'WR', 1.0),
            (1, 't2', 'other', 'WR', 'WR', 1.0), (2, 't2', 'other', 'WR', 'WR', 1.0),
            (3, 't2', 'other', 'WR', 'WR', 1.0)]
    rosters = _roster_rows(spec)
    moves = tx.reconstruct_moves(rosters)
    # the snapshot sees this as a team-to-team move, not a drop, because 'star'
    # never spends a week unrostered - that is correct and worth asserting
    check('same-week claim reads as team->team',
          tx.TEAM_TO_TEAM in moves['Type'].tolist(), True)

    # now with a genuine gap week so it is a real drop
    spec2 = [r for r in spec if not (r[0] == 2 and r[2] == 'star')]
    rosters2 = _roster_rows(spec2)
    moves2 = tx.reconstruct_moves(rosters2)
    regret = ta.drop_costs(rosters2, moves2)
    check('drop with a gap is scored', len(regret), 1)
    check('regret counts only post-drop weeks',
          float(regret.iloc[0]['Points Started After']), 20.0)


def test_week_range():
    """Regression: the pull must not drop the championship week.

    `current_week - 1` looks right and is wrong - on a finished season ESPN
    leaves current_week at the final scoring period, so 2024 (scores in all 17
    weeks, current_week 17) silently lost week 17 and 191 player-weeks with it.
    """
    print("\n[week range]")

    class FakeTeam:
        def __init__(self, scores):
            self.scores = scores

    class FakeLeague:
        def __init__(self, scores, current):
            self.teams = [FakeTeam(s) for s in scores]
            self.current_week = current

    # finished season: 17 weeks all played, current_week parked at 17
    done = FakeLeague([[10.0] * 17, [9.0] * 17], current=17)
    check('finished season keeps the last week', tx._completed_weeks(done), 17)
    check('and current_week-1 would have dropped it',
          tx._completed_weeks(done) > done.current_week - 1, True)

    # mid-season: 5 played, rest padded with zeros
    mid = FakeLeague([[10.0] * 5 + [0.0] * 12, [9.0] * 5 + [0.0] * 12], current=6)
    check('in-progress season stops at the last played week',
          tx._completed_weeks(mid), 5)

    # week 1 not yet played - must be 0, not a negative range
    fresh = FakeLeague([[0.0] * 17, [0.0] * 17], current=1)
    check('unplayed season yields no weeks', tx._completed_weeks(fresh), 0)


def test_activity_labels():
    """The 2026 path: ESPN's feed upgrades inferred moves to real ones.

    Cannot be exercised against live ESPN until a season is in progress - the
    feed 404s for every completed season - so it is pinned synthetically here.
    """
    print("\n[activity labelling]")
    spec = [(1, 't1', 'a', 'RB', 'RB', 5.0), (2, 't1', 'a', 'RB', 'RB', 5.0),
            (2, 't1', 'newguy', 'WR', 'WR', 12.0),
            (1, 't2', 'b', 'RB', 'RB', 5.0), (2, 't2', 'b', 'RB', 'RB', 5.0),
            (1, 't2', 'mover', 'WR', 'WR', 8.0), (2, 't1', 'mover', 'WR', 'WR', 8.0)]
    rosters = _roster_rows(spec)
    moves = tx.reconstruct_moves(rosters)
    before = dict(zip(moves['Player'], moves['Type']))
    check('newguy inferred as ADD', before['newguy'], tx.ADD)
    check('mover inferred as ambiguous', before['mover'], tx.TEAM_TO_TEAM)

    activity = pd.DataFrame([
        {'Player': 'newguy', 'Action': 'WAIVER ADDED', 'FAAB Bid': 17, 'Date': 0},
        {'Player': 'mover', 'Action': 'TRADED', 'FAAB Bid': 0, 'Date': 0},
    ])
    labelled = tx.apply_activity_labels(moves, activity, lambda _ms: 2)
    after = {p: (t, s, b) for p, t, s, b in zip(
        labelled['Player'], labelled['Type'], labelled['Source'], labelled['FAAB Bid'])}
    check('ambiguous move resolved to TRADE', after['mover'][0], tx.TRADE)
    check('trade marked as reported', after['mover'][1], 'activity')
    check('FAAB bid attached', after['newguy'][2], 17)
    check('add stays an add', after['newguy'][0], tx.ADD)

    # an empty feed (a completed season) must leave everything untouched
    untouched = tx.apply_activity_labels(moves, pd.DataFrame(), lambda _ms: 2)
    check('empty feed is a no-op', untouched['Type'].tolist(), moves['Type'].tolist())


def test_week_mapper():
    print("\n[activity week mapping]")
    import datetime as dt
    rosters = _roster_rows([(w, 't1', 'a', 'RB', 'RB', 1.0) for w in range(1, 15)],
                           year=2025)
    to_week = tx.week_mapper(rosters)
    # 2025: first Tuesday on/after Sep 1 is Sep 2. A Sunday in that week = wk1.
    wk1 = dt.datetime(2025, 9, 7, 18, tzinfo=dt.timezone.utc).timestamp() * 1000
    wk3 = dt.datetime(2025, 9, 21, 18, tzinfo=dt.timezone.utc).timestamp() * 1000
    check('week 1 maps to 1', to_week(wk1), 1)
    check('week 3 maps to 3', to_week(wk3), 3)
    check('garbage maps to None', to_week(None), None)
    check('far future clamps to last week', to_week(wk1 + 400 * 86400_000), 14)


# ---------------------------------------------------------------------------
def wins_by_team():
    """(League, Year, Team) -> regular-season wins, from all_matchups.csv."""
    if not os.path.exists(ALL_MATCHUPS):
        return {}
    m = pd.read_csv(ALL_MATCHUPS)
    wins = {}
    for lg, yr, hteam, ateam, winner in zip(m['League'], m['Year'], m['Home Team'],
                                            m['Away Team'], m['Actual Winner']):
        for team in (hteam, ateam):
            wins.setdefault((lg, int(yr), team), 0)
        if winner in (hteam, ateam):
            wins[(lg, int(yr), winner)] += 1
    return wins


def test_validity():
    print("\n[validity - is the metric measuring anything real?]")
    seasons = tx.available_seasons()
    if not seasons:
        print("  no backfilled seasons yet; skipping")
        return
    wins = wins_by_team()

    rows = []
    for league, year in seasons:
        rosters, moves = tx.load_season(league, year)
        if rosters.empty:
            continue
        summary = ta.owner_summary(rosters, moves)
        for team, n_moves, spar, per_add in zip(summary['Team'], summary['Moves'],
                                                summary['SPAR'], summary['SPAR per Add']):
            rows.append({'League': league, 'Year': year, 'Team': team,
                         'Moves': n_moves, 'SPAR': spar, 'SPAR per Add': per_add,
                         'Wins': wins.get((league, year, team))})
    df = pd.DataFrame(rows)
    print(f"  {len(df)} team-seasons across {len(seasons)} league-seasons")
    if len(df) < 10:
        print("  too few to correlate")
        return

    r_vol = df['Moves'].corr(df['SPAR'])
    print(f"  corr(Moves, SPAR)            = {r_vol:+.2f}   "
          f"{'<-- SPAR largely measures activity' if r_vol > 0.6 else ''}")

    have = df.dropna(subset=['Wins'])
    if len(have) >= 10:
        print(f"  corr(SPAR, Wins)             = {have['SPAR'].corr(have['Wins']):+.2f}   "
              f"(n={len(have)})")
        print(f"  corr(SPAR per Add, Wins)     = {have['SPAR per Add'].corr(have['Wins']):+.2f}")
        print(f"  corr(Moves, Wins)            = {have['Moves'].corr(have['Wins']):+.2f}")
    else:
        print("  no win data joined (check league-name alignment with all_matchups.csv)")

    # does transaction value persist for the same manager year over year?
    pairs = []
    for (league, team), grp in df.groupby(['League', 'Team']):
        grp = grp.sort_values('Year')
        for a, b in zip(grp.itertuples(index=False), list(grp.itertuples(index=False))[1:]):
            if b.Year == a.Year + 1:
                pairs.append((a.SPAR, b.SPAR))
    if len(pairs) >= 10:
        arr = np.array(pairs)
        r = np.corrcoef(arr[:, 0], arr[:, 1])[0, 1]
        print(f"  year-over-year SPAR (same team) = {r:+.2f}  (n={len(pairs)})")
    else:
        print(f"  only {len(pairs)} consecutive-season pairs; skipping persistence")


if __name__ == '__main__':
    test_reconstruction()
    test_stints_and_spar()
    test_move_impacts()
    test_drop_costs()
    test_week_range()
    test_activity_labels()
    test_week_mapper()
    test_validity()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED: {FAILURES}")
        raise SystemExit(1)
    print("all correctness checks passed")
