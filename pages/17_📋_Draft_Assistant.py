import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import os

import pandas as pd
import streamlit as st

from paths import DATA_DIR
from ffapp import league_registry as registry
from ffapp.espn import live_draft as ld
from ffapp.espn.league_settings import get_settings, parse_slot_groups, describe
from ffapp.metrics import draft_board as db
from ffapp.ui.tables import apply_display_defaults, hide_constant, show_table

RANKINGS_DIR = os.path.join(DATA_DIR, 'rankings')
POLL_CHOICES = {'Off (manual refresh)': 0, 'Every 5s': 5, 'Every 10s': 10,
                'Every 30s': 30}
SHOW = ['ECR', 'Pos', 'Player', 'NFL', 'Bye', 'ADP', 'Sheet ESPN', 'VALUE',
        'Pos VALUE', 'Need', 'Dropoff', 'Adjusted ECR', 'Target Round', 'Notes']


@st.cache_data(show_spinner=False)
def rankings_from_bytes(payload, name):
    import io
    return db.load_rankings(io.BytesIO(payload))


@st.cache_data(show_spinner=False)
def rankings_from_path(path, mtime):
    return db.load_rankings(path)


@st.cache_data(ttl=600, show_spinner='Loading the ESPN player pool...')
def pool_cached(league_id, year, rank_type, _s2, _swid):
    return ld.player_pool(league_id, year, _s2, _swid, limit=400, rank_type=rank_type)


@st.cache_data(ttl=600, show_spinner=False)
def teams_cached(league_id, year, _s2, _swid):
    return ld.teams(league_id, year, _s2, _swid)


def cols_for(df):
    return [c for c in SHOW if c in df.columns]


def local_sheets():
    if not os.path.isdir(RANKINGS_DIR):
        return []
    return sorted(f for f in os.listdir(RANKINGS_DIR) if f.lower().endswith('.csv'))


