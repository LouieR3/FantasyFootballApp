"""Read an ESPN draft while it is happening.

**`espn_api` cannot do this**, which is the whole reason this module exists. Its
`base_league._fetch_draft` opens with::

    if not data.get('draftDetail', {}).get('drafted'):
        return

and ESPN only flips `drafted` to True once the draft *completes*. So
`league.draft` is empty for the entire window you actually need it, and
`refresh_draft()` calls the same function. This talks to the `mDraftDetail` view
directly instead.

What the raw endpoint gives you, verified against real leagues:

* **The full pick order exists before anyone picks.** An undrafted 2026 league
  already returns every slot with `overallPickNumber`, `roundId`, `roundPickNumber`
  and `teamId`, with `playerId = -1` standing in for "not taken yet". So the snake
  order - including back-to-back turns at the wrap - is known up front.
* A pick landing just sets that slot's `playerId`. Taken vs available is therefore
  a single scan, with no event log to replay and nothing to miss.
* Polling is cheap: ~0.45s per call, so a few seconds between refreshes is fine.

Nothing here writes. It cannot make a pick for you.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import json

import requests

BASE = 'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl'

# ESPN's defaultPositionId. K and D/ST are included so a full board can be shown,
# even though ranking sheets usually omit them.
POSITIONS = {1: 'QB', 2: 'RB', 3: 'WR', 4: 'TE', 5: 'K', 16: 'D/ST'}

# draftRanksByRankType keys. PPR is the default because that is what most of
# these leagues use; STANDARD and SUPERFLEX are there for the ones that do not.
RANK_TYPES = ('PPR', 'STANDARD', 'SUPERFLEX', 'ELIMINATION')

NOT_PICKED = -1
TIMEOUT = 30


class DraftUnavailable(RuntimeError):
    """The league or its draft could not be read."""


def _get(league_id, year, view, s2, swid, filt=None, extra=None):
    params = {'view': view}
    params.update(extra or {})
    headers = {'x-fantasy-filter': json.dumps(filt)} if filt else {}
    url = f'{BASE}/seasons/{year}/segments/0/leagues/{league_id}'
    try:
        r = requests.get(url, cookies={'espn_s2': s2, 'SWID': swid},
                         params=params, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise DraftUnavailable(f'could not reach ESPN: {e}') from e
    if r.status_code == 401:
        raise DraftUnavailable(f'league {league_id} refused these credentials '
                               f'(espn_s2/SWID may have expired)')
    if r.status_code == 404:
        raise DraftUnavailable(f'league {league_id} has no {year} season')
    if r.status_code != 200:
        raise DraftUnavailable(f'ESPN returned HTTP {r.status_code}')
    return r.json()


# ---------------------------------------------------------------------------
# draft state
# ---------------------------------------------------------------------------

def draft_state(league_id, year, s2, swid):
    """Everything about where the draft currently stands.

    Returns a dict with:
      ``drafted`` / ``in_progress`` - ESPN's own flags
      ``slots``      - every pick slot in overall order
      ``taken``      - {player_id: slot} for picks already made
      ``on_the_clock`` - the next unfilled slot, or None if the draft is done
      ``rounds`` / ``teams`` - sizes, derived from the slots
    """
    body = _get(league_id, year, 'mDraftDetail', s2, swid)
    detail = body.get('draftDetail') or {}
    raw = detail.get('picks') or []

    slots = []
    for p in raw:
        pid = p.get('playerId')
        slots.append({
            'overall': p.get('overallPickNumber'),
            'round': p.get('roundId'),
            'round_pick': p.get('roundPickNumber'),
            'team_id': p.get('teamId'),
            'player_id': pid if (pid or NOT_PICKED) > 0 else None,
            'keeper': bool(p.get('keeper')),
            # autoDraftTypeId != 0 means ESPN picked for them
            'autodrafted': bool(p.get('autoDraftTypeId')),
        })
    slots.sort(key=lambda s: s['overall'] or 0)

    taken = {s['player_id']: s for s in slots if s['player_id']}
    pending = [s for s in slots if not s['player_id']]
    return {
        'drafted': bool(detail.get('drafted')),
        'in_progress': bool(detail.get('inProgress')),
        'slots': slots,
        'taken': taken,
        'pending': pending,
        'on_the_clock': pending[0] if pending else None,
        'picks_made': len(taken),
        'total_picks': len(slots),
        'rounds': max((s['round'] or 0 for s in slots), default=0),
        'teams': len({s['team_id'] for s in slots if s['team_id']}),
    }


def my_picks(state, team_id):
    """Overall pick numbers belonging to one team, in order."""
    return [s['overall'] for s in state['slots'] if s['team_id'] == team_id]


def picks_until(state, team_id):
    """How many picks until this team is up. 0 = on the clock, None = done.

    Counts the slots strictly before their next turn, so the answer is "how many
    other people pick first" - which is what decides whether a player survives.
    """
    clock = state['on_the_clock']
    if clock is None:
        return None
    upcoming = [s['overall'] for s in state['pending'] if s['team_id'] == team_id]
    if not upcoming:
        return None
    return max(0, upcoming[0] - clock['overall'])


def next_turns(state, team_id, n=3):
    """This team's next few overall pick numbers, and the gap before each."""
    clock = state['on_the_clock']
    if clock is None:
        return []
    base = clock['overall']
    out = []
    for s in state['pending']:
        if s['team_id'] == team_id:
            out.append({'overall': s['overall'], 'round': s['round'],
                        'picks_away': max(0, s['overall'] - base)})
            if len(out) >= n:
                break
    return out


