def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from calcPercent import percent
    from playoffNum import playoff_num

    league_id = 1259693145
    espn_s2 = "AECfQX9GAenUR7mbrWgFnjVxXJJEz4u%2BKEZUVBlsfc%2FnRHEmQJhqDOvGAxCjq%2BpWobEwQaiNR2L2kFAZRcIxX9y3pWjZd%2BHuV4KL0gq495A4Ve%2Fnza1Ap%2BGM5hQwgIpHqKL%2BosHEXvXVBfUxUmmX%2BG7HkNIir0lAZIX3CS68XAO6KXX5aEl%2BjUsc8pYqNAiaEiCEyLdULrUimPcog39bHlbmIuwYHXf2LsMHWUdQ1RrDGP%2BOIpKXx257vQLxnW%2FI72Eg7W%2Fg6Htwx1TpG5U9eMXEwQp0UEKHanE0YSgnTTELIw%3D%3D"
    swid='{B6F0817B-1DC0-4E29-B020-68B8E12B6931}'

    # Initialize the dropdown for year selection
    year_options = ['2022', '2023', '2024', '2025']
    selected_year = '2025'
    
    # selected_year = st.selectbox("Select Year", year_options, index=3)  # Defaults to 2024
    league = f"Philly Extra Special {selected_year}"
    file = "leagues/" + league + ".xlsx"
    st.title("🏈 " + league)
    # Extract the league name without the year
    league_name = " ".join(league.split()[:-1])  # Removes the year from the league string
    draft_file = f"drafts/{league_name} Draft Results {selected_year}.csv"
    odds_file = f"odds/{league} Betting Odds.xlsx"

    from page_functions import display_playoff_results, display_schedule_comparison, display_strength_of_schedule, display_playoff_odds, display_betting_odds
    from page_functions import display_playoff_odds_by_week, display_lifetime_record, display_biggest_lpi_upsets, display_lpi_by_week, display_expected_wins, display_lpi, display_draft_results
    
    display_playoff_results(file)

    display_schedule_comparison(file)

    display_lpi(league_id, espn_s2, swid, file)

    year = int(selected_year)
    display_playoff_odds(file, league_id, espn_s2, swid, year)
    if year > 2024:
        display_playoff_odds_by_week(file)

        display_betting_odds(odds_file)
    display_lpi_by_week(file)
    
    display_strength_of_schedule(file)

    display_expected_wins(file)

    display_draft_results(draft_file)
    

    display_biggest_lpi_upsets(file)

    # display_lifetime_record(file, league_id, espn_s2, swid, year_options)

app()