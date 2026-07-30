import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
from credentials import CRED
import streamlit as st
from paths import DRAFTS_DIR, LEAGUES_DIR, ODDS_DIR
from ffapp.ui.data_loader import available_years
def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from ffapp.ui.calcPercent import percent
    from ffapp.ui.playoffNum import playoff_num

    league_id = 417131856
    espn_s2 = CRED["ava_s2"]
    swid = CRED["ava_swid"]
    # Seasons with data on file - no hard-coded list to keep in sync
    year_options = available_years("Philly Extra Special")
    if not year_options:
        st.error("No season data found for Philly Extra Special.")
        return
    selected_year = st.selectbox(
        "Select Year", year_options, index=len(year_options) - 1
    )

    
    league = f"Philly Extra Special {selected_year}"
    file = f"{LEAGUES_DIR}/" + league + ".xlsx"
    st.title("🦝 " + league)
    # Extract the league name without the year
    league_name = " ".join(league.split()[:-1])  # Removes the year from the league string
    draft_file = f"{DRAFTS_DIR}/{league_name} Draft Results {selected_year}.csv"
    odds_file = f"{ODDS_DIR}/{league} Betting Odds.xlsx"

    from ffapp.ui.page_functions import display_remaining_schedule_difficulty, display_playoff_results, display_schedule_comparison, display_strength_of_schedule, display_playoff_odds, display_betting_odds
    from ffapp.ui.page_functions import display_playoff_odds_by_week, display_lifetime_record, display_biggest_lpi_upsets, display_lpi_by_week, display_expected_wins, display_lpi, display_draft_results
    
    display_playoff_results(file)

    display_schedule_comparison(file)

    display_lpi(league_id, espn_s2, swid, file)

    year = int(selected_year)
    display_playoff_odds(file, league_id, espn_s2, swid, year)
    if year > 2024:
        display_playoff_odds_by_week(file)

        display_betting_odds(odds_file)

        display_remaining_schedule_difficulty(file)
    display_lpi_by_week(file)
    
    display_strength_of_schedule(file)

    display_expected_wins(file)

    display_draft_results(draft_file)
    

    display_biggest_lpi_upsets(file)

    display_lifetime_record(file, league_id, espn_s2, swid, year_options)

app()