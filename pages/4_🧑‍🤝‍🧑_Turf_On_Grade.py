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
    # year_options = ['2022', '2023', '2024']
    # selected_year = st.selectbox("Select Year", year_options, index=2)
    # league = f"Game of Yards! {selected_year}"
    league = f"Turf On Grade 2.0 2024"
    st.title("🧑‍🤝‍🧑 " + league)
    file = league + ".xlsx"
    # st.title("🏈 " + league)

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
    st.header('Schedule Comparisson')
    st.write('What your record would be (right to left) against everyone elses schedule. Top to bottom shows what each teams record would be with your schedule')
    # league = "FamilyLeague"
    # league = "PennoniYounglings"
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

    df2 = df.style.apply(lambda x: ["background-color: khaki" 
                            if (int(x.split(" ")[0].split('-')[0]) >= top25 and int(x.split(" ")[0].split('-')[0]) < top10) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: gold" if (int(x.split(" ")[0].split('-')[0]) >= top10 and int(x.split(" ")[0].split('-')[0]) < count) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: yellow" if (int(x.split(" ")[0].split('-')[0]) == count) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot25 and int(x.split(" ")[0].split('-')[0]) > bot10) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot10 and int(x.split(" ")[0].split('-')[0]) > 0) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: red; color: white" if (int(x.split(" ")[0].split('-')[0]) == 0) 
                            else "" for x in x], axis = 1, subset=names)
    st.dataframe(df2, width=2000)

    st.header('Strength of Schedule')
    st.write("This ranks each team's schedule from hardest to easiest based on the average number of wins all other teams would have against that schedule. The Avg Wins Against Schedule column shows the hypothetical average record every team would have with that schedule over the season. Lower averages indicate a tougher slate of opponents.")
    df = pd.read_excel(file, sheet_name="Wins Against Schedule")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Wins Against Schedule'])
    st.dataframe(df3)

    st.header('Expected Wins')
    st.write('The Expected Wins column shows how many wins each fantasy football team could expect with an average schedule.')
    st.write('Teams with a higher Expected Win value than their actual wins have overcome tough schedules. Teams with lower Expected Wins have benefitted from weaker schedules.')
    df = pd.read_excel(file, sheet_name="Expected Wins")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Expected Wins'])
    st.dataframe(df3)

    st.header('*NEW* Playoff Odds')
    st.write("This chart shows what each team's odds are of getting each place in the league based on the history of each team's scores this year. It does not take projections or byes into account. It uses the team's scoring data to run 10,000 monte carlo simulations of each matchup given a team's average score and standard deviation.")
    df = pd.read_excel(file, sheet_name="Playoff Odds")
    df = df.set_index("Team")
    # Function to format and round the values
    def format_and_round(cell):
        if isinstance(cell, (int, float)):
            return f"{cell:.2f}"
        return cell

    # Apply the formatting function to the entire DataFrame
    formatted_df = df.applymap(format_and_round)
    playoff_number = 4
    slice_ = df.columns[:playoff_number]
    styled_df = formatted_df.style.set_properties(**{'background-color': 'lightgray'}, subset=slice_)

    # styled_df = formatted_df.style.apply(lambda row: ['background: lightgray' if cell < playoff_number else '' for cell in row], axis=1)
    # df = df.iloc[: , 1:]
    # df.index += 1
    # df3 = df.style.background_gradient(subset=['Expected Wins'])
    st.dataframe(styled_df)

    st.header('Louie Power Index Each Week')
    df = pd.read_excel(file, sheet_name="LPI By Week")
    df.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df = df.set_index("Teams")
    # df = df.iloc[: , 1:]
    # df.index += 1
    st.dataframe(df)

    st.header('The Louie Power Index (LPI)')
    st.write('The Louie Power Index compares Expected Wins and Strength of Schedule to produce a strength of schedule adjusted score.')
    st.write('Positive scores indicate winning against tough schedules. Negative scores mean losing with an easy schedule. Higher scores are better. Scores near zero are neutral.')
    st.write('The LPI shows which direction teams should trend - high scores but worse records suggest improvement ahead. Low scores but better records indicate expected decline.')
    df = pd.read_excel(file, sheet_name="Louie Power Index")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Louie Power Index (LPI)'])
    st.dataframe(df3)

    st.header('Biggest LPI Upsets')
    # st.write('The LPI shows which direction teams should trend - high scores but worse records suggest improvement ahead. Low scores but better records indicate expected decline.')
    df = pd.read_excel(file, sheet_name="Biggest Upsets")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['LPI Difference'])
    st.dataframe(df3)

app()