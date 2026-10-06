import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
from credentials import CRED
import streamlit as st
from paths import DRAFTS_DIR, LEAGUES_DIR, ODDS_DIR
from ffapp.ui.data_loader import available_years

# Set to True to hide Owner/Owners columns from dataframes
HIDE_OWNER_COLUMNS = True

def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from ffapp.ui.calcPercent import percent
    from ffapp.ui.playoffNum import playoff_num

    league_id = 250835749
    espn_s2 = CRED["ayush_league2_s2"]
    swid = CRED["ayush_league2_swid"]
    # Seasons with data on file - no hard-coded list to keep in sync
    year_options = available_years("Ketkar Fantasy Football 2026")
    if not year_options:
        st.error("No season data found for Ketkar Fantasy Football 2026.")
        return
    selected_year = st.selectbox(
        "Select Year", year_options, index=len(year_options) - 1
    )

    league_name = "Ketkar Fantasy Football 2026"
    league = f"{league_name} {selected_year}"
    file = f"{LEAGUES_DIR}/" + league + ".xlsx"
    st.title("🔷 Ayush's League - " + league)

    draft_file = f"{DRAFTS_DIR}/{league_name} Draft Results {selected_year}.csv"
    odds_file = f"{ODDS_DIR}/{league} Betting Odds.xlsx"

    from ffapp.ui.page_functions import display_remaining_schedule_difficulty, display_playoff_results, display_schedule_comparison, display_strength_of_schedule, display_playoff_odds, display_betting_odds
    from ffapp.ui.page_functions import display_playoff_odds_by_week, display_lifetime_record, display_biggest_lpi_upsets, display_lpi_by_week, display_expected_wins, display_lpi, display_draft_results, display_trades

    # Filter Owner/Owners columns from dataframe/table display only
    if HIDE_OWNER_COLUMNS:
        original_dataframe = st.dataframe
        original_table = st.table

        def filter_owner_columns(data, **kwargs):
            if isinstance(data, pd.DataFrame):
                cols_to_drop = [col for col in data.columns if 'owner' in col.strip().lower()]
                if cols_to_drop:
                    data = data.drop(columns=cols_to_drop, errors='ignore')
            return original_dataframe(data, **kwargs)

        def filter_owner_table(data, **kwargs):
            if isinstance(data, pd.DataFrame):
                cols_to_drop = [col for col in data.columns if 'owner' in col.strip().lower()]
                if cols_to_drop:
                    data = data.drop(columns=cols_to_drop, errors='ignore')
            return original_table(data, **kwargs)

        st.dataframe = filter_owner_columns
        st.table = filter_owner_table

    display_playoff_results(file)

    display_schedule_comparison(file)

    display_lpi(league_id, espn_s2, swid, file)

    year = int(selected_year)
    try:
        display_playoff_odds(file, league_id, espn_s2, swid, year)
    except Exception:
        st.warning("Playoff odds not available for this league/year")

    if year > 2024:
        try:
            display_playoff_odds_by_week(file)
        except Exception:
            pass

        try:
            display_betting_odds(odds_file)
        except Exception:
            pass

        try:
            display_remaining_schedule_difficulty(file)
        except Exception:
            pass

    display_lpi_by_week(file)
    display_strength_of_schedule(file)
    display_expected_wins(file)

    # Draft results and trades require draft file to exist
    try:
        display_draft_results(draft_file)
        display_trades(draft_file)
    except (FileNotFoundError, Exception):
        st.warning("Draft data not yet available for this league")

    try:
        display_lifetime_record(league_name)
    except Exception:
        pass

    display_playoff_odds_by_week(file)
    display_remaining_schedule_difficulty(file)

    try:
        display_biggest_lpi_upsets(league_name)
    except Exception:
        pass

app()
