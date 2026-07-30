"""Shared league colour-coding and legend for the cross-league pages.

Colours come from `ffapp.league_registry`, so a league is the same colour
everywhere and the legend can say whose league it is (nobody recognises
"Operators Football League"; they recognise "Ava's").

Replaces what used to be a chain of ten hard-coded `.apply()` calls per page
that keyed off `leagueList[0..9]` — positional, glob-order dependent, capped at
ten of the 42 league-seasons, and it tinted the whole row instead of the League
column.
"""
import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import streamlit as st

from ffapp import league_registry as registry


def text_on(hex_color):
    """Black or white, whichever stays readable on this background."""
    h = hex_color.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 'black' if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else 'white'


def color_league_cell(value):
    """Styler callback for a League column cell."""
    bg = registry.color(value)
    return f'background-color: {bg}; color: {text_on(bg)}'


def style_league_column(styler, column='League'):
    """Colour a League column, working on both old and new pandas.

    Element-wise styling is ``Styler.map`` from pandas 2.1 and ``applymap``
    before it (where ``map`` does not exist at all), and requirements.txt does
    not pin pandas - so pick whichever this version has.
    """
    elementwise = getattr(styler, 'map', None) or styler.applymap
    return elementwise(color_league_cell, subset=[column])


def league_color_key(leagues, columns=3, expanded=True):
    """Render the colour key: swatch, ESPN league name, and whose league it is."""
    leagues = [lg for lg in leagues if lg]
    if not leagues:
        return
    with st.expander('League colour key', expanded=expanded):
        cols = st.columns(columns)
        unconfirmed = False
        for i, lg in enumerate(leagues):
            entry = registry.get(lg)
            if not (entry or {}).get('confirmed', False):
                unconfirmed = True
                mark = ' *'
            else:
                mark = ''
            cols[i % columns].markdown(
                f"<span style='display:inline-block;width:0.8rem;height:0.8rem;"
                f"background:{registry.color(lg)};border-radius:2px;"
                f"margin-right:0.4rem;vertical-align:middle'></span>"
                f"**{lg}** — {registry.association(lg)}{mark}",
                unsafe_allow_html=True,
            )
        if unconfirmed:
            st.caption('\\* association not yet confirmed')
