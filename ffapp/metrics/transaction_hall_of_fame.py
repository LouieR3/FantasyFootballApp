"""All-time transaction feats across every league and season.

The transaction counterpart to `hall_of_fame.py`: that module ranks how teams
*played*, this one ranks how they *traded and worked the wire*. Built on
`data/transactions/` via `transaction_analysis.py`.

**Cross-league comparability is the same problem as on the rest of the Hall of
Fame page, and worse here.** SPAR is raw points above replacement, so a PPR
league inflates it against a standard one and a 17-week season inflates it
against a 15-week one. Which normalisation applies depends on what is being
ranked, and the three cases genuinely differ:

* **Team-season and manager rankings use SPAR z** - SPAR z-scored inside its own
  league-season, exactly as `PPG z` does for scoring. These are the rankings
  where an unfair league advantage would compound across a whole career.
* **Trades use raw margins.** Both sides sit in the *same* league-season, so the
  gap between them is already apples-to-apples and normalising would only
  obscure the actual point swing.
* **Individual add/drop lists use raw SPAR**, because the headline of "best
  waiver pickup ever" is the raw number. This is the one place a scoring-settings
  bias survives: a PPR league will be over-represented among big receiver and
  back pickups. Worth knowing when reading those two lists.

Carried over from `transaction_analysis.py`: none of this predicts winning.
Total SPAR tracks the raw number of moves at r = +0.69 and regular-season wins at
r = +0.01. These are feats, not a manager ranking.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import pandas as pd

from ffapp.espn import transactions as tx
from ffapp.metrics import lifetime as lt
from ffapp.metrics import transaction_analysis as ta

MIN_SEASONS_FOR_MANAGER_VIEWS = 2
# SPAR per add over one lucky pickup is noise, not efficiency.
MIN_ADDS_FOR_RATE = 5


def _owner_names():
    """owner id -> display name, tolerating a missing/partial crosswalk."""
    try:
        return lt.owner_display_names()
    except Exception:
        return {}


def transaction_seasons():
    """One row per team-season with its transaction record.

    Empty DataFrame if the backfill has never been run.

    Deliberately *not* ``lru_cache``d. The page caches this with ``st.cache_data``
    keyed on the transactions directory mtime, so a weekly run invalidates it -
    but a process-level lru_cache would sit underneath that and keep handing back
    last week's numbers, which is exactly how the stale-module traps in this repo
    have bitten before. ~13s uncached, and the page only pays it when the data
    actually changes.
    """
    names = _owner_names()
    rows = []
    for league, year in tx.available_seasons():
        rosters, moves = tx.load_season(league, year)
        if rosters.empty:
            continue
        st = ta.stints(rosters)          # shared, not recomputed per view
        for r in ta.owner_summary(rosters, moves, st).to_dict('records'):
            oid = str(r.get('Owner ID'))
            rows.append({
                'League': league, 'Year': int(year),
                'Season': f'{league} {year}',
                'Owner': names.get(oid) or r['Team'],
                'Owner ID': oid,
                'Team': r['Team'],
                'Moves': r['Moves'], 'Adds': r['Adds'], 'Drops': r['Drops'],
                'Trade Adds': r['Trade Adds'],
                'SPAR': r['SPAR'], 'SPAR per Add': r['SPAR per Add'],
                'Drop Regret': r['Drop Regret'],
                'Best Pickup': r['Best Pickup'],
                'Best Pickup SPAR': r['Best Pickup SPAR'],
                'Transaction Grade': r['Transaction Grade'],
                'Letter Grade': r['Letter Grade'],
            })
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # league-relative, so a high-scoring league cannot own every list
    for col, out in (('SPAR', 'SPAR z'), ('SPAR per Add', 'SPAR per Add z')):
        df[out] = (df.groupby(['League', 'Year'])[col]
                     .transform(lambda s: (s - s.mean()) / s.std(ddof=0)
                                if s.std(ddof=0) > 1e-9 else 0.0)).round(2)
    return df.sort_values(['Year', 'League']).reset_index(drop=True)


def all_moves():
    """(adds, drops, trades) pooled across every league-season on disk.

    Uncached for the same reason as ``transaction_seasons`` - see there.
    """
    names = _owner_names()
    adds, drops, trades = [], [], []
    for league, year in tx.available_seasons():
        rosters, moves = tx.load_season(league, year)
        if rosters.empty:
            continue
        season = f'{league} {year}'
        st = ta.stints(rosters)          # shared across all three views below

        imp = ta.move_impacts(rosters, moves, st)
        if not imp.empty:
            imp = imp.copy()
            imp['Season'] = season
            imp['Owner'] = [names.get(str(o)) or t
                            for o, t in zip(imp['Owner ID'], imp['Team'])]
            adds.append(imp)

        reg = ta.drop_costs(rosters, moves, st)
        if not reg.empty:
            reg = reg.copy()
            reg['Season'] = season
            reg['Owner'] = [names.get(str(o)) or t
                            for o, t in zip(reg['Owner ID'], reg['Dropped By'])]
            drops.append(reg)

        tr = ta.trades(rosters, moves, st)
        if not tr.empty:
            tr = tr.copy()
            tr['Season'] = season
            trades.append(tr)

    empty = pd.DataFrame()
    return (pd.concat(adds, ignore_index=True) if adds else empty,
            pd.concat(drops, ignore_index=True) if drops else empty,
            pd.concat(trades, ignore_index=True) if trades else empty)


# ------------------------------------------------------------------- trades

TRADE_COLS = ['Season', 'Week', 'Team A', 'A Received', 'A Gain',
              'Team B', 'B Received', 'B Gain', 'Margin', 'Winner']


def _with_trade_metrics(trades):
    if trades.empty:
        return trades
    t = trades.copy()
    t['Total Value'] = (t['A Gain'] + t['B Gain']).round(2)
    t['Weaker Side'] = t[['A Gain', 'B Gain']].min(axis=1).round(2)
    return t


def most_lopsided_trades(trades, n=15):
    """One side ran away with it - ranked by the rest-of-season value gap."""
    t = _with_trade_metrics(trades)
    if t.empty:
        return t
    return (t.sort_values('Margin', ascending=False).head(n)[TRADE_COLS]
            .reset_index(drop=True))


def biggest_trades(trades, n=15):
    """Most total value moved, regardless of who won it."""
    t = _with_trade_metrics(trades)
    if t.empty:
        return t
    cols = [c for c in TRADE_COLS if c != 'Winner'] + ['Total Value']
    return (t.sort_values('Total Value', ascending=False).head(n)[cols]
            .reset_index(drop=True))


def most_mutual_trades(trades, n=15):
    """Both sides genuinely gained - ranked by what the *weaker* side got.

    Maximising the weaker side is what "everyone won" actually means. Ranking on
    the total instead would just resurface blockbusters where one team was fleeced.
    """
    t = _with_trade_metrics(trades)
    if t.empty:
        return t
    both = t[(t['A Gain'] > 0) & (t['B Gain'] > 0)]
    if both.empty:
        return both
    cols = [c for c in TRADE_COLS if c != 'Winner'] + ['Total Value', 'Weaker Side']
    return (both.sort_values('Weaker Side', ascending=False).head(n)[cols]
            .reset_index(drop=True))


# --------------------------------------------------------------- adds/drops

def best_adds(adds, n=15, exclude_trades=True):
    """The best pickups ever made off the wire.

    Trades are excluded by default: they have three sections of their own, and
    left in they take every slot on this list - a trade brings back an
    established star, a waiver claim almost never does. Pass
    ``exclude_trades=False`` for the combined "best acquisition of any kind".
    """
    if adds.empty:
        return adds
    pool = adds[adds['Type'] != tx.TRADE] if exclude_trades else adds
    if pool.empty:
        return pool
    cols = ['Season', 'Week', 'Player', 'Position', 'Owner', 'Team', 'Type',
            'Weeks Started', 'Points Started', 'SPAR']
    return (pool.sort_values('SPAR', ascending=False).head(n)[cols]
            .reset_index(drop=True))


def worst_drops(drops, n=15):
    """Players released who went on to win weeks for somebody else."""
    if drops.empty:
        return drops
    cols = ['Season', 'Week', 'Player', 'Position', 'Owner', 'Dropped By',
            'Picked Up By', 'Weeks Started After', 'Points Started After',
            'SPAR After']
    return (drops.sort_values('SPAR After', ascending=False).head(n)[cols]
            .reset_index(drop=True))


# ------------------------------------------------------------- team-seasons

SEASON_COLS = ['Owner', 'Team', 'Season', 'Moves', 'Adds', 'SPAR', 'SPAR z',
               'SPAR per Add', 'Best Pickup', 'Best Pickup SPAR',
               'Transaction Grade', 'Letter Grade']


def most_spar_seasons(txn, n=15):
    """Most value ever squeezed out of the wire in a single season."""
    if txn.empty:
        return txn
    return (txn.sort_values('SPAR z', ascending=False).head(n)[SEASON_COLS]
            .reset_index(drop=True))


def best_spar_per_add(txn, n=15, min_adds=MIN_ADDS_FOR_RATE):
    """Most value per acquisition - the efficient, not merely the busiest."""
    if txn.empty:
        return txn
    eligible = txn[txn['Adds'] >= min_adds]
    if eligible.empty:
        return eligible
    return (eligible.sort_values('SPAR per Add z', ascending=False).head(n)
            [SEASON_COLS].reset_index(drop=True))


def best_transaction_grades(txn, n=15):
    if txn.empty:
        return txn
    return (txn.sort_values('Transaction Grade', ascending=False).head(n)
            [SEASON_COLS].reset_index(drop=True))


def worst_transaction_grades(txn, n=15):
    if txn.empty:
        return txn
    return (txn.sort_values('Transaction Grade').head(n)[SEASON_COLS]
            .reset_index(drop=True))


# ---------------------------------------------------------------- managers

MANAGER_COLS = ['Owner', 'Seasons', 'Leagues', 'Total Moves', 'Total SPAR',
                'Avg SPAR z', 'Avg SPAR per Add', 'Avg Grade', 'Best Season',
                'Total Drop Regret']


def manager_transaction_records(txn, min_seasons=MIN_SEASONS_FOR_MANAGER_VIEWS):
    """Career transaction record per owner, pooled across every league they play.

    Ranked on **Avg Grade**, which is already league-relative (the grade curves
    SPAR within its own league-season), so someone in a high-scoring league does
    not outrank a better operator elsewhere. Owner IDs are ESPN account SWIDs, so
    the same person pools correctly across leagues.
    """
    if txn.empty:
        return txn
    rows = []
    for _oid, g in txn.groupby('Owner ID'):
        if len(g) < min_seasons:
            continue
        best = g.sort_values('Transaction Grade', ascending=False).iloc[0]
        rows.append({
            'Owner': g['Owner'].iloc[-1],
            'Seasons': len(g),
            'Leagues': g['League'].nunique(),
            'Total Moves': int(g['Moves'].sum()),
            'Total SPAR': round(float(g['SPAR'].sum()), 1),
            'Avg SPAR z': round(float(g['SPAR z'].mean()), 2),
            'Avg SPAR per Add': round(float(g['SPAR per Add'].mean()), 2),
            'Avg Grade': round(float(g['Transaction Grade'].mean()), 2),
            'Best Season': f"{best['Season']} ({best['Transaction Grade']:.0f})",
            'Total Drop Regret': round(float(g['Drop Regret'].sum()), 1),
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return (out.sort_values('Avg Grade', ascending=False)[MANAGER_COLS]
            .reset_index(drop=True))
