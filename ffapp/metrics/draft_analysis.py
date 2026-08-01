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

from paths import MASTER_DRAFT_DATA, draft_file, free_agent_file
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
