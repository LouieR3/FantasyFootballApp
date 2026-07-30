import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import glob
import os

import pandas as pd
import streamlit as st

from paths import LEAGUES_DIR
from ffapp import league_registry as registry
from ffapp.ui.data_loader import load_sheet, sheet_names
from ffapp.ui.league_colors import league_color_key, style_league_column

LPI_COL = 'Louie Power Index (LPI)'


@st.cache_data(show_spinner=False)
def build_master(dir_key):
    """Every league-season's Louie Power Index rows in one frame."""
    rows = []
    for path in sorted(glob.glob(os.path.join(LEAGUES_DIR, '*.xlsx'))):
        # basename, not a string split on the directory - the old code split on
        # f"{LEAGUES_DIR}/" which never matches on Windows path separators.
        name_with_year = os.path.splitext(os.path.basename(path))[0]
        league, year = registry.split_league_year(name_with_year)
        if 'Louie Power Index' not in sheet_names(path):
            continue
        df = load_sheet(path, 'Louie Power Index')

        # The owner column is spelled 'Owners' in 21 workbooks, 'Owner' in 6, and
        # absent from 15. The old page dropped 'Owner' and rendered only 'Owners',
        # which is why the column looked almost empty. Normalising both spellings
        # takes owner coverage from 62 rows to 296 of 461.
        owner = None
        for candidate in ('Owner', 'Owners'):
            if candidate in df.columns:
                owner = df[candidate]
                break

        keep = pd.DataFrame({
            'Team': df['Teams'] if 'Teams' in df.columns else df.iloc[:, 1],
            'Owner': owner if owner is not None else pd.Series([None] * len(df)),
            LPI_COL: df[LPI_COL],
            'Record': df.get('Record'),
            'Change': df.get('Change From Last Week'),
            'League': league,
            'Year': year,
            'Whose league': registry.association(league),
        })
        rows.append(keep)

    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    out['Owner'] = out['Owner'].fillna('—')
    return out.sort_values(LPI_COL, ascending=False).reset_index(drop=True)


def app():
    pd.options.mode.chained_assignment = None

    st.header('Master List of LPI')
    st.write(
        'Every team from every league and season ranked by Louie Power Index. '
        'Leagues are colour-coded — the key below gives whose league each one is.'
    )

    master = build_master(os.path.getmtime(LEAGUES_DIR))
    if master.empty:
        st.error('No league data found.')
        return

    years = sorted(master['Year'].unique(), reverse=True)
    leagues = sorted(master['League'].unique())

    c1, c2, c3 = st.columns([1, 2, 2])
    with c1:
        year_pick = st.selectbox('Season', ['All'] + years)
    with c2:
        # Labelled by association so they're recognisable
        league_pick = st.multiselect(
            'Leagues', leagues, default=[],
            format_func=registry.label,
            placeholder='All leagues',
        )
    with c3:
        top_n = st.slider('Show top N', 10, max(len(master), 10),
                          min(100, len(master)), step=10)

    view = master
    if year_pick != 'All':
        view = view[view['Year'] == year_pick]
    if league_pick:
        view = view[view['League'].isin(league_pick)]

    st.caption(
        f'{len(view)} of {len(master)} team-seasons'
        + ('' if len(view) <= top_n else f' — showing the top {top_n} by LPI')
    )
    view = view.head(top_n).reset_index(drop=True)

    league_color_key(sorted(set(view['League'])))

    # --- styled table ---------------------------------------------------------
    styled = style_league_column(
        view.style
        .background_gradient(subset=[LPI_COL], cmap='YlGn')
        .format({LPI_COL: '{:.0f}'})
    )
    # ~35px per row, capped so the page stays scrollable rather than endless
    height = min(35 * (len(view) + 1) + 3, 900)
    st.dataframe(styled, height=height, hide_index=True, use_container_width=True)




app()
