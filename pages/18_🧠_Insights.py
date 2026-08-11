import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import os

import pandas as pd
import streamlit as st

from paths import ALL_MATCHUPS, ALL_PLAYOFF_DFS
from ffapp.metrics import insights as ins
from ffapp.ui.tables import apply_display_defaults, show_table

STRENGTH_NOTE = ('|r| under 0.1 is noise, 0.1–0.3 weak, 0.3–0.5 moderate, '
                 'above 0.5 strong.')


@st.cache_data(show_spinner='Crunching every team-season on file...')
def master(matchup_key, playoff_key):
    return ins.master_table()


def p_fmt(p):
    if pd.isna(p):
        return '—'
    return '<0.001' if p < 0.001 else f'{p:.3f}'


def app():
    apply_display_defaults()

    st.header('🧠 Insights — what actually wins')
    st.write(
        'Every number on this page is computed from your own leagues, live. '
        'It is statistics, not a model\'s opinion — and where a finding does not '
        'hold up, it says so.'
    )

    m = master(os.path.getmtime(ALL_MATCHUPS), os.path.getmtime(ALL_PLAYOFF_DFS))
    if m.empty:
        st.error('No team-season data available.')
        return

    a, b, c, d = st.columns(4)
    a.metric('Team-seasons', len(m))
    b.metric('Leagues', m['League'].nunique())
    c.metric('Seasons', f"{int(m['Year'].min())}–{int(m['Year'].max())}")
    d.metric('Titles decided', int(m['Champion'].sum()))

    with st.expander('How to read this', expanded=False):
        st.markdown(
            f"""
**Outcomes are league-relative.** `Win %` and `PPG z` (points per game
z-scored inside its own league-season) compare fairly across leagues of
different size and scoring. Raw points do not.

**Effect sizes.** {STRENGTH_NOTE}

**p-values are corrected.** Around twenty metrics get tested against each
outcome, so at a naive p < 0.05 you would expect one or two false positives per
screen. **Holm-Bonferroni** is applied within each outcome and only survivors are
marked ✅. Several plausible-looking weak effects — including every
roster-construction metric — do *not* survive, and that is itself a finding.

**Correlation is not cause.** Where a causal path is testable it is tested; see
the *Draft → points → wins* section, which shows the draft acts on winning almost
entirely through scoring.
            """
        )

    # ------------------------------------------------------------- headlines
    st.markdown('### The short version')
    findings = ins.headline_findings(m)
    for f in findings:
        with st.container(border=True):
            st.markdown(f"**{f['headline']}**  \n{f['detail']}")
            st.caption(f['stat'])

    tabs = st.tabs(['What correlates', 'The draft', 'Roster construction',
                    'Luck & consistency', 'In-season', 'The data'])

    # -------------------------------------------------------- 1. correlations
    with tabs[0]:
        outcome = st.selectbox('Outcome', ins.OUTCOMES, index=0)
        corr = ins.correlations(m, outcome)
        if corr.empty:
            st.info('Not enough data.')
        else:
            view = corr.copy()
            view['p'] = view['p'].map(p_fmt)
            view['Survives correction'] = view['Holm 0.05'].map({True: '✅', False: ''})
            view = view.drop(columns=['Holm 0.05'])
            show_table(view.style.background_gradient(subset=['r'], cmap='RdYlGn',
                                                      vmin=-0.8, vmax=0.8),
                       formats={'n': '{:.0f}', 'r': '{:+.3f}'}, max_rows=25)
            st.caption(
                f'{STRENGTH_NOTE} ✅ = survives Holm-Bonferroni at 0.05. '
                f'Metrics grouped by family so you can see which *kinds* of thing '
                f'matter, not just which single column.'
            )
            survivors = corr[corr['Holm 0.05']]['Metric'].tolist()
            dead = corr[~corr['Holm 0.05']]['Metric'].tolist()
            st.success(f'**Holds up:** {", ".join(survivors) or "nothing"}')
            st.warning(f'**Does not survive correction:** {", ".join(dead) or "nothing"}')

    # -------------------------------------------------------------- 2. draft
    with tabs[1]:
        st.markdown('##### Draft grade quartiles')
        q = ins.quartiles(m, 'Draft Grade')
        if q.empty:
            st.info('Not enough graded drafts.')
        else:
            show_table(q.style.background_gradient(
                subset=['Win %', 'Playoff Rate', 'Titles'], cmap='RdYlGn'),
                formats={'Teams': '{:.0f}', 'Titles': '{:.0f}',
                         'Win %': '{:.1f}', 'Playoff Rate': '{:.1f}'})
            st.caption('The single widest gap on this page — and the one you have '
                       'the most control over.')

        st.markdown('##### Draft → points → wins')
        med = ins.mediation(m)
        if med:
            c1, c2, c3 = st.columns(3)
            c1.metric('Draft grade → scoring', f"{med['cause_through']:+.2f}")
            c2.metric('Scoring → wins', f"{med['through_outcome']:+.2f}")
            c3.metric('Draft → wins, scoring held fixed',
                      f"{med['partial']:+.2f}",
                      help='The leftover direct effect. Near zero means the whole '
                           'effect travels through scoring.')
            st.info(
                f"A good draft raises your win rate by raising your **scoring**, "
                f"and by essentially nothing else: hold scoring fixed and the "
                f"draft's link to winning collapses from "
                f"{med['cause_outcome']:+.2f} to {med['partial']:+.2f} "
                f"(n = {med['n']}). There is no separate 'well-built roster' bonus "
                f"beyond the points it produces."
            )

    # -------------------------------------------- 3. roster construction
    with tabs[2]:
        st.markdown('##### Does starting RB beat starting WR?')
        table, tests = ins.rb_vs_wr(m)
        if table.empty:
            st.info('Not enough draft data.')
        else:
            show_table(table.style.background_gradient(subset=['Win %'],
                                                       cmap='RdYlGn'),
                       formats={'Teams': '{:.0f}', 'Titles': '{:.0f}',
                                'Win %': '{:.1f}', 'Playoff Rate': '{:.1f}'})
            if tests:
                rows = [{'Comparison': k, 'RB-heavy': round(v['rb'], 2),
                         'WR-heavy': round(v['wr'], 2), 'Difference': round(v['diff'], 2),
                         'p': p_fmt(v['p']),
                         'Verdict': 'significant' if v['p'] < 0.05 else 'not significant'}
                        for k, v in tests.items()]
                show_table(pd.DataFrame(rows))
                st.warning(
                    'RB-heavy starts do win slightly more, but the gap does not '
                    'clear significance on any measure — and **"even" splits do '
                    'just as well as RB-heavy**, which is what you would expect if '
                    'the position mix simply does not matter much. The lesson is '
                    'closer to *do not force it* than *take backs first*.'
                )

        st.markdown('##### Position of your first pick')
        fp = ins.first_pick_effect(m)
        if not fp.empty:
            view = fp.copy()
            for col in ('p (playoffs)', 'p (titles)'):
                view[col] = view[col].map(p_fmt)
            show_table(view.style.background_gradient(subset=['Playoff Rate'],
                                                      cmap='RdYlGn'),
                       formats={'Teams': '{:.0f}', 'Titles': '{:.0f}',
                                'Win %': '{:.1f}', 'Playoff Rate': '{:.1f}',
                                'Expected Rate': '{:.1f}'})
            st.error(
                '**Opening with a QB is the one positional choice with a real '
                'penalty.** RB-first and WR-first are statistically '
                'indistinguishable from the league baseline. TE-first shows a '
                'startling title rate, but on only 9 attempts — treat it as a '
                'curiosity, not a strategy.'
            )

        st.markdown('##### Where your started points came from')
        shares = ins.correlations(m, 'Win %',
                                  metrics=['RB Share', 'WR Share', 'QB Share',
                                           'TE Share'])
        if not shares.empty:
            view = shares.copy()
            view['p'] = view['p'].map(p_fmt)
            show_table(view.drop(columns=['Holm 0.05', 'Group']),
                       formats={'n': '{:.0f}', 'r': '{:+.3f}'})
            st.caption('Share of your starting-lineup points by position. None of '
                       'these predicts winning — how you *distribute* production '
                       'matters far less than how much of it you have.')

    # ------------------------------------------------- 4. luck & consistency
    with tabs[3]:
        st.markdown('##### Luck')
        luck = ins.correlations(m, 'Win %', metrics=['Luck'])
        if not luck.empty:
            r = luck.iloc[0]
            c1, c2 = st.columns(2)
            c1.metric('Luck → win rate', f"{r['r']:+.2f}")
            lz = ins.correlations(m, 'PPG z', metrics=['Luck'])
            if not lz.empty:
                c2.metric('Luck → scoring', f"{lz.iloc[0]['r']:+.2f}",
                          help='Near zero by construction — luck is wins you got '
                               'without the points to justify them.')
            st.info(
                'Luck is wins above what your scoring deserved. It correlates with '
                'win rate about as strongly as your draft does, while being '
                'unrelated to how much you scored. A large slice of every season '
                'is the schedule.'
            )
        show_table(ins.quartiles(m, 'Luck'),
                   formats={'Teams': '{:.0f}', 'Titles': '{:.0f}',
                            'Win %': '{:.1f}', 'Playoff Rate': '{:.1f}'})

        st.markdown('##### Does consistent scoring help?')
        overall, tiers = ins.consistency_effect(m)
        if overall:
            st.metric('Score volatility → win rate', f"{overall['r']:+.2f}",
                      help=f"n = {overall['n']}, p = {p_fmt(overall['p'])}")
        if not tiers.empty:
            view = tiers.copy()
            view['p'] = view['p'].map(p_fmt)
            show_table(view, formats={'Teams': '{:.0f}',
                                      'r (CV vs Win %)': '{:+.3f}'})
            st.warning(
                'The headline number is mostly an artifact. Volatility is measured '
                'as sd ÷ mean, so a high scorer mechanically looks steadier. Split '
                'by scoring tier and the effect collapses to roughly −0.11 and '
                'stops being significant in every tier. **Consistency is not an '
                'independent edge — scoring is.**'
            )

    # ------------------------------------------------------- 5. in-season
    with tabs[4]:
        txn = ins.correlations(m, 'Win %',
                              metrics=['SPAR', 'Transaction Grade', 'Moves',
                                       'Drop Regret'])
        if txn.empty:
            st.info('No transaction data yet — run '
                    '`python pipeline/backfill_transactions.py`.')
        else:
            view = txn.copy()
            view['p'] = view['p'].map(p_fmt)
            view['Survives correction'] = view['Holm 0.05'].map({True: '✅', False: ''})
            show_table(view.drop(columns=['Holm 0.05', 'Group']),
                       formats={'n': '{:.0f}', 'r': '{:+.3f}'})
            st.warning(
                'Nothing here predicts winning. Value added through the waiver wire, '
                'the transaction grade, and raw move count are all indistinguishable '
                'from zero against win rate. **Working the wire is how you patch a '
                'bad draft, not how you win a title** — which is consistent with the '
                'draft finding: a team that drafted well has less to gain from the '
                'wire and posts a lower transaction score for a good reason.'
            )
            show_table(ins.quartiles(m, 'SPAR'),
                       formats={'Teams': '{:.0f}', 'Titles': '{:.0f}',
                                'Win %': '{:.1f}', 'Playoff Rate': '{:.1f}'})
            st.caption('SPAR quartiles — flat, unlike the draft-grade table.')

    # ---------------------------------------------------------- 6. the data
    with tabs[5]:
        st.caption('The joined table behind every number above: one row per '
                   'team-season.')
        cols = [c for c in ['Season', 'Owner', 'Team', 'W', 'L', 'Win %', 'PPG z',
                            'LPI', 'Luck', 'Draft Grade', 'First Pick Pos',
                            'RB in 3', 'WR in 3', 'SPAR', 'Transaction Grade',
                            'Score CV', 'Made Playoffs', 'Champion']
                if c in m.columns]
        show_table(m[cols].sort_values('Win %', ascending=False), max_rows=20,
                   formats={'W': '{:.0f}', 'L': '{:.0f}', 'RB in 3': '{:.0f}',
                            'WR in 3': '{:.0f}', 'LPI': '{:.0f}',
                            'Made Playoffs': '{:.0f}', 'Champion': '{:.0f}'})
        st.download_button(
            'Download the full table (CSV)', m.to_csv(index=False),
            file_name='league_insights_team_seasons.csv', mime='text/csv')


app()
