"""Lifetime league history: careers, rivalries, playoff records and stat feats.

For leagues with more than one season on file. Everything is computed from data
already on disk - no ESPN round trip - which is only possible because of the
identity layer below.

The hard part: **who is who across seasons.** Team names change constantly
("Philadelphia British Army" becomes "Philadelphia Bills Mafia"), so a name is
not an identity. Three sources get stitched together:

1. ``data/drafts/<league> Draft Results <year>.csv`` carries an ``Owner ID`` for
   every team in all 39 league-seasons. That is the stable key.
2. ``data/all_matchups.csv`` carries only team names, and the name recorded is
   whatever the team was called *when that week was pulled* - which can differ
   from its name on draft day. Those extra names are matched onto owners by
   residual matching: within a league-season, if exactly one matchup name and
   exactly one draft name are unaccounted for, they are the same team.
3. The "Louie Power Index" sheets carry human owner names for 27 of 42
   workbooks, used for display only.

League names drift too, so everything is folded through
``league_registry.canonical()`` first - see the note there about Family League.
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

from paths import (AGGREGATED_DRAFT_GRADES, ALL_MATCHUPS, ALL_PLAYOFF_DFS,
                   DRAFTS_DIR, DRAFT_GRADES_WITH_STANDINGS, LEAGUES_DIR)
from ffapp import league_registry as registry

# Streamlit keeps already-imported modules in sys.modules across reruns and only
# re-executes the page script, so after a deploy that ADDS a symbol to an existing
# module the running process can still hold the old version. That surfaces as a
# baffling AttributeError deep in a call stack; this turns it into an instruction.
if not hasattr(registry, 'canonical'):
    raise RuntimeError(
        "ffapp.league_registry is loaded from an older deploy (no `canonical`). "
        "Streamlit reuses already-imported modules across reruns, so a deploy that "
        "adds a function needs a full process restart: Manage app -> Reboot app."
    )

DRAFT_RE = re.compile(r'^(.+?) Draft Results (\d{4})\.csv$')


# --------------------------------------------------------------- identity layer
@lru_cache(maxsize=1)
def owner_crosswalk():
    """(league, year, team) -> owner id, from the draft files.

    Memoised: called once per league while building cross-league views. Callers
    filter rather than mutate the result.
    """
    rows = []
    for path in glob.glob(os.path.join(DRAFTS_DIR, '* Draft Results *.csv')):
        m = DRAFT_RE.match(os.path.basename(path))
        if not m:
            continue
        league = registry.canonical(m.group(1))
        year = int(m.group(2))
        df = pd.read_csv(path, usecols=['Team', 'Owner ID']).drop_duplicates()
        for team, oid in zip(df['Team'], df['Owner ID']):
            if pd.isna(oid):
                continue
            rows.append({'League': league, 'Year': year,
                         'Team': str(team).strip(), 'Owner ID': str(oid)})
    return pd.DataFrame(rows).drop_duplicates()


@lru_cache(maxsize=1)
def owner_display_names():
    """owner id -> a human name, harvested from the Louie Power Index sheets.

    Those sheets name owners but not their IDs, so they are joined by team name
    within a league-season. Only 27 of 42 workbooks carry owner names at all.
    """
    xw = owner_crosswalk()
    key = dict(zip(zip(xw['League'], xw['Year'], xw['Team']), xw['Owner ID']))
    names = {}
    for path in glob.glob(os.path.join(LEAGUES_DIR, '*.xlsx')):
        base = os.path.splitext(os.path.basename(path))[0]
        league, year = registry.split_league_year(base)
        if not year:
            continue
        league = registry.canonical(league)
        try:
            df = pd.read_excel(path, sheet_name='Louie Power Index')
        except Exception:
            continue
        col = next((c for c in ('Owner', 'Owners') if c in df.columns), None)
        if not col or 'Teams' not in df.columns:
            continue
        for team, owner in df[['Teams', col]].dropna().itertuples(index=False):
            oid = key.get((league, int(year), str(team).strip()))
            if oid:
                names.setdefault(oid, str(owner).strip())
    return names


def resolve_teams(league):
    """(year, team name) -> owner id for one league, including renamed teams.

    Names seen in the matchup data but not in the draft data are matched by
    elimination: if a season has exactly one unclaimed name on each side they
    must be the same team. Anything still ambiguous is left unmapped rather than
    guessed, and surfaced by `unresolved_teams`.
    """
    league = registry.canonical(league)
    xw = owner_crosswalk()
    xw = xw[xw['League'] == league]
    mapping = dict(zip(zip(xw['Year'], xw['Team']), xw['Owner ID']))

    am = _raw_matchups()
    am = am[am['League'] == league]
    for year, g in am.groupby('Year'):
        seen = {n for n in set(g['Home Team']) | set(g['Away Team']) if n}
        drafted = set(xw[xw['Year'] == year]['Team'])
        extra = sorted(seen - drafted)
        spare = sorted(drafted - seen)

        # simple case: one unclaimed name on each side, so they are the same team
        if len(extra) == 1 and len(spare) == 1:
            mapping[(year, extra[0])] = mapping[(year, spare[0])]
            continue

        # mid-season rename: *both* names show up in the matchup data, just in
        # different weeks, so set arithmetic finds nothing. A renamed team is
        # identifiable because its two names play in disjoint weeks, never play
        # each other, and their game counts add up to a normal season.
        if not extra:
            continue
        weeks = {}
        for name in seen:
            rows = g[(g['Home Team'] == name) | (g['Away Team'] == name)]
            weeks[name] = set(rows['Week'])
        typical = max((len(w) for n, w in weeks.items() if n in drafted), default=0)
        for name in extra:
            for cand in drafted:
                if cand not in weeks:
                    continue
                played_each_other = not g[
                    ((g['Home Team'] == name) & (g['Away Team'] == cand)) |
                    ((g['Home Team'] == cand) & (g['Away Team'] == name))].empty
                if (not weeks[name] & weeks[cand]
                        and not played_each_other
                        and len(weeks[name]) + len(weeks[cand]) == typical):
                    mapping[(year, name)] = mapping[(year, cand)]
                    break
    return mapping


def unresolved_teams(league):
    """Team-seasons whose owner could not be identified - shown, not hidden."""
    league = registry.canonical(league)
    mapping = resolve_teams(league)
    am = _raw_matchups()
    am = am[am['League'] == league]
    out = []
    for year, g in am.groupby('Year'):
        for name in sorted({n for n in set(g['Home Team']) | set(g['Away Team']) if n}):
            if (year, name) not in mapping:
                out.append({'Year': year, 'Team': name})
    return pd.DataFrame(out)


# ------------------------------------------------------------------ base tables
@lru_cache(maxsize=1)
def _raw_matchups_cached():
    am = pd.read_csv(ALL_MATCHUPS)
    am = am.dropna(subset=['Home Team', 'Away Team']).copy()
    am['League'] = am['League'].map(registry.canonical)
    for c in ('Home Team', 'Away Team'):
        am[c] = am[c].astype(str).str.strip()
    return am


def _raw_matchups():
    """A copy, so callers can filter and add columns freely."""
    return _raw_matchups_cached().copy()


def multi_season_leagues(min_seasons=2):
    """Leagues with enough history for a lifetime view."""
    am = _raw_matchups()
    counts = am.groupby('League')['Year'].nunique()
    return sorted(counts[counts >= min_seasons].index)


def playoff_games(league):
    """Playoff matchups for one league, byes dropped."""
    league = registry.canonical(league)
    try:
        pg = pd.read_csv(ALL_PLAYOFF_DFS)
    except FileNotFoundError:
        return pd.DataFrame()
    pg['League'] = pg['League'].map(registry.canonical)
    pg = pg[pg['League'] == league].copy()
    for c in ('Team 1', 'Team 2'):
        pg[c] = pg[c].astype(str).str.strip()
    pg = pg[(pg['Team 2'] != 'Bye') & (pg['Team 2'] != '-') & pg['Team 2'].notna()]
    for c in ('Score 1', 'Score 2'):
        pg[c] = pd.to_numeric(pg[c], errors='coerce')
    return pg.dropna(subset=['Score 1', 'Score 2'])


def team_games(league):
    """One row per team per game: long form, owner-resolved, playoff flagged.

    This is the base every lifetime view is built from.
    """
    league = registry.canonical(league)
    am = _raw_matchups()
    am = am[am['League'] == league].copy()
    mapping = resolve_teams(league)

    # a playoff appearance is keyed on (year, team, score) so a coincidentally
    # equal score elsewhere in the season cannot be mistaken for a playoff game
    pg = playoff_games(league)
    playoff_keys = set()
    for a, b in (('Team 1', 'Score 1'), ('Team 2', 'Score 2')):
        if len(pg):
            playoff_keys |= set(zip(pg['Year'], pg[a], pg[b].round(2)))

    cols = ['Year', 'Week', 'Team', 'Opponent', 'Score', 'Opp Score', 'Predicted']
    home = am.rename(columns={'Home Team': 'Team', 'Home Score': 'Score',
                              'Home Predicted Score': 'Predicted',
                              'Away Team': 'Opponent', 'Away Score': 'Opp Score'})
    away = am.rename(columns={'Away Team': 'Team', 'Away Score': 'Score',
                              'Away Predicted Score': 'Predicted',
                              'Home Team': 'Opponent', 'Home Score': 'Opp Score'})
    tg = pd.concat([home[cols], away[cols]], ignore_index=True)
    tg = tg.dropna(subset=['Score', 'Opp Score'])
    if tg.empty:
        return tg
    tg['Score'] = tg['Score'].astype(float)
    tg['Opp Score'] = tg['Opp Score'].astype(float)
    tg['Owner ID'] = [mapping.get((y, t)) for y, t in zip(tg['Year'], tg['Team'])]
    tg['Opp Owner ID'] = [mapping.get((y, t)) for y, t in zip(tg['Year'], tg['Opponent'])]
    tg['Is Playoff'] = [(y, t, round(s, 2)) in playoff_keys
                        for y, t, s in zip(tg['Year'], tg['Team'], tg['Score'])]
    tg['Margin'] = tg['Score'] - tg['Opp Score']
    tg['Result'] = np.where(tg['Margin'] > 0, 'W', np.where(tg['Margin'] < 0, 'L', 'T'))
    tg['vs Projection'] = tg['Score'] - tg['Predicted']
    names = owner_display_names()
    tg['Owner'] = tg['Owner ID'].map(names)
    tg['Opp Owner'] = tg['Opp Owner ID'].map(names)
    # fall back to the most recent team name when no owner name is on file
    latest = (tg.sort_values('Year').groupby('Owner ID')['Team'].last())
    tg['Owner'] = tg['Owner'].fillna(tg['Owner ID'].map(latest))
    tg['Opp Owner'] = tg['Opp Owner'].fillna(tg['Opp Owner ID'].map(latest))
    return tg


# ============================================================== lifetime views
def _wlt(g):
    return (int((g['Result'] == 'W').sum()),
            int((g['Result'] == 'L').sum()),
            int((g['Result'] == 'T').sum()))


def _owner_label(g, oid):
    return g['Owner'].dropna().iloc[-1] if g['Owner'].notna().any() else str(oid)


def all_time_table(tg):
    """One row per owner: the franchise record book."""
    rows = []
    for oid, g in tg.groupby('Owner ID'):
        w, l, t = _wlt(g)
        reg, po = g[~g['Is Playoff']], g[g['Is Playoff']]
        rw, rl, _ = _wlt(reg)
        pw, pl, _ = _wlt(po)
        played = w + l + t
        rows.append({
            'Owner': _owner_label(g, oid),
            'Seasons': g['Year'].nunique(),
            'W': w, 'L': l, 'T': t,
            'Win %': round(100 * (w + 0.5 * t) / played, 1) if played else 0.0,
            'Reg Season': f"{rw}-{rl}",
            'Playoffs': f"{pw}-{pl}",
            'Playoff Apps': int(po['Year'].nunique()),
            'Points For': round(g['Score'].sum(), 1),
            'Points Against': round(g['Opp Score'].sum(), 1),
            'Avg Score': round(g['Score'].mean(), 1),
            'Best Week': round(g['Score'].max(), 1),
        })
    out = pd.DataFrame(rows).sort_values(['Win %', 'W'], ascending=False)
    return out.reset_index(drop=True)


def owner_careers(tg, league):
    """Season-by-season career table, with finish and draft grade where known."""
    league = registry.canonical(league)

    # Draft grades come from Aggregated_Draft_Grades.csv, which `regrade_drafts`
    # rewrites in full every run and therefore always covers the latest season.
    # Draft_Grades_with_Standings.csv is only used for the final Finish, because
    # that needs a live ESPN standings pull and so lags a season behind - reading
    # grades from it was why the newest year showed no draft grades at all.
    grades = {}
    if os.path.exists(AGGREGATED_DRAFT_GRADES):
        ag = pd.read_csv(AGGREGATED_DRAFT_GRADES)
        parts = ag['League Name'].str.rsplit(' ', n=1)
        ag['_league'] = parts.str[0].map(registry.canonical)
        ag['_year'] = pd.to_numeric(parts.str[1], errors='coerce')
        ag = ag[ag['_league'] == league]
        grades = {(int(y), str(t).strip()): g
                  for y, t, g in zip(ag['_year'], ag['Team'], ag['Draft Grade'])
                  if pd.notna(y)}

    standings = pd.DataFrame()
    if os.path.exists(DRAFT_GRADES_WITH_STANDINGS):
        standings = pd.read_csv(DRAFT_GRADES_WITH_STANDINGS)
        standings['League Name'] = standings['League Name'].map(registry.canonical)
        standings = standings[standings['League Name'] == league]

    # Transaction Grade belongs here and only here: it is a per-season
    # per-manager number, so the careers table is the one place it lines up with
    # the draft grade for the same team-year and the two can be read together.
    txn_grades = _transaction_grades(league)

    rows = []
    for (oid, year), g in tg.groupby(['Owner ID', 'Year']):
        reg, po = g[~g['Is Playoff']], g[g['Is Playoff']]
        rw, rl, _ = _wlt(reg)
        pw, pl, _ = _wlt(po)
        team = g.sort_values('Week')['Team'].iloc[-1]
        grade = grades.get((int(year), team), np.nan)
        finish = np.nan
        if len(standings):
            hit = standings[(standings['Year'] == year) &
                            (standings['Team'].astype(str).str.strip() == team)]
            if len(hit):
                finish = hit.iloc[0].get('Standing', np.nan)
        rows.append({
            'Owner': _owner_label(g, oid),
            'Year': year, 'Team': team,
            'Record': f"{rw}-{rl}",
            'Playoffs': f"{pw}-{pl}" if len(po) else '-',
            'Points For': round(g['Score'].sum(), 1),
            'Points Against': round(g['Opp Score'].sum(), 1),
            'Avg Score': round(g['Score'].mean(), 1),
            'Finish': finish, 'Draft Grade': grade,
            'Transaction Grade': txn_grades.get((int(year), team), np.nan),
        })
    return pd.DataFrame(rows).sort_values(['Owner', 'Year']).reset_index(drop=True)


def _transaction_grades(league):
    """(year, team) -> Transaction Grade, or {} if never backfilled.

    Imported lazily and wrapped: the transaction data is optional, and a league
    with no snapshots must still get a careers table.
    """
    try:
        from ffapp.espn import transactions as _tx
        from ffapp.metrics import transaction_analysis as _ta
    except Exception:
        return {}
    out = {}
    for lg, year in _tx.available_seasons():
        if registry.canonical(lg) != league:
            continue
        rosters, moves = _tx.load_season(lg, year)
        if rosters.empty:
            continue
        summary = _ta.owner_summary(rosters, moves)
        for team, grade in zip(summary['Team'], summary['Transaction Grade']):
            out[(int(year), str(team).strip())] = grade
    return out


def head_to_head_matrix(tg):
    """Owner x owner win totals across every season."""
    valid = tg.dropna(subset=['Owner ID', 'Opp Owner ID'])
    wins = valid[valid['Result'] == 'W']
    if wins.empty:
        return pd.DataFrame()
    piv = wins.pivot_table(index='Owner', columns='Opp Owner', values='Score',
                           aggfunc='size').fillna(0).astype(int)
    owners = sorted(set(piv.index) | set(piv.columns))
    return piv.reindex(index=owners, columns=owners, fill_value=0)


def rivalry(tg, owner_a, owner_b):
    """Every meeting between two owners, newest first."""
    g = tg[(tg['Owner'] == owner_a) & (tg['Opp Owner'] == owner_b)].copy()
    cols = ['Year', 'Week', 'Team', 'Score', 'Opp Score', 'Margin', 'Result',
            'Opponent', 'Is Playoff']
    return g.sort_values(['Year', 'Week'], ascending=False)[cols].reset_index(drop=True)


# ----------------------------------------------------------- playoffs & feats
def playoff_records(tg, league):
    """Per-owner playoff record, titles and finals appearances."""
    league = registry.canonical(league)
    pg = playoff_games(league)
    mapping = resolve_teams(league)
    champs, finals = {}, {}
    if len(pg):
        for rnd, year, t1, t2, winner in zip(pg['Round'], pg['Year'], pg['Team 1'],
                                             pg['Team 2'], pg['Winner']):
            if 'champ' not in str(rnd).strip().lower():
                continue
            for team in (t1, t2):
                tid = mapping.get((year, str(team).strip()))
                if tid:
                    finals[tid] = finals.get(tid, 0) + 1
            wid = mapping.get((year, str(winner).strip()))
            if wid:
                champs[wid] = champs.get(wid, 0) + 1

    rows = []
    for oid, g in tg[tg['Is Playoff']].groupby('Owner ID'):
        w, l, _ = _wlt(g)
        rows.append({
            'Owner': _owner_label(g, oid),
            'Playoff Apps': int(g['Year'].nunique()),
            'W': w, 'L': l,
            'Win %': round(100 * w / (w + l), 1) if (w + l) else 0.0,
            'Titles': champs.get(oid, 0),
            'Finals': finals.get(oid, 0),
            'Avg Playoff Score': round(g['Score'].mean(), 1),
        })
    if not rows:
        return pd.DataFrame()
    return (pd.DataFrame(rows)
            .sort_values(['Titles', 'Win %'], ascending=False).reset_index(drop=True))


def clutch_and_choke(tg, min_games=2):
    """Playoff scoring against the same owner's own regular-season average.

    Negative means they showed up smaller when it counted. Owners below
    ``min_games`` playoff appearances are dropped - one bad game is not a pattern.
    """
    rows = []
    for oid, g in tg.groupby('Owner ID'):
        po, reg = g[g['Is Playoff']], g[~g['Is Playoff']]
        if len(po) < min_games or reg.empty:
            continue
        rows.append({
            'Owner': _owner_label(g, oid),
            'Playoff Games': len(po),
            'Reg Season Avg': round(reg['Score'].mean(), 1),
            'Playoff Avg': round(po['Score'].mean(), 1),
            'Difference': round(po['Score'].mean() - reg['Score'].mean(), 1),
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values('Difference').reset_index(drop=True)


def _longest_run(g, result):
    """Longest run of one result for a single owner, chronologically."""
    g = g.sort_values(['Year', 'Week'])
    best = cur = 0
    span = start = None
    for r, y, w in zip(g['Result'], g['Year'], g['Week']):
        if r == result:
            cur += 1
            if cur == 1:
                start = f"{y} wk{w}"
            if cur > best:
                best, span = cur, (start, f"{y} wk{w}")
        else:
            cur = 0
    return best, (f"{span[0]} - {span[1]}" if span else '')


def streaks(tg):
    """Longest winning and losing runs per owner, spanning seasons."""
    rows = []
    for oid, g in tg.groupby('Owner ID'):
        wn, wspan = _longest_run(g, 'W')
        ln, lspan = _longest_run(g, 'L')
        rows.append({
            'Owner': _owner_label(g, oid),
            'Longest Win Streak': wn, 'When (wins)': wspan,
            'Longest Losing Streak': ln, 'When (losses)': lspan,
        })
    return (pd.DataFrame(rows)
            .sort_values('Longest Win Streak', ascending=False).reset_index(drop=True))


def records_book(tg):
    """The fun ones: single-game extremes, as a tidy list."""
    def row(label, r, value):
        return {'Record': label, 'Value': round(float(value), 1), 'Owner': r['Owner'],
                'Team': r['Team'], 'Season': int(r['Year']), 'Week': int(r['Week']),
                'Detail': f"{r['Score']:.1f} vs {r['Opp Score']:.1f} ({r['Opponent']})"}

    recs = []
    if tg.empty:
        return pd.DataFrame()
    hi = tg.loc[tg['Score'].idxmax()]
    recs.append(row('Highest score', hi, hi['Score']))
    lo = tg.loc[tg['Score'].idxmin()]
    recs.append(row('Lowest score', lo, lo['Score']))
    blow = tg.loc[tg['Margin'].idxmax()]
    recs.append(row('Most lopsided win', blow, blow['Margin']))
    close = tg[tg['Margin'] > 0]
    if len(close):
        c = close.loc[close['Margin'].idxmin()]
        recs.append(row('Narrowest win', c, c['Margin']))
    losses = tg[tg['Result'] == 'L']
    if len(losses):
        ml = losses.loc[losses['Score'].idxmax()]
        recs.append(row('Most points in a loss', ml, ml['Score']))
    wins = tg[tg['Result'] == 'W']
    if len(wins):
        fw = wins.loc[wins['Score'].idxmin()]
        recs.append(row('Fewest points in a win', fw, fw['Score']))
    po = tg[tg['Is Playoff']]
    if len(po):
        ph = po.loc[po['Score'].idxmax()]
        recs.append(row('Highest playoff score', ph, ph['Score']))
        pb = po.loc[po['Margin'].idxmax()]
        recs.append(row('Most lopsided playoff win', pb, pb['Margin']))
        pl = po.loc[po['Score'].idxmin()]
        recs.append(row('Lowest playoff score', pl, pl['Score']))
    beat = tg.dropna(subset=['vs Projection'])
    if len(beat):
        ob = beat.loc[beat['vs Projection'].idxmax()]
        recs.append(row('Most over projection', ob, ob['vs Projection']))
        ub = beat.loc[beat['vs Projection'].idxmin()]
        recs.append(row('Most under projection', ub, ub['vs Projection']))
    return pd.DataFrame(recs)


def season_extremes(tg):
    """Best and worst single seasons by points scored."""
    per = tg.groupby(['Owner', 'Year']).agg(
        **{'Points For': ('Score', 'sum'), 'Avg Score': ('Score', 'mean'),
           'Games': ('Score', 'size'),
           'Wins': ('Result', lambda s: int((s == 'W').sum()))}).reset_index()
    per['Points For'] = per['Points For'].round(1)
    per['Avg Score'] = per['Avg Score'].round(1)
    return per.sort_values('Points For', ascending=False).reset_index(drop=True)


def franchise_trends(tg):
    """Season totals per owner, shaped for line charts."""
    per = tg.groupby(['Owner', 'Year']).agg(
        Wins=('Result', lambda s: int((s == 'W').sum())),
        **{'Points For': ('Score', 'sum')}).reset_index()
    per['Points For'] = per['Points For'].round(1)
    return per
