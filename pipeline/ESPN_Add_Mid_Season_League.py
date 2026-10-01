"""Add a league that started mid-season (no complete draft data yet).

Usage:
  1. Update league_config below with league_id, espn_s2, swid, and league_name
  2. Run: python pipeline/ESPN_Add_Mid_Season_League.py
  3. Files created: [LEAGUE_NAME] [YEAR].xlsx in data/leagues/
  4. Add to all_matchups.csv if it has matches
  5. (Later, when draft is available: run ESPN_Add_Old_Season.py)
"""
import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

from credentials import CRED
import pandas as pd
from espn_api.football import League
import time
from ffapp import league_registry as registry
from ffapp.espn.all_matchups import get_years_matchups
from paths import DATA_DIR, LEAGUES_DIR

start_time = time.time()

# ====== CONFIGURATION ======
# Replace these with the league info
league_id = 250835749  # Amanda's League
espn_s2 = CRED["ayush_league2_s2"]
swid = CRED["ayush_league2_swid"]
league_name = "Ketkar Fantasy Football 2026"  # Canonical ESPN name (use registry.canonical() if unsure)
year = 2026
# ===========================

def pull_mid_season_data(league_id, espn_s2, swid, league_name, year):
    """Pull data for a league that started mid-season (live weeks only)."""

    try:
        league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    except Exception as e:
        print(f"Failed to connect to league {league_name}: {e}")
        return

    settings = league.settings
    canonical_name = registry.canonical(league_name)
    file_name = f"{canonical_name} {year}"
    file_path = f"{LEAGUES_DIR}/{file_name}.xlsx"

    print(f"Pulling {canonical_name} for {year}...")

    # Get teams
    team_names = [team.team_name for team in league.teams]
    team_scores = [team.scores for team in league.teams]
    schedules = []
    for team in league.teams:
        schedule = [opponent.team_name for opponent in team.schedule]
        schedules.append(schedule)

    # Calculate current week
    scores_df = pd.DataFrame(team_scores, index=team_names)
    zero_week = (scores_df == 0.0).all(axis=0)
    if zero_week.any():
        current_week = zero_week.idxmax() + 1
    else:
        current_week = scores_df.shape[1]

    print(f"  Current week: {current_week}")
    print(f"  Teams: {len(team_names)}")

    # Create schedule grid (who plays whom each week)
    schedules_df = pd.DataFrame(schedules, index=team_names)

    # Build head-to-head records
    records_df = pd.DataFrame(index=team_names, columns=team_names)
    records_df.fillna('', inplace=True)

    for team in team_names:
        for opp in team_names:
            wins, losses, ties = 0, 0, 0
            for week in range(current_week):
                if team == opp:
                    # vs themselves: their actual record
                    opp_team = schedules_df.loc[team, week]
                    team_score = scores_df.loc[team, week]
                    opp_score = scores_df.loc[opp_team, week]
                else:
                    # vs opponent: compare if they met that week
                    if opp == schedules_df.loc[team, week]:
                        team_score = scores_df.loc[team, week]
                        opp_score = scores_df.loc[opp, week]
                    else:
                        # They didn't play each other - hypothetical
                        team_score = scores_df.loc[team, week]
                        opp_scores = scores_df.loc[opp].tolist()
                        opp_score = opp_scores[week] if week < len(opp_scores) else 0

                if team_score > opp_score:
                    wins += 1
                elif team_score < opp_score:
                    losses += 1
                else:
                    ties += 1

            records_df.at[team, opp] = f"{wins}-{losses}-{ties}"

    # Expected wins (against average)
    rank_df = pd.DataFrame({'Team': team_names})
    rank_df['Record'] = [records_df.at[team, team] for team in team_names]
    rank_df = rank_df.sort_values(by='Record', key=lambda x: x.str.split('-').str[0].astype(int), ascending=False)
    rank_df.reset_index(drop=True, inplace=True)
    rank_df.index = rank_df.index + 1

    # Export
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        records_df.to_excel(writer, sheet_name='Schedule Grid')
        rank_df.to_excel(writer, sheet_name='Expected Wins')

    print(f"  ✓ Created {file_path}")

    # Add matchups to all_matchups.csv
    all_matchups_df = get_years_matchups(league, year)
    if all_matchups_df.empty:
        print(f"  No matchups to add (season may not have started)")
        return

    try:
        current_matchups = pd.read_csv(f"{DATA_DIR}/all_matchups.csv")
        # Remove duplicates by league+year+week+teams
        all_matchups_df = pd.concat([current_matchups, all_matchups_df]).drop_duplicates(
            subset=['League', 'Year', 'Week', 'Home Team', 'Away Team'],
            keep='last'
        ).reset_index(drop=True)
        print(f"  ✓ Merged {len(all_matchups_df)} matchups into all_matchups.csv")
    except FileNotFoundError:
        print(f"  ✓ Creating new all_matchups.csv with {len(all_matchups_df)} matchups")

    all_matchups_df.to_csv(f"{DATA_DIR}/all_matchups.csv", index=False)

if __name__ == "__main__":
    pull_mid_season_data(league_id, espn_s2, swid, league_name, year)
    print(f"\n--- {time.time() - start_time:.1f} seconds ---")
    print(f"\nNext steps:")
    print(f"1. The league data is now available in the app")
    print(f"2. Once the season ends and draft data becomes available:")
    print(f"   - Update ESPN_Add_Old_Season.py with this league's config")
    print(f"   - Run it to backfill the full season data")
