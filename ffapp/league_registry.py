"""One place that knows what every league is, who it belongs to, and how to reach it.

ESPN league names are not how anyone actually refers to these leagues - nobody
says "Operators Football League", they say "Ava's league". Every league here
therefore carries an ``association``: whose league it is / how it's known.

Before this existed, league IDs and credential keys were copy-pasted into each
page, which is how five pages ended up pointing at the wrong ESPN league (see
SCOPE.md 2a). Pages, the pipeline and the LPI Master List legend should all read
from here rather than repeating the values.

Fields
------
espn_name    exact ESPN league name; also the ``data/leagues/<name> <year>.xlsx``
             prefix, so it is the join key for everything on disk
association  whose league it is, in the terms Louie actually uses
league_id    ESPN league id
s2 / swid    keys into ``credentials.CRED`` - a member's cookies are required to
             read a private league, so these stay paired with the league_id that
             is known to work, regardless of whose name the page carries
page         the file under ``pages/`` that shows it (None = data only, no page)
color        stable hex used for this league wherever leagues are colour-coded
confirmed    False where the association is inferred rather than stated; these
             are the ones worth double-checking
ids_by_year  optional {year: league_id} for a league that was rebuilt on ESPN as
             a new league. ``league_id`` stays the historical default; look up
             through ``league_id_for(name, year)`` rather than reading either
             field directly
display      optional friendlier name for the UI. ``espn_name`` is the join key
             for every file on disk, so it cannot be changed without a data
             migration - this lets the screen say something sensible anyway

A league that ESPN rebuilt from scratch
---------------------------------------
Matt's league became a *new* ESPN league for 2026: id 261375772 -> 29400230, name
"BP- Loudoun 2025" -> "Loudoun Fantasy League (LFL)". Both halves are the same
league to everyone who plays in it, so:

* ``ids_by_year`` maps 2026 to the new id; earlier years fall back to ``league_id``
* ``ALIASES`` folds the new ESPN name onto the existing ``espn_name``, so the 2026
  pull writes ``BP- Loudoun 2025 2026.xlsx`` and the year selector shows both
  seasons instead of splitting into two leagues
* ``display`` shows "Loudoun Fantasy League" rather than the storage key, whose
  embedded "2025" would otherwise render as "BP- Loudoun 2025 2026"
"""

