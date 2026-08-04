import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import os

import pandas as pd
import streamlit as st

from paths import ALL_MATCHUPS, ALL_PLAYOFF_DFS
from ffapp import league_registry as registry
from ffapp.metrics import hall_of_fame as hof
from ffapp.metrics import lifetime as lt
from ffapp.ui.tables import apply_display_defaults, show_table

METRICS = {
    'PPG z (fairest across leagues)': 'PPG z',
    'Win %': 'Win %',
    'LPI': 'LPI',
    'Points per game': 'PPG',
}
INT_FMT = {'W': '{:.0f}', 'L': '{:.0f}', 'Year': '{:.0f}', 'LPI': '{:.0f}'}
MGR_FMT = {'Seasons': '{:.0f}', 'Leagues': '{:.0f}', 'W': '{:.0f}', 'L': '{:.0f}',
           'Playoff Apps': '{:.0f}', 'Finals': '{:.0f}', 'Titles': '{:.0f}'}


@st.cache_data(show_spinner='Building every team-season ever...')
def all_team_seasons(matchup_key, playoff_key):
    return hof.team_seasons()


def app():
    apply_display_defaults()

    st.header('🏆 All-Time Hall of Fame')
    st.write(
        'Every team-season from every league, all years, ranked for bragging rights '
        'and humiliation alike.'
    )

    ts = all_team_seasons(os.path.getmtime(ALL_MATCHUPS),
                          os.path.getmtime(ALL_PLAYOFF_DFS))
    if ts.empty:
        st.error('No team-season data available.')
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Team-seasons', len(ts))
    c2.metric('Leagues', ts['League'].nunique())
    c3.metric('Seasons', f"{ts['Year'].min()}–{ts['Year'].max()}")
    c4.metric('Championships', int(ts['Champion'].sum()))

    with st.expander('How teams from different leagues are compared', expanded=False):
        st.markdown(
            """
Leagues differ in size, scoring settings and season length, so **raw points cannot
be compared between them** — 1,900 points means something different in a 10-team
league than a 14-team one. Rankings therefore default to:

**PPG z** — points per game as a z-score *within its own league and season*. `+2.0`
means "two standard deviations better than everyone else in that league that year",
which travels fairly across leagues and eras. `Win %` and `LPI` are also
league-relative (LPI is scaled by league size in the weekly pipeline). Raw points
are shown but never used to rank across leagues.

**Luck** = actual wins − Expected Wins, from each season's Expected Wins sheet. A
big positive number means the schedule was kind.

Managers are keyed on their ESPN account id, which is the same in every league they
play in — so a manager's career pools across leagues.
            """
        )

    missing = sorted(set(lt.multi_season_leagues(min_seasons=1)) - set(ts['League']))
    if missing:
        st.caption(
            f"Not included: {', '.join(missing)} — no draft file on record, so its "
            "teams cannot be tied to a manager. Add the league to `draft_data.py` "
            "and run the draft pull to bring it in."
        )

    metric_label = st.radio('Rank by', list(METRICS), horizontal=True)
    metric = METRICS[metric_label]
    n = st.slider('How many in each list', 5, 30, 10)

    tabs = st.tabs(['Best & worst ever', 'Playoff oddities', 'Luck',
                    'Managers', 'Rises & collapses'])

    # ------------------------------------------------------- best & worst ever
    with tabs[0]:
        a, b = st.columns(2)
        with a:
            st.markdown(f'##### 🐐 Best team-seasons ever — by {metric}')
            show_table(hof.best_team_seasons(ts, n, metric)
                       .style.background_gradient(subset=[metric], cmap='Greens'),
                       max_rows=30, formats=INT_FMT)
        with b:
            st.markdown(f'##### 💩 Worst team-seasons ever — by {metric}')
            show_table(hof.worst_team_seasons(ts, n, metric)
                       .style.background_gradient(subset=[metric], cmap='Reds_r'),
                       max_rows=30, formats=INT_FMT)
        st.markdown('##### 😤 Best season that never won a title')
        show_table(hof.best_non_champions(ts, n, metric)
                   .style.background_gradient(subset=[metric], cmap='Greens'),
                   max_rows=30, formats=INT_FMT)

    # --------------------------------------------------------- playoff oddities
    with tabs[1]:
        st.markdown('##### 🚪 Best teams to miss the playoffs')
        st.caption('Good enough to win it, watching from home anyway.')
        show_table(hof.best_missed_playoffs(ts, n, metric)
                   .style.background_gradient(subset=[metric], cmap='Greens'),
                   max_rows=30, formats=INT_FMT)

        st.markdown('##### 🎟️ Worst teams to make the playoffs')
        st.caption('Backed into the bracket.')
        show_table(hof.worst_made_playoffs(ts, n, metric)
                   .style.background_gradient(subset=[metric], cmap='Reds_r'),
                   max_rows=30, formats=INT_FMT)

        a, b = st.columns(2)
        with a:
            st.markdown('##### 🥈 Worst teams to reach the final')
            show_table(hof.worst_finalists(ts, n, metric)
                       .style.background_gradient(subset=[metric], cmap='Reds_r'),
                       max_rows=30, formats=INT_FMT)
            st.caption('Includes eventual champions — reaching the final is the filter.')
        with b:
            st.markdown('##### 👑 Worst champions')
            st.caption('Hottest at the right moment, and nothing more.')
            show_table(hof.worst_champions(ts, n, metric)
                       .style.background_gradient(subset=[metric], cmap='Reds_r'),
                       max_rows=30, formats=INT_FMT)

    # ------------------------------------------------------------------- luck
    with tabs[2]:
        st.caption('Wins above or below what their scoring deserved '
                   '(actual wins − Expected Wins).')
        a, b = st.columns(2)
        with a:
            st.markdown('##### 🍀 Luckiest seasons')
            show_table(hof.luckiest(ts, n)
                       .style.background_gradient(subset=['Luck'], cmap='Greens'),
                       max_rows=30, formats=INT_FMT)
        with b:
            st.markdown('##### 🌧️ Unluckiest seasons')
            show_table(hof.unluckiest(ts, n)
                       .style.background_gradient(subset=['Luck'], cmap='Reds_r'),
                       max_rows=30, formats=INT_FMT)

    # --------------------------------------------------------------- managers
    with tabs[3]:
        st.markdown('##### 💔 Best managers without a ring')
        st.caption('Careers pooled across every league. Two seasons minimum.')
        show_table(hof.best_without_a_ring(ts, n)
                   .style.background_gradient(subset=['Win %'], cmap='RdYlGn'),
                   max_rows=30, formats=MGR_FMT)

        st.markdown('##### 😩 Heartbreak index — most playoff trips, still no title')
        show_table(hof.heartbreak(ts).head(n)
                   .style.background_gradient(subset=['Playoff Apps'], cmap='Oranges'),
                   max_rows=30, formats=MGR_FMT)

        st.markdown('##### 🏆 Dynasties')
        show_table(hof.dynasties(ts).head(n)
                   .style.background_gradient(subset=['Titles'], cmap='YlOrBr'),
                   max_rows=30, formats=MGR_FMT)

        st.markdown('##### 🧱 Iron men — most seasons played')
        show_table(hof.iron_men(ts, n)
                   .style.background_gradient(subset=['Seasons'], cmap='Blues'),
                   max_rows=30, formats=MGR_FMT)

    # ------------------------------------------------------ rises & collapses
    with tabs[4]:
        st.caption('Consecutive seasons by the same manager in the same league.')
        rise, fall = hof.biggest_swings(ts, n)
        a, b = st.columns(2)
        with a:
            st.markdown('##### 📈 Biggest turnarounds')
            show_table(rise.style.background_gradient(subset=['Win % Change'], cmap='Greens'),
                       max_rows=30)
        with b:
            st.markdown('##### 📉 Biggest collapses')
            show_table(fall.style.background_gradient(subset=['Win % Change'], cmap='Reds_r'),
                       max_rows=30)


app()
