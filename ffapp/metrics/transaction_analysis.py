"""Scoring in-season roster moves: who actually improved their team.

Companion to `draft_analysis.py`. That one grades the draft; this grades
everything after it - the waiver wire and the trade market.

The unit of value is **started points above replacement (SPAR)**. Two choices
worth stating, because both are load-bearing:

*Started, not rostered.* Points only count when the player was in a lineup slot.
Rostering a breakout you never started is not a good pickup, and raw rostered
points reward hoarding a deep bench.

*Above replacement, not absolute.* An add is worth what it beat, not what it
scored. Replacement level is the ``REPLACEMENT_PCTILE`` quantile of points among
all players rostered at that position in that league-week - an approximation of
the fringe player freely available at the time. It has to be approximated from
rostered players because ESPN does not retain weekly scores for players nobody
owned. That makes SPAR slightly conservative (the true free-agent pool is worse
than the worst rostered player), which is the right direction to err.

Why not score each add against the specific player dropped for it? At weekly
snapshot granularity, adds and drops in the same week cannot be paired reliably -
a team making three moves at once gives 9 possible pairings and no way to choose.
Replacement level sidesteps the pairing problem entirely. Drops are scored
separately, by what the player went on to do for *someone else*.

A season's moves are graded on the same 30-100 scale as the draft grade, z-scored
within league-season so the two are directly comparable and can be read together.

**What this grade is not.** Measured over 423 team-seasons from 38 backfilled
league-seasons (``tools/check_transactions.py``), total SPAR correlates with the
raw number of moves at **r = +0.69** and with regular-season wins at **r = +0.01**
(n = 361). Volume-adjusting does not rescue it: ``SPAR per Add`` versus wins is
**r = -0.06**. Nothing here predicts winning.

So this grades how much value a manager extracted *through transactions* - not
how well they managed, and not whether it worked. A team that drafted well has
little to gain from the wire and scores low for a good reason; a team patching a
broken draft can post a huge SPAR and still lose. Compare the draft grade, which
reaches r = -0.51 against final standing.

Year over year the same team repeats its SPAR at r = +0.27 (n = 153), so there
is *some* persistent tendency - mostly a tendency to be active, given the +0.69
with move count.

Making this predict wins would need the counterfactual the snapshots cannot
supply on their own: what the team *would* have started had it stood pat. That
is a lineup simulation over the drafted roster, not a transaction metric, and is
noted in SCOPE rather than faked here.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import numpy as np
import pandas as pd

from ffapp.espn import transactions as tx
from ffapp.metrics.draft_grading import (GRADE_CENTER, GRADE_PER_Z, GRADE_MIN,
                                         GRADE_MAX, grade_to_letter)

# Quantile of rostered scorers at a position/week taken as replacement level.
REPLACEMENT_PCTILE = 0.25
# Below this many players at a position in a week, the quantile is meaningless
# and replacement falls back to the week's minimum.
MIN_POOL = 4

ACQUIRING = (tx.ADD, tx.TRADE, tx.TEAM_TO_TEAM)

# Per-league-season Transaction Grade lookups, memoised because league pages ask
# team by team and each miss would otherwise rescore the whole season.
_TEAM_GRADE_CACHE = {}


# ---------------------------------------------------------------------------
# replacement level
# ---------------------------------------------------------------------------

def replacement_levels(rosters):
    """(Week, Position) -> replacement-level points for that league-season."""
    if rosters.empty:
        return {}
    out = {}
    for (week, pos), chunk in rosters.groupby(['Week', 'Position']):
        pts = chunk['Points'].astype(float)
        out[(int(week), pos)] = float(pts.min() if len(pts) < MIN_POOL
                                      else pts.quantile(REPLACEMENT_PCTILE))
    return out


def replacement_table(rosters):
    """Replacement level per position per week, for display."""
    levels = replacement_levels(rosters)
    rows = [{'Week': w, 'Position': p, 'Replacement': round(v, 2)}
            for (w, p), v in sorted(levels.items())]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# ownership stints
# ---------------------------------------------------------------------------

def stints(rosters):
    """One row per unbroken run of weeks a player spent on one roster.

    A player added, dropped and re-added is three separate stints, which is what
    lets each move be scored against the spell it actually started.
    """
    if rosters.empty:
        return pd.DataFrame(columns=['Player', 'Position', 'Team', 'Owner ID',
                                     'Start Week', 'End Week', 'Weeks',
                                     'Weeks Started', 'Points Started',
                                     'Points Benched', 'SPAR'])
    levels = replacement_levels(rosters)
    df = rosters.sort_values(['Player', 'Week'])

    rows = []
    cur = None
    for player, week, team, owner, pos, started, pts in zip(
            df['Player'], df['Week'], df['Team'], df['Owner ID'],
            df['Position'], df['Started'], df['Points']):
        week = int(week)
        started = bool(started)
        pts = float(pts or 0)
        contiguous = (cur is not None and cur['Player'] == player
                      and cur['Team'] == team and week == cur['End Week'] + 1)
        if not contiguous:
            if cur is not None:
                rows.append(cur)
            cur = {'Player': player, 'Position': pos, 'Team': team,
                   'Owner ID': owner, 'Start Week': week, 'End Week': week,
                   'Weeks': 0, 'Weeks Started': 0, 'Points Started': 0.0,
                   'Points Benched': 0.0, 'SPAR': 0.0}
        cur['End Week'] = week
        cur['Weeks'] += 1
        if started:
            repl = levels.get((week, pos), 0.0)
            cur['Weeks Started'] += 1
            cur['Points Started'] += pts
            cur['SPAR'] += pts - repl
        else:
            cur['Points Benched'] += pts
    if cur is not None:
        rows.append(cur)

    out = pd.DataFrame(rows)
    for col in ('Points Started', 'Points Benched', 'SPAR'):
        out[col] = out[col].round(2)
    return out


# ---------------------------------------------------------------------------
# per-move impact
# ---------------------------------------------------------------------------

def move_impacts(rosters, moves, st=None):
    """Every acquisition scored by what it went on to produce.

    Joined to the stint that begins in the acquiring week, so a player acquired
    twice is credited separately for each spell.

    ``st`` accepts a pre-computed ``stints()`` frame. Without it a full
    cross-league build recomputes stints six times per league-season - once each
    for impacts, drops and trades, twice more inside owner_summary - which is
    most of a 47-second page load.
    """
    empty = pd.DataFrame(columns=['League', 'Year', 'Week', 'Type', 'Player',
                                  'Position', 'Team', 'Owner ID', 'From Team',
                                  'FAAB Bid', 'Source', 'Weeks Held',
                                  'Weeks Started', 'Points Started',
                                  'Points Benched', 'SPAR'])
    if rosters.empty or moves.empty:
        return empty

    st = stints(rosters) if st is None else st
    # zip over columns rather than itertuples: itertuples mangles names with
    # spaces ('Start Week' -> _5), which has bitten this codebase twice already
    by_start = {}
    for player, team, start, weeks, wstarted, pstarted, pbench, spar in zip(
            st['Player'], st['Team'], st['Start Week'], st['Weeks'],
            st['Weeks Started'], st['Points Started'], st['Points Benched'],
            st['SPAR']):
        by_start[(player, team, int(start))] = (weeks, wstarted, pstarted,
                                                pbench, spar)

    acq = moves[moves['Type'].isin(ACQUIRING)]
    rows = []
    for (league, year, week, kind, player, pos, frm, to, owner, bid,
         source) in zip(acq['League'], acq['Year'], acq['Week'], acq['Type'],
                        acq['Player'], acq['Position'], acq['From Team'],
                        acq['To Team'], acq['Owner ID'], acq['FAAB Bid'],
                        acq['Source']):
        hit = by_start.get((player, to, int(week)))
        if hit is None:
            continue
        weeks, wstarted, pstarted, pbench, spar = hit
        rows.append({
            'League': league, 'Year': year, 'Week': int(week), 'Type': kind,
            'Player': player, 'Position': pos, 'Team': to, 'Owner ID': owner,
            'From Team': frm, 'FAAB Bid': bid, 'Source': source,
            'Weeks Held': weeks, 'Weeks Started': wstarted,
            'Points Started': pstarted, 'Points Benched': pbench, 'SPAR': spar,
        })
    out = pd.DataFrame(rows, columns=empty.columns)
    return out.sort_values('SPAR', ascending=False, ignore_index=True)


def drop_costs(rosters, moves, st=None):
    """What each dropped player went on to score - for whoever picked them up.

    Points the player scored *in someone else's lineup* after the drop. That is
    the measurable regret; points scored while unrostered are ignored because
    nobody captured them.
    """
    empty = pd.DataFrame(columns=['League', 'Year', 'Week', 'Player', 'Position',
                                  'Dropped By', 'Owner ID', 'Picked Up By',
                                  'Weeks Started After', 'Points Started After',
                                  'SPAR After'])
    if rosters.empty or moves.empty:
        return empty

    st = stints(rosters) if st is None else st
    drops = moves[moves['Type'] == tx.DROP]
    rows = []
    for (league, year, week, player, pos, frm, owner) in zip(
            drops['League'], drops['Year'], drops['Week'], drops['Player'],
            drops['Position'], drops['From Team'], drops['Owner ID']):
        later = st[(st['Player'] == player) & (st['Start Week'] >= int(week))
                   & (st['Team'] != frm)]
        if later.empty:
            continue
        rows.append({
            'League': league, 'Year': year, 'Week': int(week), 'Player': player,
            'Position': pos, 'Dropped By': frm, 'Owner ID': owner,
            'Picked Up By': ', '.join(sorted(later['Team'].unique())),
            'Weeks Started After': int(later['Weeks Started'].sum()),
            'Points Started After': round(float(later['Points Started'].sum()), 2),
            'SPAR After': round(float(later['SPAR'].sum()), 2),
        })
    out = pd.DataFrame(rows, columns=empty.columns)
    return out.sort_values('SPAR After', ascending=False, ignore_index=True)


def trades(rosters, moves, st=None):
    """Both sides of each confirmed trade, with the rest-of-season margin."""
    empty = pd.DataFrame(columns=['League', 'Year', 'Week', 'Team A', 'Team B',
                                  'A Received', 'B Received', 'A Gain', 'B Gain',
                                  'Margin', 'Winner', 'Source'])
    if rosters.empty or moves.empty:
        return empty

    impacts = move_impacts(rosters, moves, st)
    traded = moves[moves['Type'] == tx.TRADE]
    if traded.empty:
        return empty

    gain = {(r_player, r_team, r_week): r_spar for r_player, r_team, r_week, r_spar
            in zip(impacts['Player'], impacts['Team'], impacts['Week'], impacts['SPAR'])}

    rows = []
    for week, chunk in traded.groupby('Week'):
        # pair up teams that both sent and received in this week
        pairs = set()
        for frm, to in zip(chunk['From Team'], chunk['To Team']):
            pairs.add(tuple(sorted((frm, to))))
        for a, b in pairs:
            a_got = chunk[(chunk['To Team'] == a) & (chunk['From Team'] == b)]
            b_got = chunk[(chunk['To Team'] == b) & (chunk['From Team'] == a)]
            if a_got.empty or b_got.empty:
                continue
            a_gain = sum(gain.get((p, a, int(week)), 0.0) for p in a_got['Player'])
            b_gain = sum(gain.get((p, b, int(week)), 0.0) for p in b_got['Player'])
            rows.append({
                'League': chunk['League'].iloc[0], 'Year': int(chunk['Year'].iloc[0]),
                'Week': int(week), 'Team A': a, 'Team B': b,
                'A Received': ', '.join(a_got['Player']),
                'B Received': ', '.join(b_got['Player']),
                'A Gain': round(a_gain, 2), 'B Gain': round(b_gain, 2),
                'Margin': round(abs(a_gain - b_gain), 2),
                'Winner': a if a_gain >= b_gain else b,
                'Source': chunk['Source'].iloc[0],
            })
    return pd.DataFrame(rows, columns=empty.columns)


# ---------------------------------------------------------------------------
# owner-level summary
# ---------------------------------------------------------------------------

def owner_summary(rosters, moves, st=None):
    """One row per team: activity, value gained, and a 30-100 grade."""
    cols = ['Team', 'Owner ID', 'Moves', 'Adds', 'Drops', 'Trade Adds',
            'FAAB Spent', 'Points Started', 'SPAR', 'SPAR per Add',
            'Best Pickup', 'Best Pickup SPAR', 'Drop Regret',
            'Transaction Grade', 'Letter Grade']
    if rosters.empty:
        return pd.DataFrame(columns=cols)

    st = stints(rosters) if st is None else st
    impacts = move_impacts(rosters, moves, st)
    regret = drop_costs(rosters, moves, st)
    teams = sorted(rosters['Team'].unique())
    owner_of = dict(zip(rosters['Team'], rosters['Owner ID']))

    rows = []
    for team in teams:
        mine = impacts[impacts['Team'] == team]
        team_moves = moves[(moves['To Team'] == team) | (moves['From Team'] == team)] \
            if len(moves) else moves
        adds = int((team_moves['Type'] == tx.ADD).sum()) if len(team_moves) else 0
        drops = int((team_moves['Type'] == tx.DROP).sum()) if len(team_moves) else 0
        # players received by trade. Counting every TRADE row involving the team
        # would double a 1-for-1 - the team appears once as sender, once as
        # receiver - so restrict to the incoming leg, matching how Adds works.
        trade_n = int(((team_moves['Type'] == tx.TRADE)
                       & (team_moves['To Team'] == team)).sum()) if len(team_moves) else 0
        best = mine.iloc[0] if len(mine) else None
        lost = regret[regret['Dropped By'] == team]
        rows.append({
            'Team': team,
            'Owner ID': owner_of.get(team),
            'Moves': int(len(team_moves)),
            'Adds': adds, 'Drops': drops, 'Trade Adds': trade_n,
            'FAAB Spent': float(team_moves['FAAB Bid'].sum()) if len(team_moves) else 0.0,
            'Points Started': round(float(mine['Points Started'].sum()), 2),
            'SPAR': round(float(mine['SPAR'].sum()), 2),
            'SPAR per Add': round(float(mine['SPAR'].mean()), 2) if len(mine) else 0.0,
            'Best Pickup': best['Player'] if best is not None else '—',
            'Best Pickup SPAR': round(float(best['SPAR']), 2) if best is not None else 0.0,
            'Drop Regret': round(float(lost['SPAR After'].sum()), 2),
        })

    out = pd.DataFrame(rows)
    out = _grade(out, 'SPAR')
    return out[cols].sort_values('SPAR', ascending=False, ignore_index=True)


def _grade(df, column):
    """z-score within this league-season and map onto the draft-grade scale."""
    vals = df[column].astype(float)
    sd = vals.std(ddof=0)
    z = (vals - vals.mean()) / sd if sd > 1e-9 else vals * 0.0
    df['Transaction Grade'] = (GRADE_CENTER + GRADE_PER_Z * z).clip(GRADE_MIN, GRADE_MAX).round(2)
    df['Letter Grade'] = df['Transaction Grade'].apply(grade_to_letter)
    return df


# ---------------------------------------------------------------------------
# convenience
# ---------------------------------------------------------------------------

def load_and_score(league_name, year):
    """Everything for one league-season, read off disk. Returns a dict of frames."""
    rosters, moves = tx.load_season(league_name, year)
    st = stints(rosters)                 # computed once, shared by all five views
    return {
        'rosters': rosters,
        'moves': moves,
        'stints': st,
        'impacts': move_impacts(rosters, moves, st),
        'drops': drop_costs(rosters, moves, st),
        'trades': trades(rosters, moves, st),
        'owners': owner_summary(rosters, moves, st),
        'replacement': replacement_table(rosters),
    }


def waiver_wire_hits(rosters, moves, n=15):
    """The best pickups of the season, league-wide."""
    impacts = move_impacts(rosters, moves)
    if impacts.empty:
        return impacts
    return impacts.head(n)[['Week', 'Player', 'Position', 'Team', 'Type',
                            'Weeks Started', 'Points Started', 'SPAR', 'Source']]


def biggest_mistakes(rosters, moves, n=15):
    """Drops that hurt most - what the player did for whoever claimed them."""
    regret = drop_costs(rosters, moves)
    if regret.empty:
        return regret
    return regret.head(n)[['Week', 'Player', 'Position', 'Dropped By',
                           'Picked Up By', 'Weeks Started After',
                           'Points Started After', 'SPAR After']]


def team_transaction_grade(league_name, year, team_name):
    """One team-season's Transaction Grade, or (None, None) if not backfilled.

    The counterpart to ``draft_grading.team_draft_grade``, so a league page can
    show the two side by side. Reads the stored snapshots rather than ESPN, and
    caches per league-season because the caller asks team by team.
    """
    key = (str(league_name), int(year))
    cached = _TEAM_GRADE_CACHE.get(key)
    if cached is None:
        rosters, moves = tx.load_season(league_name, int(year))
        if rosters.empty:
            _TEAM_GRADE_CACHE[key] = {}
            return None, None
        summary = owner_summary(rosters, moves)
        cached = {str(t).strip(): (g, l) for t, g, l in
                  zip(summary['Team'], summary['Transaction Grade'],
                      summary['Letter Grade'])}
        _TEAM_GRADE_CACHE[key] = cached
    return cached.get(str(team_name).strip(), (None, None))
