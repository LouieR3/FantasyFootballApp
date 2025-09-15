def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from calcPercent import percent
    from playoffNum import playoff_num

    league_id = 1118513122
    espn_s2='AECbYb8WaMMCKHklAi740KXDsHbXHTaW5mI%2FLPUegrKbIb6MRovW0L4NPTBpsC%2Bc2%2Fn7UeX%2Bac0lk3KGEwyeI%2FgF9WynckxWNIfe8m8gh43s68UyfhDj5K187Fj5764WUA%2BTlCh1AF04x9xnKwwsneSvEng%2BfACneWjyu7hJy%2FOVWsHlEm3nfMbU7WbQRDBRfkPy7syz68C4pgMYN2XaU1kgd9BRj9rwrmXZCvybbezVEOEsApniBWRtx2lD3yhJnXYREAupVlIbRcd3TNBP%2F5Frfr6pnMMfUZrR9AP1m1OPGcQ0bFaZbJBoAKdWDk%2F6pJs%3D'
    swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}'

    # Initialize the dropdown for year selection
    year_options = ['2024', '2025']
    selected_year = st.selectbox("Select Year", year_options, index=1)  # Defaults to 2024
    # selected_year = '2024'
    # league = f"Game of Yards! {selected_year}"
    league = f"Turf On Grade 2.0 {selected_year}"
    st.title("🧑‍🤝‍🧑 " + league)
    file = "leagues/" + league + ".xlsx"
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
    # display_playoff_odds(file, league_id, espn_s2, swid, year)
    display_lpi_by_week(file)

    display_lpi(league_id, espn_s2, swid, file)

    display_draft_results(draft_file)
    

    display_biggest_lpi_upsets(file)

    # display_lifetime_record(file, league_id, espn_s2, swid, '2024')

app()