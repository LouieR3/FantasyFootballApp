"""Display helpers for the Draft Results section on a league page.

The section used to be one bare `AgGrid(df)` over ~180 rows sorted by grade -
technically complete and almost unreadable. Nobody scans a draft as a flat list;
they look at it as a board (who went where, round by round) and then at one
team's haul.

Three views, each answering a different question:

* **Board** - rounds down, teams across, coloured by pick grade. Snake order is
  preserved, so you can see a run of receivers develop across a round.
* **All picks** - the flat table, but styled: gradient on the grade, sane
  decimals, and filters by team and position.
* **By team** - one row per manager: overall grade, best and worst pick, and how
  they spent the draft by position.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import numpy as np
import pandas as pd

# Grade -> background. Matches the RdYlGn feel of the rest of the app but as
# discrete bands, because a continuous gradient over a text cell is unreadable.
GRADE_BANDS = [
    (90, '#1a7f37', '#ffffff'),   # A
    (80, '#4a9c5d', '#ffffff'),   # B
    (70, '#b8a53d', '#000000'),   # C
    (60, '#c96a2b', '#ffffff'),   # D
    (0,  '#a83232', '#ffffff'),   # F
]


def _round_of(df):
    """Round number per pick, derived rather than parsed.

    The `Pick` column is a '4 - 10' string and `Total Pick` is the overall
    number; deriving the round from the overall pick and the team count survives
    either being formatted differently.
    """
    n_teams = max(int(df['Team'].nunique()), 1)
    total = pd.to_numeric(df['Total Pick'], errors='coerce')
    return np.ceil(total / n_teams), n_teams


def board_grid(df):
    """(labels, grades) - two aligned frames, rounds x teams.

    `labels` holds the display text, `grades` the numeric grade used to colour
    it. Kept separate because a Styler needs numbers to colour by and text to
    show, and the two cannot live in the same cell.
    """
    d = df.copy()
    d['_round'], n_teams = _round_of(d)
    d['_total'] = pd.to_numeric(d['Total Pick'], errors='coerce')
    d = d.dropna(subset=['_round', '_total'])
    if d.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Column order = the first-round draft order, so the board reads like a real
    # one instead of alphabetically.
    first = d[d['_round'] == 1].sort_values('_total')
    order = list(dict.fromkeys(first['Team'])) or sorted(d['Team'].unique())
    order += [t for t in sorted(d['Team'].unique()) if t not in order]

    rounds = sorted(d['_round'].unique())
    labels = pd.DataFrame('', index=[f'R{int(r)}' for r in rounds], columns=order,
                          dtype=object)
    grades = pd.DataFrame(np.nan, index=labels.index, columns=order)
    for r, team, player, pos, grade, letter in zip(
            d['_round'], d['Team'], d['Player'], d['Position'],
            d['Draft Grade'], d['Letter Grade']):
        if team not in order:
            continue
        row = f'R{int(r)}'
        g = pd.to_numeric(grade, errors='coerce')
        tag = f'  {letter}' if isinstance(letter, str) and letter else ''
        labels.at[row, team] = f'{player} ({pos}){tag}'
        grades.at[row, team] = g
    return labels, grades


def band_colors(grades):
    """Styler-ready CSS frame for the board, from the numeric grades."""
    def css(v):
        if pd.isna(v):
            return ''
        for floor, bg, fg in GRADE_BANDS:
            if v >= floor:
                return f'background-color: {bg}; color: {fg}'
        return ''
    return grades.map(css) if hasattr(grades, 'map') else grades.applymap(css)


def team_summary(df):
    """One row per team: grade, best and worst pick, positional spend."""
    d = df.copy()
    d['Draft Grade'] = pd.to_numeric(d['Draft Grade'], errors='coerce')
    d['Points'] = pd.to_numeric(d.get('Points'), errors='coerce')
    d['_round'], _ = _round_of(d)

    rows = []
    for team, g in d.groupby('Team'):
        graded = g.dropna(subset=['Draft Grade'])
        best = graded.loc[graded['Draft Grade'].idxmax()] if len(graded) else None
        worst = graded.loc[graded['Draft Grade'].idxmin()] if len(graded) else None
        counts = g['Position'].value_counts()
        early = g[g['_round'] <= 5]['Position'].value_counts()
        rows.append({
            'Team': team,
            'Picks': len(g),
            'Avg Pick Grade': round(float(graded['Draft Grade'].mean()), 1)
                              if len(graded) else np.nan,
            'Total Points': round(float(g['Points'].sum()), 1),
            'Best Pick': f"{best['Player']} ({best['Draft Grade']:.0f})"
                         if best is not None else '—',
            'Worst Pick': f"{worst['Player']} ({worst['Draft Grade']:.0f})"
                          if worst is not None else '—',
            'RB': int(counts.get('RB', 0)), 'WR': int(counts.get('WR', 0)),
            'QB': int(counts.get('QB', 0)), 'TE': int(counts.get('TE', 0)),
            'First 5 Rds': ', '.join(f'{n}{p}' for p, n in early.items()) or '—',
        })
    out = pd.DataFrame(rows)
    return out.sort_values('Avg Pick Grade', ascending=False,
                           na_position='last').reset_index(drop=True)


def steals_and_busts(df, n=5):
    """Biggest overperformers and underperformers relative to draft slot."""
    d = df.copy()
    d['Draft Grade'] = pd.to_numeric(d['Draft Grade'], errors='coerce')
    d = d.dropna(subset=['Draft Grade'])
    if d.empty:
        return d, d
    cols = [c for c in ('Pick', 'Total Pick', 'Player', 'Position', 'Team',
                        'Points', 'Draft Grade', 'Letter Grade') if c in d.columns]
    ranked = d.sort_values('Draft Grade', ascending=False)
    return ranked.head(n)[cols], ranked.tail(n)[cols].iloc[::-1]
