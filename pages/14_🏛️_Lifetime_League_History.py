import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import os

import pandas as pd
import streamlit as st

from paths import ALL_MATCHUPS, TRANSACTIONS_DIR
from ffapp import league_registry as registry
from ffapp.metrics import lifetime as lt
from ffapp.metrics import transaction_hall_of_fame as thof
from ffapp.ui.tables import apply_display_defaults, show_table


@st.cache_data(show_spinner=False)
def leagues_with_history(file_key):
    return lt.multi_season_leagues()


def transactions_key():
    """Cache key that changes when the transaction data does."""
    return os.path.getmtime(TRANSACTIONS_DIR) if os.path.isdir(TRANSACTIONS_DIR) else 0


@st.cache_data(show_spinner='Scoring this league\'s transaction history...')
def league_transactions(league, dir_key):
    """One league's owner-level transaction record, plus headline totals."""
    if not dir_key:
        return pd.DataFrame(), {}
    txn = thof.transaction_seasons()
    _adds, _drops, trades = thof.all_moves()
    return (thof.league_transaction_history(league, txn, trades),
            thof.league_transaction_totals(league, txn, _adds, _drops, trades))


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
                    'Record book', 'Streaks & feats', 'Transactions'])

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
        grad = [c for c in ('Draft Grade', 'Transaction Grade') if c in view.columns]
        styled = view.style
        if grad:
            styled = styled.background_gradient(subset=grad, cmap='RdYlGn')
        if 'Finish' in view.columns:
            styled = styled.background_gradient(subset=['Finish'], cmap='RdYlGn_r')
        show_table(styled, max_rows=25,
                   formats={'Year': '{:.0f}', 'Finish': '{:.0f}'})
        st.caption(
            'How the season was built, start to finish: **Draft Grade** for the draft, '
            '**Transaction Grade** for everything after it. Both curve within their own '
            'league-season, so 75 is average either way. Transaction Grade is shown here '
            'and nowhere else on this page — it is a per-season number, and this is the '
            'one table where it lines up with the draft grade for the same team-year.'
        )
        blank_finish = sorted(careers.loc[careers['Finish'].isna(), 'Year'].unique())
        if blank_finish:
            st.caption(
                '⚠️ **Finish** is blank for '
                f"{', '.join(str(int(y)) for y in blank_finish)}: the final standing is "
                'ESPN\'s own `final_standing` and cannot be rebuilt from the stored data '
                '(reconstructing it from brackets and records matches on only ~62% of '
                'team-seasons). Run `python pipeline/refresh_standings.py` to fill it in.'
            )
        blank_txn = ('Transaction Grade' in careers.columns
                     and careers['Transaction Grade'].isna().any())
        if blank_txn:
            years = sorted(careers.loc[careers['Transaction Grade'].isna(),
                                       'Year'].unique())
            st.caption(
                '**Transaction Grade** is blank for '
                f"{', '.join(str(int(y)) for y in years)} — run "
                '`python pipeline/backfill_transactions.py` to pull those seasons.'
            )

        st.markdown('##### Franchise trends')
        trends = lt.franchise_trends(tg)
        metric = st.radio('Metric', ['Points For', 'Wins'], horizontal=True)
        chart = trends.pivot(index='Year', columns='Owner', values=metric)
        if pick:
            chart = chart[[c for c in chart.columns if c in pick]]
        st.line_chart(chart)

    # ------------------------------------------------------------- head to head
    with tabs[2]:
        st.markdown('##### All-time grid, row versus column')
        view = st.radio(
            'Show', ['Total meetings', 'Record (W-L)', 'Wins only'],
            horizontal=True, key='h2h_view',
            help='A bare win total is ambiguous - 4 could be 4-0 or 4-9 - so '
                 'total meetings is the default. Record spells it out.')
        if view == 'Record (W-L)':
            rec = lt.head_to_head_records(tg)
            if rec.empty:
                st.info('Not enough resolved matchups yet.')
            else:
                show_table(rec, hide_index=False, precision=None, max_rows=25)
                st.caption("Row's record against column. Blank diagonal; "
                           '"-" means they have never met.')
        else:
            metric = 'wins' if view == 'Wins only' else 'meetings'
            h2h = lt.head_to_head_matrix(tg, metric)
            if h2h.empty:
                st.info('Not enough resolved matchups yet.')
            else:
                cmap = 'Greens' if metric == 'wins' else 'Blues'
                show_table(h2h.style.background_gradient(cmap=cmap, axis=None),
                           hide_index=False, precision=0, max_rows=25)
                st.caption(
                    'Games each pair has played all time - symmetric, so the '
                    'grid reads the same both ways. Use **Record** for who won '
                    'them, or the rivalry view below for game-by-game.'
                    if metric == 'meetings' else
                    "Row's wins over each column.")

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

    # ------------------------------------------------------------ transactions
    with tabs[6]:
        history, totals = league_transactions(league, transactions_key())
        if history.empty:
            st.info(
                'No transaction data for this league yet. Run '
                '`python pipeline/backfill_transactions.py` to build weekly roster '
                'snapshots back to 2019.'
            )
        else:
            st.markdown('##### League-wide transaction history')
            a, b, c, d = st.columns(4)
            a.metric('Total moves', f"{totals['moves']:,}")
            b.metric('Value added (SPAR)', f"{totals['spar_total']:,.0f}")
            c.metric('Trades', totals['trades'])
            d.metric('Avg trade margin',
                     f"{totals['avg_trade_margin']:.1f}"
                     if totals['avg_trade_margin'] is not None else '—')

            a, b, c, d = st.columns(4)
            a.metric('From the wire', f"{totals['spar_from_wire']:,.0f}")
            b.metric('From trades', f"{totals['spar_from_trades']:,.0f}")
            c.metric('Avg SPAR per team-season', f"{totals['spar_avg']:,.0f}")
            d.metric('Total drop regret', f"{totals['drop_regret']:,.0f}")
            st.caption(
                f"{totals['seasons']} seasons · {totals['adds']:,} adds · "
                f"{totals['drops']:,} drops. **SPAR** = started points above "
                'replacement — value that actually reached a starting lineup.'
            )

            st.markdown('##### By owner')
            st.caption(
                'Raw SPAR, deliberately not z-scored: everyone here played the same '
                'league under the same scoring, so the raw number is already '
                'comparable and is the more legible one. **Avg Trade Margin** is '
                'signed from that owner\'s side — positive means they came out ahead '
                'on the average trade.'
            )
            show_table(
                history.style
                    .background_gradient(subset=['Total SPAR', 'Avg SPAR',
                                                 'SPAR per Add', 'Avg Grade'],
                                         cmap='RdYlGn')
                    .background_gradient(subset=['Avg Trade Margin'], cmap='RdYlGn')
                    .background_gradient(subset=['Drop Regret'], cmap='Reds'),
                formats={'Seasons': '{:.0f}', 'Moves': '{:.0f}', 'Adds': '{:.0f}',
                         'Trade Adds': '{:.0f}', 'Trades': '{:.0f}'},
            )

            traders = history[history['Trades'] > 0]
            if len(traders) >= 2:
                best = traders.iloc[traders['Avg Trade Margin'].argmax()]
                worst = traders.iloc[traders['Avg Trade Margin'].argmin()]
                a, b = st.columns(2)
                a.success(
                    f"**Best trader — {best['Owner']}**  \n"
                    f"{best['Avg Trade Margin']:+.1f} avg margin over "
                    f"{int(best['Trades'])} trade(s) ({best['Trade Record']})"
                )
                b.error(
                    f"**Worst trader — {worst['Owner']}**  \n"
                    f"{worst['Avg Trade Margin']:+.1f} avg margin over "
                    f"{int(worst['Trades'])} trade(s) ({worst['Trade Record']})"
                )
                st.caption(
                    'Trade counts in these leagues are small, so a single lopsided '
                    'deal can decide both titles — read them as a fact about those '
                    'trades, not a verdict on the manager.'
                )


app()
