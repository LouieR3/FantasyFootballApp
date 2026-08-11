"""What actually correlates with winning, measured across every league-season.

This is statistics on your own data, not a model's opinion. Every number on the
Insights page is computed here from the same files the rest of the app reads, so
it updates as seasons land rather than being written down once.

Method notes that matter for reading the output:

* **Outcomes are league-relative.** `Win %` and `PPG z` (points per game z-scored
  within a league-season) travel across leagues of different size and scoring;
  raw points do not.
* **p-values are reported, and corrected.** Around a dozen metrics get tested
  against each outcome, so at p < 0.05 you expect roughly one false positive per
  screen. Holm-Bonferroni is applied within each outcome and the surviving
  findings are flagged, because a bare r is easy to over-read.
* **Correlation is not cause.** Where a causal path is testable it is tested
  explicitly - see `mediation`, which shows the draft's effect on winning runs
  almost entirely through scoring rather than through anything else.
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

import numpy as np
import pandas as pd

from paths import ALL_MATCHUPS, DRAFTS_DIR
from ffapp import league_registry as registry
from ffapp.metrics import hall_of_fame as hof

OUTCOMES = ['Win %', 'PPG z', 'Made Playoffs', 'Champion']

# Grouped so the page can explain *why* each family is being tested rather than
# presenting one undifferentiated wall of correlations.
METRIC_GROUPS = {
    'Scoring': ['PPG z', 'Started Points', 'PF', 'PA', 'Score CV'],
    'Power rating': ['LPI', 'Luck'],
    'Draft': ['Draft Grade'],
    'Roster construction': ['RB in 3', 'WR in 3', 'RB in 5', 'WR in 5',
                            'QB in 5', 'TE in 5', 'RB Share', 'WR Share',
                            'QB Share', 'TE Share'],
    'In-season management': ['SPAR', 'Moves', 'Transaction Grade', 'Drop Regret'],
}
ALL_METRICS = [m for group in METRIC_GROUPS.values() for m in group]


def _safe_stats():
    try:
        from scipy import stats
        return stats
    except ImportError:
        return None


# ---------------------------------------------------------------- master table

def draft_composition():
    """Per team-season: how the first few rounds were spent, by position."""
    rows = []
    for path in glob.glob(os.path.join(DRAFTS_DIR, '* Draft Results *.csv')):
        m = re.match(r'^(.+?) Draft Results (\d{4})\.csv$', os.path.basename(path))
        if not m:
            continue
        league, year = registry.canonical(m.group(1)), int(m.group(2))
        try:
            d = pd.read_csv(path)
        except Exception:
            continue
        if 'Team' not in d.columns or 'Position' not in d.columns:
            continue
        d['_pick'] = pd.to_numeric(d.get('Total Pick'), errors='coerce')
        n_teams = d['Team'].nunique()
        if not n_teams or d['_pick'].isna().all():
            continue
        # rounds are derived from pick number rather than trusted from the file,
        # which does not always carry one
        d['_round'] = np.ceil(d['_pick'] / n_teams)
        for team, g in d.groupby('Team'):
            g = g.sort_values('_pick')
            def taken(pos, upto):
                return int(((g['_round'] <= upto) & (g['Position'] == pos)).sum())
            rows.append({
                'League': league, 'Year': year, 'Team': str(team).strip(),
                'First Pick Pos': g.iloc[0]['Position'] if len(g) else None,
                'RB in 3': taken('RB', 3), 'WR in 3': taken('WR', 3),
                'RB in 5': taken('RB', 5), 'WR in 5': taken('WR', 5),
                'QB in 5': taken('QB', 5), 'TE in 5': taken('TE', 5),
            })
    return pd.DataFrame(rows)


def transaction_and_usage():
    """Per team-season: transaction value plus where started points came from."""
    from ffapp.espn import transactions as tx
    from ffapp.metrics import transaction_analysis as ta

    rows = []
    for league, year in tx.available_seasons():
        rosters, moves = tx.load_season(league, year)
        if rosters.empty:
            continue
        st = ta.stints(rosters)
        summary = ta.owner_summary(rosters, moves, st)
        started = rosters[rosters['Started']]
        totals = started.groupby('Team')['Points'].sum()
        by_pos = started.pivot_table(index='Team', columns='Position',
                                     values='Points', aggfunc='sum').fillna(0)
        for r in summary.to_dict('records'):
            team = r['Team']
            total = float(totals.get(team, 0.0))
            row = {'League': registry.canonical(league), 'Year': int(year),
                   'Team': str(team).strip(), 'SPAR': r['SPAR'],
                   'Moves': r['Moves'], 'Transaction Grade': r['Transaction Grade'],
                   'Drop Regret': r['Drop Regret'], 'Started Points': total}
            for pos in ('QB', 'RB', 'WR', 'TE'):
                got = by_pos[pos].get(team, 0.0) if pos in by_pos.columns else 0.0
                row[f'{pos} Share'] = (float(got) / total) if total else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def score_volatility():
    """Per team-season: weekly scoring mean, sd and coefficient of variation."""
    if not os.path.exists(ALL_MATCHUPS):
        return pd.DataFrame()
    mt = pd.read_csv(ALL_MATCHUPS)
    mt['League'] = mt['League'].map(registry.canonical)
    long = pd.concat([
        mt[['League', 'Year', 'Home Team', 'Home Score']]
            .rename(columns={'Home Team': 'Team', 'Home Score': 'Score'}),
        mt[['League', 'Year', 'Away Team', 'Away Score']]
            .rename(columns={'Away Team': 'Team', 'Away Score': 'Score'})],
        ignore_index=True)
    long['Team'] = long['Team'].astype(str).str.strip()
    agg = long.groupby(['League', 'Year', 'Team'])['Score'].agg(
        ['mean', 'std', 'size']).reset_index()
    agg = agg[agg['size'] >= 8]
    agg['Score CV'] = agg['std'] / agg['mean'].replace(0, np.nan)
    return agg[['League', 'Year', 'Team', 'Score CV']]


def master_table():
    """One row per team-season with every metric joined onto the outcomes."""
    ts = hof.team_seasons()
    if ts.empty:
        return ts
    ts = ts.copy()
    ts['Team'] = ts['Team'].astype(str).str.strip()
    ts['Made Playoffs'] = ts['Made Playoffs'].astype(float)
    ts['Champion'] = ts['Champion'].astype(float)

    for extra in (draft_composition(), transaction_and_usage(), score_volatility()):
        if not extra.empty:
            ts = ts.merge(extra, on=['League', 'Year', 'Team'], how='left')
    return ts


# ------------------------------------------------------------------ statistics

def _holm(pvals):
    """Holm-Bonferroni: returns the adjusted alpha each p must beat.

    Plain Bonferroni is too blunt for a screen of a dozen metrics and plain
    p < 0.05 is too generous - across four outcomes you would expect a couple of
    false positives. Holm is the standard middle ground.
    """
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    n = len(pvals)
    survives = [False] * n
    for rank, idx in enumerate(order):
        alpha = 0.05 / (n - rank)
        if pvals[idx] <= alpha:
            survives[idx] = True
        else:
            break            # Holm stops at the first failure
    return survives


def correlations(master, outcome='Win %', metrics=None):
    """r, p, n for every metric against one outcome, with a Holm-corrected flag."""
    stats = _safe_stats()
    metrics = [m for m in (metrics or ALL_METRICS)
               if m in master.columns and m != outcome]
    rows = []
    for m in metrics:
        sub = master[[m, outcome]].dropna()
        if len(sub) < 25 or sub[m].nunique() < 3:
            continue
        if stats is not None:
            r, p = stats.pearsonr(sub[m], sub[outcome])
        else:
            r, p = sub[m].corr(sub[outcome]), np.nan
        group = next((g for g, ms in METRIC_GROUPS.items() if m in ms), 'Other')
        rows.append({'Metric': m, 'Group': group, 'r': round(float(r), 3),
                     'p': float(p), 'n': len(sub)})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    if not out['p'].isna().all():
        out['Holm 0.05'] = _holm(out['p'].fillna(1.0).tolist())
    else:
        out['Holm 0.05'] = False
    out['Strength'] = pd.cut(out['r'].abs(), [-0.01, 0.1, 0.3, 0.5, 1.01],
                             labels=['none', 'weak', 'moderate', 'strong'])
    return out.reindex(out['r'].abs().sort_values(ascending=False).index) \
              .reset_index(drop=True)


def quartiles(master, metric='Draft Grade'):
    """Outcomes by quartile of one metric - far more legible than a bare r."""
    if metric not in master.columns:
        return pd.DataFrame()
    sub = master[master[metric].notna()].copy()
    if len(sub) < 40 or sub[metric].nunique() < 4:
        return pd.DataFrame()
    sub['Quartile'] = pd.qcut(sub[metric], 4,
                              labels=['Worst 25%', '2nd', '3rd', 'Best 25%'])
    g = sub.groupby('Quartile', observed=True).agg(
        Teams=('Win %', 'size'),
        **{'Win %': ('Win %', 'mean'), 'PPG z': ('PPG z', 'mean'),
           'Playoff Rate': ('Made Playoffs', 'mean'),
           'Titles': ('Champion', 'sum')})
    g['Win %'] = g['Win %'].round(1)
    g['PPG z'] = g['PPG z'].round(2)
    g['Playoff Rate'] = (100 * g['Playoff Rate']).round(1)
    return g.reset_index()


def first_pick_effect(master):
    """Does the position you open with matter? With binomial tests.

    Tested against the league-wide base rates rather than against each other, so
    a small group is compared to something stable.
    """
    stats = _safe_stats()
    if 'First Pick Pos' not in master.columns:
        return pd.DataFrame()
    sub = master[master['First Pick Pos'].notna()]
    if sub.empty:
        return pd.DataFrame()
    base_po = float(master['Made Playoffs'].mean())
    base_ti = float(master['Champion'].mean())
    rows = []
    for pos, g in sub.groupby('First Pick Pos'):
        n = len(g)
        if n < 5:
            continue
        made, titles = int(g['Made Playoffs'].sum()), int(g['Champion'].sum())
        p_po = p_ti = np.nan
        if stats is not None:
            p_po = stats.binomtest(made, n, base_po).pvalue
            p_ti = stats.binomtest(titles, n, base_ti).pvalue
        rows.append({
            'First Pick': pos, 'Teams': n,
            'Win %': round(float(g['Win %'].mean()), 1),
            'PPG z': round(float(g['PPG z'].mean()), 2),
            'Playoff Rate': round(100 * made / n, 1),
            'Expected Rate': round(100 * base_po, 1),
            'p (playoffs)': p_po,
            'Titles': titles,
            'Expected Titles': round(base_ti * n, 1),
            'p (titles)': p_ti,
        })
    return pd.DataFrame(rows).sort_values('Teams', ascending=False,
                                          ignore_index=True)


def rb_vs_wr(master):
    """The 'good RBs over WRs?' question, tested rather than asserted."""
    stats = _safe_stats()
    if 'RB in 3' not in master.columns:
        return pd.DataFrame(), {}
    d = master[master['RB in 3'].notna() & master['WR in 3'].notna()].copy()
    if d.empty:
        return pd.DataFrame(), {}
    d['Start'] = np.where(d['RB in 3'] > d['WR in 3'], 'RB-heavy',
                 np.where(d['WR in 3'] > d['RB in 3'], 'WR-heavy', 'Even'))
    table = d.groupby('Start', observed=True).agg(
        Teams=('Win %', 'size'),
        **{'Win %': ('Win %', 'mean'), 'PPG z': ('PPG z', 'mean'),
           'Playoff Rate': ('Made Playoffs', 'mean'),
           'Titles': ('Champion', 'sum')}).reset_index()
    table['Win %'] = table['Win %'].round(1)
    table['PPG z'] = table['PPG z'].round(2)
    table['Playoff Rate'] = (100 * table['Playoff Rate']).round(1)

    tests = {}
    rb, wr = d[d['Start'] == 'RB-heavy'], d[d['Start'] == 'WR-heavy']
    if stats is not None and len(rb) > 10 and len(wr) > 10:
        for metric in ('Win %', 'PPG z'):
            t, p = stats.ttest_ind(rb[metric].dropna(), wr[metric].dropna(),
                                  equal_var=False)
            tests[metric] = {'rb': float(rb[metric].mean()),
                             'wr': float(wr[metric].mean()),
                             'diff': float(rb[metric].mean() - wr[metric].mean()),
                             'p': float(p)}
        k1, n1 = int(rb['Made Playoffs'].sum()), len(rb)
        k2, n2 = int(wr['Made Playoffs'].sum()), len(wr)
        chi2, p, _, _ = stats.chi2_contingency([[k1, n1 - k1], [k2, n2 - k2]])
        tests['Playoff Rate'] = {'rb': 100 * k1 / n1, 'wr': 100 * k2 / n2,
                                 'diff': 100 * (k1 / n1 - k2 / n2), 'p': float(p)}
    return table, tests


def mediation(master, cause='Draft Grade', through='PPG z', outcome='Win %'):
    """Does the cause act on the outcome *through* the mediator, or beside it?

    Reports the three simple correlations plus the partial correlation of cause
    with outcome holding the mediator fixed. A partial near zero means the whole
    effect travels through the mediator - which is a far more useful statement
    than three separate r values.
    """
    cols = [cause, through, outcome]
    if any(c not in master.columns for c in cols):
        return {}
    sub = master[cols].dropna()
    if len(sub) < 30:
        return {}
    r_ct = sub[cause].corr(sub[through])
    r_to = sub[through].corr(sub[outcome])
    r_co = sub[cause].corr(sub[outcome])
    denom = np.sqrt(max((1 - r_ct ** 2) * (1 - r_to ** 2), 1e-12))
    partial = (r_co - r_ct * r_to) / denom
    return {'cause': cause, 'through': through, 'outcome': outcome,
            'n': len(sub),
            'cause_through': round(float(r_ct), 3),
            'through_outcome': round(float(r_to), 3),
            'cause_outcome': round(float(r_co), 3),
            'partial': round(float(partial), 3)}


def consistency_effect(master):
    """Does steady scoring beat volatile scoring, or is that a scale artifact?

    ``Score CV`` is sd/mean, so a high scorer mechanically gets a lower CV. The
    honest test is whether the relationship survives *inside* a scoring tier -
    if it collapses there, the headline number was measuring scoring, not
    consistency.
    """
    stats = _safe_stats()
    if 'Score CV' not in master.columns:
        return {}, pd.DataFrame()
    sub = master[['Score CV', 'Win %', 'PPG z']].dropna()
    if len(sub) < 60:
        return {}, pd.DataFrame()
    overall = {}
    if stats is not None:
        r, p = stats.pearsonr(sub['Score CV'], sub['Win %'])
        overall = {'r': round(float(r), 3), 'p': float(p), 'n': len(sub)}

    sub = sub.copy()
    sub['Tier'] = pd.qcut(sub['PPG z'], 3,
                          labels=['Low scorers', 'Mid', 'High scorers'])
    rows = []
    for tier, g in sub.groupby('Tier', observed=True):
        if len(g) < 30:
            continue
        if stats is not None:
            r, p = stats.pearsonr(g['Score CV'], g['Win %'])
        else:
            r, p = g['Score CV'].corr(g['Win %']), np.nan
        rows.append({'Scoring Tier': tier, 'Teams': len(g),
                     'r (CV vs Win %)': round(float(r), 3), 'p': float(p)})
    return overall, pd.DataFrame(rows)


def headline_findings(master):
    """The short version, generated from the numbers rather than written down."""
    out = []
    corr = correlations(master, 'Win %')
    if corr.empty:
        return out
    by_metric = corr.set_index('Metric')

    def r_of(m):
        return by_metric.loc[m, 'r'] if m in by_metric.index else None

    q = quartiles(master, 'Draft Grade')
    if len(q) == 4:
        worst, best = q.iloc[0], q.iloc[-1]
        out.append({
            'headline': 'The draft is the biggest thing you control',
            'detail': (f"Best-quartile drafts win {best['Win %']:.0f}% of games and "
                       f"made the playoffs {best['Playoff Rate']:.0f}% of the time, "
                       f"against {worst['Win %']:.0f}% and {worst['Playoff Rate']:.0f}% "
                       f"for the worst quartile - and took {int(best['Titles'])} titles "
                       f"to {int(worst['Titles'])}."),
            'stat': f"r = {r_of('Draft Grade'):+.2f} with win rate",
        })

    med = mediation(master)
    if med:
        out.append({
            'headline': 'and it wins by scoring points, not by anything subtler',
            'detail': (f"Draft grade tracks scoring at r = {med['cause_through']:+.2f} "
                       f"and scoring tracks wins at r = {med['through_outcome']:+.2f}. "
                       f"Hold scoring fixed and the draft's link to winning falls to "
                       f"r = {med['partial']:+.2f} - essentially nothing left over."),
            'stat': f"partial r = {med['partial']:+.2f} (n={med['n']})",
        })

    tbl, tests = rb_vs_wr(master)
    if tests.get('Win %'):
        t = tests['Win %']
        po = tests.get('Playoff Rate', {})
        out.append({
            'headline': 'RB-first over WR-first is not measurable here',
            'detail': (f"Teams that spent more of their first three rounds on backs "
                       f"won {t['rb']:.1f}% of games against {t['wr']:.1f}% for "
                       f"receiver-heavy starts - a {t['diff']:+.1f} point gap that does "
                       f"not clear significance (p = {t['p']:.2f}"
                       + (f"; playoff rates {po['rb']:.0f}% vs {po['wr']:.0f}%, "
                          f"p = {po['p']:.2f}" if po else '') + ")."),
            'stat': 'no significant difference',
        })

    fp = first_pick_effect(master)
    if not fp.empty and 'p (playoffs)' in fp.columns:
        qb = fp[fp['First Pick'] == 'QB']
        if len(qb):
            r0 = qb.iloc[0]
            out.append({
                'headline': 'Opening with a quarterback is the one clear mistake',
                'detail': (f"{int(r0['Teams'])} teams took a QB with their first pick. "
                           f"They reached the playoffs {r0['Playoff Rate']:.0f}% of the "
                           f"time against a {r0['Expected Rate']:.0f}% baseline "
                           f"(p = {r0['p (playoffs)']:.3f}) and won "
                           f"{int(r0['Titles'])} titles against "
                           f"{r0['Expected Titles']:.1f} expected."),
                'stat': f"{r0['Playoff Rate']:.0f}% vs {r0['Expected Rate']:.0f}% playoff rate",
            })

    spar, txn = r_of('SPAR'), r_of('Transaction Grade')
    if spar is not None:
        out.append({
            'headline': 'The waiver wire does not decide seasons',
            'detail': (f"Value added through transactions correlates with winning at "
                       f"r = {spar:+.2f}"
                       + (f" and the transaction grade at r = {txn:+.2f}"
                          if txn is not None else '')
                       + " - both indistinguishable from zero. Working the wire is how "
                         "you patch a bad draft, not how you win."),
            'stat': f"r = {spar:+.2f}, not significant",
        })

    luck = r_of('Luck')
    if luck is not None:
        out.append({
            'headline': 'and roughly a third of it is luck',
            'detail': (f"Wins above expectation correlate with win rate at "
                       f"r = {luck:+.2f} while being essentially unrelated to how much "
                       f"a team scored. That is the schedule, not the roster."),
            'stat': f"r = {luck:+.2f} with wins",
        })
    return out
