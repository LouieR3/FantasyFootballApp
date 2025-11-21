def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from calcPercent import percent
    from playoffNum import playoff_num

    league_id = 1675186799
    espn_s2 = "AEATfV13bzJs4HpWGw5IMP0Hoh9yD7FJ%2FWPkdfAC8pOMFdD9RT8wgdt%2BoACXFYuTYIBcpKSl1vPlVip8kDK8mqBlSh2ulGveo35%2BZMYhANuNP%2FfZCdttmqnrzzYjA7UedbVQfVpUcNgwrTD6Xn0dkyHQyDoOqrJbGGFbDkz%2F%2B8Tlas275RhFZ4jXhdZNgddmK0qiYgZABl13Ou8Gv2zzhgk77Pbf%2FhKvWxcN20pZHpN58x%2FwUAajmiZgEl2Nt4gbojRhLGTRqGBqYQ7C%2BqCpBw5KImrN72sLGJuqi5%2BgJHgaIw%3D%3D"
    swid='{AAD245A4-298A-4362-A70B-5F838E0D6F64}'

    # Initialize the dropdown for year selection
    year_options = ['2022', '2023', '2024', '2025']
    selected_year = '2025'
    
    # selected_year = st.selectbox("Select Year", year_options, index=3)  # Defaults to 2024
    league = f"OnP Fantasy {selected_year}"
    file = "leagues/" + league + ".xlsx"
    st.title("🏈 " + league)
    # Extract the league name without the year
    league_name = " ".join(league.split()[:-1])  # Removes the year from the league string
    draft_file = f"drafts/{league_name} Draft Results {selected_year}.csv"
    
    from page_functions import display_playoff_results, display_schedule_comparison, display_strength_of_schedule, display_playoff_odds
    from page_functions import display_playoff_odds_by_week, display_lifetime_record, display_biggest_lpi_upsets, display_lpi_by_week, display_expected_wins, display_lpi, display_draft_results
    
    display_playoff_results(file)

    display_schedule_comparison(file)

    display_lpi(league_id, espn_s2, swid, file)

    year = int(selected_year)
    display_playoff_odds(file, league_id, espn_s2, swid, year)
    if year > 2024:
        display_playoff_odds_by_week(file)
    display_lpi_by_week(file)
    
    display_strength_of_schedule(file)

    display_expected_wins(file)

    display_draft_results(draft_file)
    

    display_biggest_lpi_upsets(file)

    # display_lifetime_record(file, league_id, espn_s2, swid, year_options)

app()