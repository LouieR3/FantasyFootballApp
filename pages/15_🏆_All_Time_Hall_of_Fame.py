import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import os

import pandas as pd
import streamlit as st

from paths import ALL_MATCHUPS, ALL_PLAYOFF_DFS, TRANSACTIONS_DIR
from ffapp import league_registry as registry
from ffapp.metrics import hall_of_fame as hof
from ffapp.metrics import lifetime as lt
from ffapp.metrics import transaction_hall_of_fame as thof
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


TXN_INT = {'Week': '{:.0f}', 'Weeks Started': '{:.0f}', 'Moves': '{:.0f}',
           'Adds': '{:.0f}', 'Weeks Started After': '{:.0f}'}
TXN_MGR_FMT = {'Seasons': '{:.0f}', 'Leagues': '{:.0f}', 'Total Moves': '{:.0f}'}


@st.cache_data(show_spinner='Building every team-season ever...')
def all_team_seasons(matchup_key, playoff_key):
    return hof.team_seasons()


def transactions_key():
    """Cache key that changes when the transaction data does."""
    return os.path.getmtime(TRANSACTIONS_DIR) if os.path.isdir(TRANSACTIONS_DIR) else 0


@st.cache_data(show_spinner='Scoring every transaction ever made...')
def transaction_data(dir_key):
    """All-time transaction frames. Empty ones if the backfill never ran."""
    if not dir_key:
        empty = pd.DataFrame()
        return empty, empty, empty, empty
    txn = thof.transaction_seasons()
    adds, drops, trades = thof.all_moves()
    return txn, adds, drops, trades


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
                    'Managers', 'Rises & collapses', 'Trades', 'Wire & drops',
                    'Transaction feats'])

    # ------------------------------------------------------- best & worst ever
    with tabs[0]:
        # a, b = st.columns(2)
        # with a:
        st.markdown(f'##### 🐐 Best team-seasons ever — by {metric}')
        show_table(hof.best_team_seasons(ts, n, metric)
                    .style.background_gradient(subset=[metric], cmap='Greens'),
                    max_rows=30, formats=INT_FMT)
        # with b:
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

        # a, b = st.columns(2)
        # with a:
        st.markdown('##### 🥈 Worst teams to reach the final')
        st.caption('Includes eventual champions — reaching the final is the filter.')
        show_table(hof.worst_finalists(ts, n, metric)
                    .style.background_gradient(subset=[metric], cmap='Reds_r'),
                    max_rows=30, formats=INT_FMT)
        # with b:
        st.markdown('##### 👑 Worst champions')
        st.caption('Hottest at the right moment, and nothing more.')
        show_table(hof.worst_champions(ts, n, metric)
                    .style.background_gradient(subset=[metric], cmap='Reds_r'),
                    max_rows=30, formats=INT_FMT)

    # ------------------------------------------------------------------- luck
    with tabs[2]:
        st.caption('Wins above or below what their scoring deserved '
                   '(actual wins − Expected Wins).')
        # a, b = st.columns(2)
        # with a:
        st.markdown('##### 🍀 Luckiest seasons')
        show_table(hof.luckiest(ts, n)
                    .style.background_gradient(subset=['Luck'], cmap='Greens'),
                    max_rows=30, formats=INT_FMT)
        # with b:
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
        # a, b = st.columns(2)
        # with a:
        st.markdown('##### 📈 Biggest turnarounds')
        show_table(rise.style.background_gradient(subset=['Win % Change'], cmap='Greens'),
                    max_rows=30)
        # with b:
        st.markdown('##### 📉 Biggest collapses')
        show_table(fall.style.background_gradient(subset=['Win % Change'], cmap='Reds_r'),
                    max_rows=30)

    # =====================================================================
    # Transaction feats. Separate data source (data/transactions/) from the
    # rest of this page, so each tab degrades on its own if it was never
    # backfilled rather than taking the whole page down.
    # =====================================================================
    txn, adds, drops, trades = transaction_data(transactions_key())

    def _needs_backfill():
        st.info(
            'No transaction data yet. Run `python pipeline/backfill_transactions.py` '
            'to build weekly roster snapshots back to 2019.'
        )

    # ------------------------------------------------------------------ trades
    with tabs[5]:
        if trades.empty:
            _needs_backfill() if txn.empty else st.info(
                'No confirmed trades on record. A trade is only identifiable from '
                'weekly snapshots when both sides move in the same week.'
            )
        else:
            st.caption(
                f'{len(trades)} confirmed trades. Gain = rest-of-season SPAR from the '
                'players each side received. Both sides of a trade sit in the same '
                'league-season, so these margins are directly comparable — no '
                'normalising needed.'
            )
            st.markdown('##### ⚖️ Most lopsided trades')
            show_table(thof.most_lopsided_trades(trades, n)
                       .style.background_gradient(subset=['Margin'], cmap='Reds'),
                       formats=TXN_INT, max_rows=30)

            st.markdown('##### 💰 Biggest trades — most value moved')
            show_table(thof.biggest_trades(trades, n)
                       .style.background_gradient(subset=['Total Value'], cmap='Purples'),
                       formats=TXN_INT, max_rows=30)

            st.markdown('##### 🤝 Most mutually beneficial')
            mutual = thof.most_mutual_trades(trades, n)
            if mutual.empty:
                st.info('No trade yet where both sides came out ahead.')
            else:
                st.caption('Ranked by what the **weaker** side got — that is what '
                           '"everyone won" means. Ranking on the total would just '
                           'resurface blockbusters where one team got fleeced.')
                show_table(mutual.style.background_gradient(subset=['Weaker Side'],
                                                            cmap='Greens'),
                           formats=TXN_INT, max_rows=30)

    # ----------------------------------------------------------- wire & drops
    with tabs[6]:
        if adds.empty and drops.empty:
            _needs_backfill()
        else:
            st.caption(
                'These two lists rank on **raw SPAR**, because the headline of a '
                'best-ever pickup is the raw number. It is the one place scoring '
                'settings still bias the ranking — a PPR league will be '
                'over-represented among big receiver and back pickups.'
            )
            st.markdown('##### 💎 Best pickups off the wire')
            with_trades = st.checkbox('Include players acquired by trade', value=False,
                                      key='hof_add_trades')
            best = thof.best_adds(adds, n, exclude_trades=not with_trades)
            if best.empty:
                st.info('No scored acquisitions.')
            else:
                show_table(best.style.background_gradient(subset=['SPAR'], cmap='Greens'),
                           formats=TXN_INT, max_rows=30)

            st.markdown('##### 🗑️ Worst drops — what they did for somebody else')
            worst = thof.worst_drops(drops, n)
            if worst.empty:
                st.info('No dropped player was picked up and started elsewhere.')
            else:
                show_table(worst.style.background_gradient(subset=['SPAR After'],
                                                           cmap='Reds'),
                           formats=TXN_INT, max_rows=30)

    # ------------------------------------------------------ transaction feats
    with tabs[7]:
        if txn.empty:
            _needs_backfill()
        else:
            st.caption(
                f'{len(txn)} team-seasons of transaction data. These rank on **SPAR z** '
                '— SPAR z-scored within its own league-season — so a high-scoring '
                'league cannot own every list, the same way PPG z works above.'
            )
            st.warning(
                'None of this predicts winning. Total SPAR tracks the raw *number* of '
                'moves at **r = +0.69** and regular-season wins at **r = +0.01**. '
                'A team that drafted well has little to gain from the wire and scores '
                'low here for a good reason. These are feats, not a manager ranking.'
            )

            st.markdown('##### 🔥 Most value from the wire in one season')
            show_table(thof.most_spar_seasons(txn, n)
                       .style.background_gradient(subset=['SPAR z'], cmap='RdYlGn'),
                       formats=TXN_INT, max_rows=30)

            st.markdown(f'##### 🎯 Best value per add '
                        f'(min {thof.MIN_ADDS_FOR_RATE} adds)')
            st.caption('The efficient operators rather than the busiest — one lucky '
                       'pickup over two adds is noise, not skill.')
            show_table(thof.best_spar_per_add(txn, n)
                       .style.background_gradient(subset=['SPAR per Add'], cmap='RdYlGn'),
                       formats=TXN_INT, max_rows=30)

            a, b = st.columns(2)
            with a:
                st.markdown('##### 🅰️ Best transaction grades')
                show_table(thof.best_transaction_grades(txn, n)
                           .style.background_gradient(subset=['Transaction Grade'],
                                                      cmap='Greens'),
                           formats=TXN_INT, max_rows=30)
            with b:
                st.markdown('##### 🇫 Worst transaction grades')
                show_table(thof.worst_transaction_grades(txn, n)
                           .style.background_gradient(subset=['Transaction Grade'],
                                                      cmap='Reds_r'),
                           formats=TXN_INT, max_rows=30)

            st.markdown('##### 🧠 Best managers by average transaction grade')
            st.caption(
                f'Career record pooled across every league an owner plays in '
                f'(min {thof.MIN_SEASONS_FOR_MANAGER_VIEWS} seasons). Ranked on average '
                'grade, which is already league-relative.'
            )
            mgr = thof.manager_transaction_records(txn)
            if mgr.empty:
                st.info('Not enough multi-season owners yet.')
            else:
                show_table(mgr.style.background_gradient(subset=['Avg Grade'],
                                                         cmap='RdYlGn')
                              .background_gradient(subset=['Total Drop Regret'],
                                                   cmap='Reds'),
                           formats=TXN_MGR_FMT, max_rows=30)


app()
