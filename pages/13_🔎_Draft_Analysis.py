import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import glob
import os
import re

import pandas as pd
import streamlit as st

from paths import DRAFTS_DIR
from ffapp import league_registry as registry
from ffapp.metrics import draft_analysis as da
from ffapp.ui.data_loader import load_csv


@st.cache_data(show_spinner=False)
def drafted_seasons(dir_key):
    """(league, year) pairs that have a draft file, newest first."""
    out = []
    for path in glob.glob(os.path.join(DRAFTS_DIR, '* Draft Results *.csv')):
        m = re.match(r'^(.+?) Draft Results (\d{4})\.csv$', os.path.basename(path))
        if m:
            out.append((m.group(1), int(m.group(2))))
    return sorted(out, key=lambda t: (-t[1], t[0]))


@st.cache_data(show_spinner=False)
def season_analysis(league, year, dir_key):
    df, meta = da.load_season(league, year)
    return df, meta


def app():
    st.header('🔎 Post-Season Draft Analysis')
    st.write(
        'A full post-mortem of one league\'s draft: who actually drafted well, who '
        'just got lucky, the steals and busts, and how much value was left on the board.'
    )

    seasons = drafted_seasons(os.path.getmtime(DRAFTS_DIR))
    if not seasons:
        st.error('No draft files found.')
        return

    leagues = sorted({lg for lg, _ in seasons})
    c1, c2 = st.columns([3, 1])
    with c1:
        league = st.selectbox('League', leagues, format_func=registry.label,
                              index=leagues.index('EBC League') if 'EBC League' in leagues else 0)
    years = [y for lg, y in seasons if lg == league]
    with c2:
        year = st.selectbox('Season', years)

    df, meta = season_analysis(league, year, os.path.getmtime(DRAFTS_DIR))
    st.caption(f'{len(df)} picks · {df["Team"].nunique()} teams · '
               f'{registry.association(league)}')

    # ------------------------------------------------------------ how to read it
    with st.expander('How these numbers work', expanded=False):
        st.markdown(
            """
Every pick is measured against **Expected** — what that draft slot historically
returns, fit from every league-season on file (the *N*th quarterback taken, the
*N*th running back, and so on). That makes a round-12 hit and a round-1 hit
comparable.

- **Value Over Slot** = Actual points − Expected. Positive means the pick beat
  what that slot usually gives you.
- **Accuracy vs Avg** = the pick's *preseason projection* versus Expected. Did you
  take a player the market already rated above the slot? That part you chose.
- **Luck vs Avg** = Actual versus that projection. Breakouts, injuries, situation
  — mostly not your doing.

Accuracy and Luck add up exactly to Value. Both are shown **relative to this
league-season's average**, because raw projections sit about 46 points per pick
above median outcomes (ESPN assumes a full healthy season), which uncentred would
make every manager look accurate and desperately unlucky. Zero = an average
drafter in this league.

> **Why "accuracy" and not "skill".** Across 102 consecutive-season owner pairs in
> this data, accuracy repeats year over year at only **r = +0.08** — at that sample
> size, indistinguishable from zero (luck: +0.03; total value: +0.24). So treat
> accuracy as a description of *how a draft was built* relative to the market, not
> as proof that someone is a better drafter.
            """
        )
    if not meta['has_skill_luck']:
        st.warning(
            f'Only {meta["projection_coverage"]:.0%} of this season\'s picks have a '
            'preseason projection on file, so the accuracy/luck split is hidden. '
            'Value Over Slot is still exact.'
        )

    tabs = st.tabs(['Owner scorecard', 'Steals & busts', 'By round',
                    'By position', 'Best available', 'Best lineup', 'Retention'])

    # -------------------------------------------------------- 1. owner scorecard
    with tabs[0]:
        summary = da.owner_summary(df)
        if not meta['has_skill_luck']:
            summary = summary.drop(columns=['Accuracy vs Avg', 'Luck vs Avg'])
        grad = ['Value Over Slot', 'Draft Grade', 'Hit Rate']
        if meta['has_skill_luck']:
            grad += ['Accuracy vs Avg', 'Luck vs Avg']
        st.dataframe(summary.style.background_gradient(subset=grad, cmap='RdYlGn'),
                     hide_index=True, use_container_width=True)

        if meta['has_skill_luck']:
            st.markdown('##### Draft accuracy vs luck')
            st.caption('Right = drafted well. Up = got lucky. '
                       'Top-left is a fortunate draft; bottom-right is a good draft that went wrong.')
            chart = summary.set_index('Team')[['Accuracy vs Avg', 'Luck vs Avg']]
            st.scatter_chart(chart, x='Accuracy vs Avg', y='Luck vs Avg')

    # ---------------------------------------------------------- 2. steals & busts
    with tabs[1]:
        n = st.slider('How many', 5, 25, 10, key='sb')
        steals, busts = da.steals_and_busts(df, n)
        a, b = st.columns(2)
        with a:
            st.markdown('##### 💎 Biggest steals')
            st.dataframe(steals.style.background_gradient(subset=['Value'], cmap='Greens'),
                         hide_index=True, use_container_width=True)
        with b:
            st.markdown('##### 💀 Biggest busts')
            st.dataframe(busts.style.background_gradient(subset=['Value'], cmap='Reds_r'),
                         hide_index=True, use_container_width=True)

    # ---------------------------------------------------------------- 3. by round
    with tabs[2]:
        st.markdown('##### Best pick of each round')
        st.dataframe(da.best_pick_per_round(df), hide_index=True, use_container_width=True)
        st.markdown('##### How each round performed')
        st.caption('Avg Value below zero means that round generally disappointed across the league.')
        ra = da.round_accuracy(df)
        st.dataframe(ra.style.background_gradient(subset=['Avg Value', 'Hit Rate'], cmap='RdYlGn'),
                     hide_index=True, use_container_width=True)
        st.bar_chart(ra.set_index('Round')['Avg Value'])

    # ------------------------------------------------------------- 4. by position
    with tabs[3]:
        st.markdown('##### Value gained by position')
        st.caption('Where each manager actually won or lost the draft.')
        vbp = da.value_by_position(df)
        st.dataframe(vbp.style.background_gradient(cmap='RdYlGn', axis=None),
                     use_container_width=True)
        st.markdown('##### Draft tendencies — position taken each round')
        st.dataframe(da.position_by_round(df), use_container_width=True)

    # --------------------------------------------------------- 5. best available
    with tabs[4]:
        st.markdown('##### Points left on the board')
        st.caption(
            'For each pick, the highest-scoring player still undrafted at that moment. '
            'This is pure hindsight — nobody could have known — so read it as "how the '
            'board fell", not as a grade.'
        )
        ba = da.best_available(df)
        st.dataframe(da.left_on_board_by_owner(ba)
                     .style.background_gradient(subset=['Total Left On Board'], cmap='Reds'),
                     hide_index=True, use_container_width=True)
        with st.expander('Every pick vs the best available'):
            st.dataframe(ba.style.background_gradient(subset=['Left On Board'], cmap='Reds'),
                         hide_index=True, use_container_width=True)

    # ------------------------------------------------------------- 6. best lineup
    with tabs[5]:
        st.markdown('##### Best possible lineup from your own picks')
        st.caption(
            'The highest-scoring legal starting lineup each manager could have fielded '
            f'from the players they drafted, by full-season points. Slots assumed: '
            f'{", ".join(f"{n}×{p}" for p, n in da.DEFAULT_SLOTS)}.'
        )
        team = st.selectbox('Team', sorted(df['Team'].unique()), key='bl')
        lineup = da.best_lineup(df, team)
        left, right = st.columns([2, 1])
        with left:
            st.dataframe(lineup[['Player', 'Position', 'Pick', 'Points', 'Expected', 'Value']],
                         hide_index=True, use_container_width=True)
        with right:
            drafted_total = df[df['Team'] == team]['Points'].sum()
            st.metric('Best lineup points', f"{lineup['Points'].sum():,.1f}")
            st.metric('All drafted players', f"{drafted_total:,.1f}")
            st.metric('Left on the bench', f"{drafted_total - lineup['Points'].sum():,.1f}")

    # --------------------------------------------------------------- 7. retention
    with tabs[6]:
        st.markdown('##### Draft retention — how much of your draft you kept')
        ret = da.roster_retention(league, year)
        if ret is None:
            st.info(
                'No final-roster snapshot on file for this season yet. '
                '`draft_data.py` now records end-of-season rosters, so this fills in '
                'from the next pull onward. Older seasons cannot be reconstructed — '
                'ESPN only exposes current rosters.'
            )
        else:
            st.caption('Share of a manager\'s own draft picks still on their roster at season end.')
            st.dataframe(ret.style.background_gradient(subset=['Retention %'], cmap='RdYlGn'),
                         hide_index=True, use_container_width=True)


app()
