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
    draft_file = f"drafts/EBC League Draft Results {selected_year}.csv"
    
    file = "leagues/" + league + ".xlsx"
    from page_functions import display_playoff_results, display_schedule_comparison, display_strength_of_schedule, display_playoff_odds, display_lpi_by_week, display_expected_wins, display_lpi
    
    display_playoff_results(file)
    

    display_schedule_comparison(file)
    
    display_strength_of_schedule(file)

    display_expected_wins(file)

    display_playoff_odds(file)
    display_lpi_by_week(file)
    
    display_lpi(file)


    df = pd.read_csv(draft_file)
    st.header('Draft Results')
    df = df.drop(columns=['Owner ID'])
    # Increment index to start at 1
    df.index += 1
    AgGrid(df)


    st.header('Biggest LPI Upsets')
    # st.write('The LPI shows which direction teams should trend - high scores but worse records suggest improvement ahead. Low scores but better records indicate expected decline.')
    df = pd.read_excel(file, sheet_name="Biggest Upsets")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['LPI Difference'])
    st.dataframe(df3)

    st.header('Lifetime Record')
    st.write('Select a team and see their record vs all other teams over every year and every game of that league')
 
    selected_team = st.selectbox("Select Team", names)
    def convert_to_int_list(original_list):
        """
        Converts all elements in a list to integers.

        Parameters:
        - original_list (list): A list of elements that can be converted to integers.

        Returns:
        - list: A new list with all elements as integers.
        """
        return [int(item) for item in original_list]

    # Convert to integers
    years = convert_to_int_list(year_options)
    print(years)
    lifetime_record_df, year_df, all_matchups_df = lifetime_record(league_id, espn_s2, swid, years, selected_team)
    
    df4 = lifetime_record_df.style.background_gradient(subset=['Win Percentage'])
    st.dataframe(df4)

    # df5 = year_df.style.background_gradient(subset=['Win Percentage'])
    st.write("Here is this team's record by year:")
    st.dataframe(year_df)

    # st.write("Breakdown a team's performance vs. another team")
 
    # selected_team = st.selectbox("Select Team", names)

app()