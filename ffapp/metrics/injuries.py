"""Track starter injuries: first-round picks and key contributors across seasons.

Detects injuries by comparing actual vs projected performance and games played,
then aggregates injury timing, frequency, and impact by team, owner, and round.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import glob
import os
import re
from functools import lru_cache

import numpy as np
import pandas as pd

from paths import DRAFTS_DIR
from ffapp import league_registry as registry
from ffapp.metrics import lifetime as lt

DRAFT_RE = re.compile(r'^(.+?) Draft Results (\d{4})\.csv$')


def clear_caches():
    """Drop the memoised analysis cache."""
    for fn in (injury_analysis, injury_summary, injury_luck_by_owner):
        try:
            fn.cache_clear()
        except AttributeError:
            pass


def _parse_pick(pick_str):
    """Extract round from 'round - pick' format, e.g., '1 - 6' -> 1."""
    try:
        return int(str(pick_str).split('-')[0].strip())
    except (ValueError, IndexError, AttributeError):
        return None


def _owner_display_name(owner_id):
    """Get display name for owner ID, fallback to ID if not found."""
    if not owner_id:
        return '?'
    names = lt.owner_display_names()
    return names.get(str(owner_id), str(owner_id))


def _injury_score(projected_avg, actual_avg, games_played, expected_games=16):
    """Score indicating how much a player underperformed (0=no injury, 1=severe).

    Combines games played and performance:
    - Games played < 12 is a strong injury signal
    - Actual avg 30% below projected is a strong signal
    - Multiplies them to weight joint evidence
    """
    if projected_avg <= 0:
        return 0.0

    # Games played factor: 0 at 16, approaches 1 as you drop to 0
    games_factor = max(0, 1 - (games_played / expected_games))

    # Performance factor: 0 if met projection, 1 if 30%+ below
    perf_gap = max(0, projected_avg - actual_avg) / projected_avg
    perf_factor = min(1, perf_gap / 0.3)

    # Weight games played more heavily (it's a cleaner signal)
    return 0.6 * games_factor + 0.4 * perf_factor


@lru_cache(maxsize=32)
def injury_analysis(league, year, rounds=(1, 2)):
    """Top picks injured this season, ranked by severity.

    Parameters
    ----------
    league : str
        Canonical league name
    year : int
        Season year
    rounds : tuple
        Which rounds to analyze, e.g., (1, 2) for first two rounds.

    Returns
    -------
    pd.DataFrame
        Columns: Team, Owner, Player, Pick, Position, Round, Projected Avg,
        Actual Avg, Games Played, Injury Score, Injured (bool)
    """
    league = registry.canonical(league)
    path = None
    for p in glob.glob(os.path.join(DRAFTS_DIR, f'* Draft Results {year}.csv')):
        m = DRAFT_RE.match(os.path.basename(p))
        if m and registry.canonical(m.group(1)) == league:
            path = p
            break

    if not path:
        return pd.DataFrame()

    df = pd.read_csv(path)

    # Filter to top rounds
    df['Round'] = df['Pick'].apply(_parse_pick)
    df = df[df['Round'].isin(rounds)].copy()

    if df.empty:
        return pd.DataFrame()

    # Calculate injury scores
    df['Injury Score'] = df.apply(
        lambda r: _injury_score(
            r.get('Projected Avg Points', 0) or 0,
            r.get('Avg Points', 0) or 0,
            r.get('Games Played', 0) or 0
        ),
        axis=1
    )

    # Flag as injured if score > 0.3 OR games played < 12
    df['Injured'] = (df['Injury Score'] > 0.3) | (df['Games Played'] < 12)

    # Clean up columns
    df = df.rename(columns={
        'Pick': 'Pick Display',
        'Team': 'Team',
        'Player': 'Player',
        'Position': 'Position',
        'Projected Avg Points': 'Projected Avg',
        'Avg Points': 'Actual Avg',
        'Round': 'Round',
    })

    return df[[
        'Team', 'Owner ID', 'Player', 'Pick Display', 'Position', 'Round',
        'Projected Avg', 'Actual Avg', 'Games Played', 'Injury Score', 'Injured'
    ]].sort_values('Injury Score', ascending=False)


@lru_cache(maxsize=16)
def injury_summary(league):
    """Injury trends across all seasons: first starter injured timing, by owner.

    Returns
    -------
    pd.DataFrame
        Columns: Year, Team, Owner, First Injured, First Position, Injury Week (inferred),
        Injured Count (rounds 1-2), Games Missed
    """
    league = registry.canonical(league)
    rows = []

    for path in glob.glob(os.path.join(DRAFTS_DIR, f'* Draft Results *.csv')):
        m = DRAFT_RE.match(os.path.basename(path))
        if not m or registry.canonical(m.group(1)) != league:
            continue

        year = int(m.group(2))
        inj = injury_analysis(league, year, rounds=(1, 2))

        if inj.empty:
            continue

        # Per team, find first injured starter (by pick order)
        for team in inj['Team'].unique():
            team_inj = inj[inj['Team'] == team].sort_values('Injury Score', ascending=False)
            if team_inj.empty:
                continue

            injured_rows = team_inj[team_inj['Injured']]
            if injured_rows.empty:
                continue

            first = injured_rows.iloc[0]
            owner_id = first['Owner ID']
            owner_name = _owner_display_name(owner_id)
            games_missed = 16 - int(first['Games Played'])

            rows.append({
                'Year': year,
                'Team': team,
                'Owner': owner_name,
                'First Injured': first['Player'],
                'First Position': first['Position'],
                'Round': int(first['Round']),
                'Injury Score': round(float(first['Injury Score']), 2),
                'Games Played': int(first['Games Played']),
                'Games Missed': games_missed,
                'Injured Count R1-R2': len(injured_rows),
            })

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values(['Year', 'Team']).reset_index(drop=True)


@lru_cache(maxsize=16)
def injury_luck_by_owner(league):
    """Aggregate injury stats by owner across all seasons.

    Returns
    -------
    pd.DataFrame
        Columns: Owner, Seasons, Avg Injuries Per Season, Total Games Missed,
        First Injury By Week (median timing), Injury Frequency
    """
    league = registry.canonical(league)
    summary = injury_summary(league)

    if summary.empty:
        return pd.DataFrame()

    rows = []
    for owner in summary['Owner'].unique():
        owner_data = summary[summary['Owner'] == owner]

        rows.append({
            'Owner': owner,
            'Seasons': len(owner_data),
            'Injuries (R1-R2)': owner_data['Injured Count R1-R2'].sum(),
            'Avg Injuries / Season': round(owner_data['Injured Count R1-R2'].mean(), 2),
            'Total Games Missed': owner_data['Games Missed'].sum(),
            'Avg Games Missed / Injury': round(
                owner_data['Games Missed'].sum() / max(1, owner_data['Injured Count R1-R2'].sum()),
                1
            ),
        })

    return (pd.DataFrame(rows)
            .sort_values('Total Games Missed', ascending=False)
            .reset_index(drop=True))
