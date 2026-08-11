"""Join an external ranking sheet to ESPN's live draft board.

Takes a rankings CSV (FantasyPros ECR export, or a sheet built on one) plus the
live player pool from `live_draft.py`, and answers the draft-day question: of the
players still available, who is going later than they should?

Three things here are load-bearing.

**Name matching is the real work.** ESPN carries suffixes; ranking sheets strip
them. Measured against a real 200-player sheet, 11% of names differ purely in
punctuation or a suffix - `James Cook III` vs `James Cook`, `Kyle Pitts Sr.` vs
`Kyle Pitts`, `Travis Etienne Jr.`, `A.J. Brown`, `Amon-Ra St. Brown`. So matching
normalises both sides, then falls back to last-name-plus-position, and *reports*
whatever is left over. Silently dropping Ja'Marr Chase mid-draft is the worst
failure this could have, so unmatched players are surfaced, never swallowed.

**Value must be computed within position.** Comparing raw ranks across positions
puts kickers and defences at the top of every value list: ESPN ranks a D/ST near
400 while a ranking sheet puts it near 190, so the naive difference is +200 and
swamps every real edge. Position-relative comparison removes that entirely.

**ADP beats editorial rank for "value".** A sheet's rank is an opinion about who
is better; ADP is evidence about where players actually go. `VALUE` here is
therefore ECR-vs-ADP - who the room is letting slide - and ESPN's own rank is
carried alongside as a second opinion rather than the basis.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import re

import numpy as np
import pandas as pd

# Suffixes that appear on ESPN names and almost never on ranking sheets.
SUFFIXES = {'jr', 'sr', 'ii', 'iii', 'iv', 'v'}

# Column names accepted for each field, in preference order. Ranking sheets are
# hand-built and inconsistent, so this is matched case-insensitively.
COLUMN_ALIASES = {
    'name': ('name', 'player', 'player name', 'playername'),
    'position': ('pos', 'position'),
    'pro_team': ('team', 'tm', 'nfl team'),
    'ecr': ('fantasypros', 'ecr', 'fp', 'rank', 'overall rank', 'rk',
            'fantasypros rank', 'consensus'),
    'sheet_adp': ('adp', 'avg pick', 'average draft position'),
    'sheet_espn': ('espn', 'espn rank'),
    'bye': ('bye', 'bye week'),
    'tier': ('tier',),
    'round': ('round', 'rd'),
    'notes': ('landmine', 'notes', 'note'),
}

# D/ST show up under many spellings; normalise to the city/nickname token ESPN uses.
DST_WORDS = ('dst', 'd/st', 'defense', 'def')


def _clean(text):
    """Normalise a player name for matching.

    Lowercases, strips a trailing generational suffix, and handles the two kinds
    of punctuation differently on purpose:

    * periods and apostrophes are **deleted** - `A.J. Brown` -> `aj brown`,
      `Ja'Marr Chase` -> `jamarr chase`, matching sheets that drop them entirely
    * hyphens become **spaces** - `Amon-Ra St. Brown` -> `amon ra st brown`, so a
      sheet writing `Amon Ra` still matches. Deleting them instead yields
      `amonra`, which matches neither spelling.

    The suffix strip is what makes `James Cook III` and `James Cook` one player.
    """
    s = str(text or '').lower().strip()
    s = s.replace('&', ' and ')
    s = re.sub(r"[.'`’,]", '', s)          # A.J. -> aj, Ja'Marr -> jamarr
    s = re.sub(r'[-/]', ' ', s)            # Amon-Ra -> amon ra
    s = re.sub(r'\s+', ' ', s).strip()
    parts = [p for p in s.split(' ') if p]
    while len(parts) > 1 and parts[-1] in SUFFIXES:
        parts.pop()
    return ' '.join(parts)


def _tight(text):
    """`_clean` with all spaces removed - catches the opposite spelling choice.

    A sheet that writes `AmonRa StBrown` normalises to the same thing as ESPN's
    `Amon-Ra St. Brown` only once spacing is ignored too.
    """
    return _clean(text).replace(' ', '')


def _is_dst(name, position=None):
    low = str(name or '').lower()
    return (str(position or '').lower().replace('/', '') in ('dst', 'def')
            or any(w in low for w in DST_WORDS))


def _resolve_columns(df):
    """{field: actual column name} for whatever this sheet happens to call things."""
    lower = {str(c).strip().lower(): c for c in df.columns}
    found = {}
    for field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lower:
                found[field] = lower[alias]
                break
    return found


def load_rankings(source):
    """Read a rankings CSV into a tidy frame. `source` is a path or file object.

    Requires a name column and a rank column; everything else is optional and
    passed through when present.
    """
    df = pd.read_csv(source)
    # hand-built sheets usually carry an unnamed index column
    df = df.loc[:, ~df.columns.astype(str).str.match(r'^Unnamed')]
    cols = _resolve_columns(df)

    if 'name' not in cols:
        raise ValueError(
            f'No name column found. Looked for {COLUMN_ALIASES["name"]}; '
            f'the file has {list(df.columns)}')
    if 'ecr' not in cols:
        raise ValueError(
            f'No ranking column found. Looked for {COLUMN_ALIASES["ecr"]}; '
            f'the file has {list(df.columns)}')

    out = pd.DataFrame({
        'Player': df[cols['name']].astype(str).str.strip(),
        'ECR': pd.to_numeric(df[cols['ecr']], errors='coerce'),
    })
    for field, label in (('position', 'Pos'), ('pro_team', 'NFL'),
                         ('sheet_adp', 'Sheet ADP'), ('sheet_espn', 'Sheet ESPN'),
                         ('bye', 'Bye'), ('tier', 'Tier'), ('notes', 'Notes')):
        if field in cols:
            val = df[cols[field]]
            out[label] = (pd.to_numeric(val, errors='coerce')
                          if field in ('sheet_adp', 'sheet_espn', 'bye', 'tier')
                          else val.astype(str).str.strip())

    # A sparse Round column marks where each round begins in the sheet's own
    # recommended order - i.e. tier boundaries. Forward-fill turns it into a
    # per-player target round.
    if 'round' in cols:
        out['Target Round'] = pd.to_numeric(df[cols['round']],
                                            errors='coerce').ffill()

    out = out.dropna(subset=['ECR'])
    out['_key'] = out['Player'].map(_clean)
    return out.sort_values('ECR').reset_index(drop=True)


def match_to_espn(rankings, pool):
    """Attach ESPN player ids to a rankings frame.

    Returns ``(matched, unmatched_rankings, unmatched_espn)``.

    Three passes, each stricter about ambiguity than the last: exact on the
    normalised name, then spacing-insensitive, then last name + position. The
    fallbacks only fire when there is exactly one candidate, so they can never
    silently pick the wrong Josh Allen.
    """
    by_key, by_tight, by_lastpos = {}, {}, {}
    for pid, p in pool.items():
        key = _clean(p['name'])
        by_key.setdefault(key, []).append(pid)
        by_tight.setdefault(_tight(p['name']), []).append(pid)
        last = key.split(' ')[-1] if key else ''
        by_lastpos.setdefault((last, p['position']), []).append(pid)

    used, rows, unmatched = set(), [], []
    for r in rankings.to_dict('records'):
        key, pos = r['_key'], str(r.get('Pos') or '').upper()
        hit = None

        candidates = [p for p in by_key.get(key, []) if p not in used]
        if len(candidates) == 1:
            hit = candidates[0]
        elif len(candidates) > 1 and pos:
            same = [p for p in candidates if pool[p]['position'] == pos]
            hit = same[0] if len(same) == 1 else candidates[0]

        if hit is None and key:
            tight = [p for p in by_tight.get(key.replace(' ', ''), [])
                     if p not in used]
            if len(tight) == 1:
                hit = tight[0]

        if hit is None and key:
            last = key.split(' ')[-1]
            fallback = [p for p in by_lastpos.get((last, pos), []) if p not in used]
            if len(fallback) == 1:                 # unambiguous only
                hit = fallback[0]

        if hit is None:
            unmatched.append(r)
            continue
        used.add(hit)
        espn = pool[hit]
        rows.append({**{k: v for k, v in r.items() if k != '_key'},
                     'player_id': hit,
                     'ESPN Name': espn['name'],
                     'Pos': r.get('Pos') or espn['position'],
                     'ESPN Rank': espn['espn_rank'],
                     'ADP': espn['adp'],
                     'Owned %': espn['percent_owned'],
                     'Injured': espn['injured'],
                     'Injury': espn['injury_status']})

    matched = pd.DataFrame(rows)
    leftover = pd.DataFrame(unmatched).drop(columns=['_key'], errors='ignore')

    # Best players ESPN knows about that the sheet does not list. Kickers and
    # defences are dropped because ranking sheets deliberately omit them - that
    # is not a gap worth reporting. Capped by list length rather than by a rank
    # threshold so a thin sheet still surfaces what it is missing.
    espn_left = [
        {'player_id': pid, 'ESPN Name': p['name'], 'Pos': p['position'],
         'ESPN Rank': p['espn_rank'], 'ADP': p['adp']}
        for pid, p in pool.items()
        if pid not in used and p['position'] != 'K'
        and not _is_dst(p['name'], p['position'])
    ]
    espn_left.sort(key=lambda r: r['ESPN Rank'] or 10_000)
    return matched, leftover, pd.DataFrame(espn_left[:50])


def recent_picks(state, pool, team_names=None, n=12):
    """The last n picks made, newest first.

    Resolved from the ESPN pool rather than the matched board, because ranking
    sheets omit kickers and defences - and those still get drafted. Reading them
    off the board alone would make the draft log skip picks.

    Reads ``state['taken']``, the same source ``board()`` uses, rather than
    re-scanning ``slots``. Two functions deriving "what has been picked" from
    different fields can disagree, and a draft log that contradicts the board is
    worse than no log.
    """
    # taken is keyed by player id, so take it from the key rather than expecting
    # the slot to repeat it - one less field a hand-built state has to get right
    made = sorted(state['taken'].items(),
                  key=lambda kv: kv[1].get('overall') or 0, reverse=True)[:n]
    names = team_names or {}
    rows = []
    for pid, s in made:
        p = pool.get(pid) or {}
        rows.append({
            'Pick': s.get('overall'), 'Round': s.get('round'),
            'Team': names.get(s.get('team_id'), f"Team {s.get('team_id')}"),
            'Player': p.get('name') or f'(player {pid})',
            'Pos': p.get('position', '?'),
            'ADP': p.get('adp'),
            'Auto': bool(s.get('autodrafted')),
        })
    return pd.DataFrame(rows)


def add_value(matched):
    """Add the value columns, all computed *within position*.

    ``VALUE`` = ADP minus ECR. Positive means the room is letting them slide
    later than the consensus rates them - the pick you want. Negative means they
    are going earlier than they are worth.

    ``Pos VALUE`` is the same idea on position rank, which is the honest
    cross-position comparison: it asks "how far past their positional value is
    this player falling", so a QB and a TE can be compared without kickers and
    defences swamping the list.
    """
    if matched.empty:
        return matched
    df = matched.copy()

    # ECR is the only column that must exist. ADP and ESPN Rank are optional:
    # a sheet with no ADP still gives a usable ranked board, and plenty of sheets
    # carry no ESPN column at all. Requiring them outright meant a perfectly
    # valid two-column sheet raised a KeyError instead of degrading.
    df['ECR'] = pd.to_numeric(df['ECR'], errors='coerce')
    for col in ('ADP', 'ESPN Rank'):
        df[col] = (pd.to_numeric(df[col], errors='coerce')
                   if col in df.columns else np.nan)
    if 'Pos' not in df.columns:
        df['Pos'] = '?'

    # position rank on each scale, so the two are comparable within a position
    df['Pos ECR'] = df.groupby('Pos')['ECR'].rank(method='min')
    df['Pos ADP'] = df.groupby('Pos')['ADP'].rank(method='min')
    df['Pos ESPN'] = df.groupby('Pos')['ESPN Rank'].rank(method='min')

    df['VALUE'] = (df['ADP'] - df['ECR']).round(1)
    df['Pos VALUE'] = (df['Pos ADP'] - df['Pos ECR']).round(1)
    # ESPN as a second opinion, not the basis - see the module docstring
    df['ESPN vs ECR'] = (df['Pos ESPN'] - df['Pos ECR']).round(1)
    return df


def board(matched, state, pool=None):
    """The still-available players, with who took the rest.

    ``state`` comes from ``live_draft.draft_state``. Anything whose ESPN id
    appears in ``state['taken']`` is off the board.
    """
    if matched.empty:
        return matched, matched
    taken_ids = set(state['taken'])
    is_taken = matched['player_id'].isin(taken_ids)
    available = matched[~is_taken].copy()
    gone = matched[is_taken].copy()
    if not gone.empty:
        gone['Pick'] = [state['taken'][p]['overall'] for p in gone['player_id']]
        gone['Round'] = [state['taken'][p]['round'] for p in gone['player_id']]
        gone['By Team'] = [state['taken'][p]['team_id'] for p in gone['player_id']]
        gone = gone.sort_values('Pick')
    return available.sort_values('ECR').reset_index(drop=True), gone


def best_available(available, n=20, position=None, by='ECR'):
    """Top of the board, optionally filtered to one position."""
    if available.empty:
        return available
    df = available if not position else available[available['Pos'] == position]
    ascending = by in ('ECR', 'ADP', 'ESPN Rank', 'Pos ECR')
    return df.sort_values(by, ascending=ascending).head(n)


def value_picks(available, n=20, min_value=0.0):
    """Players falling furthest past their positional value."""
    if available.empty or 'Pos VALUE' not in available.columns:
        return available
    df = available[available['Pos VALUE'].notna() & (available['Pos VALUE'] > min_value)]
    return df.sort_values('Pos VALUE', ascending=False).head(n)


def reaches(available, n=15):
    """Players the room is taking *earlier* than they are worth - fade these."""
    if available.empty or 'Pos VALUE' not in available.columns:
        return available
    df = available[available['Pos VALUE'].notna()]
    return df.sort_values('Pos VALUE').head(n)


def survival(available, picks_away, n=25):
    """Who is likely to still be there at your next turn.

    Uses ADP as the estimate of where a player goes. Crude on purpose: ADP is a
    league-wide average and your leaguemates are not average, so this is a
    prior, not a prediction. Shown as a gap in picks rather than a probability
    so it does not imply more precision than it has.
    """
    if available.empty or picks_away is None:
        return available
    df = available[available['ADP'].notna()].copy()
    if df.empty:
        return df
    # ADP is an overall pick number; compare it to where your turn lands
    df['ADP Gap'] = (df['ADP'] - picks_away).round(1)
    df['Likely There'] = df['ADP Gap'] > 0
    return df.sort_values('ECR').head(n)


# ===========================================================================
# Roster construction: what should I actually take?
# ===========================================================================
# A conventional ESPN lineup, used only when the league's real settings are not
# available. Surfaced in the UI rather than assumed silently.
DEFAULT_SLOTS = [(('QB',), 1), (('RB',), 2), (('WR',), 2), (('TE',), 1),
                 (('RB', 'WR', 'TE'), 1), (('D/ST',), 1), (('K',), 1)]

# Default positional lean - the "RB > WR > TE/QB" path, made explicit and tunable
# rather than baked into the scoring. The gaps are deliberately wide enough to
# actually bite: an earlier version used 1.15/1.10, a 4% edge that vanished next
# to ECR differences and produced WR-WR-WR starts with no back until round 6.
DEFAULT_PRIORITY = {'RB': 1.30, 'WR': 1.10, 'TE': 0.95, 'QB': 0.85,
                    'D/ST': 0.55, 'K': 0.45}

# Starters outweigh bench depth, but not infinitely - once the lineup is set the
# next good back is still worth taking.
NEED_WEIGHT_STARTER = 1.0
NEED_WEIGHT_BENCH = 0.45
# Extra urgency per *additional* unfilled starter at a position. Needing two
# backs is more pressing than needing one receiver, and without this they scored
# identically - which is how the RB hole stayed open while the pool drained.
NEED_WEIGHT_PER_EXTRA = 0.30

# Bench depth worth advising *beyond* a position's startable slots. The flat
# bench weight cannot tell that a third quarterback is worth less than a second
# back, so a simulated draft happily took three of them - and with a hard RB
# preference it took nine backs and no quarterback at all, a roster that cannot
# field a lineup. Caps are derived from the league's real slots (see
# `position_caps`) so they adapt to superflex, 3-WR, TE-premium and so on.
BENCH_ALLOWANCE = {'RB': 3, 'WR': 3, 'TE': 1, 'QB': 1, 'K': 0, 'D/ST': 0}
DEFAULT_BENCH_ALLOWANCE = 1


def position_caps(slot_groups=None):
    """{position: most worth drafting} = startable slots + bench allowance.

    Flex slots count toward every position they accept, so a 1-flex league lets
    you carry an extra back *or* receiver without inflating both caps beyond what
    the bench can hold.
    """
    groups = list(slot_groups or DEFAULT_SLOTS)
    dedicated, flexible = {}, {}
    for allowed, n in groups:
        for pos in allowed:
            if len(allowed) == 1:
                dedicated[pos] = dedicated.get(pos, 0) + n
            else:
                flexible[pos] = flexible.get(pos, 0) + n
    positions = set(dedicated) | set(flexible) | set(BENCH_ALLOWANCE)
    return {pos: (dedicated.get(pos, 0) + flexible.get(pos, 0)
                  + BENCH_ALLOWANCE.get(pos, DEFAULT_BENCH_ALLOWANCE))
            for pos in positions}


def roster_counts(my_players, matched=None):
    """{position: count} for the players you have already taken.

    ``my_players`` is a list of positions, or of rows carrying a 'Pos'.
    """
    counts = {}
    for item in my_players or []:
        pos = item if isinstance(item, str) else (item or {}).get('Pos')
        if pos:
            counts[pos] = counts.get(pos, 0) + 1
    return counts


def remaining_needs(counts, slot_groups=None):
    """Starting slots you have not filled yet, per position.

    Flex-aware, and greedy in the right order: dedicated slots are filled before
    flex ones, so a third WR counts toward the flex rather than pretending your
    WR2 is still open. ``slot_groups`` is what
    ``league_settings.parse_slot_groups`` returns.

    Returns ``(needs, flex_open)`` - ``needs`` is per-position starters still
    required, ``flex_open`` is how many flex spots remain after that.
    """
    groups = list(slot_groups or DEFAULT_SLOTS)
    # single-position slots first; parse_slot_groups already sorts this way but
    # a hand-built list might not
    groups.sort(key=lambda g: (len(g[0]), g[0]))

    have = dict(counts or {})
    needs = {}
    flex_open = 0
    for allowed, n in groups:
        if len(allowed) == 1:
            pos = allowed[0]
            used = min(have.get(pos, 0), n)
            have[pos] = have.get(pos, 0) - used
            if n - used > 0:
                needs[pos] = needs.get(pos, 0) + (n - used)
        else:
            # flex: soak up whatever surplus exists across the allowed positions
            for _ in range(n):
                donor = max(allowed, key=lambda p: have.get(p, 0))
                if have.get(donor, 0) > 0:
                    have[donor] -= 1
                else:
                    flex_open += 1
                    for p in allowed:
                        needs.setdefault(p, needs.get(p, 0))
    return needs, flex_open


def positional_dropoff(available, next_pick=None, survival_buffer=0.0):
    """Per position: how much worse your best option gets if you wait a turn.

    This is the honest version of "take RB before WR". For each position it
    compares the best ECR available now against the best ECR likely to still be
    there at your next turn, using ADP as the survival estimate. A big gap means
    waiting is expensive; a small gap means the position can wait.

    Grounding it in measured scarcity rather than a fixed order means it adapts:
    if the room has ignored TE, the TE dropoff is small and it will tell you so.

    ADP is a league-wide average and your leaguemates are not average, so treat
    this as a prior. ``survival_buffer`` shifts the threshold if your league
    reaches (positive) or lets players slide (negative).
    """
    if available.empty:
        return pd.DataFrame()
    rows = []
    for pos, g in available.groupby('Pos'):
        ecr = g['ECR'].dropna()
        if ecr.empty:
            continue
        best_now = float(ecr.min())
        best_later = np.nan
        if next_pick is not None:
            threshold = next_pick + survival_buffer
            later = g[g['ADP'].notna() & (g['ADP'] > threshold)]['ECR'].dropna()
            if len(later):
                best_later = float(later.min())
        rows.append({
            'Pos': pos,
            'Available': len(g),
            'Best ECR Now': best_now,
            'Best ECR Later': best_later,
            'Dropoff': (round(best_later - best_now, 1)
                        if pd.notna(best_later) else np.nan),
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values('Dropoff', ascending=False,
                           na_position='last').reset_index(drop=True)


def position_scores(available, my_counts, slot_groups=None, next_pick=None,
                    priority=None, survival_buffer=0.0, lean=1.0):
    """{position: weight} - how much you want *that position* on this pick.

    Multiplies three things, all reported so it is never a black box:

    * **Dropoff** - what waiting a turn costs at that position (the real signal)
    * **Need** - whether it still fills a starting slot
    * **Priority** - your positional lean, adjustable, default RB/WR-early

    This answers "which position", deliberately separate from "which player" -
    conflating the two is what made an earlier version recommend a round-11 back
    over a round-5 one.

    ``lean`` scales how hard the positional preference bites, as an exponent on
    the priority weights: ``0`` ignores position entirely and drafts pure ECR,
    ``1`` is the default lean, ``3`` follows the path almost regardless of ECR.
    It exists because a modest lean *should* lose to a big ECR gap - at a middle
    draft slot the default correctly takes a receiver ranked 14 spots higher over
    filling an empty backfield - and whether that is right is a matter of taste,
    not of arithmetic. The knob makes the taste explicit.
    """
    priority = dict(priority or DEFAULT_PRIORITY)
    if lean != 1.0:
        priority = {p: max(w, 1e-6) ** float(lean) for p, w in priority.items()}
    needs, flex_open = remaining_needs(my_counts, slot_groups)
    drop = positional_dropoff(available, next_pick, survival_buffer)
    drop_by_pos = dict(zip(drop['Pos'], drop['Dropoff'])) if len(drop) else {}
    vals = [v for v in drop_by_pos.values() if pd.notna(v)]
    span = (max(vals) - min(vals)) if len(vals) > 1 else 0.0

    have = dict(my_counts or {})
    caps = position_caps(slot_groups)
    out = {}
    for pos in (available['Pos'].dropna().unique() if not available.empty else []):
        cap = caps.get(pos)
        if cap is not None and have.get(pos, 0) >= cap:
            out[pos] = {'score': 0.0, 'need': 0, 'dropoff': drop_by_pos.get(pos),
                        'capped': True}
            continue
        need = needs.get(pos, 0)
        starter = need > 0 or (flex_open > 0 and pos in ('RB', 'WR', 'TE'))
        if need > 0:
            # scaled by how many are still open, so two holes beat one
            need_w = NEED_WEIGHT_STARTER + NEED_WEIGHT_PER_EXTRA * (need - 1)
        elif starter:
            need_w = NEED_WEIGHT_STARTER
        else:
            need_w = NEED_WEIGHT_BENCH
        d = drop_by_pos.get(pos)
        drop_w = 1.0 if (d is None or pd.isna(d) or span <= 0) else \
            1.0 + (d - min(vals)) / span
        out[pos] = {'score': round(drop_w * need_w * priority.get(pos, 1.0), 3),
                    'need': need if need else ('FLEX' if starter else 0),
                    'dropoff': d, 'capped': False}
    return out


def recommend(available, my_counts, slot_groups=None, next_pick=None,
              priority=None, n=15, survival_buffer=0.0, lean=1.0):
    """Ranked suggestions for the pick you are on, with the reasoning shown.

    Two separate questions, combined at the end:

    1. **Which position?** ``position_scores`` above - need, dropoff, priority.
    2. **Which player at it?** The best one by ECR. Nothing else.

    They combine as ``Adjusted ECR = ECR / position score``, lower being better.
    A position you urgently need has its players' effective rank improved, so a
    clearly better player at a less urgent position can still outrank a worse
    player at the urgent one - which is what you actually want on the clock.

    An earlier version instead used value-over-ADP as a tie-break inside the
    score. Because deep players fall furthest past their ADP, that inverted
    player quality outright: at pick 24 it offered Tyrone Tracy (ECR 131) ahead
    of D'Andre Swift (ECR 60). Value-over-ADP is a "who is a bargain later"
    signal and belongs on the Value tab, not on the pick you are making now.
    """
    if available.empty:
        return available
    scores = position_scores(available, my_counts, slot_groups, next_pick,
                             priority, survival_buffer, lean)
    rows = []
    for r in available.to_dict('records'):
        info = scores.get(r.get('Pos')) or {'score': 1.0, 'need': 0, 'dropoff': None}
        ecr = r.get('ECR')
        adj = (float(ecr) / info['score']) if (ecr and info['score']) else np.nan
        rows.append({**r, 'Need': info['need'], 'Dropoff': info['dropoff'],
                     'Pos Score': info['score'], 'Adjusted ECR': round(adj, 1)})
    out = pd.DataFrame(rows)
    return (out.sort_values(['Adjusted ECR', 'ECR'], na_position='last')
            .head(n).reset_index(drop=True))


def draft_plan(available, my_upcoming, my_counts, slot_groups=None,
               priority=None, survival_buffer=0.0, lean=1.0):
    """A pick-by-pick sketch of the rest of your draft.

    Walks your remaining turns in order. At each one it takes the position the
    recommender favours, assumes you take the best survivor there, and carries
    that into the next turn's needs - so the plan reflects a roster being built
    rather than the same advice repeated.

    Explicitly a projection, not a prediction: it assumes every player goes at
    his ADP and that nobody reaches. Its value is showing *which positions* the
    board pushes you toward and where the squeeze lands, not the specific names.
    """
    if available.empty or not my_upcoming:
        return pd.DataFrame()

    pool = available.copy()
    counts = dict(my_counts or {})
    rows = []
    for turn in my_upcoming:
        overall = turn['overall'] if isinstance(turn, dict) else turn
        rnd = turn.get('round') if isinstance(turn, dict) else None
        # who plausibly survives to this pick
        survivors = pool[pool['ADP'].isna() | (pool['ADP'] > overall + survival_buffer)]
        if survivors.empty:
            survivors = pool
        recs = recommend(survivors, counts, slot_groups, next_pick=overall,
                         priority=priority, n=1,
                         survival_buffer=survival_buffer, lean=lean)
        if recs.empty:
            break
        pick = recs.iloc[0]
        needs, flex_open = remaining_needs(counts, slot_groups)
        rows.append({
            'Pick': overall, 'Round': rnd,
            'Target Pos': pick['Pos'],
            'Likely Best': pick.get('ESPN Name') or pick.get('Player'),
            'ECR': pick.get('ECR'),
            'ADP': pick.get('ADP'),
            'Dropoff': pick.get('Dropoff'),
            'Still Need': ', '.join(f'{p}x{c}' for p, c in sorted(needs.items())
                                    if c) or ('FLEX' if flex_open else 'starters set'),
        })
        counts[pick['Pos']] = counts.get(pick['Pos'], 0) + 1
        pool = pool[pool['player_id'] != pick.get('player_id')] \
            if 'player_id' in pool.columns else pool.drop(index=pick.name, errors='ignore')
    return pd.DataFrame(rows)


def my_drafted(state, team_id, matched):
    """The rows of your board you have already drafted, in pick order."""
    if matched.empty:
        return matched
    mine = {pid: s for pid, s in state['taken'].items()
            if s.get('team_id') == team_id}
    got = matched[matched['player_id'].isin(mine)].copy()
    if got.empty:
        return got
    got['Pick'] = [mine[p]['overall'] for p in got['player_id']]
    got['Round'] = [mine[p].get('round') for p in got['player_id']]
    return got.sort_values('Pick').reset_index(drop=True)


def position_scarcity(available, tiers=(12, 24, 36)):
    """How many of each position remain inside the next few tiers of ECR.

    Answers "if I skip TE now, what is left" better than a flat count does.
    """
    if available.empty:
        return pd.DataFrame()
    rows = []
    for pos, g in available.groupby('Pos'):
        row = {'Pos': pos, 'Available': len(g)}
        ecr = g['ECR'].dropna()
        for t in tiers:
            row[f'Top {t}'] = int((ecr <= ecr.min() + t).sum()) if len(ecr) else 0
        row['Best ECR'] = float(ecr.min()) if len(ecr) else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values('Best ECR').reset_index(drop=True)
