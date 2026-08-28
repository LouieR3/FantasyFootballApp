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

    from ffapp import league_registry as registry

    # "BP- Loudoun 2025" is the storage key every file on disk is named after, so
    # it stays. ESPN rebuilt this league for 2026 under a new id and name, and the
    # registry knows the two belong together - see league_registry's docstring.
    LEAGUE = "BP- Loudoun 2025"
    espn_s2 = CRED["matt_s2"]
    swid = CRED["matt_swid"]
    # Seasons with data on file - no hard-coded list to keep in sync
    year_options = available_years(LEAGUE)
    if not year_options:
        st.error(f"No season data found for {registry.display_name(LEAGUE)}.")
        return
    selected_year = st.selectbox(
        "Select Year", year_options, index=len(year_options) - 1
    )

    # The id differs by season, so every live ESPN call below has to ask per year
    # rather than trust one constant. 2025 and earlier read the original league;
    # 2026 onward read the rebuilt one.
    league_id = registry.league_id_for(LEAGUE, selected_year)

    league = f"{LEAGUE} {selected_year}"
    file = f"{LEAGUES_DIR}/" + league + ".xlsx"
    st.title("👷🏻‍♀️ "
             + f"{registry.display_name(LEAGUE)} {selected_year}")
    if registry.seasons_with_other_id(LEAGUE):
        st.caption(
            f"Reading ESPN league `{league_id}` for {selected_year}. This league "
            "was rebuilt on ESPN, so seasons before and after live under different "
            "ESPN ids but are treated as one league here."
        )
    # Extract the league name without the year
    league_name = " ".join(league.split()[:-1])  # Removes the year from the league string
    draft_file = f"{DRAFTS_DIR}/{league_name} Draft Results {selected_year}.csv"
    odds_file = f"{ODDS_DIR}/{league} Betting Odds.xlsx"

    from ffapp.ui.page_functions import display_remaining_schedule_difficulty, display_playoff_results, display_schedule_comparison, display_strength_of_schedule, display_playoff_odds, display_betting_odds
    from ffapp.ui.page_functions import display_playoff_odds_by_week, display_lifetime_record, display_biggest_lpi_upsets, display_lpi_by_week, display_expected_wins, display_lpi, display_draft_results, display_trades
    
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

    # Trades and post-draft roster value, tracked week by week.
    display_trades(league_name, selected_year)

    

    display_biggest_lpi_upsets(file)

    # display_lifetime_record(file, league_id, espn_s2, swid, year_options)

app()