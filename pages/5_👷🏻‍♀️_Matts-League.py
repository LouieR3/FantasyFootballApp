def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from calcPercent import percent
    from playoffNum import playoff_num
    from lifetime_record import lifetime_record

    league_id = 1049459
    espn_s2='AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D'
    swid='{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}'

    # Initialize the dropdown for year selection
    year_options = ['2022', '2023', '2024', '2025']
    selected_year = '2025'
    
    # selected_year = st.selectbox("Select Year", year_options, index=3)  # Defaults to 2024
    league = f"BP- Loudoun 2025 {selected_year}"
    file = "leagues/" + league + ".xlsx"
    st.title("🏈 " + league)
    # Extract the league name without the year
    league_name = " ".join(league.split()[:-1])  # Removes the year from the league string
    draft_file = f"drafts/{league_name} Draft Results {selected_year}.csv"
    
    from page_functions import display_playoff_results, display_schedule_comparison, display_strength_of_schedule, display_playoff_odds
    from page_functions import display_lifetime_record, display_biggest_lpi_upsets, display_lpi_by_week, display_expected_wins, display_lpi, display_draft_results
    
    display_playoff_results(file)

    display_schedule_comparison(file)
    
    display_strength_of_schedule(file)

    display_expected_wins(file)

    year = int(selected_year)
    display_playoff_odds(file, league_id, espn_s2, swid, year)
    display_lpi_by_week(file)

    display_lpi(file)

    display_draft_results(draft_file)
    

    display_biggest_lpi_upsets(file)

    # display_lifetime_record(file, league_id, espn_s2, swid, year_options)

app()