import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import os

import pandas as pd
import streamlit as st

from paths import TRANSACTIONS_DIR
from ffapp import league_registry as registry
from ffapp.espn import transactions as tx
from ffapp.metrics import transaction_analysis as ta
from ffapp.ui.tables import apply_display_defaults, show_table


@st.cache_data(show_spinner=False)
def seasons(dir_key):
    return tx.available_seasons()


@st.cache_data(show_spinner='Scoring the season\'s moves...')
def scored(league, year, dir_key):
    return ta.load_and_score(league, year)


def app():
    apply_display_defaults()

    st.header('🔄 Transaction Analysis')
    st.write(
        'Every add, drop and trade of the season, scored by what it actually '
        'produced in a starting lineup.'
    )

    if not os.path.isdir(TRANSACTIONS_DIR):
        st.error('No transaction data yet. Run `python pipeline/backfill_transactions.py`.')
        return

    available = seasons(os.path.getmtime(TRANSACTIONS_DIR))
    if not available:
        st.error('No transaction data yet. Run `python pipeline/backfill_transactions.py`.')
        return

    leagues = sorted({lg for lg, _ in available})
    c1, c2 = st.columns([3, 1])
    with c1:
        league = st.selectbox('League', leagues, format_func=registry.label)
    years = [y for lg, y in available if lg == league]
    with c2:
        year = st.selectbox('Season', years)

    d = scored(league, year, os.path.getmtime(TRANSACTIONS_DIR))
    rosters, moves = d['rosters'], d['moves']
    if rosters.empty:
        st.warning('No weekly roster data for this league-season.')
        return

    inferred = (moves['Source'] == 'snapshot').all() if len(moves) else True
    n_moves = len(moves)
    st.caption(f'{n_moves} moves · {rosters["Week"].nunique()} weeks · '
               f'{rosters["Team"].nunique()} teams · {registry.association(league)}')

    if inferred:
        st.info(
            'Reconstructed from weekly rosters. ESPN only serves its transaction '
            'log for the **current** season, so for this year the move types are '
            'inferred rather than reported: a **TEAM→TEAM** row is either a trade '
            'or a drop-and-claim in the same week, and FAAB bids are unavailable.'
        )

    with st.expander('How these numbers work', expanded=False):
        st.markdown(
            """
Every acquisition is scored by **SPAR** — started points above replacement.

- **Started, not rostered.** Points only count in weeks the player was in a
  lineup slot. Rostering a breakout you never started is not a good pickup.
- **Above replacement.** An add is worth what it *beat*, not what it scored.
  Replacement is the 25th percentile of points among everyone rostered at that
  position that week — roughly the fringe player available for free at the time.

Replacement has to be estimated from rostered players because ESPN does not keep
weekly scores for players nobody owned. The real free-agent pool is worse than
the worst rostered player, so SPAR is mildly conservative.

**Drops** are scored separately, by what the player went on to do *in someone
else's lineup*. Points scored while unrostered are ignored — nobody captured them.

> **This grades transactions, not managers — and it does not predict winning.**
> Measured over 413 team-seasons across 37 league-seasons: total SPAR tracks the
> sheer *number* of moves at **r = +0.69**, and tracks regular-season wins at
> **r = +0.01**. Volume-adjusting does not rescue it — SPAR per Add versus wins
> is **r = −0.06**. For contrast the draft grade reaches r = −0.51 against final
> standing.
>
> A team that drafted well has little to gain from the wire and scores low here
> for a good reason; a team patching a broken draft can post a huge SPAR and
> still lose. Read this page as *"where did value come from after the draft"* —
> not as a manager leaderboard.
            """
        )

    tabs = st.tabs(['Manager scorecard', 'Best pickups', 'Drops that hurt',
                    'Trades', 'All moves', 'Weekly rosters'])

    # ------------------------------------------------------- 1. manager scorecard
    with tabs[0]:
        owners = d['owners']
        show_table(
            owners.drop(columns=['Owner ID']).style.background_gradient(
                subset=['SPAR', 'SPAR per Add', 'Transaction Grade'], cmap='RdYlGn'
            ).background_gradient(subset=['Drop Regret'], cmap='Reds'),
            formats={'Moves': '{:.0f}', 'Adds': '{:.0f}', 'Drops': '{:.0f}',
                     'Trade Adds': '{:.0f}', 'FAAB Spent': '{:.0f}'},
        )
        st.caption(
            'SPAR = value added through acquisitions. Drop Regret = what players '
            'they released went on to start elsewhere. The grade curves SPAR within '
            'this league-season — it is not a manager ranking (see above).'
        )

        st.markdown('##### Activity vs payoff')
        st.caption('Right = more moves. Up = more value gained. '
                   'Bottom-right is churn without reward.')
        st.scatter_chart(owners.set_index('Team')[['Moves', 'SPAR']],
                         x='Moves', y='SPAR')

    # ------------------------------------------------------------ 2. best pickups
    with tabs[1]:
        n = st.slider('How many', 5, 40, 15, key='pickups')
        hits = ta.waiver_wire_hits(rosters, moves, n)
        if hits.empty:
            st.info('No scored acquisitions for this season.')
        else:
            show_table(hits.style.background_gradient(subset=['SPAR'], cmap='Greens'),
                       formats={'Week': '{:.0f}', 'Weeks Started': '{:.0f}'},
                       max_rows=25)

    # -------------------------------------------------------- 3. drops that hurt
    with tabs[2]:
        n = st.slider('How many', 5, 40, 15, key='drops')
        regret = ta.biggest_mistakes(rosters, moves, n)
        if regret.empty:
            st.info('No dropped player was picked up and started by another team.')
        else:
            show_table(regret.style.background_gradient(subset=['SPAR After'], cmap='Reds'),
                       formats={'Week': '{:.0f}', 'Weeks Started After': '{:.0f}'},
                       max_rows=25)

    # -------------------------------------------------------------- 4. trades
    with tabs[3]:
        trades = d['trades']
        if trades.empty:
            st.info(
                'No confirmed trades. A trade is only identifiable from weekly '
                'snapshots when both sides move in the same week — check the '
                '**All moves** tab for TEAM→TEAM rows, which may be trades whose '
                'legs landed a week apart.'
            )
        else:
            show_table(
                trades.drop(columns=['League', 'Year']).style.background_gradient(
                    subset=['Margin'], cmap='Oranges'),
                formats={'Week': '{:.0f}'},
            )
            st.caption('Gain = rest-of-season SPAR from the players each side received.')

    # ------------------------------------------------------------ 5. all moves
    with tabs[4]:
        kinds = sorted(moves['Type'].unique()) if len(moves) else []
        picked = st.multiselect('Type', kinds, default=kinds)
        view = moves[moves['Type'].isin(picked)] if picked else moves
        show_table(view.drop(columns=['League', 'Year', 'Owner ID']),
                   formats={'Week': '{:.0f}', 'FAAB Bid': '{:.0f}'},
                   max_rows=20)

    # -------------------------------------------------------- 6. weekly rosters
    with tabs[5]:
        team = st.selectbox('Team', sorted(rosters['Team'].unique()))
        wk = st.slider('Week', int(rosters['Week'].min()),
                       int(rosters['Week'].max()), int(rosters['Week'].min()))
        view = rosters[(rosters['Team'] == team) & (rosters['Week'] == wk)]
        view = view[['Slot', 'Player', 'Position', 'Started', 'Points', 'Projected']]
        show_table(view.sort_values(['Started', 'Points'], ascending=[False, False]),
                   max_rows=20)


app()
