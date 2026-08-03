"""Post-season draft analysis for one league-season.

Builds on the grading engine in `draft_grading.py`. Where that answers "how good
was this pick", this answers "how good was this *drafter*, and why".

The central idea is splitting a pick's value over slot into the part the drafter
controlled and the part they didn't:

    Expected  = what that draft slot historically returns (position-rank curve,
                fit across every league-season on file)
    Projected = ESPN's preseason projection for the player actually taken
    Actual    = what the player really scored

    ACCURACY = Projected - Expected  you took a player the market already rated
                                     above what that slot usually returns
    LUCK     = Actual - Projected    the player beat (or missed) their own
                                     projection: breakouts, injuries, situation
    VALUE    = Actual - Expected     = ACCURACY + LUCK

The decomposition is exact by construction and separates "drafted well" from "got
lucky" - two owners with identical value can have opposite stories.

Two honest caveats, both measured rather than assumed:

* It is called ACCURACY, not "skill", deliberately. Across 102 consecutive-season
  owner pairs in this data, accuracy repeats year over year at only r = +0.08 -
  indistinguishable from zero at that sample size (luck: +0.03, total value:
  +0.24). So accuracy describes how a draft was built relative to the market; it
  is not yet evidence of durable drafting talent.
* 2023 draft files carry projections for only ~16% of picks, so the split is
  unavailable for that season. VALUE is still exact and is reported alone.
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

from functools import lru_cache

from paths import MASTER_DRAFT_DATA, draft_file, free_agent_file
from ffapp.espn import league_settings
from ffapp.metrics.draft_grading import build_expectation_curves

# A conventional ESPN starting lineup. League settings vary, so this is an
# assumption used only for "best possible lineup" style questions - it is
# surfaced in the UI rather than hidden.
DEFAULT_SLOTS = [('QB', 1), ('RB', 2), ('WR', 2), ('TE', 1),
                 ('FLEX', 1), ('D/ST', 1), ('K', 1)]
FLEX_POSITIONS = ('RB', 'WR', 'TE')
# Below this share of picks carrying a projection, the skill/luck split is noise.
MIN_PROJECTION_COVERAGE = 0.5


def _add_round(df):
    df = df.copy()
    df['Round'] = df['Pick'].astype(str).str.split(' - ').str[0].astype(int)
    return df


def expectation_curves():
    """Position-rank -> expected season points curves, fit on every league-season."""
    pool = pd.read_csv(MASTER_DRAFT_DATA)
    return build_expectation_curves(pool)


def load_season(league_name, year, curves=None):
    """One league-season's picks with Expected / Skill / Luck / Value attached.

    Returns (df, meta) where meta flags whether the skill/luck split is usable.
    """
    df = pd.read_csv(draft_file(league_name, year))
    df = _add_round(df)
    df['League'], df['Year'] = league_name, int(year)

    if curves is None:
        curves, _ = expectation_curves()
    else:
        curves = curves[0] if isinstance(curves, tuple) else curves

    df['PosRank'] = (df.sort_values('Total Pick').groupby('Position').cumcount() + 1)

    def expected(row):
        curve = curves.get(row['Position'])
        if curve is None or len(curve) == 0:
            return np.nan
        return curve[min(int(row['PosRank']), len(curve)) - 1]

    df['Expected'] = df.apply(expected, axis=1)
    df['Value'] = df['Points'] - df['Expected']

    coverage = float((df['Projected Points'] > 0).mean())
    has_split = coverage >= MIN_PROJECTION_COVERAGE
    if has_split:
        proj = df['Projected Points'].where(df['Projected Points'] > 0)
        df['Accuracy'] = proj - df['Expected']
        df['Luck'] = df['Points'] - proj

        # Raw accuracy/luck carry a league-wide bias and are meaningless as
        # absolute numbers: ESPN projections assume a full healthy season, so
        # they sit ~46 points per pick above the median outcome the slot curve is
        # fit on. Uncentred, that makes *every* drafter look accurate and
        # desperately unlucky. Centring on this season's own mean fixes the
        # reading - 0 is an average drafter in this league, positive accuracy
        # means you targeted better-projected players than your rivals did at the
        # same slots. Centring is a constant shift, so the identity
        # Accuracy vs Avg + Luck vs Avg == Value vs Avg still holds exactly.
        #
        # Centre over exactly the picks that have a projection, and blank the
        # rest: centring over different row sets would break that identity for
        # any owner holding a pick with no projection on file.
        have = proj.notna() & df['Expected'].notna()
        df['Accuracy vs Avg'] = (df['Accuracy'] - df['Accuracy'][have].mean()).where(have)
        df['Luck vs Avg'] = (df['Luck'] - df['Luck'][have].mean()).where(have)
        df['Value vs Avg'] = (df['Value'] - df['Value'][have].mean()).where(have)
    else:
        for c in ('Accuracy', 'Luck', 'Accuracy vs Avg', 'Luck vs Avg', 'Value vs Avg'):
            df[c] = np.nan

    meta = {'projection_coverage': coverage, 'has_skill_luck': has_split,
            'mean_projection_bias': float(df['Luck'].mean()) if has_split else None}
    return df, meta


# ---------------------------------------------------------------- owner views
def owner_summary(df):
    """Per-owner draft scorecard: value, its skill/luck split, grade, hit rate."""
    rows = []
    for team, g in df.groupby('Team'):
        starters = _optimal_lineup(g)
        rows.append({
            'Team': team,
            'Picks': len(g),
            'Draft Grade': round(g['Draft Grade'].mean(), 1),
            'Total Points': round(g['Points'].sum(), 1),
            'Value Over Slot': round(g['Value'].sum(), 1),
            'Accuracy vs Avg': round(g['Accuracy vs Avg'].sum(), 1) if g['Accuracy vs Avg'].notna().any() else np.nan,
            'Luck vs Avg': round(g['Luck vs Avg'].sum(), 1) if g['Luck vs Avg'].notna().any() else np.nan,
            'Hits': int((g['Value'] > 0).sum()),
            'Hit Rate': round(float((g['Value'] > 0).mean()) * 100, 1),
            'Best Lineup Pts': round(starters['Points'].sum(), 1) if len(starters) else 0.0,
        })
    out = pd.DataFrame(rows).sort_values('Value Over Slot', ascending=False)
    return out.reset_index(drop=True)


def _optimal_lineup(players, slots=DEFAULT_SLOTS):
    """Highest-scoring legal starting lineup from a set of players (season points)."""
    pool = players.sort_values('Points', ascending=False)
    used, chosen = set(), []
    for pos, count in slots:
        if pos == 'FLEX':
            continue
        picks = pool[(pool['Position'] == pos) & (~pool.index.isin(used))].head(count)
        used.update(picks.index)
        chosen.append(picks)
    flex_count = dict(slots).get('FLEX', 0)
    if flex_count:
        flex = pool[(pool['Position'].isin(FLEX_POSITIONS)) & (~pool.index.isin(used))].head(flex_count)
        used.update(flex.index)
        chosen.append(flex)
    return pd.concat(chosen) if chosen else players.iloc[0:0]


def best_lineup(df, team, slots=DEFAULT_SLOTS):
    """The optimal starting lineup a team could field from its own draft picks."""
    return _optimal_lineup(df[df['Team'] == team], slots).sort_values('Points', ascending=False)


# ------------------------------------------------------------- pick-level views
def best_pick_per_round(df):
    """The single best-value pick in each round, with who made it."""
    idx = df.groupby('Round')['Value'].idxmax().dropna()
    cols = ['Round', 'Pick', 'Total Pick', 'Player', 'Position', 'Team',
            'Points', 'Expected', 'Value', 'Draft Grade']
    return df.loc[idx, cols].sort_values('Round').reset_index(drop=True)


def steals_and_busts(df, n=10):
    """Picks that most beat, and most missed, what their slot usually returns."""
    cols = ['Pick', 'Total Pick', 'Player', 'Position', 'Team', 'Points',
            'Expected', 'Value', 'Draft Grade', 'Letter Grade']
    ranked = df.sort_values('Value', ascending=False)
    return ranked.head(n)[cols].reset_index(drop=True), \
        ranked.tail(n)[cols].iloc[::-1].reset_index(drop=True)


def position_by_round(df):
    """Owner x round grid of which position each owner took - draft tendencies."""
    grid = df.pivot_table(index='Team', columns='Round', values='Position',
                          aggfunc=lambda s: s.iloc[0])
    return grid.fillna('')


def value_by_position(df):
    """Per owner x position: how much value they extracted there."""
    piv = df.pivot_table(index='Team', columns='Position', values='Value',
                         aggfunc='sum').round(1)
    piv['Total'] = piv.sum(axis=1).round(1)
    return piv.sort_values('Total', ascending=False)


def round_accuracy(df):
    """League-wide: how each round performed against its slot expectation."""
    g = df.groupby('Round').agg(
        Picks=('Player', 'size'),
        **{'Avg Points': ('Points', 'mean'),
           'Avg Expected': ('Expected', 'mean'),
           'Avg Value': ('Value', 'mean'),
           'Hit Rate': ('Value', lambda s: float((s > 0).mean()) * 100)}
    ).round(1)
    return g.reset_index()


# ------------------------------------------------- best-available counterfactual
def best_available(df):
    """At each pick, the best player still on the board - points left behind.

    A pure hindsight measure: it asks what the highest-scoring undrafted player
    was at that moment, so 'Left On Board' is the cost of the pick versus perfect
    foresight, not versus a realistic alternative.
    """
    order = df.sort_values('Total Pick').reset_index(drop=True)
    remaining = set(order.index)
    rows = []
    for i, row in order.iterrows():
        pool = order.loc[list(remaining)]
        best = pool.loc[pool['Points'].idxmax()]
        rows.append({
            'Total Pick': row['Total Pick'], 'Pick': row['Pick'], 'Team': row['Team'],
            'Player': row['Player'], 'Position': row['Position'], 'Points': row['Points'],
            'Best Available': best['Player'], 'BA Position': best['Position'],
            'BA Points': best['Points'],
            'Left On Board': round(best['Points'] - row['Points'], 1),
        })
        remaining.discard(i)
    return pd.DataFrame(rows)


def left_on_board_by_owner(ba_df):
    """Total hindsight points each owner passed on."""
    g = ba_df.groupby('Team').agg(
        Picks=('Player', 'size'),
        **{'Total Left On Board': ('Left On Board', 'sum'),
           'Worst Single Pick': ('Left On Board', 'max')}
    ).round(1)
    return g.sort_values('Total Left On Board').reset_index()


# ------------------------------------------------------------- roster retention
def roster_retention(league_name, year):
    """How much of each team's final roster came from its own draft.

    Requires a 'Final Roster' capture that `draft_data.py` only started writing
    recently; returns None when that file does not exist for this league-season,
    so callers can hide the section rather than guess.
    """
    path = draft_file(league_name, year).replace('Draft Results', 'Final Roster')
    if not os.path.exists(path):
        return None
    final = pd.read_csv(path)
    drafted = pd.read_csv(draft_file(league_name, year))
    own = drafted[['Player', 'Team']].rename(columns={'Team': 'Drafted By'})
    merged = final.merge(own, on='Player', how='left')
    rows = []
    for team, g in merged.groupby('Team'):
        kept = int((g['Drafted By'] == team).sum())
        n_drafted = int((drafted['Team'] == team).sum())
        rows.append({
            'Team': team,
            'Roster Size': len(g),
            'Own Draft Picks Kept': kept,
            'Of Picks Made': n_drafted,
            'Retention %': round(kept / n_drafted * 100, 1) if n_drafted else 0.0,
            'Acquired Elsewhere': len(g) - kept,
        })
    return pd.DataFrame(rows).sort_values('Retention %', ascending=False).reset_index(drop=True)


# ==========================================================================
# What was the best lineup you could actually have drafted?
# ==========================================================================
# Full hindsight ("best 9 in the draft, order ignored") gives every manager the
# identical number, so it ranks nobody. This instead holds each manager to their
# own draft slots: at pick 9 you may have anyone who really went 9th or later.
# A late-round star like a 4th-round WR who finished 7th in points was reachable
# by everyone, and that is the point - it shows who actually reached.
#
# Exactness: only starters score, so this is "choose players to fill the lineup,
# each assigned to one of your pick slots, maximising points". A player with
# actual pick a is reachable at your slot p iff a >= p, so the reachable sets are
# nested as p grows. That means an optimal assignment never needs to cross - if
# x is cheaper (earlier) than y, giving x the earlier slot is always feasible -
# so walking players in actual-pick order and slots in order is optimal, not
# greedy. That turns it into a DP over (player, slot, slots filled).
#
# One simplification, stated rather than hidden: every *other* manager's picks
# stay as they really were. Taking a player somebody else drafted later does not
# ripple through their draft.

# Fallback when a league-season has no captured ESPN settings (pre-capture
# seasons). Standard ESPN: QB1 RB2 WR2 TE1 FLEX1 D/ST1 K1.
FALLBACK_SLOT_GROUPS = [(('D/ST',), 1), (('K',), 1), (('QB',), 1), (('RB',), 2),
                        (('TE',), 1), (('WR',), 2), (('RB', 'WR', 'TE'), 1)]
# A lineup needs at most 3 of any one position, but availability matters - the
# best RBs may all be gone by your slots - so keep a deep buffer. Verified to
# give answers identical to a 40-deep pool on 8 league-seasons while cutting the
# solve time roughly in half.
MAX_PER_POSITION = 25


def league_slot_groups(league_name, year):
    """(slot_groups, source) for a league-season - real ESPN settings if captured."""
    stored = league_settings.get_settings(league_name, year)
    if stored and stored.get('roster'):
        groups = league_settings.parse_slot_groups(stored['roster'])
        if groups:
            return groups, 'espn'
    return FALLBACK_SLOT_GROUPS, 'assumed'


def _reachable_pool(df, slots):
    """Players a manager could have taken at some slot of theirs, trimmed."""
    pool = df[df['Total Pick'] >= slots[0]].copy()
    pool = pool.sort_values('Points', ascending=False).groupby('Position').head(MAX_PER_POSITION)
    return pool.sort_values('Total Pick').reset_index(drop=True)


def best_possible_at_own_slots(df, team, slot_groups):
    """Exact best startable lineup this team could have drafted at its own slots.

    Returns (total_points, chosen_rows_DataFrame).
    """
    slots = sorted(df[df['Team'] == team]['Total Pick'].tolist())
    if not slots:
        return 0.0, df.iloc[0:0]
    pool = _reachable_pool(df, slots)
    picks = tuple(pool['Total Pick'].tolist())
    pts = tuple(pool['Points'].fillna(0.0).tolist())
    pos = tuple(pool['Position'].tolist())
    caps = tuple(n for _, n in slot_groups)
    allowed = tuple(frozenset(a) for a, _ in slot_groups)
    n, k, ng = len(pool), len(slots), len(slot_groups)
    slots_t = tuple(slots)

    @lru_cache(maxsize=None)
    def best(j, i, filled):
        # every point is non-negative, so there is no reason to stop early;
        # running out of players or slots simply ends the lineup where it is
        if j >= n or i >= k:
            return 0.0
        out = best(j + 1, i, filled)             # pass on this player
        alt = best(j, i + 1, filled)             # spend this slot on a bench player
        if alt > out:
            out = alt
        if picks[j] >= slots_t[i]:               # still on the board at this slot
            p = pos[j]
            for g in range(ng):
                if filled[g] < caps[g] and p in allowed[g]:
                    nf = list(filled); nf[g] += 1
                    cand = pts[j] + best(j + 1, i + 1, tuple(nf))
                    if cand > out:
                        out = cand
        return out

    start = (0,) * ng
    total = best(0, 0, start)

    # walk the memo table back out to recover which players were chosen
    chosen, j, i, filled = [], 0, 0, start
    while j < n and i < k:
        target = best(j, i, filled)
        if abs(best(j + 1, i, filled) - target) < 1e-9:
            j += 1
            continue
        if abs(best(j, i + 1, filled) - target) < 1e-9:
            i += 1
            continue
        moved = False
        if picks[j] >= slots_t[i]:
            for g in range(ng):
                if filled[g] < caps[g] and pos[j] in allowed[g]:
                    nf = list(filled); nf[g] += 1
                    if abs(pts[j] + best(j + 1, i + 1, tuple(nf)) - target) < 1e-9:
                        chosen.append((pool.index[j], '/'.join(sorted(allowed[g]))
                                       if len(allowed[g]) > 1 else pos[j], slots_t[i]))
                        filled = tuple(nf); j += 1; i += 1; moved = True
                        break
        if not moved:
            j += 1
    best.cache_clear()

    if not chosen:
        return total, pool.iloc[0:0]
    idx = [c[0] for c in chosen]
    out = pool.loc[idx].copy()
    out['Slot'] = [c[1] for c in chosen]
    out['Your Pick Used'] = [c[2] for c in chosen]
    return total, out.sort_values('Points', ascending=False)


def redraft_efficiency(df, slot_groups):
    """League table: actual best lineup vs the ceiling reachable at own slots."""
    rows = []
    for team in sorted(df['Team'].unique()):
        ceiling, _ = best_possible_at_own_slots(df, team, slot_groups)
        actual = _optimal_lineup_groups(df[df['Team'] == team], slot_groups)
        act_pts = float(actual['Points'].sum())
        rows.append({
            'Team': team,
            'Actual Best Lineup': round(act_pts, 1),
            'Could Have Drafted': round(ceiling, 1),
            'Missed By': round(ceiling - act_pts, 1),
            'Efficiency %': round(act_pts / ceiling * 100, 1) if ceiling else 0.0,
            'First Pick': int(df[df['Team'] == team]['Total Pick'].min()),
        })
    return pd.DataFrame(rows).sort_values('Efficiency %', ascending=False).reset_index(drop=True)


def _optimal_lineup_groups(players, slot_groups):
    """Best legal lineup from a fixed set of players, honouring flex slots."""
    pool = players.sort_values('Points', ascending=False)
    used, chosen = set(), []
    # single-position slots first so a flex is not filled by someone a strict
    # slot needed; slot_groups is already ordered that way
    for allowed, count in slot_groups:
        picks = pool[(pool['Position'].isin(allowed)) & (~pool.index.isin(used))].head(count)
        used.update(picks.index)
        chosen.append(picks)
    return pd.concat(chosen) if chosen else players.iloc[0:0]
