import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

from credentials import CRED
import streamlit as st
from pathlib import Path
import pandas as pd
from paths import DRAFTS_DIR, LEAGUES_DIR, ODDS_DIR
from ffapp.ui.data_loader import available_years

def app():
    import glob
    from ffapp.ui.page_functions import (
        display_playoff_results, display_schedule_comparison, display_lpi,
        display_playoff_odds, display_lpi_by_week, display_strength_of_schedule,
        display_expected_wins, display_draft_results, display_trades,
        display_biggest_lpi_upsets, display_lifetime_record, display_playoff_odds_by_week,
        display_remaining_schedule_difficulty, display_betting_odds
    )

    st.header('📦 Archived Leagues')
    st.write("Completed seasons from past years. Select a league to view its full history.")

    # Find all archived league files (2025 only, no 2026)
    all_files = glob.glob(f"{LEAGUES_DIR}/*.xlsx")
    archived_leagues = {}

    for file_path in all_files:
        file_name = Path(file_path).stem  # Remove .xlsx
        parts = file_name.rsplit(' ', 1)

        if len(parts) == 2:
            league_name, year = parts[0], parts[1]

            # Check if this league has ONLY 2025 data (archived)
            has_2025 = any(f"{league_name} 2025" in f for f in all_files)
            has_2026 = any(f"{league_name} 2026" in f for f in all_files)

            if has_2025 and not has_2026:
                if league_name not in archived_leagues:
                    archived_leagues[league_name] = []
                try:
                    archived_leagues[league_name].append(int(year))
                except ValueError:
                    pass

    # Sort by league name
    archived_leagues = dict(sorted(archived_leagues.items()))

    if not archived_leagues:
        st.info("No archived leagues found. All leagues have current season data!")
        return

    # Create dropdown options: "League Name (Year)"
    options = []
    league_year_map = {}

    for league_name in sorted(archived_leagues.keys()):
        years = sorted(archived_leagues[league_name], reverse=True)
        for year in years:
            display_text = f"{league_name} ({year})"
            options.append(display_text)
            league_year_map[display_text] = (league_name, year)

    selected = st.selectbox(
        "Select a league and year",
        options,
        index=0 if options else None
    )

    if not selected or selected not in league_year_map:
        st.info("No archived leagues available.")
        return

    league_name, selected_year = league_year_map[selected]

    # Load files
    league = f"{league_name} {selected_year}"
    file = f"{LEAGUES_DIR}/{league}.xlsx"
    draft_file = f"{DRAFTS_DIR}/{league_name} Draft Results {selected_year}.csv"
    odds_file = f"{ODDS_DIR}/{league} Betting Odds.xlsx"

    st.title(f"📦 {league}")
    st.divider()

    # Display all sections
    display_playoff_results(file)
    st.divider()

    display_schedule_comparison(file)
    st.divider()

    # LPI needs league_id, s2, swid - we'll skip for archived since we don't have active access
    st.subheader("💡 League Power Index (LPI)")
    st.info("LPI data requires active ESPN access. View the archived season's final standings above.")
    st.divider()

    display_lpi_by_week(file)
    st.divider()

    display_strength_of_schedule(file)
    st.divider()

    display_expected_wins(file)
    st.divider()

    # Draft results if available
    if Path(draft_file).exists():
        display_draft_results(draft_file)
        st.divider()

    # Trades
    display_trades(league_name, selected_year)
    st.divider()

    display_biggest_lpi_upsets(file)
    st.divider()

    # Lifetime record doesn't apply to single-year view, but show standings
    st.subheader("📊 Final Standings")
    try:
        standings = pd.read_excel(file, sheet_name="Standings")
        st.dataframe(standings, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning(f"Could not load standings: {e}")

app()
