def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from calcPercent import percent
    from playoffNum import playoff_num

    league_id = 558148583
    espn_s2 = "AEAVdXHc27USh4ku3cV29OmfzPAysyGlSqIQuU0%2FX2OR2yXn4P51Fbq0rmxpRhWFjwLehTCw6uZ7a6RhnamZ2CKnsleRO0UZ9bnpbNSMC9NR%2BvLkrqEniQKURmJFcf9NnF9ee36YYaHJwKdzxzpcHJfuV8MXumVPBRhOJdLWRL4RsnxcDa0R8kztme9xMvULhkxtIeK9nZWI%2FcKD1lp%2B%2F2CqmeOAx5ddZssKEUT3l%2BORqAyEkH%2BvhicLfAzrLNsKQUpp%2FBuHavXfKvFSX%2BbE7DyBjC7XvvOjezSdMCpiHh0Ys5SdTeGXlPSN%2F4Tq%2FFZQJVs%3D"
    swid='{668E3A23-4B03-4D9E-9804-4C9D479F4E8F}'

    # Initialize the dropdown for year selection
    year_options = ['2022', '2023', '2024', '2025']
    selected_year = '2025'
    
    # selected_year = st.selectbox("Select Year", year_options, index=3)  # Defaults to 2024
    league = f"Ross' Fantasy League {selected_year}"
    file = "leagues/" + league + ".xlsx"
    st.title("🏈 " + league)
    # Extract the league name without the year
    league_name = " ".join(league.split()[:-1])  # Removes the year from the league string
    draft_file = f"drafts/{league_name} Draft Results {selected_year}.csv"
    
    from page_functions import display_playoff_results, display_schedule_comparison, display_strength_of_schedule, display_playoff_odds
    from page_functions import display_lifetime_record, display_biggest_lpi_upsets, display_lpi_by_week, display_expected_wins, display_lpi, display_draft_results
    
    display_playoff_results(file)

    display_schedule_comparison(file)

    display_lpi(league_id, espn_s2, swid, file)

    year = int(selected_year)
    display_playoff_odds(file, league_id, espn_s2, swid, year)
    display_lpi_by_week(file)
    
    display_strength_of_schedule(file)

    display_expected_wins(file)

    display_draft_results(draft_file)

    display_biggest_lpi_upsets(file)

    # display_lifetime_record(file, league_id, espn_s2, swid, year_options)

app()