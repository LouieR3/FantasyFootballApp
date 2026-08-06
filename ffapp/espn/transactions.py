"""Weekly roster snapshots and the transaction log behind them.

Two sources, deliberately layered, because they have very different lifespans.

**Weekly roster snapshots** (``league.box_scores(week=w)``) are the substrate.
Each call returns every team's full roster for that week - bench included - with
the lineup slot and the points scored. Diffing consecutive weeks yields ownership
intervals, and therefore adds, drops and trades, without replaying an event log.
Verified working for every season back to 2019 despite the library docstring
warning it is current-season only.

**The activity feed** (``league.recent_activity()``) is the labelling layer. It
gives the exact transaction type and the FAAB bid, but ESPN only serves it for
the *current* season: every past year returns HTTP 404 ("This Communication Group
does not exist") on both the ``/seasons/{year}/`` and ``/leagueHistory/``
endpoints. So it enriches the current season and is simply absent for backfill.

What that costs on a backfilled season:

* adds and drops reconstruct cleanly
* a trade is only identifiable when both legs land in the same week. A player who
  moves team-to-team without a same-week return leg is ambiguous between a real
  trade and "dropped, then claimed off waivers by someone else" - those are
  labelled ``TEAM->TEAM`` rather than guessed at
* FAAB bids are unavailable, permanently
* churn inside a single week (added Tuesday, dropped Friday) is invisible

Every move therefore carries a ``Source`` column - ``activity`` when ESPN told us
what it was, ``snapshot`` when we inferred it - so the UI can be honest about
which is which.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import os
from collections import defaultdict

import pandas as pd

from paths import TRANSACTIONS_DIR, weekly_roster_file, moves_file
from ffapp.espn import week_utils
from ffapp.metrics.owner_overrides import owner_id_for

# Roster spots that are not a starting lineup slot.
BENCH_SLOTS = {'BE', 'IR', 'BENCH', 'RES'}

# Move types. TEAM_TO_TEAM is deliberately not called a trade - see module docs.
ADD = 'ADD'
DROP = 'DROP'
TRADE = 'TRADE'
TEAM_TO_TEAM = 'TEAM->TEAM'

# ESPN activity actions -> our move types.
ACTIVITY_TYPES = {
    'FA ADDED': ADD,
    'WAIVER ADDED': ADD,
    'DROPPED': DROP,
    'TRADED': TRADE,
}

ROSTER_COLUMNS = ['League', 'Year', 'Week', 'Team', 'Owner ID', 'Player',
                  'Position', 'Slot', 'Started', 'Points', 'Projected']
MOVE_COLUMNS = ['League', 'Year', 'Week', 'Type', 'Player', 'Position',
                'From Team', 'To Team', 'Owner ID', 'FAAB Bid', 'Source']


def say(msg):
    """print() that cannot take down a pull.

    League names carry emoji ("The Girl's Room 💞🏈") and the Windows console is
    cp1252, so a plain print raises UnicodeEncodeError. That killed the whole
    league here, not just its logging - the header prints before any work, so
    the exception fired before a single week was fetched and the season was
    recorded as a failure with no data.
    """
    try:
        print(msg)
    except UnicodeEncodeError:
        enc = getattr(_sys.stdout, 'encoding', None) or 'ascii'
        print(msg.encode(enc, errors='replace').decode(enc, errors='replace'))


# ---------------------------------------------------------------------------
# pulling
# ---------------------------------------------------------------------------

def pull_weekly_rosters(league, league_name, year, through_week=None):
    """Every team's roster for every completed week, as a tidy DataFrame.

    One ESPN request per week. ``through_week`` defaults to the last week anyone
    actually scored in; pass it explicitly to limit the pull.

    The last week is found with ``week_utils.completed_weeks`` rather than
    ``current_week - 1``. On a finished season ESPN leaves ``current_week`` at
    the final scoring period, so ``- 1`` silently drops the championship week -
    2024 has scores in all 17 weeks but that arithmetic stops at 16.
    """
    reg = getattr(league.settings, 'reg_season_count', 14) or 14
    last = through_week if through_week else _completed_weeks(league)
    last = max(int(last or 0), 0)

    owner_cache = {t.team_name: owner_id_for(league, t) for t in league.teams}

    rows = []
    for week in range(1, last + 1):
        try:
            boxes = league.box_scores(week=week)
        except Exception as e:                      # a single bad week must not
            say(f"    week {week}: box_scores failed ({e})")   # kill the pull
            continue
        for box in boxes:
            for team, lineup in ((box.home_team, box.home_lineup),
                                 (box.away_team, box.away_lineup)):
                name = getattr(team, 'team_name', None)
                if name is None:                    # bye weeks come back as 0
                    continue
                for p in lineup:
                    slot = p.slot_position
                    rows.append({
                        'League': league_name,
                        'Year': year,
                        'Week': week,
                        'Team': name,
                        'Owner ID': owner_cache.get(name),
                        'Player': p.name,
                        'Position': p.position,
                        'Slot': slot,
                        'Started': slot not in BENCH_SLOTS,
                        'Points': round(float(p.points or 0), 2),
                        'Projected': round(float(p.projected_points or 0), 2),
                    })
    df = pd.DataFrame(rows, columns=ROSTER_COLUMNS)
    say(f"    rosters: {len(df)} player-weeks over {df['Week'].nunique() if len(df) else 0} weeks "
          f"(reg_season={reg})")
    return df


def _completed_weeks(league):
    """How many weeks have actually been played.

    Delegates to week_utils, which counts weeks where *someone* scored - the
    same rule the weekly update uses, so the two cannot drift apart.
    """
    scores = pd.DataFrame([t.scores for t in league.teams])
    if scores.empty:
        return 0
    return week_utils.completed_weeks(scores)


def pull_activity(league, league_name, year, page_size=25, max_pages=200):
    """The full season transaction log, or an empty frame for past seasons.

    Pages until exhausted - ESPN caps ``limitPerMessageSet`` at 25 internally, so
    a single call silently truncates a full season to the most recent handful.

    Returns ``(DataFrame, note)``. ``note`` explains an empty result rather than
    leaving the caller to guess whether the league simply had no transactions.
    """
    rows, seen = [], set()
    offset = 0
    for _ in range(max_pages):
        try:
            page = league.recent_activity(size=page_size, offset=offset)
        except Exception as e:
            if offset == 0:
                # 404 here is the expected outcome for any completed season.
                return pd.DataFrame(columns=MOVE_COLUMNS), _activity_note(e)
            break                                    # partial log beats none
        if not page:
            break
        new = 0
        for act in page:
            for (team, action, player, bid) in act.actions:
                team_name = getattr(team, 'team_name', None)
                key = (act.date, team_name, action, getattr(player, 'name', None))
                if key in seen:
                    continue
                seen.add(key)
                new += 1
                rows.append({
                    'League': league_name,
                    'Year': year,
                    'Date': act.date,
                    'Team': team_name,
                    'Action': action,
                    'Player': getattr(player, 'name', None),
                    'Position': getattr(player, 'position', None),
                    'FAAB Bid': bid or 0,
                })
        if new == 0:
            break
        offset += page_size

    df = pd.DataFrame(rows)
    note = '' if len(df) else 'no transactions reported for this season'
    return df, note


def _activity_note(exc):
    name = type(exc).__name__
    if 'InvalidLeague' in name or '404' in str(exc):
        return ('activity feed unavailable (ESPN serves it for the current season '
                'only) - moves reconstructed from weekly rosters')
    return f'activity feed unavailable ({name}: {exc})'


# ---------------------------------------------------------------------------
# reconstruction
# ---------------------------------------------------------------------------

def reconstruct_moves(rosters):
    """Adds, drops and trades inferred from week-over-week roster diffs.

    A trade requires a genuine two-way swap between the *same pair* of teams in
    the same week. Only requiring that a team both gained and lost someone that
    week massively over-counts - it labelled 37 trades in a season that really
    had 2, because any team active on the waiver wire trips it.
    """
    if rosters is None or rosters.empty:
        return pd.DataFrame(columns=MOVE_COLUMNS)

    league = rosters['League'].iloc[0]
    year = int(rosters['Year'].iloc[0])

    # week -> player -> team, plus a position lookup that survives a player
    # sitting on nobody's roster for a stretch
    by_week = {}
    for week, chunk in rosters.groupby('Week'):
        by_week[int(week)] = dict(zip(chunk['Player'], chunk['Team']))
    position = dict(zip(rosters['Player'], rosters['Position']))
    owner = {}
    for team, chunk in rosters.groupby('Team'):
        owner[team] = chunk['Owner ID'].iloc[0]

    weeks = sorted(by_week)
    out = []
    for prev_wk, wk in zip(weeks, weeks[1:]):
        prev, cur = by_week[prev_wk], by_week[wk]

        # every team-to-team movement this week, keyed by the pair involved
        pair_moves = defaultdict(list)
        for player, team in cur.items():
            was = prev.get(player)
            if was and was != team:
                pair_moves[(was, team)].append(player)

        traded, paired = set(), set()
        for (a, b), players in pair_moves.items():
            if (b, a) in pair_moves and (a, b) not in paired:
                paired.add((a, b))
                paired.add((b, a))
                traded.update(players)
                traded.update(pair_moves[(b, a)])

        for player, team in cur.items():
            was = prev.get(player)
            if was == team:
                continue
            if was:
                kind = TRADE if player in traded else TEAM_TO_TEAM
                out.append(_move(league, year, wk, kind, player, position,
                                 was, team, owner.get(team)))
            else:
                out.append(_move(league, year, wk, ADD, player, position,
                                 '(FA)', team, owner.get(team)))

        for player, team in prev.items():
            if player not in cur:
                out.append(_move(league, year, wk, DROP, player, position,
                                 team, '(FA)', owner.get(team)))

    return pd.DataFrame(out, columns=MOVE_COLUMNS)


def _move(league, year, week, kind, player, position, frm, to, owner_id):
    return {
        'League': league, 'Year': year, 'Week': int(week), 'Type': kind,
        'Player': player, 'Position': position.get(player),
        'From Team': frm, 'To Team': to, 'Owner ID': owner_id,
        'FAAB Bid': 0, 'Source': 'snapshot',
    }


def apply_activity_labels(moves, activity, week_of_date):
    """Upgrade inferred moves with the real type and FAAB bid where ESPN has them.

    Matched on (week, player) rather than an exact timestamp: the snapshot places
    a move in the week its effect first shows up, which can be the week after the
    transaction itself when someone claims a player mid-week.
    """
    if moves.empty or activity is None or activity.empty:
        return moves

    act = activity.copy()
    act['Week'] = act['Date'].map(week_of_date)
    act = act.dropna(subset=['Week'])
    act['Week'] = act['Week'].astype(int)

    # a player can be added and dropped in one week; prefer the definitive labels
    lookup = {}
    for player, week, action, bid in zip(act['Player'], act['Week'],
                                         act['Action'], act['FAAB Bid']):
        mapped = ACTIVITY_TYPES.get(action)
        if not mapped:
            continue
        for w in (week, week + 1):          # effect can surface a week later
            lookup.setdefault((player, w, mapped), bid)

    moves = moves.copy()
    for i, (player, week, kind) in enumerate(zip(moves['Player'], moves['Week'],
                                                 moves['Type'])):
        # TEAM->TEAM is the ambiguous case the feed can actually resolve
        for candidate in ((kind,) if kind != TEAM_TO_TEAM else (TRADE, ADD)):
            hit = lookup.get((player, week, candidate))
            if hit is not None:
                moves.iat[i, moves.columns.get_loc('Type')] = candidate
                moves.iat[i, moves.columns.get_loc('FAAB Bid')] = hit
                moves.iat[i, moves.columns.get_loc('Source')] = 'activity'
                break
    return moves


def week_mapper(rosters):
    """Epoch-ms -> week number, derived from the weeks actually pulled.

    ESPN stamps activity with a timestamp and no week. Rather than hard-coding a
    season calendar, this buckets by the NFL week boundary (Tuesday 08:00 UTC,
    comfortably after Monday night and before Thursday) anchored on week 1.
    """
    import datetime as _dt
    weeks = sorted(rosters['Week'].unique()) if len(rosters) else []
    if not weeks:
        return lambda _ms: None
    year = int(rosters['Year'].iloc[0])
    # NFL week 1 Tuesday: first Tuesday on/after Sep 1 of that season
    d = _dt.datetime(year, 9, 1, 8, tzinfo=_dt.timezone.utc)
    while d.weekday() != 1:                 # 1 == Tuesday
        d += _dt.timedelta(days=1)
    anchor = d.timestamp() * 1000.0
    last = int(max(weeks))

    def to_week(ms):
        try:
            offset = (float(ms) - anchor) / (7 * 24 * 3600 * 1000.0)
        except (TypeError, ValueError):
            return None
        return min(max(int(offset) + 1, 1), last)
    return to_week


# ---------------------------------------------------------------------------
# orchestration
# ---------------------------------------------------------------------------

def build_season(league, league_name, year, through_week=None, write=True):
    """Pull, reconstruct, label and (optionally) write one league-season.

    Returns ``(rosters, moves, note)``.
    """
    say(f"  {league_name} {year}")
    rosters = pull_weekly_rosters(league, league_name, year, through_week)
    if rosters.empty:
        return rosters, pd.DataFrame(columns=MOVE_COLUMNS), 'no roster data'

    moves = reconstruct_moves(rosters)
    activity, note = pull_activity(league, league_name, year)
    if not activity.empty:
        moves = apply_activity_labels(moves, activity, week_mapper(rosters))
        note = f'activity feed applied ({len(activity)} messages)'

    counts = moves['Type'].value_counts().to_dict() if len(moves) else {}
    say(f"    moves: {counts or 'none'}")
    say(f"    {note}")

    if write:
        os.makedirs(TRANSACTIONS_DIR, exist_ok=True)
        rosters.to_csv(weekly_roster_file(league_name, year), index=False)
        moves.to_csv(moves_file(league_name, year), index=False)
    return rosters, moves, note


def load_season(league_name, year):
    """Read a previously built league-season back off disk.

    Falls back to an uncompressed roster file so data written before the switch
    to .csv.gz still loads.
    """
    rp = weekly_roster_file(league_name, year)
    if not os.path.exists(rp) and os.path.exists(rp[:-3]):
        rp = rp[:-3]
    mp = moves_file(league_name, year)
    rosters = pd.read_csv(rp) if os.path.exists(rp) else pd.DataFrame(columns=ROSTER_COLUMNS)
    moves = pd.read_csv(mp) if os.path.exists(mp) else pd.DataFrame(columns=MOVE_COLUMNS)
    return rosters, moves


def available_seasons():
    """(league, year) pairs that have weekly roster data, newest first."""
    import glob
    import re
    out = set()
    for pattern in ('* Weekly Rosters *.csv.gz', '* Weekly Rosters *.csv'):
        for path in glob.glob(os.path.join(TRANSACTIONS_DIR, pattern)):
            m = re.match(r'^(.+?) Weekly Rosters (\d{4})\.csv(\.gz)?$',
                         os.path.basename(path))
            if m:
                out.add((m.group(1), int(m.group(2))))
    return sorted(out, key=lambda t: (-t[1], t[0]))
