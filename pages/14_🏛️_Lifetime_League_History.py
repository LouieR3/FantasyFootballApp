import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import os

import pandas as pd
import streamlit as st

from paths import ALL_MATCHUPS
from ffapp import league_registry as registry
from ffapp.metrics import lifetime as lt
from ffapp.ui.tables import apply_display_defaults, show_table


@st.cache_data(show_spinner=False)
def leagues_with_history(file_key):
    return lt.multi_season_leagues()


@st.cache_data(show_spinner='Stitching together every season...')
def season_games(league, file_key):
    return lt.team_games(league)


@st.cache_data(show_spinner=False)
def unresolved(league, file_key):
    return lt.unresolved_teams(league)


def app():
    apply_display_defaults()

    st.header('🏛️ Lifetime League History')
    st.write(
        'Every season of a league stitched into one history — careers, rivalries, '
        'playoff records and the record book. Only leagues with more than one '
        'season on file appear here.'
    )

    key = os.path.getmtime(ALL_MATCHUPS)
    leagues = leagues_with_history(key)
    if not leagues:
        st.error('No league has more than one season of matchup data yet.')
        return

    league = st.selectbox('League', leagues, format_func=registry.label)
    tg = season_games(league, key)
    if tg.empty:
        st.error(f'No matchup data for {league}.')
        return

    seasons = sorted(tg['Year'].unique())
    st.caption(f"{len(seasons)} seasons ({seasons[0]}–{seasons[-1]}) · "
               f"{len(tg) // 2} games · {tg['Owner ID'].nunique()} managers · "
               f"{registry.association(league)}")

    with st.expander('How managers are tracked across seasons', expanded=False):
        st.markdown(
            """
Team names change constantly, so a name is not an identity. Managers are keyed on
the **owner ID** recorded in each season's draft file, which is stable across
renames — so "Philadelphia British Army" becoming "Philadelphia Bills Mafia" stays
one franchise.

Two wrinkles are handled explicitly:

- The matchup data stores whatever a team was called *when that week was pulled*,
  which can differ from its draft-day name. A team renamed **mid-season** shows up
  under both names; those are merged when the two names play in non-overlapping
  weeks, never play each other, and their game counts add up to one season.
- ESPN league names drift too — 2025 has games filed under both "Family League"
  and "Family Fantasy" for the same league — so league names are canonicalised
  first.

Regular season versus playoffs is taken from the playoff bracket data rather than
a week cutoff, since leagues start their postseason in different weeks.
            """
        )
    miss = unresolved(league, key)
    if len(miss):
        st.warning(f'{len(miss)} team-season(s) could not be matched to a manager '
                   f'and are excluded: {", ".join(f"{r.Team} ({r.Year})" for r in miss.itertuples())}')

    tabs = st.tabs(['All-time', 'Careers', 'Head to head', 'Playoffs',
                    'Record book', 'Streaks & feats'])

    # ---------------------------------------------------------------- all-time
    with tabs[0]:
        st.markdown('##### All-time standings')
        at = lt.all_time_table(tg)
        show_table(at.style.background_gradient(subset=['Win %'], cmap='RdYlGn'),
                   formats={'Seasons': '{:.0f}', 'W': '{:.0f}', 'L': '{:.0f}',
                            'T': '{:.0f}', 'Playoff Apps': '{:.0f}'})
        st.caption('Playoff games are included in W/L; the Reg Season and Playoffs '
                   'columns split them out.')

    # ------------------------------------------------------------------ careers
    with tabs[1]:
        st.markdown('##### Season by season')
        careers = lt.owner_careers(tg, league)
        owners = sorted(careers['Owner'].unique())
        pick = st.multiselect('Managers', owners, default=[], placeholder='Everyone')
        view = careers[careers['Owner'].isin(pick)] if pick else careers
        show_table(view, max_rows=25,
                   formats={'Year': '{:.0f}', 'Finish': '{:.0f}'})

        st.markdown('##### Franchise trends')
        trends = lt.franchise_trends(tg)
        metric = st.radio('Metric', ['Points For', 'Wins'], horizontal=True)
        chart = trends.pivot(index='Year', columns='Owner', values=metric)
        if pick:
            chart = chart[[c for c in chart.columns if c in pick]]
        st.line_chart(chart)

    # ------------------------------------------------------------- head to head
    with tabs[2]:
        st.markdown('##### All-time wins, row versus column')
        h2h = lt.head_to_head_matrix(tg)
        if h2h.empty:
            st.info('Not enough resolved matchups yet.')
        else:
            show_table(h2h.style.background_gradient(cmap='Greens', axis=None),
                       hide_index=False, precision=0, max_rows=25)
            st.caption('Read across a row for that manager\'s wins over each rival.')

        st.divider()
        st.markdown('##### Rivalry')
        owners = sorted(tg['Owner'].dropna().unique())
        c1, c2 = st.columns(2)
        with c1:
            a = st.selectbox('Manager', owners, key='rv_a')
        with c2:
            others = [o for o in owners if o != a] or owners
            b = st.selectbox('versus', others, key='rv_b')
        games = lt.rivalry(tg, a, b)
        if games.empty:
            st.info(f'{a} and {b} have never played.')
        else:
            w = int((games['Result'] == 'W').sum())
            l = int((games['Result'] == 'L').sum())
            m1, m2, m3 = st.columns(3)
            m1.metric(f'{a} record', f'{w}-{l}')
            m2.metric('Avg margin', f"{games['Margin'].mean():+.1f}")
            m3.metric('Playoff meetings', int(games['Is Playoff'].sum()))
            show_table(games.style.background_gradient(subset=['Margin'], cmap='RdYlGn'),
                       max_rows=20, formats={'Year': '{:.0f}', 'Week': '{:.0f}'})

    # ----------------------------------------------------------------- playoffs
    with tabs[3]:
        st.markdown('##### Playoff records')
        pr = lt.playoff_records(tg, league)
        if pr.empty:
            st.info('No playoff data on file for this league yet.')
        else:
            show_table(pr.style.background_gradient(subset=['Win %'], cmap='RdYlGn')
                         .background_gradient(subset=['Titles'], cmap='YlOrBr'),
                       formats={'Playoff Apps': '{:.0f}', 'W': '{:.0f}', 'L': '{:.0f}',
                                'Titles': '{:.0f}', 'Finals': '{:.0f}'})

        st.divider()
        st.markdown('##### Clutch or choke')
        st.caption(
            'Playoff scoring against that same manager\'s own regular-season average, '
            'so it measures showing up when it counts rather than just being good. '
            'Negative is a choker. Managers with fewer than two playoff games are '
            'left out — one bad game is not a pattern.'
        )
        cc = lt.clutch_and_choke(tg)
        if cc.empty:
            st.info('Not enough playoff games yet.')
        else:
            show_table(cc.style.background_gradient(subset=['Difference'], cmap='RdYlGn'),
                       formats={'Playoff Games': '{:.0f}'})

    # -------------------------------------------------------------- record book
    with tabs[4]:
        st.markdown('##### The record book')
        st.caption('Single-game extremes across every season on file.')
        show_table(lt.records_book(tg), formats={'Season': '{:.0f}', 'Week': '{:.0f}'})

        st.divider()
        st.markdown('##### Best and worst seasons')
        show_table(lt.season_extremes(tg)
                   .style.background_gradient(subset=['Points For'], cmap='RdYlGn'),
                   max_rows=20, formats={'Year': '{:.0f}', 'Games': '{:.0f}',
                                         'Wins': '{:.0f}'})

    # ------------------------------------------------------------ streaks/feats
    with tabs[5]:
        st.markdown('##### Longest streaks')
        st.caption('Runs carry across seasons — a hot finish plus a hot start counts.')
        show_table(lt.streaks(tg)
                   .style.background_gradient(subset=['Longest Win Streak'], cmap='Greens')
                   .background_gradient(subset=['Longest Losing Streak'], cmap='Reds'),
                   formats={'Longest Win Streak': '{:.0f}',
                            'Longest Losing Streak': '{:.0f}'})


app()