def app():
    apply_display_defaults()

    st.header('📋 Live Draft Assistant')
    st.write(
        'Your rankings sheet is the source of truth. It tells you who is still '
        'on the board, who is falling past their value, and — given your roster '
        'and your league\'s lineup — what to take next.'
    )

    # =================================================== 1. the rankings sheet
    st.markdown('##### 1. Your rankings sheet')
    up = st.file_uploader('Upload the CSV (use the version closest to your draft)',
                          type='csv')
    rankings = None
    if up is not None:
        try:
            rankings = rankings_from_bytes(up.getvalue(), up.name)
            st.success(f'{len(rankings)} players from **{up.name}**')
        except Exception as e:
            st.error(f'Could not read that CSV: {e}')
            return
    else:
        local = local_sheets()
        if local:
            pick = st.selectbox('…or a sheet already in `data/rankings/`',
                                ['—'] + local)
            if pick != '—':
                path = os.path.join(RANKINGS_DIR, pick)
                try:
                    rankings = rankings_from_path(path, os.path.getmtime(path))
                    st.info(f'{len(rankings)} players from **{pick}**')
                except Exception as e:
                    st.error(f'Could not read {pick}: {e}')
                    return
    if rankings is None:
        st.info('Upload a rankings CSV to begin.')
        with st.expander('What the file needs'):
            st.markdown(
                """
Two required columns (matched case-insensitively):

| Field | Also accepted as |
|---|---|
| **Name** | `Player`, `Player Name` |
| **Rank** | `FantasyPros`, `ECR`, `Rk`, `Rank`, `Overall Rank`, `Consensus` |

Used when present: `Pos`, `Team`, `ADP`, `Bye`, `Tier`, `Round`, `ESPN`,
`Landmine`/`Notes`. A leading unnamed index column is ignored. A sparse `Round`
column is treated as tier markers and forward-filled into **Target Round**.
                """
            )
        return

    has_adp = 'Sheet ADP' in rankings.columns
    if not has_adp:
        st.warning(
            'This sheet has no ADP column, so value, survival and dropoff cannot '
            'be computed — the board will still work as a ranked available list.'
        )

    # ================================================== 2. tracking the draft
    st.markdown('##### 2. How to track the draft')
    mode = st.radio(
        'Source for who has been picked',
        ['Manual (no ESPN connection)', 'Live ESPN draft'],
        horizontal=True,
        help='Manual needs no credentials and no network — tick players off as '
             'they go. Live reads the ESPN draft feed as picks land.')
    live = mode.startswith('Live')

    league = league_id = s2 = swid = None
    slot_groups = None
    if live:
        c1, c2, c3 = st.columns([3, 1, 1])
        names = [l['espn_name'] for l in registry.LEAGUES]
        with c1:
            league = st.selectbox('League', names, format_func=registry.label)
        with c2:
            year = st.number_input('Season', 2019, 2100,
                                   pd.Timestamp.today().year, 1)
        with c3:
            rank_type = st.selectbox('ESPN scoring', ld.RANK_TYPES, index=0)
        creds = ld.credentials_for(league)
        if not creds:
            st.error(f'No credentials on file for {league}.')
            return
        league_id, s2, swid = creds
        stored = get_settings(league, int(year))
        if stored and stored.get('roster'):
            slot_groups = parse_slot_groups(stored['roster'])

    # ------------------------------------------------- lineup + draft settings
    with st.expander('League lineup and draft settings', expanded=slot_groups is None):
        if slot_groups:
            st.success(f'Using {league} {int(year)} settings: {describe(slot_groups)}')
        else:
            st.caption('No stored settings for this league-season — set your '
                       'starting lineup here. This drives roster needs, flex '
                       'handling and how deep it is worth going at a position.')
            d1, d2, d3, d4 = st.columns(4)
            n_qb = d1.number_input('QB', 0, 4, 1)
            n_rb = d2.number_input('RB', 0, 5, 2)
            n_wr = d3.number_input('WR', 0, 6, 2)
            n_te = d4.number_input('TE', 0, 3, 1)
            e1, e2, e3, e4 = st.columns(4)
            n_flex = e1.number_input('FLEX (RB/WR/TE)', 0, 4, 1)
            n_k = e2.number_input('K', 0, 2, 1)
            n_dst = e3.number_input('D/ST', 0, 2, 1)
            teams_n = e4.number_input('Teams', 4, 20, 12)
            slot_groups = parse_slot_groups({
                'QB': n_qb, 'RB': n_rb, 'WR': n_wr, 'TE': n_te,
                'RB/WR/TE': n_flex, 'K': n_k, 'D/ST': n_dst})
        caps = db.position_caps(slot_groups)
        st.caption(f'Worth drafting at most — ' +
                   ', '.join(f'{p} {c}' for p, c in sorted(caps.items())) +
                   ' (startable slots plus bench depth). Stops the recommender '
                   'hoarding one position and leaving a starting slot empty.')

    # ------------------------------------------------------- strategy controls
    with st.expander('Strategy — positional path and how hard to follow it'):
        st.markdown(
            'The recommender answers **which position** (need × what waiting '
            'costs × your lean) and **which player** (best ECR) separately, then '
            'combines them as `Adjusted ECR = ECR ÷ position score`.'
        )
        lean = st.slider(
            'Positional lean strength', 0.0, 3.0, 1.0, 0.25,
            help='0 = ignore position, draft pure ECR and need. 1 = a mild '
                 'RB > WR > TE/QB path. 3 = follow the path almost regardless '
                 'of ECR.')
        p1, p2, p3, p4 = st.columns(4)
        priority = {
            'RB': p1.number_input('RB weight', 0.1, 3.0,
                                  db.DEFAULT_PRIORITY['RB'], 0.05),
            'WR': p2.number_input('WR weight', 0.1, 3.0,
                                  db.DEFAULT_PRIORITY['WR'], 0.05),
            'TE': p3.number_input('TE weight', 0.1, 3.0,
                                  db.DEFAULT_PRIORITY['TE'], 0.05),
            'QB': p4.number_input('QB weight', 0.1, 3.0,
                                  db.DEFAULT_PRIORITY['QB'], 0.05),
        }
        priority['D/ST'] = db.DEFAULT_PRIORITY['D/ST']
        priority['K'] = db.DEFAULT_PRIORITY['K']
        buffer = st.slider(
            'Survival adjustment', -12, 12, 0,
            help='Positive if your league reaches (players go earlier than ADP), '
                 'negative if they let players slide. Shifts the estimate of who '
                 'lasts until your next turn.')
        st.caption(
            '⚠️ The lean is deliberately allowed to lose to a big ECR gap. At a '
            'middle draft slot the default takes a receiver ranked 14 spots '
            'higher over filling an empty backfield — whether that is right is '
            'taste, not arithmetic, which is what this slider is for.'
        )

    # ============================================== 3. build the board
    if live:
        try:
            pool = pool_cached(league_id, int(year), rank_type, s2, swid)
            team_names = teams_cached(league_id, int(year), s2, swid)
        except ld.DraftUnavailable as e:
            st.error(f'{e}\n\nSwitch to **Manual** above to keep drafting.')
            return
        matched, unmatched, missing = db.match_to_espn(rankings, pool)
        if matched.empty:
            st.error('None of the sheet matched ESPN — check the season.')
            return
        # the sheet is the source of truth for rank; ESPN ADP fills gaps only
        if has_adp:
            matched['ADP'] = matched['Sheet ADP'].fillna(matched['ADP'])
        valued = db.add_value(matched)
        if len(unmatched):
            with st.expander(f'⚠️ {len(unmatched)} sheet players did not match ESPN',
                             expanded=len(unmatched) > 5):
                show_table(unmatched, max_rows=15)
    else:
        # fully offline: the sheet supplies everything, ids are row numbers
        valued = rankings.copy()
        valued['Player'] = valued['Player']
        valued['ADP'] = valued['Sheet ADP'] if has_adp else pd.NA
        valued['ESPN Rank'] = valued.get('Sheet ESPN', pd.NA)
        valued['player_id'] = range(len(valued))
        valued = db.add_value(valued)
        team_names, missing, unmatched = {}, pd.DataFrame(), pd.DataFrame()

    label = (valued['ESPN Name'] if 'ESPN Name' in valued.columns
             else valued['Player'])
    valued = valued.assign(Player=label)

    # --------------------------------------------------------- who is taken
    st.markdown('##### 3. The board')

    def board_ui():
        if live:
            try:
                state = ld.draft_state(league_id, int(year), s2, swid)
            except ld.DraftUnavailable as e:
                st.error(str(e))
                return
            my_team = st.selectbox(
                'Your team', sorted(team_names, key=lambda t: team_names[t]),
                format_func=lambda t: team_names.get(t, f'Team {t}'))
            available, gone = db.board(valued, state)
            mine_rows = db.my_drafted(state, my_team, valued)
            my_counts = db.roster_counts(mine_rows.to_dict('records'))
            away = ld.picks_until(state, my_team)
            turns = ld.next_turns(state, my_team, 6)
            next_pick = turns[0]['overall'] if turns else None
            after = turns[1]['overall'] if len(turns) > 1 else None
        else:
            opts = valued.sort_values('ECR')['Player'].tolist()
            taken = st.multiselect(
                'Players already drafted (by anyone)', opts,
                help='Type to filter. Everything not listed stays on the board.')
            mine_names = st.multiselect('…of those, the ones YOU took',
                                        taken or opts)
            available = valued[~valued['Player'].isin(taken)].copy()
            gone = valued[valued['Player'].isin(taken)].copy()
            mine_rows = valued[valued['Player'].isin(mine_names)]
            my_counts = db.roster_counts(mine_rows.to_dict('records'))
            c1, c2 = st.columns(2)
            next_pick = c1.number_input('Your next overall pick', 1, 400,
                                        max(len(taken) + 1, 1))
            after = c2.number_input('The pick after that', 1, 400,
                                    int(next_pick) + 12)
            away = max(0, int(next_pick) - len(taken) - 1)
            state = None

        needs, flex_open = db.remaining_needs(my_counts, slot_groups)
        a, b, c, d = st.columns(4)
        a.metric('On the board', len(available))
        b.metric('Picks until you', '—' if away is None else ('YOU' if away == 0 else away))
        c.metric('Your roster', sum(my_counts.values()) or 0)
        d.metric('Starters still needed',
                 ', '.join(f'{p}×{n}' for p, n in sorted(needs.items()) if n)
                 or ('FLEX' if flex_open else 'set'))

        tabs = st.tabs(['🎯 Recommend', 'Best available', '💰 Value',
                        'Dropoff', 'My roster', '🗺️ Draft plan', 'Gone'])

        # the pick after next is what "waiting" actually costs you
        wait_to = after if after else next_pick

        with tabs[0]:
            recs = db.recommend(available, my_counts, slot_groups,
                                next_pick=wait_to, priority=priority,
                                n=20, survival_buffer=buffer, lean=lean)
            if recs.empty:
                st.info('Nothing left to recommend.')
            else:
                st.caption(
                    'Sorted by **Adjusted ECR** (lower is better). **Need** is '
                    'unfilled starting slots at that position; **Dropoff** is how '
                    'much worse your best option there gets by your next turn.'
                )
                cc = cols_for(recs)
                show_table(recs[cc].style.background_gradient(
                    subset=[c for c in ('Adjusted ECR',) if c in cc],
                    cmap='RdYlGn_r'),
                    formats={'ECR': '{:.0f}', 'Sheet ESPN': '{:.0f}',
                             'Bye': '{:.0f}', 'Target Round': '{:.0f}'},
                    max_rows=15)

        with tabs[1]:
            pos = st.radio('Position', ['All'] + sorted(available['Pos'].dropna().unique()),
                           horizontal=True)
            view = db.best_available(available, 40,
                                     position=None if pos == 'All' else pos)
            show_table(view[cols_for(view)], max_rows=18,
                       formats={'ECR': '{:.0f}', 'Sheet ESPN': '{:.0f}',
                                'Bye': '{:.0f}', 'Target Round': '{:.0f}'})

        with tabs[2]:
            if not has_adp:
                st.info('No ADP column in this sheet, so value cannot be computed.')
            else:
                st.caption('Falling furthest past their **positional** value. '
                           'Position-relative on purpose — raw rank differences '
                           'put kickers and defences on top of every value list.')
                view = db.value_picks(available, 25)
                if view.empty:
                    st.info('Nothing currently falling past its value.')
                else:
                    show_table(view[cols_for(view)], max_rows=18,
                               formats={'ECR': '{:.0f}', 'Bye': '{:.0f}',
                                        'Target Round': '{:.0f}'})

        with tabs[3]:
            st.caption(f'What it costs to wait from pick {next_pick} to {wait_to}. '
                       'High dropoff = take that position now.')
            drop = db.positional_dropoff(available, wait_to, buffer)
            if drop.empty:
                st.info('Not enough ADP data to estimate dropoff.')
            else:
                show_table(drop.style.background_gradient(subset=['Dropoff'],
                                                          cmap='Reds'),
                           formats={'Available': '{:.0f}', 'Best ECR Now': '{:.0f}',
                                    'Best ECR Later': '{:.0f}'})

        with tabs[4]:
            if mine_rows.empty:
                st.info('Nothing drafted yet.')
            else:
                show_table(mine_rows[cols_for(mine_rows) +
                                     [c for c in ('Pick', 'Round') if c in mine_rows.columns]],
                           max_rows=20, formats={'ECR': '{:.0f}', 'Pick': '{:.0f}',
                                                 'Round': '{:.0f}', 'Bye': '{:.0f}'})
            st.markdown('**Roster shape**')
            shape = pd.DataFrame([
                {'Pos': p, 'Have': my_counts.get(p, 0),
                 'Starters Needed': needs.get(p, 0),
                 'Worth Drafting': db.position_caps(slot_groups).get(p, '—')}
                for p in sorted(set(list(my_counts) + list(needs)
                                    + ['QB', 'RB', 'WR', 'TE']))])
            show_table(shape, formats={'Have': '{:.0f}', 'Starters Needed': '{:.0f}'})

        with tabs[5]:
            if not has_adp:
                st.info('A draft plan needs ADP to estimate who survives.')
            elif live and not turns:
                st.info('No remaining picks.')
            else:
                upcoming = (turns if live else
                            [{'overall': int(next_pick), 'round': None},
                             {'overall': int(after), 'round': None}])
                plan = db.draft_plan(available, upcoming, my_counts, slot_groups,
                                     priority=priority, survival_buffer=buffer,
                                     lean=lean)
                if plan.empty:
                    st.info('Not enough left to project.')
                else:
                    st.caption(
                        'A projection, not a prediction: it assumes everyone goes '
                        'at their ADP and nobody reaches. Read it for **which '
                        'positions** the board pushes you toward, not the names.'
                    )
                    show_table(plan, formats={'Pick': '{:.0f}', 'Round': '{:.0f}',
                                              'ECR': '{:.0f}'})

        with tabs[6]:
            if live and state is not None:
                log = db.recent_picks(state, pool, team_names, n=25)
                if log.empty:
                    st.info('No picks yet.')
                else:
                    show_table(hide_constant(log, ['Auto']),
                               formats={'Pick': '{:.0f}', 'Round': '{:.0f}'},
                               max_rows=18)
                if len(missing):
                    with st.expander(f'{len(missing)} ESPN players not on your sheet'):
                        st.caption('Kickers and defences excluded — sheets omit those.')
                        show_table(missing, formats={'ESPN Rank': '{:.0f}'},
                                   max_rows=15)
            elif gone.empty:
                st.info('Nobody marked as drafted yet.')
            else:
                show_table(gone[cols_for(gone)].sort_values('ECR'), max_rows=18,
                           formats={'ECR': '{:.0f}', 'Bye': '{:.0f}'})

    if live:
        poll = POLL_CHOICES[st.radio('Auto-refresh', list(POLL_CHOICES),
                                     horizontal=True, index=0)]
        if poll and hasattr(st, 'fragment'):
            st.fragment(run_every=poll)(board_ui)()
        else:
            st.button('🔄 Refresh board', type='primary')
            board_ui()
        st.caption(
            '⚠️ Run this locally (`streamlit run streamlit-app.py`) during a live '
            'draft — it polls ESPN with your `espn_s2` cookie, and anyone with the '
            'public URL would see your board. It only ever reads; it cannot pick '
            'for you.'
        )
    else:
        board_ui()


app()
