"""Analyze most common players on undefeated, winless, 1st place, and last place teams by week.

Aggregates across all 2026 leagues to show which players are most common on:
- 3-0 teams (undefeated)
- 0-3 teams (no wins)
- 1st place teams
- Last place teams

Output: CSV files by week and an aggregate summary
"""
import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

from credentials import CRED
import pandas as pd
from espn_api.football import League
from collections import defaultdict
from ffapp import league_registry as registry
from paths import DATA_DIR
import time

start_time = time.time()

# Get all 2026 leagues from registry
LEAGUES_2026 = [
    ("Pennoni Younglings", 310334683, "louie_s2_pages", "louie_swid"),
    ("Family Fantasy", 1343668602, "louie_s2_pages", "louie_swid"),  # 2026 override
    ("EBC League", 1118513122, "louie_s2_pages", "louie_swid"),
    ("0755 Fantasy Football", 1339704102, "prahlad_s2", "prahlad_swid"),
    ("Game of Yards!", 1781851, "prahlad_s2", "prahlad_swid"),
    ("Brown Munde", 367134149, "prahlad_s2", "prahlad_swid"),
    ("Turf On Grade 2.0", 1242265374, "turf_s2", "prahlad_swid"),
    ("THE BEST OF THE BEST", 1049459, "la_s2", "la_swid"),
    ("The Girl's Room 💞🏈", 1399036372, "hannah_s2", "hannah_swid"),
    ("Operators Football League", 1259693145, "elle_s2", "elle_swid"),
    ("Philly Extra Special", 417131856, "ava_s2", "ava_swid"),
    ("OnP Fantasy", 1675186799, "dave_s2", "dave_swid"),
    ("The Mike Daisy Sports IQ League", 1924463077, "dave_s2", "dave_swid"),
    ("Ross' Fantasy League", 558148583, "ayush_s2_2026", "ayush_swid_2026"),
    ("Amanda's League", 1165085642, "amanda_s2", "amanda_swid"),
    ("Ketkar Fantasy Football 2026", 250835749, "ayush_league2_s2", "ayush_league2_swid"),
    ("BP- Loudoun 2025", 29400230, "matt_s2", "matt_swid"),
    ("The Goofy Goobers", 1616305229, "prahlad2_s2", "prahlad_swid"),
    ("Campers and Skiers and Prahlad", 47829282, "prahlad2_s2", "prahlad_swid"),
    ("Board Fantasy Football", 496646254, "nolan_s2", "nolan_swid"),
]

def get_team_record_by_week(league, team, week):
    """Calculate a team's record (wins-losses) up to and including a specific week."""
    wins, losses = 0, 0
    for i in range(min(week, len(team.schedule))):
        opponent = team.schedule[i]
        if opponent is None:
            continue
        # Get scores up to this week (0-indexed)
        team_score = team.scores[i]
        opp_score = opponent.scores[i]
        if team_score > opp_score:
            wins += 1
        elif team_score < opp_score:
            losses += 1
    return wins, losses

def get_team_rank_by_week(league, week):
    """Get ranked teams (by points for) at a specific week."""
    teams_with_pf = []
    for team in league.teams:
        # Sum points for up to this week
        pf = sum(team.scores[:week])
        teams_with_pf.append((team.team_name, pf, team))
    # Sort by points for (descending)
    teams_with_pf.sort(key=lambda x: x[1], reverse=True)
    return teams_with_pf

def analyze_week(league, league_name, week):
    """Analyze a league for a specific week and return player stats by category."""
    results = {
        '3-0': defaultdict(int),  # Undefeated
        '0-3': defaultdict(int),  # Winless
        '1st': defaultdict(int),  # 1st place by points
        'Last': defaultdict(int),  # Last place by points
    }

    team_counts = {k: 0 for k in results.keys()}

    # Get rankings by points for
    ranked = get_team_rank_by_week(league, week)
    first_place_team = ranked[0][2] if ranked else None
    last_place_team = ranked[-1][2] if ranked else None

    # Check each team
    for team in league.teams:
        wins, losses = get_team_record_by_week(league, team, week)

        # Categorize team
        if wins == 3 and losses == 0:
            category = '3-0'
        elif wins == 0 and losses == 3:
            category = '0-3'
        elif team == first_place_team:
            category = '1st'
        elif team == last_place_team:
            category = 'Last'
        else:
            continue

        team_counts[category] += 1

        # Count players on this team
        for player in team.roster:
            player_name = player.name
            results[category][player_name] += 1

    return results, team_counts