LEAGUES = [
    # --- Louie's own leagues ---
    dict(espn_name="Pennoni Younglings", association="Louie - Pennoni coworkers",
         league_id=310334683, s2="louie_s2_pages", swid="louie_swid",
         page="1_🏈_Pennoni_Younglings.py", color="#1f77b4", confirmed=True),
    dict(espn_name="Family Fantasy", association="Louie - family",
         league_id=996930954, ids_by_year={2026: 1343668602},
         s2="louie_s2_pages", swid="louie_swid",
         page="1_👪_Family_League.py", color="#2ca02c", confirmed=True),
    dict(espn_name="EBC League", association="Louie - EBC friends",
         league_id=1118513122, s2="louie_s2_pages", swid="louie_swid",
         page="1_🎮_EBC_League.py", color="#9467bd", confirmed=True),

    # --- Prahlad's ---
    dict(espn_name="0755 Fantasy Football", association="Prahlad - Pennoni Transportation",
         league_id=1339704102, s2="prahlad_s2", swid="prahlad_swid",
         page="1_🛠️_Pennoni_Transportation.py", color="#8c564b", confirmed=True),
    dict(espn_name="Game of Yards!", association="Prahlad - friends",
         league_id=1781851, s2="prahlad_s2", swid="prahlad_swid",
         page="3_🧑‍🤝‍🧑_Prahlad_Friends_League.py", color="#e377c2", confirmed=True),
    dict(espn_name="Brown Munde", association="Prahlad - Brown Munde",
         league_id=367134149, s2="prahlad_s2", swid="prahlad_swid",
         page="3_🧑‍🤝‍🧑_Brown_Munde.py", color="#7f7f7f", confirmed=True),
    dict(espn_name="Turf On Grade 2.0", association="Prahlad - Turf On Grade",
         league_id=1242265374, s2="turf_s2", swid="prahlad_swid",
         page="4_🧑‍🤝‍🧑_Turf_On_Grade.py", color="#bcbd22", confirmed=True),

    # --- friends' leagues ---
    dict(espn_name="THE BEST OF THE BEST", association="Las league",
         league_id=1049459, s2="la_s2", swid="la_swid",
         page="5_🍝_Las_League.py", color="#d62728", confirmed=False),
    dict(espn_name="The Girl's Room 💞🏈", association="Hannah",
         league_id=1399036372, s2="hannah_s2", swid="hannah_swid",
         page="5_💅_The_Girls_Room.py", color="#ff9896", confirmed=True),
    # Louie: "I only know Operators Football League as Ava's league".
    # The s2/swid keys below are historical labels from the old inline code and
    # do NOT match the association - they are kept because this pairing is the
    # one known to read this league id successfully.
    dict(espn_name="Operators Football League", association="Ava",
         league_id=1259693145, s2="elle_s2", swid="elle_swid",
         page="5_👱🏻‍♀️_Avas_League.py", color="#17becf", confirmed=True),
    dict(espn_name="Philly Extra Special", association="Elle",
         league_id=417131856, s2="ava_s2", swid="ava_swid",
         page="5_🦝_Elles_League.py", color="#aec7e8", confirmed=False),
    dict(espn_name="OnP Fantasy", association="Dave - work (OnP)",
         league_id=1675186799, s2="dave_s2", swid="dave_swid",
         page="5_🍹_Dave_Redbull_League.py", color="#ffbb78", confirmed=True),
    dict(espn_name="The Mike Daisy Sports IQ League", association="Dave - friends",
         league_id=1924463077, s2="dave_s2", swid="dave_swid",
         page="5_🎮_Dave_Friend_League.py", color="#98df8a", confirmed=True),
    dict(espn_name="Ross' Fantasy League", association="Ayush (Dukes)",
         league_id=558148583, s2="ayush_s2", swid="ayush_swid",
         page="6_👑_Dukes_League.py", color="#c5b0d5", confirmed=False),
    # Rebuilt on ESPN for 2026 under a new id and name - see the module docstring.
    dict(espn_name="BP- Loudoun 2025", association="Matt",
         display="Loudoun Fantasy League",
         league_id=29400230, ids_by_year={2026: 29400230},
         s2="matt_s2", swid="matt_swid",
         page="5_👷🏻‍♀️_Matts-League.py", color="#c49c94", confirmed=True),

    # --- additional leagues (2026 new) ---
    dict(espn_name="The Goofy Goobers", association="Louie - new 2026",
         league_id=1616305229, s2="prahlad2_s2", swid="prahlad_swid",
         page="2_🤪_Goofy_Goobers.py", color="#ff7f0e", confirmed=True),
    dict(espn_name="Campers and Skiers and Prahlad", association="Prahlad - new 2026",
         league_id=47829282, s2="prahlad2_s2", swid="prahlad_swid",
         page="2_🏕️_Campers_and_Skiers.py", color="#1abc9c", confirmed=True),

    # --- data on disk but no page ---
    dict(espn_name="RRR On Premise ", association="Dave - older On Premise league",
         league_id=None, s2=None, swid=None,
         page=None, color="#f7b6d2", confirmed=False),
    dict(espn_name="Board Fantasy Football", association="Nolan - friends",
         league_id=496646254, s2="nolan_s2", swid="nolan_swid",
         page=None, color="#9b59b6", confirmed=True),
]

