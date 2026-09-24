import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
from credentials import CRED
import pandas as pd
from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
# import xlsxwriter
from itertools import combinations
import itertools
import math
import numpy as np
import random
import os
from test_fantasypros_scrape import fantasypros_ros_ranks
from test_fantasypros_scrape import fantasypros_week_ranks
from paths import DATA_DIR
import re
start_time = time.time()

espn_s2 = CRED["louie_s2"]

# Pennoni Younglings
year = 2026
# league = League(league_id=310334683, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])
# Family League
# league = League(league_id=996930954, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])
# EBC League
# league = League(league_id=1118513122, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])
# Pennoni Transportation
# league = League(league_id=1339704102, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])
# Game of Yards
# league = League(league_id=1781851, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])
# Brown Munde
# league = League(league_id=367134149, year=2022, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])
# Turf On Grade League
# league = League(league_id=1242265374, year=2024, espn_s2=CRED["turf_s2"], swid=CRED["prahlad_swid"])
# Las League
# league = League(league_id=1049459, year=2025, espn_s2=CRED["la_s2"], swid=CRED["la_swid"])
# Hannahs League
hannah_s2 = CRED["hannah_s2"]
# league = League(league_id=1399036372, year=2025, espn_s2=hannah_s2, swid=CRED["hannah_swid"])

ava_s2 = CRED["ava_s2"]
matt_s2 = CRED["matt_s2"]
elle_s2 = CRED["elle_s2"]

# print(league.free_agents(position='QB'))
# print()
# print(league.free_agents(position='WR'))
# print()
# print(league.free_agents(position='RB'))
# print()
# print(league.free_agents(position='TE'))
# print()
# print(league.free_agents(position='D/ST'))
# asdf

# Matts League
# league = League(league_id=261375772, year=year, espn_s2=matt_s2, swid=CRED["matt_swid"])
# team_name = "Graesser's Golden Receivers"

# Pennoni Younglings
# league = League(league_id=310334683, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])
# team_name = "The Golden Receivers"
# Family League
# league = League(league_id=1343668602, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])
# team_name = "Big Bosh Bashers"
# EBC League
# league = League(league_id=1118513122, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])
# team_name = "P90 Asiimov"

# Avas League
# league = League(league_id=417131856, year=year, espn_s2=ava_s2, swid=CRED["ava_swid"])
# team_name = "Big Ballsy Bozos"

# Hannahs League
league = League(league_id=1399036372, year=year, espn_s2=hannah_s2, swid=CRED["hannah_swid"])
team_name = "It's Miller Time"
# team_name = "Immaculate Concepcion"

# Las League
# league = League(league_id=1049459, year=year, espn_s2=CRED["la_s2"], swid=CRED["la_swid"])
# team_name = "Team Rodriguez"

fantasypros_rank_df = fantasypros_ros_ranks()
# Define draft order
slot_order = {
    "QB": 1,
    "RB": 2,
    "WR": 3,
    "TE": 4,
    "D/ST": 6,
    "K": 7,
}

print(team_name)

