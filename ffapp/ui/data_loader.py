"""Cached data access for the Streamlit app.

Streamlit re-runs a page's whole script on every widget interaction, so any
uncached read happens again each time you touch the year dropdown. Before
this module a single league page did 20 separate ``pd.read_excel`` calls
(re-parsing the same workbook 20 times - the Schedule Grid sheet alone was
read 10 times) plus one live ESPN ``League`` construction per season, and paid
all of it again on every interaction.

Everything here is cached:

* ``load_sheet`` / ``load_workbook`` - the workbook is parsed once per file
  and every sheet request is served from that one parse. Measured: ~450 ms of
  Excel reads per render becomes ~0 ms on repeat renders.
* ``load_csv`` - same idea for the draft/aggregate CSVs.
* ``get_league`` - ESPN ``League`` objects are cached (network round trips are
  by far the most expensive thing a page does).
* ``load_owner_df`` - the team/owner table derived from a League.

Cache keys include the file's modification time, so editing a data file
locally invalidates the cache without a restart. Credential arguments are
prefixed with an underscore, which tells Streamlit not to hash them - they
never become part of a cache key.

Importable outside Streamlit: if streamlit isn't available (pipeline scripts,
plain python), the decorators degrade to a plain in-process memo so the same
functions still work.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import functools
import io
import os

import pandas as pd

from ffapp.metrics.owner_overrides import resolve_owner
from paths import LEAGUES_DIR

try:
    import streamlit as st
    _cache_data = functools.partial(st.cache_data, show_spinner=False)
    _cache_resource = functools.partial(st.cache_resource, show_spinner=False)
except Exception:  # running outside Streamlit - fall back to a simple memo
    def _cache_data(**_kwargs):
        def deco(fn):
            return functools.lru_cache(maxsize=None)(fn)
        return deco
    _cache_resource = _cache_data


def _file_key(path):
    """Modification time, so edits invalidate the cache. 0 if missing."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


@_cache_resource()
def _workbook(path, mtime):
    """The opened workbook. Held so individual sheets can be parsed on demand.

    Deliberately NOT a full ``read_excel(sheet_name=None)``: pages that pull one
    sheet from all 42 league files (LPI Master List, Biggest Upsets) would
    otherwise parse ~11 sheets per file to use one. Measured 2.6x faster on
    that pattern and identical for a league page. ~20 MB for all 42 workbooks.

    The bytes are read into memory first so no OS file handle stays open - a
    cached handle would stop the pipeline scripts from rewriting these same
    xlsx files on Windows.
    """
    with open(path, "rb") as fh:
        return pd.ExcelFile(io.BytesIO(fh.read()))


def sheet_names(path):
    """Sheets present in the workbook (no sheet parsing)."""
    return list(_workbook(path, _file_key(path)).sheet_names)


@_cache_data()
def _parse_sheet(path, sheet, mtime):
    return _workbook(path, mtime).parse(sheet)


def load_sheet(path, sheet):
    """One sheet as a DataFrame. Raises KeyError if the sheet isn't present.

    Returns a copy, so callers can mutate freely (the page code renames
    columns, shifts the index and drops columns in place).
    """
    if sheet not in sheet_names(path):
        raise KeyError(f"Worksheet named '{sheet}' not found in {path}")
    return _parse_sheet(path, sheet, _file_key(path)).copy()


def load_all_sheets(path):
    """Every sheet of a workbook as {name: DataFrame} (cached, copies)."""
    return {s: load_sheet(path, s) for s in sheet_names(path)}


@_cache_data()
def _read_csv(path, mtime, **kwargs):
    return pd.read_csv(path, **kwargs)


def load_csv(path, **kwargs):
    """A CSV as a DataFrame (cached, returns a copy)."""
    return _read_csv(path, _file_key(path), **kwargs).copy()


@_cache_data()
def _years_for(league_name, dir_mtime):
    import re
    pattern = re.compile(r'^' + re.escape(league_name) + r' (\d{4})\.xlsx$')
    years = []
    try:
        entries = os.listdir(LEAGUES_DIR)
    except OSError:
        return []
    for name in entries:
        m = pattern.match(name)
        if m:
            years.append(m.group(1))
    return sorted(years)


def available_years(league_name):
    """Seasons this league actually has data for, oldest first.

    Pages used to hard-code a year list, which drifted out of sync with the
    files: six leagues advertised four seasons while only 2025 existed, so
    picking any other year broke the page (the workaround was to comment the
    selector out and pin the year). Deriving it means new seasons appear on
    their own and only real options are offered.
    """
    return _years_for(league_name, _file_key(LEAGUES_DIR))


@_cache_resource()
def get_league(league_id, year, _espn_s2=None, _swid=None):
    """A cached ESPN League. Credentials are excluded from the cache key.

    espn_api is imported here rather than at module scope so this module stays
    importable (and the file loaders usable) without it.
    """
    from espn_api.football import League
    return League(league_id=league_id, year=year, espn_s2=_espn_s2, swid=_swid)


@_cache_data()
def load_owner_df(league_id, year, _espn_s2=None, _swid=None):
    """Display Name / ID / Team Name per team, with co-owners resolved."""
    league = get_league(league_id, year, _espn_s2, _swid)
    return pd.DataFrame([
        {
            "Display Name": f"{o.get('firstName', '')} {o.get('lastName', '')}".strip(),
            "ID": o.get('id'),
            "Team Name": team.team_name,
        }
        for team, o in ((t, resolve_owner(league, t)) for t in league.teams)
    ])
