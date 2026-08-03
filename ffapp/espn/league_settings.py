"""Per-league lineup settings, captured from ESPN and cached on disk.

Analysis that asks "what was the best lineup possible" needs to know what a legal
lineup actually is, and that differs per league - one flex or two, superflex or
not, 2 WR or 3. ESPN exposes it as ``league.settings.roster``, e.g.

    {'QB': 1, 'RB': 2, 'WR': 2, 'TE': 1, 'RB/WR/TE': 1,
     'D/ST': 1, 'K': 1, 'BE': 7}

Bench ('BE') and injured reserve ('IR') are not lineup slots. Anything containing
'/' is a flex that accepts several positions.

Stored in ``data/league_settings.json`` keyed ``"<league>|<year>"`` so the app can
read real settings without an ESPN round trip, and so historical seasons keep the
settings they were actually played under.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import json
import os

from paths import DATA_DIR

SETTINGS_PATH = os.path.join(DATA_DIR, 'league_settings.json')

NON_LINEUP = {'BE', 'IR', 'BENCH', 'RES'}
# Positions whose own name contains a slash. Without this, 'D/ST' gets treated as
# a flex accepting "D" or "ST" - neither of which is a real position - so the
# defence slot can never be filled and every lineup silently loses a starter.
SINGLE_POSITIONS_WITH_SLASH = {'D/ST'}
# Positions that may appear inside a flex slot name.
KNOWN_POSITIONS = {'QB', 'RB', 'WR', 'TE', 'K', 'D/ST', 'DST', 'DEF', 'P'}
# ESPN writes flex slots as slash-joined position lists; a few have proper names.
FLEX_ALIASES = {
    'OP': ('QB', 'RB', 'WR', 'TE'),        # superflex / offensive player
    'FLEX': ('RB', 'WR', 'TE'),
    'RB/WR': ('RB', 'WR'),
    'WR/TE': ('WR', 'TE'),
    'RB/WR/TE': ('RB', 'WR', 'TE'),
    'QB/RB/WR/TE': ('QB', 'RB', 'WR', 'TE'),
}


def _load_all():
    if not os.path.exists(SETTINGS_PATH):
        return {}
    try:
        with open(SETTINGS_PATH, encoding='utf-8') as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {}


def key(league_name, year):
    return f"{league_name}|{year}"


def save_settings(league_name, year, settings):
    """Record one league-season's settings. Merges into the existing file."""
    roster = dict(getattr(settings, 'roster', {}) or {})
    payload = {
        'roster': roster,
        'reg_season_count': getattr(settings, 'reg_season_count', None),
        'playoff_team_count': getattr(settings, 'playoff_team_count', None),
        'team_count': getattr(settings, 'team_count', None),
    }
    data = _load_all()
    data[key(league_name, year)] = payload
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2, sort_keys=True, ensure_ascii=False)
    return payload


def get_settings(league_name, year):
    """One league-season's stored settings, or None if never captured."""
    return _load_all().get(key(league_name, year))


def parse_slot_groups(roster):
    """ESPN roster dict -> [(allowed_positions_tuple, count), ...] lineup slots.

    Bench/IR dropped. Flex slots expand to the positions they accept, so a
    superflex league is handled without special-casing.
    """
    groups = []
    for slot, count in (roster or {}).items():
        name = str(slot).strip()
        if not count or name.upper() in NON_LINEUP:
            continue
        if name.upper() in SINGLE_POSITIONS_WITH_SLASH:
            allowed = (name,)                      # 'D/ST' is one position
        elif name.upper() in FLEX_ALIASES:
            allowed = FLEX_ALIASES[name.upper()]
        elif '/' in name:
            parts = tuple(p.strip() for p in name.split('/') if p.strip())
            # only a genuine flex if every part is a position we recognise;
            # otherwise assume the slash belongs to the position's own name
            allowed = parts if all(p.upper() in KNOWN_POSITIONS for p in parts) else (name,)
        else:
            allowed = (name,)
        groups.append((allowed, int(count)))
    # single-position slots first: keeps the DP's state ordering stable and puts
    # the constrained slots before the permissive flex ones
    groups.sort(key=lambda g: (len(g[0]), g[0]))
    return groups


def describe(groups):
    """'1×QB, 2×RB, 2×WR, 1×TE, 1×RB/WR/TE, 1×D/ST, 1×K' for display."""
    return ', '.join(f"{n}×{'/'.join(pos)}" for pos, n in groups)
