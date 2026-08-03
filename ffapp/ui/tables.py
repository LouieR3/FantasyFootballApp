"""Shared table display: sane decimals and heights that don't scroll.

Two problems this solves.

**Decimals.** pandas' ``styler.format.precision`` defaults to **6**, so any
styled table renders 1954.3 as ``1954.300000``. The fix is a Styler format, not
casting to string - strings would break the colour gradients and sorting.

**Heights.** Streamlit sizes a dataframe to a default ~400px and scrolls the
rest, which is wrong for league tables that are always one row per team. A table
of n rows needs ``35px`` per row plus a ``35px`` header, so ``table_height``
returns exactly that and nothing scrolls. This generalises the old inline
``460 + (len(names) - 12) * 40`` (which happened to be right for 12 teams) to any
league size - 8, 10, 12, 14 or otherwise.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import pandas as pd
import streamlit as st

ROW_PX = 35        # Streamlit's default data row height
HEADER_PX = 35     # the column header row
PAD_PX = 3         # borders, so the last row isn't clipped into a scrollbar
DEFAULT_PRECISION = 1


def apply_display_defaults(precision=DEFAULT_PRECISION):
    """Set the pandas Styler float precision for this session.

    Explicit ``.format()`` calls still win, so a table that wants different
    decimals can just say so.
    """
    pd.set_option('styler.format.precision', precision)


def table_height(n_rows, max_rows=None):
    """Pixel height that shows n_rows with no scrolling.

    Pass ``max_rows`` for long tables (every pick in a draft, say) to cap the
    height and allow scrolling past that point.
    """
    rows = int(n_rows)
    if max_rows is not None:
        rows = min(rows, int(max_rows))
    return HEADER_PX + ROW_PX * max(rows, 1) + PAD_PX


def show_table(data, precision=DEFAULT_PRECISION, formats=None, max_rows=None,
               hide_index=True, use_container_width=True, **kwargs):
    """st.dataframe with tidy decimals and a no-scroll height.

    Accepts a DataFrame or an already-styled Styler, so gradients survive.
    ``formats`` is an optional per-column override, e.g. ``{'LPI': '{:.0f}'}``.
    """
    styler = data if hasattr(data, 'data') else data.style
    frame = styler.data

    if precision is not None:
        # general precision first so per-column overrides below take priority
        styler = styler.format(precision=precision, na_rep='—')
    if formats:
        styler = styler.format(formats)

    st.dataframe(styler,
                 height=table_height(len(frame), max_rows),
                 hide_index=hide_index,
                 use_container_width=use_container_width,
                 **kwargs)