# Older names ESPN used for the same league. `all_matchups.csv` carries whatever
# the league was called when each week was pulled, so 2025 has 18 games filed
# under "Family League" and 87 under "Family Fantasy" - the same league. Without
# canonicalising, that franchise's lifetime history splits in two.
ALIASES = {
    'Family League': 'Family Fantasy',
    # 2026 Family League is a rebuild - folding the new name onto the old storage
    # key keeps both seasons in one league everywhere - one page, one year selector,
    # one lifetime history (like Matt's league).
    '2026 Family League': 'Family Fantasy',
    # Matt's league was rebuilt as a new ESPN league for 2026. Folding the new
    # name onto the old storage key keeps both seasons in one league everywhere -
    # one page, one year selector, one lifetime history.
    'Loudoun Fantasy League (LFL)': 'BP- Loudoun 2025',
    'Loudoun Fantasy League': 'BP- Loudoun 2025',
    # the pipelines label it without the stale year
    'BP- Loudoun': 'BP- Loudoun 2025',
}

BY_NAME = {lg["espn_name"]: lg for lg in LEAGUES}


def canonical(espn_name):
    """Fold a historical league name onto the name used on disk today."""
    return ALIASES.get(str(espn_name).strip(), str(espn_name).strip())

# Anything not in the registry still needs a colour when charted.
FALLBACK_COLOR = "#cccccc"


def get(espn_name):
    """Registry entry for an ESPN league name, or None."""
    return BY_NAME.get(espn_name)


def league_id_for(espn_name, year=None):
    """The ESPN league id to use for this league in this season.

    A league rebuilt on ESPN has a different id per era, so callers must ask for
    a year rather than reading ``league_id``. Falls back to the historical id when
    the year is unknown or not overridden.
    """
    lg = BY_NAME.get(canonical(espn_name))
    if not lg:
        return None
    overrides = lg.get('ids_by_year') or {}
    if year is not None and overrides:
        try:
            asked = int(year)
        except (TypeError, ValueError):
            asked = None
        if asked is not None:
            # "from this season onward", not "exactly this season". A league
            # rebuilt on ESPN keeps its new id for every later year too, so 2027
            # must not fall back to the retired one.
            applicable = [y for y in overrides if y <= asked]
            if applicable:
                return overrides[max(applicable)]
    return lg.get('league_id')


def credentials_for(espn_name, year=None):
    """(league_id, s2_key, swid_key) for a league-season, or None."""
    lg = BY_NAME.get(canonical(espn_name))
    if not lg:
        return None
    return league_id_for(espn_name, year), lg['s2'], lg['swid']


def display_name(espn_name):
    """Friendly name for the screen; falls back to the ESPN name.

    Kept separate from ``espn_name`` because that one is the join key for every
    file under ``data/`` - renaming it means migrating filenames and the League
    column of six aggregates, which is not worth it just to fix a label.
    """
    lg = BY_NAME.get(canonical(espn_name))
    return (lg.get('display') or lg['espn_name']) if lg else str(espn_name)


def seasons_with_other_id(espn_name):
    """{year: league_id} overrides for a league, empty for the normal case."""
    lg = BY_NAME.get(canonical(espn_name))
    return dict((lg.get('ids_by_year') or {})) if lg else {}


def association(espn_name, default="unknown"):
    lg = BY_NAME.get(espn_name)
    return lg["association"] if lg else default


def color(espn_name):
    lg = BY_NAME.get(espn_name)
    return lg["color"] if lg else FALLBACK_COLOR


def label(espn_name):
    """'Operators Football League (Ava)' - for legends and dropdowns.

    Uses the display name, so a league whose storage key carries a stale year
    ("BP- Loudoun 2025") reads as itself rather than as its filename.
    """
    lg = BY_NAME.get(canonical(espn_name))
    if not lg:
        return espn_name
    return f"{display_name(espn_name)} ({lg['association']})"


def split_league_year(name_with_year):
    """'EBC League 2022' -> ('EBC League', '2022').

    Splits on the trailing 4-digit year rather than assuming a word count, so
    names containing digits or emoji survive.
    """
    parts = name_with_year.rsplit(" ", 1)
    if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 4:
        return parts[0], parts[1]
    return name_with_year, ""
