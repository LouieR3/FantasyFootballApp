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
from ffapp.ui.tables import apply_display_defaults, show_table


@st.cache_data(show_spinner=False)
def build_upsets(dir_key):
    """Every league-season's biggest upsets in one frame."""
    rows = []
    for path in sorted(glob.glob(os.path.join(LEAGUES_DIR, '*.xlsx'))):
        # basename, not a split on the directory string - the old version split
        # on f"{LEAGUES_DIR}/", which never matches Windows path separators.
        name_with_year = os.path.splitext(os.path.basename(path))[0]
        league, year = registry.split_league_year(name_with_year)
        if 'Biggest Upsets' not in sheet_names(path):
            continue
        df = load_sheet(path, 'Biggest Upsets')
        df = df.drop(columns=[c for c in df.columns if str(c).startswith('Unnamed')],
                     errors='ignore')
        df['League'] = league
        df['Year'] = year
        rows.append(df)

    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    return out.sort_values('LPI Difference', ascending=False).reset_index(drop=True)


def app():
    apply_display_defaults()
    pd.options.mode.chained_assignment = None

    st.header('Biggest Upsets By LPI')
    st.write(
        'The most unlikely results across every league and season — games won by '
        'the team with the worse Louie Power Index. Bigger LPI Difference means a '
        'bigger upset. Leagues are colour-coded; the key gives whose league each is.'
    )

    master = build_upsets(os.path.getmtime(LEAGUES_DIR))
    if master.empty:
        st.error('No league data found.')
        return

    years = sorted(master['Year'].unique(), reverse=True)
    leagues = sorted(master['League'].unique())

    c1, c2, c3 = st.columns([1, 2, 2])
    with c1:
        year_pick = st.selectbox('Season', ['All'] + years)
    with c2:
        league_pick = st.multiselect('Leagues', leagues, default=[],
                                     format_func=registry.label,
                                     placeholder='All leagues')
    with c3:
        top_n = st.slider('Show top N', 10, max(len(master), 10),
                          min(100, len(master)), step=10)

    view = master
    if year_pick != 'All':
        view = view[view['Year'] == year_pick]
    if league_pick:
        view = view[view['League'].isin(league_pick)]

    st.caption(f'{len(view)} of {len(master)} upsets'
               + ('' if len(view) <= top_n else f' — showing the top {top_n}'))
    view = view.head(top_n).reset_index(drop=True)

    league_color_key(sorted(set(view['League'])))

    styled = style_league_column(
        view.style.background_gradient(subset=['LPI Difference'], cmap='YlOrRd'))
    show_table(styled, max_rows=25)


app()