def teams(league_id, year, s2, swid):
    """{team_id: name} so the board can show who took whom."""
    body = _get(league_id, year, 'mTeam', s2, swid)
    out = {}
    for t in body.get('teams') or []:
        name = (t.get('name')
                or ' '.join(filter(None, (t.get('location'), t.get('nickname'))))
                or f"Team {t.get('id')}")
        out[t.get('id')] = name.strip()
    return out


# ---------------------------------------------------------------------------
# player pool
# ---------------------------------------------------------------------------

def player_pool(league_id, year, s2, swid, limit=400, rank_type='PPR'):
    """The draftable player pool with ESPN's own rank and ADP.

    ``limit`` is how deep to go by ESPN draft rank. 400 comfortably covers a
    17-round 12-team draft (204 picks) plus everyone worth watching after.
    """
    if rank_type not in RANK_TYPES:
        rank_type = 'PPR'
    filt = {'players': {'limit': int(limit),
                        'sortDraftRanks': {'sortPriority': 1, 'sortAsc': True,
                                           'value': rank_type}}}
    body = _get(league_id, year, 'kona_player_info', s2, swid, filt)

    out = {}
    for entry in body.get('players') or []:
        p = entry.get('player') or {}
        pid = p.get('id')
        if pid is None:
            continue
        own = p.get('ownership') or {}
        ranks = p.get('draftRanksByRankType') or {}
        adp = own.get('averageDraftPosition')
        out[pid] = {
            'player_id': pid,
            'name': p.get('fullName') or '',
            'position': POSITIONS.get(p.get('defaultPositionId'), '?'),
            'pro_team_id': p.get('proTeamId'),
            'espn_rank': (ranks.get(rank_type) or {}).get('rank'),
            'adp': round(adp, 1) if isinstance(adp, (int, float)) and adp > 0 else None,
            'percent_owned': round((own.get('percentOwned') or 0), 1),
            'injured': bool(p.get('injured')),
            'injury_status': p.get('injuryStatus'),
        }
    return out


def credentials_for(league_name):
    """(league_id, s2, swid) for a league in the registry, or None."""
    from credentials import CRED
    from ffapp import league_registry as registry
    entry = registry.get(league_name)
    if not entry:
        return None
    try:
        return entry['league_id'], CRED[entry['s2']], CRED[entry['swid']]
    except KeyError:
        return None