def main():
    """Pull and analyze data for all 2026 leagues."""
    print("=" * 80)
    print("FANTASY FOOTBALL PLAYER ANALYSIS BY TEAM RECORD - 2026 LEAGUES")
    print("=" * 80)

    # Determine max week
    max_week = 0
    league_data = {}

    print("\nFetching league data...")
    for league_name, league_id, s2_key, swid_key in LEAGUES_2026:
        safe_name = league_name.encode('ascii', 'replace').decode('ascii')
        try:
            espn_s2 = CRED.get(s2_key)
            swid = CRED.get(swid_key)
            if not espn_s2 or not swid:
                print(f"  [WARN] {safe_name}: Missing credentials")
                continue

            league = League(league_id=league_id, year=2026, espn_s2=espn_s2, swid=swid)
            league_data[league_name] = league

            # Count weeks with scores
            if league.teams:
                weeks_played = len(league.teams[0].scores)
                max_week = max(max_week, weeks_played)
                print(f"  [OK] {safe_name}: {weeks_played} weeks")
        except Exception as e:
            err_msg = str(e)[:60].encode('ascii', 'replace').decode('ascii')
            print(f"  [FAIL] {safe_name}: {err_msg}")

    if not league_data:
        print("No leagues loaded successfully")
        return

    print(f"\nAnalyzing weeks 1-{max_week}...")

    # Analyze each week
    all_weeks = {}
    for week in range(1, max_week + 1):
        print(f"\n--- WEEK {week} ---")

        aggregate = {
            '3-0': defaultdict(int),
            '0-3': defaultdict(int),
            '1st': defaultdict(int),
            'Last': defaultdict(int),
        }
        total_teams = {k: 0 for k in aggregate.keys()}

        for league_name, league in league_data.items():
            try:
                results, team_counts = analyze_week(league, league_name, week)

                # Aggregate
                for category in aggregate.keys():
                    for player, count in results[category].items():
                        aggregate[category][player] += count
                    total_teams[category] += team_counts[category]
            except Exception as e:
                safe_name = league_name.encode('ascii', 'replace').decode('ascii')
                err_msg = str(e)[:60].encode('ascii', 'replace').decode('ascii')
                print(f"  [WARN] {safe_name}: {err_msg}")

        all_weeks[week] = (aggregate, total_teams)

        # Print summary
        for category in ['3-0', '0-3', '1st', 'Last']:
            print(f"\n{category} Teams ({total_teams[category]} teams across all leagues):")

            if not aggregate[category]:
                print("  (none found)")
                continue

            # Sort by count descending
            sorted_players = sorted(aggregate[category].items(), key=lambda x: x[1], reverse=True)
            for player, count in sorted_players[:10]:
                print(f"  {player}: {count}")

    # Save CSV files
    output_dir = f"{DATA_DIR}/player_analysis"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n\nSaving to {output_dir}...")

    # Save by week
    for week, (aggregate, total_teams) in all_weeks.items():
        week_data = []
        for category in ['3-0', '0-3', '1st', 'Last']:
            for player, count in sorted(aggregate[category].items(), key=lambda x: x[1], reverse=True):
                week_data.append({
                    'Week': week,
                    'Category': category,
                    'Player': player,
                    'Count': count,
                    'Pct_of_Category': f"{count * 100 / total_teams[category]:.1f}%" if total_teams[category] > 0 else "N/A"
                })

        if week_data:
            df = pd.DataFrame(week_data)
            df.to_csv(f"{output_dir}/Week_{week}.csv", index=False)
            print(f"  [OK] Week {week}.csv ({len(week_data)} rows)")

    # Save aggregate across all weeks (top players)
    agg_players = defaultdict(lambda: defaultdict(int))
    for week, (aggregate, _) in all_weeks.items():
        for category in aggregate:
            for player, count in aggregate[category].items():
                agg_players[category][player] += count

    agg_data = []
    for category in ['3-0', '0-3', '1st', 'Last']:
        for player, total_count in sorted(agg_players[category].items(), key=lambda x: x[1], reverse=True):
            agg_data.append({
                'Category': category,
                'Player': player,
                'Total_Appearances': total_count,
                'Avg_Per_Week': f"{total_count / max_week:.1f}"
            })

    if agg_data:
        df = pd.DataFrame(agg_data)
        df.to_csv(f"{output_dir}/Aggregate_All_Weeks.csv", index=False)
        print(f"  [OK] Aggregate_All_Weeks.csv ({len(agg_data)} rows)")

    elapsed = time.time() - start_time
    print(f"\n--- {elapsed:.1f} seconds ---")

if __name__ == "__main__":
    import os
    main()