def fantasypros_freeagents(league, fantasypros_rank_df):
    # Draft order / normalization mapping
    position_map = {
        "DST": "D/ST",
        "DEF": "D/ST"
    }

    # Suffixes to strip
    suffixes = ["ii", "iii", "jr", "sr", "iv"]

    def clean_name(name):
        name = name.lower()
        for s in suffixes:
            name = re.sub(rf"\b{s}\b", "", name)
        name = re.sub(r"[^a-z0-9\s.']", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name

    def build_free_agent_df(league, fantasypros_rank_df, position, top_n_threshold):
        fa_list = league.free_agents(position=position)
        
        # Normalize FP data
        fp = fantasypros_rank_df.copy()
        fp['player_name_clean'] = fp['player_name'].apply(clean_name)
        fp['player_positions_norm'] = fp['player_position_id'].replace(position_map)

        enriched = []
        for p in fa_list:
            name = p.name
            clean_roster_name = clean_name(name)

            match = fp[fp['player_name_clean'].str.contains(clean_roster_name, na=False)]
            if len(match) == 0:
                enriched.append({
                    "player_name": name,
                    "player_positions_norm": "UNKNOWN",
                    "pos_rank": "(not found)",
                    "positional_rank": 9999  # numeric placeholder
                })
            else:
                r = match.iloc[0]
                pos_rank_str = r['pos_rank']  # e.g., 'RB3', 'WR2', 'TE5'
                # Extract numeric part
                numeric_rank = int(re.search(r'\d+', str(pos_rank_str)).group()) if pd.notnull(pos_rank_str) else 9999
                
                enriched.append({
                    "player_name": name,
                    "player_positions_norm": r['player_positions_norm'],
                    "pos_rank": pos_rank_str,
                    "positional_rank": numeric_rank
                })

        # Convert to DataFrame
        fa_df = pd.DataFrame(enriched)
        # print(fa_df)

        # Example: filter top 50 RB/WR, top 20 QB/TE
        if position in ["RB", "WR"]:
            fa_df = fa_df[fa_df['positional_rank'] <= 50]
        elif position in ["QB", "TE"]:
            fa_df = fa_df[fa_df['positional_rank'] <= 20]

        # Sort by numeric positional_rank
        fa_df = fa_df.sort_values('positional_rank').reset_index(drop=True)
        
        return fa_df

    # -----------------------------
    # Example usage
    # -----------------------------
    qb_df = build_free_agent_df(league, fantasypros_rank_df, "QB", top_n_threshold=20)
    rb_df = build_free_agent_df(league, fantasypros_rank_df, "RB", top_n_threshold=50)
    wr_df = build_free_agent_df(league, fantasypros_rank_df, "WR", top_n_threshold=50)
    te_df = build_free_agent_df(league, fantasypros_rank_df, "TE", top_n_threshold=20)

    print("Top QB Free Agents:")
    print(qb_df)

    print("\nTop RB Free Agents:")
    print(rb_df)

    print("\nTop WR Free Agents:")
    print(wr_df)

    print("\nTop TE Free Agents:")
    print(te_df)


def print_team_with_fantasypros_ranks(league, fantasypros_rank_df, team_name):
    # ------------------
    # Find team
    # ------------------
    team_names = [team.team_name for team in league.teams]
    if team_name not in team_names:
        print(f"Team '{team_name}' not found! Available teams: {team_names}")
        return
    
    team = league.teams[team_names.index(team_name)]
    print(f"\n----- {team.team_name} -----\n")

    roster = team.roster

    # ------------------
    # Normalize FantasyPros names
    # ------------------
    suffixes = ["ii", "iii", "jr", "sr", "iv"]

    def clean_name(name):
        name = name.lower()
        for s in suffixes:
            name = re.sub(rf"\b{s}\b", "", name)
        name = re.sub(r"[^a-z0-9\s.']", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name

    fp = fantasypros_rank_df.copy()
    fp['player_name_clean'] = fp['player_name'].apply(clean_name)
    fp['player_positions_norm'] = fp['player_position_id'].replace({
        "DST": "D/ST",
        "DEF": "D/ST"
    })

    
    # ------------------
    # Build enriched roster DataFrame
    # ------------------
    enriched = []
    for p in roster:
        raw_name = p.name
        roster_clean = clean_name(raw_name)

        match = fp[fp['player_name_clean'].str.contains(roster_clean, na=False)]
        if len(match) == 0:
            enriched.append({
                "raw_name": raw_name,
                "clean_name": roster_clean,
                "player_position_id": "UNKNOWN",
                "pos_rank": "(not found)",
                "pos_rank_num": 9999
            })
        else:
            r = match.iloc[0]

            # Extract number from pos_rank like RB13 → 13
            pos_rank_str = r["pos_rank"]
            if isinstance(pos_rank_str, str) and re.search(r"\d+", pos_rank_str):
                pos_rank_num = int(re.search(r"\d+", pos_rank_str).group())
            else:
                pos_rank_num = 9999

            enriched.append({
                "raw_name": raw_name,
                "clean_name": roster_clean,
                "player_position_id": r['player_positions_norm'],
                "pos_rank": r['pos_rank'],
                "pos_rank_num": pos_rank_num
            })

    enriched_df = pd.DataFrame(enriched)

    # ------------------
    # Sort by draft order, THEN pos rank
    # ------------------
    enriched_df["slot_sort"] = enriched_df["player_position_id"].map(slot_order).fillna(999)

    enriched_df = enriched_df.sort_values(
        by=["slot_sort", "pos_rank_num"],
        ascending=[True, True]
    )

    # ------------------
    # Print in order
    # ------------------
    for _, row in enriched_df.iterrows():
        print(f"{row['player_position_id']:<6} {row['raw_name']:<25} → {row['pos_rank']}")

    print("\n-----------------------------\n")


def test_team_data(league):
    team_names = [team.team_name for team in league.teams]
    print(team_names)

    # team_owners = [team.owners[0]['id'] for team in league.teams]
    # # print(team_owners)

    # team_scores = [team.scores for team in league.teams] 
    # print(team_scores)

    teams = league.teams
    # schedules = [[opponent.owners[0]['id'] for opponent in team.schedule] for team in teams]
    # schedules = [team.schedule for team in teams]
    # # print(schedules)
    # scores_df = pd.DataFrame(team_scores, index=team_owners)

    # current_week = scores_df.apply(lambda row: row[row != 0.0].last_valid_index(), axis=1).max() + 1
    # print(current_week)
    print(league.current_week)

    # team = teams[11]
    team = teams[5]
    
    outcomes = team.outcomes
    # Find the index of the first 'U'
    current_week = outcomes.index('U') + 1 if 'U' in outcomes else len(outcomes)

    print(current_week)  # Output: 6


    print(team.team_name)
    print(team.outcomes)
    print(team.acquisitions)
    print(team.roster)
    # for player in team.roster:
    #     print(player)
    #     # print(player.stats)
    #     # print(player.projected_points)
    #     print(player.slot_position)
    #     print("==")

    current_week_boxscores = league.box_scores(week=current_week)
    print(current_week_boxscores)
    # Find the box score that includes the team
    # team_matchup = next(
    #     (matchup for matchup in current_week_boxscores
    #     if matchup.home_team == team or matchup.away_team == team),
    #     None
    # )
    team_name = "At Risk of CTE"
    # team_name = "yay football woo"
    # team_name = "Big Ballsy Bozos"
    # team_name = "The Golden Receivers"
    team_matchup = next(
        (matchup for matchup in current_week_boxscores
        if matchup.home_team.team_name == team_name or matchup.away_team.team_name == team_name),
        None
    )
    
    if not team_matchup:
        print("No matchup found.")
    else:
        slot_order = {
            "QB": 1,
            "RB": 2,
            "WR": 3,
            "TE": 4,
            "RB/WR/TE": 5,
            "D/ST": 6,
            "K": 7,
            "BE": 8,
            "IR": 9
        }

        def sort_lineup(lineup):
            return sorted(
                lineup,
                key=lambda p: slot_order.get(p.slot_position, 99)
            )

        # --- HOME TEAM ---
        print(team_matchup.home_team)
        print(team_matchup.home_projected)

        sorted_home = sort_lineup(team_matchup.home_lineup)
        for player in sorted_home:
            print(f"{player.name}: {player.points} points, {player.projected_points} projected, {player.slot_position}")

        print()

        # --- AWAY TEAM ---
        print(team_matchup.away_team)
        print(team_matchup.away_projected)

        sorted_away = sort_lineup(team_matchup.away_lineup)
        for player in sorted_away:
            print(f"{player.name}: {player.points} points, {player.projected_points} projected, {player.slot_position}")
    print()

# test_team_data(league)

def suggest_lineup(league, team_name):
    flex_df, qb_df = fantasypros_week_ranks()

    suffixes = ["ii", "iii", "jr", "sr", "iv"]

    def clean_name(name):
        name = name.lower()
        for s in suffixes:
            name = re.sub(rf"\b{s}\b", "", name)
        name = re.sub(r"[^a-z0-9\s.']", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name

    flex_df = flex_df.copy()
    qb_df = qb_df.copy()
    flex_df['player_name_clean'] = flex_df['player_name'].apply(clean_name)
    qb_df['player_name_clean'] = qb_df['player_name'].apply(clean_name)

    def get_week_rank(player_name, position):
        # Only QB/RB/WR/TE are covered by the scraped weekly ranking pages
        if position == "QB":
            df = qb_df
        elif position in ("RB", "WR", "TE"):
            df = flex_df
        else:
            return None, None

        clean = clean_name(player_name)
        match = df[df['player_name_clean'] == clean]
        if match.empty:
            match = df[df['player_name_clean'].str.contains(clean, na=False)]
        if match.empty:
            return None, None

        r = match.iloc[0]
        return r['rank_ecr'], r['pos_rank']

    # ------------------
    # Find team
    # ------------------
    team_names = [team.team_name for team in league.teams]
    if team_name not in team_names:
        print(f"Team '{team_name}' not found! Available teams: {team_names}")
        return

    team = league.teams[team_names.index(team_name)]

    slot_order = {
        "QB": 1,
        "RB": 2,
        "WR": 3,
        "TE": 4,
        "RB/WR/TE": 5,
        "D/ST": 6,
        "K": 7,
        "BE": 8,
        "IR": 9,
    }

    players_info = []
    for p in team.roster:
        rank_ecr, pos_rank = get_week_rank(p.name, p.position)
        players_info.append({
            "name": p.name,
            "position": p.position,
            "slot_position": p.lineupSlot,
            "rank_ecr": rank_ecr if rank_ecr is not None else float('inf'),
            "pos_rank": pos_rank if pos_rank is not None else "(n/a)",
        })

    current_starters = [p for p in players_info if p['slot_position'] not in ("BE", "IR")]
    bench = [p for p in players_info if p['slot_position'] == "BE"]

    # ------------------
    # Figure out how many starting slots exist per position (flex counted separately)
    # ------------------
    slot_counts = {}
    flex_slots = 0
    for p in current_starters:
        if p['slot_position'] == "RB/WR/TE":
            flex_slots += 1
        else:
            slot_counts[p['slot_position']] = slot_counts.get(p['slot_position'], 0) + 1

    pool = current_starters + bench
    used = set()
    suggested = {}

    for pos, count in slot_counts.items():
        if pos in ("D/ST", "K"):
            # No weekly ranking data scraped for these -- keep current starters as-is
            chosen = [p for p in current_starters if p['slot_position'] == pos]
        else:
            candidates = [p for p in pool if p['position'] == pos and p['name'] not in used]
            candidates.sort(key=lambda x: x['rank_ecr'])
            chosen = candidates[:count]
        suggested[pos] = chosen
        for p in chosen:
            used.add(p['name'])

    if flex_slots:
        flex_candidates = [p for p in pool if p['position'] in ("RB", "WR", "TE") and p['name'] not in used]
        flex_candidates.sort(key=lambda x: x['rank_ecr'])
        chosen = flex_candidates[:flex_slots]
        suggested["RB/WR/TE"] = chosen
        for p in chosen:
            used.add(p['name'])

    # ------------------
    # Ignore cosmetic reshuffles: RB/WR/TE all feed the FLEX slot, so the
    # greedy pass above can relabel two players who were already both
    # starting (e.g. swap which one is "TE" vs "FLEX") with no real bench
    # call-up happening. Only keep the reassignment if the actual set of
    # starting RB/WR/TE-eligible players changed.
    # ------------------
    flex_group_slots = [s for s in ("RB", "WR", "TE") if s in slot_counts] + (["RB/WR/TE"] if flex_slots else [])
    current_flex_group_names = {
        p['name'] for p in current_starters if p['slot_position'] in flex_group_slots
    }
    suggested_flex_group_names = {
        p['name'] for slot in flex_group_slots for p in suggested.get(slot, [])
    }
    if current_flex_group_names == suggested_flex_group_names:
        for slot in flex_group_slots:
            suggested[slot] = sorted(
                [p for p in current_starters if p['slot_position'] == slot],
                key=lambda x: x['rank_ecr']
            )

    # ------------------
    # Print current vs suggested, slot by slot, in slot_order
    # ------------------
    print(f"\n----- {team_name}: Current vs. Suggested Lineup (this week) -----\n")
    for slot_pos in sorted(slot_counts.keys() | ({"RB/WR/TE"} if flex_slots else set()), key=lambda s: slot_order.get(s, 99)):
        current_list = sorted(
            [p for p in current_starters if p['slot_position'] == slot_pos],
            key=lambda x: x['rank_ecr']
        )
        suggested_list = sorted(suggested.get(slot_pos, []), key=lambda x: x['rank_ecr'])

        for current_p, suggested_p in zip(current_list, suggested_list):
            swap_flag = "  <-- SWAP" if current_p['name'] != suggested_p['name'] else ""
            print(
                f"{slot_pos:<10} "
                f"{current_p['name']:<22} {str(current_p['pos_rank']):<8} -> "
                f"{suggested_p['name']:<22} {str(suggested_p['pos_rank']):<8}"
                f"{swap_flag}"
            )

    print("\n-----------------------------\n")


def _clean_player_name(name):
    suffixes = ["ii", "iii", "jr", "sr", "iv"]
    name = name.lower()
    for s in suffixes:
        name = re.sub(rf"\b{s}\b", "", name)
    name = re.sub(r"[^a-z0-9\s.']", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


TRADE_POSITIONS = ["QB", "RB", "WR", "TE"]


def _build_league_wide_df(league, fantasypros_rank_df):
    """One row per rostered player, league-wide, with FantasyPros ROS rank,
    ESPN's own positional rank, actual points-to-date, and ESPN's rest-of-season
    projection -- the raw ingredients for spotting value/inefficiency."""
    fp = fantasypros_rank_df.copy()
    fp['player_name_clean'] = fp['player_name'].apply(_clean_player_name)
    fp['player_positions_norm'] = fp['player_position_id'].replace({"DST": "D/ST", "DEF": "D/ST"})
    fp['fp_pos_rank_num'] = fp['pos_rank'].apply(
        lambda s: int(re.search(r'\d+', str(s)).group()) if pd.notnull(s) and re.search(r'\d+', str(s)) else np.nan
    )
    fp_max_rank_by_pos = fp.groupby('player_positions_norm')['fp_pos_rank_num'].max().to_dict()

    rows = []
    for team in league.teams:
        for p in team.roster:
            clean = _clean_player_name(p.name)
            match = fp[fp['player_name_clean'].str.contains(clean, na=False)]
            if len(match):
                r = match.iloc[0]
                fp_pos_rank_str = r['pos_rank']
                fp_pos_rank_num = r['fp_pos_rank_num']
            else:
                fp_pos_rank_str, fp_pos_rank_num = None, np.nan

            rows.append({
                "team_name": team.team_name,
                "name": p.name,
                "position": p.position,
                "lineup_slot": p.lineupSlot,
                "fp_pos_rank_str": fp_pos_rank_str if fp_pos_rank_str is not None else "(n/a)",
                "fp_pos_rank": fp_pos_rank_num,
                "fp_max_rank_at_pos": fp_max_rank_by_pos.get(p.position, np.nan),
                "espn_pos_rank": p.posRank if p.posRank else np.nan,
                "total_points": p.total_points,
                "projected_total_points": p.projected_total_points,
                "avg_points": p.avg_points,
                "projected_avg_points": p.projected_avg_points,
            })

    df = pd.DataFrame(rows)

    # Rank players within their own position, league-wide among ROSTERED players only,
    # by ESPN's rest-of-season pace (proj_rank) and by how they've actually scored (actual_rank).
    # Blend 60/40 toward the forward-looking projection -- it's still the best signal for
    # what a player is worth going forward, while giving weight to real, in-season production.
    df['proj_rank'] = df.groupby('position')['projected_avg_points'].rank(ascending=False, method='min')
    df['actual_rank'] = df.groupby('position')['avg_points'].rank(ascending=False, method='min')
    df['point_value_rank'] = df['proj_rank'] * 0.6 + df['actual_rank'] * 0.4

    pos_rostered_count = df.groupby('position')['name'].transform('count')
    df['point_value_pct'] = df['point_value_rank'] / pos_rostered_count
    df['fp_pct'] = df['fp_pos_rank'] / df['fp_max_rank_at_pos']

    # Positive inefficiency = the market (FantasyPros consensus) ranks this player worse than
    # their actual+projected points warrant -> undervalued, a buy-low target on someone else's roster.
    # Negative inefficiency = reputation is running ahead of production -> a sell-high trade chip.
    df['inefficiency'] = df['fp_pct'] - df['point_value_pct']

    # Negative hot_cold = outperforming ESPN's rest-of-season projection right now (hot, sell
    # before regression). Positive = currently cold relative to a projection that still likes them
    # (buy-low window before it rebounds).
    df['hot_cold'] = df['actual_rank'] - df['proj_rank']

    return df


def _compute_team_starters(team_df, position_slot_counts):
    """Fill the team's actual starting lineup slots (base positions + flex) using the
    best-by-point-value player available, so positional need reflects this specific
    roster's personnel rather than a generic slot count."""
    base_needs = {
        "QB": position_slot_counts.get("QB", 0) + position_slot_counts.get("OP", 0),
        "RB": position_slot_counts.get("RB", 0),
        "WR": position_slot_counts.get("WR", 0),
        "TE": position_slot_counts.get("TE", 0),
    }
    flex_slots = (
        position_slot_counts.get("RB/WR/TE", 0)
        + position_slot_counts.get("RB/WR", 0)
        + position_slot_counts.get("WR/TE", 0)
    )

    needs = dict(base_needs)
    starters = {pos: [] for pos in needs}
    used_names = set()

    for pos, n in base_needs.items():
        pos_players = team_df[team_df['position'] == pos].sort_values('point_value_rank')
        chosen = pos_players.head(n)
        starters[pos] = chosen['name'].tolist()
        used_names.update(chosen['name'])

    if flex_slots:
        flex_pool = team_df[
            team_df['position'].isin(["RB", "WR", "TE"]) & ~team_df['name'].isin(used_names)
        ].sort_values('point_value_rank')
        flex_chosen = flex_pool.head(flex_slots)
        for _, row in flex_chosen.iterrows():
            needs[row['position']] = needs.get(row['position'], 0) + 1
            starters[row['position']].append(row['name'])
            used_names.add(row['name'])

    return needs, starters, used_names


def _analyze_team(team_name, league_df, position_slot_counts, gap_pct_threshold=0.55, surplus_pct_threshold=0.5):
    """Return (needs, starters, gaps, surplus) for a single team.

    gaps: positions where the best available starting lineup is still weak (starter
    point-value percentile worse than gap_pct_threshold, or a required slot has no
    rostered player at all).
    surplus: positions with quality bench depth beyond what's needed to start --
    "quality" meaning top half (surplus_pct_threshold) of the league-wide rostered
    pool at that position.
    """
    team_df = league_df[league_df['team_name'] == team_name]
    needs, starters, used_names = _compute_team_starters(team_df, position_slot_counts)

    gaps = {}
    surplus = {}
    for pos in TRADE_POSITIONS:
        pos_df = team_df[team_df['position'] == pos]
        starter_names = starters.get(pos, [])
        n_needed = needs.get(pos, 0)

        if n_needed > 0:
            starter_rows = pos_df[pos_df['name'].isin(starter_names)]
            if len(starter_rows) < n_needed:
                gaps[pos] = {"reason": "no rostered player to fill this slot", "starter_pct": 1.0}
            else:
                starter_pct = starter_rows['point_value_pct'].mean()
                if starter_pct >= gap_pct_threshold:
                    gaps[pos] = {"reason": "weak starter production", "starter_pct": starter_pct}

        bench_rows = pos_df[~pos_df['name'].isin(starter_names)]
        quality_bench = bench_rows[bench_rows['point_value_pct'] <= surplus_pct_threshold]
        if len(quality_bench) > 0:
            surplus[pos] = quality_bench.sort_values('point_value_pct')

    return needs, starters, gaps, surplus


def _fmt_player_line(row):
    fp = f"{row['position']}{int(row['fp_pos_rank'])}" if pd.notnull(row['fp_pos_rank']) else row['fp_pos_rank_str']
    espn_rk = f"{row['position']}{int(row['espn_pos_rank'])}" if pd.notnull(row['espn_pos_rank']) else "n/a"
    tag = ""
    if row['inefficiency'] >= 0.15:
        tag = "  [undervalued: FantasyPros ranks it worse than actual/projected points support]"
    elif row['inefficiency'] <= -0.15:
        tag = "  [FantasyPros reputation is running ahead of actual production]"
    elif row['hot_cold'] <= -3:
        tag = "  [hot: currently outscoring its own ESPN rest-of-season pace]"
    elif row['hot_cold'] >= 3:
        tag = "  [cold: underscoring a projection that still likes it]"
    return (
        f"{row['name']:<24} FP {fp:<7} ESPN {espn_rk:<7} "
        f"actual {row['avg_points']:>5.1f} ppg ({row['total_points']:>6.1f} total)  "
        f"proj {row['projected_avg_points']:>5.1f} ppg ({row['projected_total_points']:>6.1f} ROS){tag}"
    )


def _export_league_rosters(league, league_df, output_path):
    """Write one sheet per team: Position, Player, FP Rank, ESPN Rank, Actual PPG, Proj PPG."""
    slot_order_export = {"QB": 1, "RB": 2, "WR": 3, "TE": 4, "D/ST": 5, "K": 6}

    export_df = league_df.copy()
    export_df['FP Rank'] = export_df.apply(
        lambda r: f"{r['position']}{int(r['fp_pos_rank'])}" if pd.notnull(r['fp_pos_rank']) else r['fp_pos_rank_str'],
        axis=1
    )
    export_df['ESPN Rank'] = export_df.apply(
        lambda r: f"{r['position']}{int(r['espn_pos_rank'])}" if pd.notnull(r['espn_pos_rank']) else "n/a",
        axis=1
    )
    export_df['Actual PPG'] = export_df['avg_points']
    export_df['Proj PPG'] = export_df['projected_avg_points']
    export_df['_slot_sort'] = export_df['position'].map(slot_order_export).fillna(99)
    export_df = export_df.sort_values(['_slot_sort', 'fp_pos_rank'])

    cols = ['position', 'name', 'FP Rank', 'ESPN Rank', 'Actual PPG', 'Proj PPG']
    rename = {'position': 'Position', 'name': 'Player'}

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for team in league.teams:
            team_sheet = export_df[export_df['team_name'] == team.team_name][cols].rename(columns=rename)
            sheet_name = re.sub(r'[\[\]:*?/\\]', '', team.team_name)[:31] or "Team"
            team_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Wrote per-team roster export to {output_path}\n")
    return output_path


def find_trade_partners(league, team_name):
    team_names = [team.team_name for team in league.teams]
    if team_name not in team_names:
        print(f"Team '{team_name}' not found! Available teams: {team_names}")
        return

    print_team_with_fantasypros_ranks(league, fantasypros_rank_df, team_name)

    league_df = _build_league_wide_df(league, fantasypros_rank_df)
    position_slot_counts = league.settings.position_slot_counts

    export_path = os.path.join(DATA_DIR, "trade_analysis", f"league_rosters_{year}_wk{league.current_week}.xlsx")
    _export_league_rosters(league, league_df, export_path)

    print(
        f"Week {league.current_week} of the season -- actual-points columns reflect a small "
        f"in-season sample, so weight the projection columns more heavily early on.\n"
    )

    my_needs, my_starters, my_gaps, my_surplus = _analyze_team(team_name, league_df, position_slot_counts)

    print(f"\n===== {team_name}: Needs & Assets =====\n")
    if my_gaps:
        print("GAPS (weak starting production):")
        for pos, info in my_gaps.items():
            print(f"  {pos}: {info['reason']} (starter percentile {info['starter_pct']:.0%} of rostered {pos}s)")
    else:
        print("GAPS: none detected -- every starting slot grades out above-average.")

    if my_surplus:
        print("\nSURPLUS (tradeable depth beyond your starting lineup):")
        for pos, rows in my_surplus.items():
            print(f"  {pos}:")
            for _, row in rows.iterrows():
                print(f"    {_fmt_player_line(row)}")
    else:
        print("\nSURPLUS: no clear tradeable depth beyond your starters.")

    if not my_gaps:
        print("\nNo starting-lineup gaps found, so there's no urgent need to trade -- "
              "showing partner fits anyway based on your surplus below.")

    # ------------------------------------------------------------------
    # Score every other team as a trade partner: do they have surplus at one
    # of my gap positions, and a gap at one of my surplus positions?
    # ------------------------------------------------------------------
    partner_scores = []
    other_team_analysis = {}
    for other in league.teams:
        if other.team_name == team_name:
            continue
        needs, starters, gaps, surplus = _analyze_team(other.team_name, league_df, position_slot_counts)
        other_team_analysis[other.team_name] = (needs, starters, gaps, surplus)

        fills_my_gap = [pos for pos in my_gaps if pos in surplus]
        wants_my_surplus = [pos for pos in my_surplus if pos in gaps]

        score = len(fills_my_gap) * 2 + len(wants_my_surplus) * 2

        if score > 0:
            partner_scores.append((other.team_name, score, fills_my_gap, wants_my_surplus))

    partner_scores.sort(key=lambda x: x[1], reverse=True)

    print(f"\n\n===== Trade Partner Fit for {team_name} =====\n")
    if not partner_scores:
        print("No team currently has a clean surplus/gap match against your roster.")
        return

    for rank, (other_name, score, fills_my_gap, wants_my_surplus) in enumerate(partner_scores, start=1):
        needs, starters, gaps, surplus = other_team_analysis[other_name]
        print(f"{rank}. {other_name}  (fit score {score})")
        if fills_my_gap:
            print(f"   Their surplus fills your gap at: {', '.join(fills_my_gap)}")
        if wants_my_surplus:
            print(f"   Their gap matches your surplus at: {', '.join(wants_my_surplus)}")
        if not fills_my_gap and not wants_my_surplus:
            partial = [pos for pos in my_gaps if pos in surplus]
            print(f"   Partial fit -- they have surplus at: {', '.join(partial)} (no reciprocal need of yours)")

        if fills_my_gap:
            print("   TARGET (buy toward your gap):")
            for pos in fills_my_gap:
                for _, row in surplus[pos].iterrows():
                    print(f"     {_fmt_player_line(row)}")

        if wants_my_surplus:
            print("   OFFER (sell from your surplus, they need it):")
            for pos in wants_my_surplus:
                for _, row in my_surplus[pos].iterrows():
                    print(f"     {_fmt_player_line(row)}")

        print()

# find_trade_partners(league, team_name)

fantasypros_freeagents(league, fantasypros_rank_df)
print_team_with_fantasypros_ranks(league, fantasypros_rank_df, team_name)
suggest_lineup(league, team_name)