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
    year_options = ['2022', '2023', '2024']
    
    selected_year = st.selectbox("Select Year", year_options, index=2)  # Defaults to 2024
    # st.title(f'🍝 Las League {selected_year}')
    league = f"THE BEST OF THE BEST {selected_year}"
    file = league + ".xlsx"
    st.title("🏈 " + league)
    # Try reading the "Playoff Results" sheet and display it if it exists
    try:
        playoff_results_df = pd.read_excel(file, sheet_name="Playoff Results")

        # Drop unnecessary columns
        playoff_results_df = playoff_results_df.drop(columns=["Total Points 1", "Total Points 2"])

        # Style the DataFrame
        def style_playoff_results(df):
            def highlight_championship_and_winner(row):
                # Highlight the "Round" column if it's "Championship"
                round_color = 'background-color: gold' if row["Round"] == "Championship" else ''
                # Highlight the "Winner" column
                winner_color = ['background-color: gold' if (col == "Winner" and row["Round"] == "Championship") else '' for col in df.columns]
                return [round_color] + winner_color[1:]

            return df.style.apply(highlight_championship_and_winner, axis=1)

        # Apply styling and remove the index
        styled_playoff_results = style_playoff_results(playoff_results_df)

        st.header('Season Results')
        st.dataframe(styled_playoff_results, width=2000, hide_index=True)
    except Exception as e:
        st.write(e)
    # st.title(f'🍝 Las League 2024')
    st.header('Schedule Comparisson')
    st.write('What your record would be (right to left) against everyone elses schedule. Top to bottom shows what each teams record would be with your schedule')

    # Create the league string based on the selected year
    # league = f"THE BEST OF THE BEST 2024"
    
    file = league + ".xlsx"
    df = pd.read_excel(file, sheet_name="Schedule Grid")
    df.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    
    df = df.set_index("Teams")
    pd.options.mode.chained_assignment = None
    names = []
    for col in df.columns:
        if col != "Teams":
            names.append(col)
    
    percentList = percent(file)
    count = percentList[0]
    top25 = percentList[1]
    bot25 = percentList[2]
    top10 = percentList[3]
    bot10 = percentList[4]

    # df2 = df.style.apply(lambda x: ["background-color: white" if (int(x.split(" ")[0].split('-')[0]) >= top25 and int(x.split(" ")[0].split('-')[0]) < top10) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: gold" if (int(x.split(" ")[0].split('-')[0]) >= top10 and int(x.split(" ")[0].split('-')[0]) < count) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: goldenrod" if (int(x.split(" ")[0].split('-')[0]) == count) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot25 and int(x.split(" ")[0].split('-')[0]) > bot10) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: red; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot10 and int(x.split(" ")[0].split('-')[0]) > 0) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: maroon; color: white" if (int(x.split(" ")[0].split('-')[0]) == 0) else "" for x in x], axis=1, subset=names)
    # df2 = df.style.apply(lambda x: ["background-color: khaki" 
    #                         if (int(i.split(" ")[0]) >= top25 and int(i.split(" ")[0]) < top10) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: gold" if (int(i.split(" ")[0]) >= top10 and int(i.split(" ")[0]) < count) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: goldenrod" if (int(i.split(" ")[0]) == count) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(i.split(" ")[0]) <= bot25 and int(i.split(" ")[0]) > bot10) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: red; color: white" if (int(i.split(" ")[0]) <= bot10 and int(i.split(" ")[0]) > 0) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: maroon; color: white" if (int(i.split(" ")[0]) == 0) 
    #                         else "" for i in x], axis = 1, subset=names)
        # df2 = df.style.apply(lambda x: ["background-color: khaki" 
    #                         if (int(i.split(" ")[0]) >= top25 and int(i.split(" ")[0]) < top10) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: gold" if (int(i.split(" ")[0]) >= top10 and int(i.split(" ")[0]) < count) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: goldenrod" if (int(i.split(" ")[0]) == count) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(i.split(" ")[0]) <= bot25 and int(i.split(" ")[0]) > bot10) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: red; color: white" if (int(i.split(" ")[0]) <= bot10 and int(i.split(" ")[0]) > 0) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: maroon; color: white" if (int(i.split(" ")[0]) == 0) 
    #                         else "" for i in x], axis = 1, subset=names)

    df2 = df.style.apply(lambda x: ["background-color: khaki" 
                            if (int(x.split(" ")[0].split('-')[0]) >= top25 and int(x.split(" ")[0].split('-')[0]) < top10) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: gold" if (int(x.split(" ")[0].split('-')[0]) >= top10 and int(x.split(" ")[0].split('-')[0]) < count) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: yellow" if (int(x.split(" ")[0].split('-')[0]) == count) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot25 and int(x.split(" ")[0].split('-')[0]) > bot10) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot10 and int(x.split(" ")[0].split('-')[0]) > 0) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: red; color: white" if (int(x.split(" ")[0].split('-')[0]) == 0) 
                            else "" for x in x], axis = 1, subset=names)
    st.dataframe(df2, width=2000, height=540)

    st.header('Strength of Schedule')
    st.write("This ranks each team's schedule from hardest to easiest based on the average number of wins all other teams would have against that schedule. The Avg Wins Against Schedule column shows the hypothetical average record every team would have with that schedule over the season. Lower averages indicate a tougher slate of opponents.")
    df = pd.read_excel(file, sheet_name="Wins Against Schedule")
    
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Wins Against Schedule'])
    st.dataframe(df3, height=540)

    st.header('Expected Wins')
    st.write('The Expected Wins column shows how many wins each fantasy football team could expect with an average schedule.')
    st.write('Teams with a higher Expected Win value than their actual wins have overcome tough schedules. Teams with lower Expected Wins have benefitted from weaker schedules.')
    df = pd.read_excel(file, sheet_name="Expected Wins")
    
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Expected Wins'])
    st.dataframe(df3, height=540)

    st.header('*UNDER CONSTRUCTION* Playoff Odds')
    st.write("This chart shows what each team's odds are of getting each place in the league based on the history of each team's scores this year. It does not take projections or byes into account. It uses the team's scoring data to run 10,000 monte carlo simulations of each matchup given a team's average score and standard deviation.")
    df = pd.read_excel(file, sheet_name="Playoff Odds")
    
    df = df.set_index("Team")
    df = df.sort_values(by='Chance of making playoffs', ascending=False)
    # Function to format and round the values
    def format_and_round(cell):
        if isinstance(cell, (int, float)):
            return f"{cell:.2f}"
        return cell

    # Apply the formatting function to the entire DataFrame
    formatted_df = df.applymap(format_and_round)
    # playoff_number = playoff_num(file)
    playoff_number = 8
    slice_ = df.columns[:playoff_number]
    styled_df = formatted_df.style.set_properties(**{'background-color': 'lightgray'}, subset=slice_)

    # styled_df = formatted_df.style.apply(lambda row: ['background: lightgray' if cell < playoff_number else '' for cell in row], axis=1)
    # df = df.iloc[: , 1:]
    # df.index += 1
    # df3 = df.style.background_gradient(subset=['Expected Wins'])
    st.dataframe(styled_df, height=540)

    st.header('Louie Power Index Each Week')
    df = pd.read_excel(file, sheet_name="LPI By Week")
    df.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    
    df = df.set_index("Teams")
    # df = df.iloc[: , 1:]
    # df.index += 1
    st.dataframe(df, height=540)

    st.header('The Louie Power Index (LPI)')
    st.write('The Louie Power Index compares Expected Wins and Strength of Schedule to produce a strength of schedule adjusted score.')
    st.write('Positive scores indicate winning against tough schedules. Negative scores mean losing with an easy schedule. Higher scores are better. Scores near zero are neutral.')
    st.write('The LPI shows which direction teams should trend - high scores but worse records suggest improvement ahead. Low scores but better records indicate expected decline.')
    df = pd.read_excel(file, sheet_name="Louie Power Index")
    
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Louie Power Index (LPI)'])
    st.dataframe(df3, height=560)

    try:
        df = pd.read_excel(file, sheet_name="Playoff Results")
        st.header('Playoff Results')

        # Increment index to start at 1
        df.index += 1

        # Round the specified columns to the 100th
        columns_to_round = ["Score 1", "Total Points 1", "Score 2", "Total Points 2"]
        df[columns_to_round] = df[columns_to_round].round(2).astype(str)

        def style_gold_and_bold(df):
            """
            Styles the last row bright gold, the 2nd and 3rd to last rows muted gold,
            and bolds the winning team's columns.
            """
            def highlight_rows(row):
                # Index of the row in the DataFrame
                row_idx = row.name
                
                # Last row: bright gold
                if row_idx == len(df):
                    return ['background-color: #FFD700'] * len(row)
                # Second and third to last rows: muted gold
                elif row_idx == len(df) - 1 or row_idx == len(df) - 2:
                    return ['background-color: #ffe064'] * len(row)
                # Default: no styling
                return [''] * len(row)

            def bold_winner(row):
                # Determine the winner columns
                winner = row["Winner"]
                print("BOLD ASSESS:")
                print(winner == row["Team 1"])
                if winner == row["Team 1"]:
                    return ['font-weight: bold' if col.endswith("1") else '' for col in df.columns]
                elif winner == row["Team 2"]:
                    return ['font-weight: bold' if col.endswith("2") else '' for col in df.columns]
                return [''] * len(row)

            # Combine the row and column styles
            styled = df.style.apply(highlight_rows, axis=1).apply(bold_winner, axis=1)
            return styled

        # Apply the styling function
        styled_df = style_gold_and_bold(df)

        # Display the styled DataFrame
        st.dataframe(styled_df)
    except:
        print("No Playoffs Yet")

    # st.header('Upset Factor of Previous Week')
    # st.write('This simply compares both the Expected Win total against the Strength of Schedule total to see which teams are best')
    # df = pd.read_excel(file, sheet_name="Louie Power Index")
    # df = df.iloc[: , 1:]
    # df.index += 1
    # df3 = df.style.background_gradient(subset=['Louie Power Index (LPI)'])
    # st.dataframe(df3)

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
    # year_options = ['2018', '2019', '2020', '2021', '2022', '2023', '2024']
    years = convert_to_int_list(year_options)
    print(years)
    lifetime_record_df, year_df, all_matchups_df = lifetime_record(league_id, espn_s2, swid, years, selected_team)
    
    df4 = lifetime_record_df.style.background_gradient(subset=['Win Percentage'])
    st.dataframe(df4, height=540)

    # df5 = year_df.style.background_gradient(subset=['Win Percentage'])
    st.write("Here is this team's record by year:")
    st.dataframe(year_df)

    # st.write("Breakdown a team's performance vs. another team")
 
    # selected_team = st.selectbox("Select Team", names)

app()