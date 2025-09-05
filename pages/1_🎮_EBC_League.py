def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from calcPercent import percent
    from playoffNum import playoff_num
    from lifetime_record import lifetime_record
    from st_aggrid import AgGrid

    league_id = 1118513122
    espn_s2='AEB%2Bzu7FGxYPXt8rgNkQWTV8c4yxT2T3KNZZVkZUVKh9TOdH7iUalV08hSloqYJ5dDtxZVK6d4WC503CH3mH0UkNCPOgbTXYz44W3IJtXsplT%2BLoqNYCU8T7W1HU%2Fgh4PnasvHIkDZgTZFWkUFhcLA0eLkwH8AvYe2%2FCIlhdk7%2FdMeiM0ijsS8vhSYYB8LUhSrB0kuTXE2v85gSIrJQSbs3mPvP5p6pFr3w2OxWicVi9pe8p3eVDhSOLiPMYrPgpuL%2FLBZIGHxhKz5lzGRSL2uTA'
    swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}'

    # Initialize the dropdown for year selection
    year_options = ['2021', '2022', '2023', '2024']
    
    selected_year = st.selectbox("Select Year", year_options, index=3)  # Defaults to 2024
    st.title(f'🎮 EBC League {selected_year}')
    
    # Create the league string based on the selected year
    league = f"EBC League {selected_year}"
    # Extract the league name without the year
    league_name = " ".join(league.split()[:-1])  # Removes the year from the league string
    draft_file = f"drafts/{league_name} Draft Results {selected_year}.csv"
    
    file = "leagues/" + league + ".xlsx"

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

    display_lifetime_record(file, league_id, espn_s2, swid, year_options)
   

    # st.write("Breakdown a team's performance vs. another team")
 
    # selected_team = st.selectbox("Select Team", names)

app()