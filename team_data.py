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
from test_fantasypros_scrape import fantasypros_ranks
import re
start_time = time.time()

espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"

# Pennoni Younglings
year = 2025
league = League(league_id=310334683, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=996930954, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Pennoni Transportation
# league = League(league_id=1339704102, year=year, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Game of Yards
# league = League(league_id=1781851, year=year, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Brown Munde
# league = League(league_id=367134149, year=2022, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Turf On Grade League
# league = League(league_id=1242265374, year=2024, espn_s2="AECbYb8WaMMCKHklAi740KXDsHbXHTaW5mI%2FLPUegrKbIb6MRovW0L4NPTBpsC%2Bc2%2Fn7UeX%2Bac0lk3KGEwyeI%2FgF9WynckxWNIfe8m8gh43s68UyfhDj5K187Fj5764WUA%2BTlCh1AF04x9xnKwwsneSvEng%2BfACneWjyu7hJy%2FOVWsHlEm3nfMbU7WbQRDBRfkPy7syz68C4pgMYN2XaU1kgd9BRj9rwrmXZCvybbezVEOEsApniBWRtx2lD3yhJnXYREAupVlIbRcd3TNBP%2F5Frfr6pnMMfUZrR9AP1m1OPGcQ0bFaZbJBoAKdWDk%2F6pJs%3D", swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Las League
# league = League(league_id=1049459, year=2025, espn_s2='AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D', swid='{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}')

# Hannahs League
hannah_s2 = "AEBy%2FXPWgz4DEVTKf5Z1y9k7Lco6fLP6tO80b1nl5a1p9CBOLF0Z0AlBcStZsywrAAdgHUABmm7G9Cy8l2IJCjgEAm%2BT5NHVNFPgtfDPjT0ei81RfEzwugF1UTbYc%2FlFrpWqK9xL%2FQvSoCW5TV9H4su6ILsqHLnI4b0xzH24CIDIGKInjez5Ivt8r1wlufknwMWo%2FQ2QaJfm6VPlcma3GJ0As048W4ujzwi68E9CWOtPT%2FwEQpfqN3g8WkKdWYCES0VdWmQvSeHnphAk8vlieiBTsh3BBegGULXInpew87nuqA%3D%3D"
league = League(league_id=1399036372, year=2025, espn_s2=hannah_s2, swid='{46993514-CB12-4CFA-9935-14CB122CFA5F}')

ava_s2 = "AEBL5xTPsfrhYhP04Dc%2FHGojCvZAK7pmvEtoKwm%2FDUFjM86FeGyFUfomgi6VkRTlpDC0bXAOQyOy9UfdWQm%2FAbZUPauwvbn%2Bfn9pkW4BTpHapwqDSJyXSMWoH7GJyQjI8Oq7AF4bkD8A5Vm31unAN0dn6ar5h2YdSy7USKAbm8vH%2BVmQ3yAoT8QQ23V4mCQM7ztjkA3hkEYf%2BFfyB1ASlVb%2B0286sPBoPaaESQv45qLuCUG6883kq4SXq7PUACFpAUICO7ahS%2F06pr1Gg%2BzhO79cea6jXKNJsgRYQLQmHea7Yw%3D%3D"
matt_s2 = "AEApTMk4bKXLS%2ByFC85I7AlYVnFOTx28Qn8C5ElSPEEY3%2BV6Jn0RzRDIb1H39fmRU9ABSWxJBwDaxottGDrfteMllIgOnF6QDw%2Bv2v6ox%2FDJGV4DJav5ntyQn3oihvOstkQsXIvSGD5jFAQFTJcb6GOCe9jG0WuATob3%2BU5fi2fZdZJ%2Blpx65ty5SNBe8znFW3T52EfNFbEOrCFW13IHqmEUiO9%2BooinLTMwIhsD2Txzg7peD6bKhs%2BOQL7pqc2xE1x084MSLRZ33UZioi8aNJdJx%2FBO8BUaBy%2FB3VFUkB2S1CFUUnlY5S96e98QD9vgmLY%3D"
elle_s2 = "AECfQX9GAenUR7mbrWgFnjVxXJJEz4u%2BKEZUVBlsfc%2FnRHEmQJhqDOvGAxCjq%2BpWobEwQaiNR2L2kFAZRcIxX9y3pWjZd%2BHuV4KL0gq495A4Ve%2Fnza1Ap%2BGM5hQwgIpHqKL%2BosHEXvXVBfUxUmmX%2BG7HkNIir0lAZIX3CS68XAO6KXX5aEl%2BjUsc8pYqNAiaEiCEyLdULrUimPcog39bHlbmIuwYHXf2LsMHWUdQ1RrDGP%2BOIpKXx257vQLxnW%2FI72Eg7W%2Fg6Htwx1TpG5U9eMXEwQp0UEKHanE0YSgnTTELIw%3D%3D"

# Elles League
# league = League(league_id=1259693145, year=2025, espn_s2=elle_s2, swid='{B6F0817B-1DC0-4E29-B020-68B8E12B6931}')

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

# Elles League
# league = League(league_id=1259693145, year=2025, espn_s2=elle_s2, swid='{B6F0817B-1DC0-4E29-B020-68B8E12B6931}')
# team_name = "yay football woo"

# Matts League
league = League(league_id=261375772, year=2025, espn_s2=matt_s2, swid='{F8FBCEF4-616F-45CD-BBCE-F4616FE5CD64}')
team_name = "At Risk of CTE"

# Pennoni Younglings
# league = League(league_id=310334683, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# team_name = "The Golden Receivers"
# Family League
# league = League(league_id=996930954, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# team_name = "Golden Receivers"
# EBC League
# league = League(league_id=1118513122, year=year, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# team_name = "Werewolves of London"

# Avas League
# league = League(league_id=417131856, year=2025, espn_s2=ava_s2, swid='{9B611343-247D-458B-88C3-50BB33789365}')
# team_name = "Big Ballsy Bozos"

# Hannahs League
# league = League(league_id=1399036372, year=2025, espn_s2=hannah_s2, swid='{46993514-CB12-4CFA-9935-14CB122CFA5F}')
# team_name = "It's Miller Time"
# team_name = "Nothing Beats A Jets 2 Holiday"

# Las League
# league = League(league_id=1049459, year=year, espn_s2='AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D', swid='{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}')
# team_name = "Team Rodriguez"

fantasypros_rank_df = fantasypros_ranks()
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

fantasypros_freeagents(league, fantasypros_rank_df)

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

# print_team_with_fantasypros_ranks(league, fantasypros_rank_df, team_name)

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

def find_trade_partners(league, team_name):
    print_team_with_fantasypros_ranks(league, fantasypros_rank_df, team_name)

    team_names = [team.team_name for team in league.teams]
    if team_name not in team_names:
        print(f"Team '{team_name}' not found! Available teams: {team_names}")
        return
    
    team = league.teams[team_names.index(team_name)]
    print(f"\n----- Finding trade partners for {team.team_name} -----\n")

    for other_team in league.teams:
        if other_team.team_name == team.team_name:
            continue
        print(f"Potential trade partner: {other_team.team_name}")
        print_team_with_fantasypros_ranks(league, fantasypros_rank_df, other_team.team_name)
        print(f"\n----------")

find_trade_partners(league, team_name)