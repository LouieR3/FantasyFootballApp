"""Checks for the live draft assistant.

Offline assertions on the matching and value maths, then - if credentials are
available - a live replay against a real completed draft, which is the only way
to prove the board actually tracks a draft.

    python tools/check_draft_board.py
    python tools/check_draft_board.py --csv "path/to/rankings.csv"
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import argparse
import io

import pandas as pd

from ffapp.metrics import draft_board as db

FAILURES = []


def check(label, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {label}: got {got!r}, want {want!r}")
    if not ok:
        FAILURES.append(label)


# ---------------------------------------------------------------- normalisation
def test_names():
    print("\n[name normalisation]")
    # the 11% of names that differ only by suffix or punctuation
    pairs = [('James Cook III', 'James Cook'),
             ('Kenneth Walker III', 'Kenneth Walker'),
             ('Travis Etienne Jr.', 'Travis Etienne'),
             ('Kyle Pitts Sr.', 'Kyle Pitts'),
             ('Marvin Harrison Jr.', 'Marvin Harrison'),
             ('A.J. Brown', 'AJ Brown'),
             ("Ja'Marr Chase", 'JaMarr Chase'),
             ('Amon-Ra St. Brown', 'Amon Ra St Brown'),
             ("De'Von Achane", 'DeVon Achane'),
             ('Michael Pittman Jr.', 'Michael Pittman')]
    for espn, sheet in pairs:
        check(f'{espn!r} == {sheet!r}', db._clean(espn), db._clean(sheet))

    # must NOT collapse genuinely different people
    print("  -- and must keep different players apart --")
    check('Josh Allen != Keenan Allen',
          db._clean('Josh Allen') == db._clean('Keenan Allen'), False)
    check('Michael Carter != Michael Carter II is the same person',
          db._clean('Michael Carter') == db._clean('Michael Carter II'), True)


def test_column_aliases():
    print("\n[flexible column names]")
    csv = io.StringIO(",Player,POS,Rk,ADP\n,Bijan Robinson,RB,1,2.5\n"
                      ",Ja'Marr Chase,WR,2,3.1\n")
    rk = db.load_rankings(csv)
    check('reads Player/Rk/POS/ADP', list(rk.columns[:4]),
          ['Player', 'ECR', 'Pos', 'Sheet ADP'])
    check('drops the unnamed index column',
          any(str(c).startswith('Unnamed') for c in rk.columns), False)

    print("  -- and fails loudly on a sheet it cannot read --")
    try:
        db.load_rankings(io.StringIO('a,b\n1,2\n'))
        check('missing name column raises', False, True)
    except ValueError as e:
        check('missing name column raises ValueError', 'name column' in str(e), True)


def test_matching_and_value():
    print("\n[matching + value maths]")
    pool = {
        11: {'player_id': 11, 'name': 'James Cook III', 'position': 'RB',
             'pro_team_id': 2, 'espn_rank': 12, 'adp': 13.0,
             'percent_owned': 99.0, 'injured': False, 'injury_status': None},
        12: {'player_id': 12, 'name': "Ja'Marr Chase", 'position': 'WR',
             'pro_team_id': 4, 'espn_rank': 4, 'adp': 4.7,
             'percent_owned': 99.8, 'injured': False, 'injury_status': None},
        13: {'player_id': 13, 'name': 'Kyle Pitts Sr.', 'position': 'TE',
             'pro_team_id': 1, 'espn_rank': 71, 'adp': 90.0,
             'percent_owned': 70.0, 'injured': False, 'injury_status': None},
        14: {'player_id': 14, 'name': '49ers D/ST', 'position': 'D/ST',
             'pro_team_id': 25, 'espn_rank': 234, 'adp': 190.0,
             'percent_owned': 50.0, 'injured': False, 'injury_status': None},
        15: {'player_id': 15, 'name': 'Nobody Onsheet', 'position': 'WR',
             'pro_team_id': 3, 'espn_rank': 60, 'adp': 65.0,
             'percent_owned': 20.0, 'injured': False, 'injury_status': None},
    }
    rk = db.load_rankings(io.StringIO(
        ",Name,Pos,FantasyPros,ADP\n"
        ",James Cook,RB,16,13\n"
        ",Ja'Marr Chase,WR,1,3\n"
        ",Kyle Pitts,TE,79,71\n"
        ",Ghost Player,WR,120,150\n"))
    m, left, espn_left = db.match_to_espn(rk, pool)
    check('3 of 4 sheet rows matched', len(m), 3)
    check('the unmatched one is reported', left['Player'].tolist(), ['Ghost Player'])
    check('suffix names matched', sorted(m['ESPN Name']),
          ["Ja'Marr Chase", 'James Cook III', 'Kyle Pitts Sr.'])
    check('D/ST excluded from the missing-from-sheet report',
          '49ers D/ST' in set(espn_left['ESPN Name']), False)
    check('a real missing player IS reported',
          'Nobody Onsheet' in set(espn_left['ESPN Name']), True)

    v = db.add_value(m)
    # Kyle Pitts: ADP 90, ECR 79 -> falling 11 picks past consensus
    pitts = v[v['Pos'] == 'TE'].iloc[0]
    check('VALUE = ADP - ECR', float(pitts['VALUE']), 11.0)
    # only one player per position here, so every position rank is 1 -> Pos VALUE 0
    check('Pos VALUE is position-relative', float(pitts['Pos VALUE']), 0.0)

    # board: mark Chase taken and confirm he leaves the board
    state = {'taken': {12: {'overall': 3, 'round': 1, 'team_id': 5}},
             'slots': [{'overall': 3, 'round': 1, 'team_id': 5, 'player_id': 12,
                        'autodrafted': False}]}
    avail, gone = db.board(v, state)
    check('taken player leaves the board',
          "Ja'Marr Chase" in set(avail['ESPN Name']), False)
    check('taken player appears in the gone list', len(gone), 1)
    check('gone carries the pick number', int(gone.iloc[0]['Pick']), 3)

    log = db.recent_picks(state, pool, {5: 'Team Five'})
    check('draft log resolves the pick', log.iloc[0]['Player'], "Ja'Marr Chase")


def test_kdst_in_log():
    print("\n[K/DST still appear in the draft log]")
    # the sheet has no kickers, but people draft them - the log must not skip picks
    pool = {14: {'player_id': 14, 'name': '49ers D/ST', 'position': 'D/ST',
                 'adp': 190.0, 'espn_rank': 234, 'percent_owned': 1,
                 'injured': False, 'injury_status': None, 'pro_team_id': 25}}
    state = {'taken': {14: {'overall': 140, 'round': 12, 'team_id': 2}},
             'slots': [{'overall': 140, 'round': 12, 'team_id': 2,
                        'player_id': 14, 'autodrafted': False}]}
    log = db.recent_picks(state, pool, {2: 'Team Two'})
    check('D/ST pick shows in the log', log.iloc[0]['Player'], '49ers D/ST')


def test_roster_logic():
    print("\n[roster needs + caps]")
    sg = [(('D/ST',), 1), (('K',), 1), (('QB',), 1), (('RB',), 2),
          (('TE',), 1), (('WR',), 2), (('RB', 'WR', 'TE'), 1)]

    needs, flex = db.remaining_needs({}, sg)
    check('empty roster needs 2 RB', needs.get('RB'), 2)
    check('empty roster has the flex open', flex, 1)

    # a third back must soak the flex, not leave WR2 looking open
    needs, flex = db.remaining_needs({'RB': 3, 'WR': 2, 'QB': 1, 'TE': 1}, sg)
    check('3rd RB fills the flex', flex, 0)
    check('and WR is not still wanted', needs.get('WR', 0), 0)
    check('only K/DST left', sorted(p for p, n in needs.items() if n),
          ['D/ST', 'K'])

    caps = db.position_caps(sg)
    check('RB cap = 2 starters + flex + bench', caps['RB'], 6)
    check('QB cap = 1 starter + 1 bench', caps['QB'], 2)
    check('K cap = 1, no bench', caps['K'], 1)


def test_recommend_ordering():
    """Regression: the pick you make now must not be driven by value-over-ADP."""
    print("\n[recommend ordering]")
    frame = pd.DataFrame([
        # a clearly better back, going roughly at his rank
        {'player_id': 1, 'Player': 'Good Back', 'Pos': 'RB', 'ECR': 20, 'ADP': 22},
        # a much worse back who happens to be falling a long way
        {'player_id': 2, 'Player': 'Deep Sleeper', 'Pos': 'RB', 'ECR': 130,
         'ADP': 175},
        {'player_id': 3, 'Player': 'Good Wr', 'Pos': 'WR', 'ECR': 25, 'ADP': 26},
    ])
    v = db.add_value(frame)
    recs = db.recommend(v, {}, None, next_pick=40, n=3)
    check('the better player is recommended first, not the bigger bargain',
          recs.iloc[0]['Player'], 'Good Back')
    check('the deep sleeper is not first',
          recs.iloc[0]['Player'] == 'Deep Sleeper', False)

    # the lean knob must actually change the answer
    rb_first = db.recommend(v, {}, None, next_pick=40, n=1, lean=3,
                            priority={'RB': 1.4, 'WR': 1.0})
    wr_first = db.recommend(v, {}, None, next_pick=40, n=1, lean=3,
                            priority={'RB': 1.0, 'WR': 1.4})
    check('a strong RB lean takes the back', rb_first.iloc[0]['Pos'], 'RB')
    check('a strong WR lean takes the receiver', wr_first.iloc[0]['Pos'], 'WR')

    # a capped position must drop out entirely
    capped = db.recommend(v, {'RB': 9}, None, next_pick=40, n=3)
    top = capped.iloc[0]
    check('past the RB cap it stops suggesting backs', top['Pos'], 'WR')


def test_dropoff():
    print("\n[dropoff]")
    frame = pd.DataFrame([
        {'player_id': 1, 'Player': 'A', 'Pos': 'RB', 'ECR': 10, 'ADP': 12},
        {'player_id': 2, 'Player': 'B', 'Pos': 'RB', 'ECR': 60, 'ADP': 80},
        {'player_id': 3, 'Player': 'C', 'Pos': 'TE', 'ECR': 30, 'ADP': 33},
        {'player_id': 4, 'Player': 'D', 'Pos': 'TE', 'ECR': 34, 'ADP': 90},
    ])
    v = db.add_value(frame)
    drop = db.positional_dropoff(v, next_pick=50).set_index('Pos')
    # RB: best now 10, best surviving past 50 is B at 60 -> waiting costs 50
    check('RB dropoff', float(drop.loc['RB', 'Dropoff']), 50.0)
    # TE: best now 30, best survivor is D at 34 -> waiting costs 4
    check('TE dropoff', float(drop.loc['TE', 'Dropoff']), 4.0)
    check('the scarcer position sorts first', drop.index[0], 'RB')


def test_live(csv_path):
    """Replay a real completed draft as if it were happening."""
    print("\n[live replay against a real draft]")
    try:
        from credentials import CRED
        from ffapp.espn import live_draft as ld
    except Exception as e:
        print(f"  skipped (no credentials): {e}")
        return
    if not csv_path or not os.path.exists(csv_path):
        print("  skipped (pass --csv to replay with a real rankings sheet)")
        return

    LID, S2, SWID = 310334683, CRED['louie_s2'], CRED['louie_swid']
    try:
        pool = ld.player_pool(LID, 2026, S2, SWID, limit=400)
        state25 = ld.draft_state(LID, 2025, S2, SWID)
        state26 = ld.draft_state(LID, 2026, S2, SWID)
    except Exception as e:
        print(f"  skipped ({type(e).__name__}: {e})")
        return

    check('completed draft reports drafted=True', state25['drafted'], True)
    check('undrafted season reports drafted=False', state26['drafted'], False)
    check('pick order exists before the draft', state26['total_picks'] > 0, True)
    check('nothing taken yet in the undrafted season', state26['picks_made'], 0)

    first = state26['on_the_clock']
    team = first['team_id']
    check('someone is on the clock pre-draft', first['overall'], 1)
    check('picks_until is 0 for the team on the clock',
          ld.picks_until(state26, team), 0)
    turns = ld.next_turns(state26, team, 3)
    check('next_turns returns ascending picks',
          [t['overall'] for t in turns] == sorted(t['overall'] for t in turns), True)

    rk = db.load_rankings(csv_path)
    m, left, espn_left = db.match_to_espn(rk, pool)
    rate = len(m) / max(len(rk), 1)
    print(f"  match rate against live ESPN pool: {len(m)}/{len(rk)} = {rate:.1%}")
    check('match rate above 95%', rate > 0.95, True)
    v = db.add_value(m)

    # freeze the completed 2025 draft partway and confirm the board shrinks
    for cut in (0, 24, 100):
        frozen = {'taken': {s['player_id']: s for s in state25['slots']
                            if s['player_id'] and (s['overall'] or 0) <= cut},
                  'slots': state25['slots']}
        avail, gone = db.board(v, frozen)
        print(f"    after pick {cut:>3}: {len(avail):>3} on the board, {len(gone):>3} of the sheet gone")
    check('board shrinks as picks are made',
          len(db.board(v, {'taken': {}, 'slots': []})[0])
          > len(db.board(v, {'taken': {s['player_id']: s for s in state25['slots']
                                       if s['player_id']}, 'slots': state25['slots']})[0]),
          True)

    top = db.value_picks(v, 5)
    if len(top):
        print("  biggest positional value on the full board:")
        for r in top.to_dict('records'):
            print(f"    {r['Pos']:>4}  {r['ESPN Name']:22.22s} "
                  f"ECR {r['ECR']:>5.0f}  ADP {r['ADP']:>6}  Pos VALUE {r['Pos VALUE']:+.1f}")
        check('value list excludes K/DST',
              set(top['Pos']) & {'K', 'D/ST'}, set())


if __name__ == '__main__':
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default=None, help='a real rankings CSV to replay with')
    args = ap.parse_args()

    test_names()
    test_column_aliases()
    test_matching_and_value()
    test_kdst_in_log()
    test_roster_logic()
    test_recommend_ordering()
    test_dropoff()
    test_live(args.csv)

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED: {FAILURES}")
        raise SystemExit(1)
    print("draft board checks passed")
