"""All-time feats across every league and every season.

One row per team-season for all 16 leagues, then the fun rankings on top: best and
worst teams ever, the best team to miss the playoffs, the worst team to win it all,
the best manager still without a ring.

**Cross-league comparability is the whole problem.** Leagues differ in size,
scoring settings and season length, so raw points cannot be compared between them -
a 1,900-point season means different things in a 10-team PPR league and a 14-team
standard one. Two comparable measures are used instead:

* ``PPG z`` - points per game expressed as a z-score *within its own league-season*.
  +2.0 means "two standard deviations better than that league that year", which
  travels across leagues and eras.
* ``Win %`` and ``LPI`` - already league-relative (LPI is scaled by league size in
  the weekly pipeline).

Raw points are still shown, just never used for cross-league ranking.

Owner IDs are ESPN account SWIDs, so the same person carries the same ID in every
league they play in - which is what makes the manager views work across leagues.
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

from paths import AGGREGATED_DRAFT_GRADES, ALL_PLAYOFF_DFS, LEAGUES_DIR
from ffapp import league_registry as registry
from ffapp.metrics import lifetime as lt

MIN_SEASONS_FOR_MANAGER_VIEWS = 2


def _norm_round(name):
    """Round labels, with the 'Quater Final' typo in two older workbooks fixed."""
    s = str(name).strip()
    return 'Quarter Final' if s.lower().startswith(('quater', 'quarter')) else s


def _playoff_outcomes():
    """Per (league, year, team): made playoffs, reached the final, won it."""
    if not os.path.exists(ALL_PLAYOFF_DFS):
        return {}, {}, {}
    pg = pd.read_csv(ALL_PLAYOFF_DFS)
    pg['League'] = pg['League'].map(registry.canonical)
    pg['Round'] = pg['Round'].map(_norm_round)
    made, finalists, champs = set(), set(), set()
    # zip over columns rather than itertuples: names like 'Team 1' are not valid
    # Python identifiers, so namedtuple access silently renames them
    for league, year, rnd, t1, t2, winner in zip(
            pg['League'], pg['Year'], pg['Round'],
            pg['Team 1'], pg['Team 2'], pg['Winner']):
        year = int(year)
        teams = [str(t).strip() for t in (t1, t2)
                 if str(t).strip() not in ('', 'Bye', '-', 'nan', 'None')]
        # a bye row still means that team was in the bracket
        for t in teams:
            made.add((league, year, t))
        if 'champ' in str(rnd).lower():
            for t in teams:
                finalists.add((league, year, t))
            wname = str(winner).strip()
            if wname and wname not in ('nan', 'None'):
                champs.add((league, year, wname))
    return made, finalists, champs


def _sheet_metrics():
    """Per (league, year, team): LPI and Expected Wins, from the workbooks."""
    lpi, expw = {}, {}
    import glob
    for path in glob.glob(os.path.join(LEAGUES_DIR, '*.xlsx')):
        base = os.path.splitext(os.path.basename(path))[0]
        league, year = registry.split_league_year(base)
        if not year:
            continue
        league, year = registry.canonical(league), int(year)
        try:
            df = pd.read_excel(path, sheet_name='Louie Power Index')
            col = next((c for c in df.columns if 'Louie Power Index' in str(c)), None)
            if col and 'Teams' in df.columns:
                for t, v in zip(df['Teams'], df[col]):
                    lpi[(league, year, str(t).strip())] = v
        except Exception:
            pass
        try:
            df = pd.read_excel(path, sheet_name='Expected Wins')
            if 'Team' in df.columns and 'Expected Wins' in df.columns:
                for t, v in zip(df['Team'], df['Expected Wins']):
                    expw[(league, year, str(t).strip())] = v
        except Exception:
            pass
    return lpi, expw


def _draft_grades():
    if not os.path.exists(AGGREGATED_DRAFT_GRADES):
        return {}
    ag = pd.read_csv(AGGREGATED_DRAFT_GRADES)
    parts = ag['League Name'].str.rsplit(' ', n=1)
    league = parts.str[0].map(registry.canonical)
    year = pd.to_numeric(parts.str[1], errors='coerce')
    return {(l, int(y), str(t).strip()): g
            for l, y, t, g in zip(league, year, ag['Team'], ag['Draft Grade'])
            if pd.notna(y)}


def team_seasons():
    """One row per team-season across every league. The base for every feat."""
    made, finalists, champs = _playoff_outcomes()
    lpi, expw = _sheet_metrics()
    grades = _draft_grades()

    rows = []
    for league in lt.multi_season_leagues(min_seasons=1):
        tg = lt.team_games(league)
        if tg.empty:
            continue
        for (oid, year), g in tg.groupby(['Owner ID', 'Year']):
            if oid is None or pd.isna(oid):
                continue
            team = g.sort_values('Week')['Team'].iloc[-1]
            reg, po = g[~g['Is Playoff']], g[g['Is Playoff']]
            w = int((g['Result'] == 'W').sum())
            l = int((g['Result'] == 'L').sum())
            t = int((g['Result'] == 'T').sum())
            games = w + l + t
            # a team can appear under more than one name in a season, so check all
            names = {str(n).strip() for n in g['Team']}
            key = lambda d: next((d[(league, year, n)] for n in names
                                  if (league, year, n) in d), np.nan)
            rows.append({
                'League': league, 'Year': int(year),
                'Owner': g['Owner'].dropna().iloc[-1] if g['Owner'].notna().any() else str(oid),
                'Team': team,
                'Games': games, 'W': w, 'L': l, 'T': t,
                'Win %': round(100 * (w + 0.5 * t) / games, 1) if games else 0.0,
                'PF': round(g['Score'].sum(), 1),
                'PA': round(g['Opp Score'].sum(), 1),
                'PPG': round(g['Score'].mean(), 1),
                'LPI': key(lpi),
                'Expected W': key(expw),
                'Playoff W': int((po['Result'] == 'W').sum()),
                'Playoff L': int((po['Result'] == 'L').sum()),
                'Made Playoffs': any((league, year, n) in made for n in names),
                'Reached Final': any((league, year, n) in finalists for n in names),
                'Champion': any((league, year, n) in champs for n in names),
                'Draft Grade': key(grades),
                'Owner ID': str(oid),
            })
    ts = pd.DataFrame(rows)
    if ts.empty:
        return ts

    # points per game, z-scored inside its own league-season: the only fair way to
    # compare a team from a 10-team league against one from a 14-team league
    ts['PPG z'] = (ts.groupby(['League', 'Year'])['PPG']
                     .transform(lambda s: (s - s.mean()) / s.std(ddof=0)
                                if s.std(ddof=0) > 1e-9 else 0.0)).round(2)
    ts['Luck'] = (ts['W'] - ts['Expected W']).round(1)
    ts['Season'] = ts['League'] + ' ' + ts['Year'].astype(str)
    return ts.sort_values(['Year', 'League']).reset_index(drop=True)


# --------------------------------------------------------------------- feats
DISPLAY = ['Owner', 'Team', 'Season', 'W', 'L', 'Win %', 'PPG', 'PPG z', 'LPI',
           'Luck', 'Made Playoffs', 'Champion', 'Draft Grade']


def _top(ts, n, by, ascending=False, cols=None):
    out = ts.sort_values(by, ascending=ascending).head(n)
    return out[cols or DISPLAY].reset_index(drop=True)


def best_team_seasons(ts, n=15, by='PPG z'):
    return _top(ts, n, by)


def worst_team_seasons(ts, n=15, by='PPG z'):
    return _top(ts, n, by, ascending=True)


def best_missed_playoffs(ts, n=15, by='PPG z'):
    """Strong teams that still missed the bracket - the unlucky ones."""
    return _top(ts[~ts['Made Playoffs']], n, by)


def worst_made_playoffs(ts, n=15, by='PPG z'):
    """Weak teams that snuck in anyway."""
    return _top(ts[ts['Made Playoffs']], n, by, ascending=True)


def worst_finalists(ts, n=10, by='PPG z'):
    return _top(ts[ts['Reached Final']], n, by, ascending=True)


def worst_champions(ts, n=10, by='PPG z'):
    return _top(ts[ts['Champion']], n, by, ascending=True)


def best_non_champions(ts, n=15, by='PPG z'):
    """The best seasons that ended without a title."""
    return _top(ts[~ts['Champion']], n, by)


def luckiest(ts, n=10):
    """Most wins above what their scoring deserved."""
    return _top(ts.dropna(subset=['Luck']), n, 'Luck')


def unluckiest(ts, n=10):
    return _top(ts.dropna(subset=['Luck']), n, 'Luck', ascending=True)


def manager_records(ts, min_seasons=MIN_SEASONS_FOR_MANAGER_VIEWS):
    """Career totals per manager, pooled across every league they play in."""
    rows = []
    for oid, g in ts.groupby('Owner ID'):
        seasons = len(g)
        if seasons < min_seasons:
            continue
        games = g['Games'].sum()
        w, l = int(g['W'].sum()), int(g['L'].sum())
        rows.append({
            'Owner': g['Owner'].iloc[-1],
            'Seasons': seasons,
            'Leagues': g['League'].nunique(),
            'W': w, 'L': l,
            'Win %': round(100 * w / games, 1) if games else 0.0,
            'Avg PPG z': round(g['PPG z'].mean(), 2),
            'Playoff Apps': int(g['Made Playoffs'].sum()),
            'Finals': int(g['Reached Final'].sum()),
            'Titles': int(g['Champion'].sum()),
            'Best Season': g.loc[g['PPG z'].idxmax(), 'Season'] if len(g) else '',
            'Owner ID': oid,
        })
    if not rows:
        return pd.DataFrame()
    return (pd.DataFrame(rows).sort_values(['Win %', 'Avg PPG z'], ascending=False)
            .reset_index(drop=True))


MANAGER_COLS = ['Owner', 'Seasons', 'Leagues', 'W', 'L', 'Win %', 'Avg PPG z',
                'Playoff Apps', 'Finals', 'Titles', 'Best Season']


def best_without_a_ring(ts, n=15, min_seasons=MIN_SEASONS_FOR_MANAGER_VIEWS):
    """Strongest careers with no championship - the ringless greats."""
    mgr = manager_records(ts, min_seasons)
    if mgr.empty:
        return mgr
    ringless = mgr[mgr['Titles'] == 0]
    return ringless.head(n)[MANAGER_COLS].reset_index(drop=True)


def heartbreak(ts, min_seasons=MIN_SEASONS_FOR_MANAGER_VIEWS):
    """Most trips to the playoffs with nothing to show for it."""
    mgr = manager_records(ts, min_seasons)
    if mgr.empty:
        return mgr
    out = mgr[(mgr['Titles'] == 0) & (mgr['Playoff Apps'] > 0)]
    return (out.sort_values(['Playoff Apps', 'Finals'], ascending=False)
            [MANAGER_COLS].reset_index(drop=True))


def dynasties(ts, min_seasons=MIN_SEASONS_FOR_MANAGER_VIEWS):
    """Managers with silverware, most decorated first."""
    mgr = manager_records(ts, min_seasons)
    if mgr.empty:
        return mgr
    out = mgr[mgr['Titles'] > 0].sort_values(['Titles', 'Win %'], ascending=False)
    return out[MANAGER_COLS].reset_index(drop=True)


def biggest_swings(ts, n=12):
    """Largest year-on-year jumps and collapses by the same manager in a league."""
    rows = []
    for (oid, league), g in ts.groupby(['Owner ID', 'League']):
        g = g.sort_values('Year')
        prev = None
        for row in g.to_dict('records'):
            if prev is not None and row['Year'] == prev['Year'] + 1:
                rows.append({
                    'Owner': row['Owner'], 'League': league,
                    'From': f"{prev['Year']} ({prev['W']}-{prev['L']})",
                    'To': f"{row['Year']} ({row['W']}-{row['L']})",
                    'Win % Change': round(row['Win %'] - prev['Win %'], 1),
                    'PPG z Change': round(row['PPG z'] - prev['PPG z'], 2),
                })
            prev = row
    if not rows:
        return pd.DataFrame(), pd.DataFrame()
    sw = pd.DataFrame(rows)
    cols = ['Owner', 'League', 'From', 'To', 'Win % Change', 'PPG z Change']
    rise = sw.sort_values('Win % Change', ascending=False).head(n)[cols]
    fall = sw.sort_values('Win % Change').head(n)[cols]
    return rise.reset_index(drop=True), fall.reset_index(drop=True)


def iron_men(ts, n=15):
    """Most seasons played, and how spread across leagues."""
    mgr = manager_records(ts, min_seasons=1)
    if mgr.empty:
        return mgr
    return (mgr.sort_values(['Seasons', 'Win %'], ascending=False)
            .head(n)[MANAGER_COLS].reset_index(drop=True))
