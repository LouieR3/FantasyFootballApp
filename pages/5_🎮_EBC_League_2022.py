def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from calcPercent import percent
    from playoffNum import playoff_num

    st.title('🎮 EBC League 2022')
    st.header('Schedule Comparisson')
    st.write('What your record would be (right to left) against everyone elses schedule. Top to bottom shows what each teams record would be with your schedule')
    league = "EBC League 2022"
    # league = "FamilyLeague"
    # league = "PennoniYounglings"
    file = league + ".xlsx"
    df = pd.read_excel(file, sheet_name="Schedule Grid")
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
                            if (int(i.split(" ")[0]) >= top25 and int(i.split(" ")[0]) < top10) 
                            else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: gold" if (int(i.split(" ")[0]) >= top10 and int(i.split(" ")[0]) < count) 
                            else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: goldenrod" if (int(i.split(" ")[0]) == count) 
                            else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(i.split(" ")[0]) <= bot25 and int(i.split(" ")[0]) > bot10) 
                            else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: red; color: white" if (int(i.split(" ")[0]) <= bot10 and int(i.split(" ")[0]) > 0) 
                            else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: maroon; color: white" if (int(i.split(" ")[0]) == 0) 
                            else "" for i in x], axis = 1, subset=names)
    # Custom function to apply styling based on wins
    # def style_wins(val):
    #     wins = int(val.split(' ')[0])  # Extract wins as an integer
    #     if wins >= top10:  # Top 10% (10 wins out of 10 weeks)
    #         return 'background-color: gold'
    #     elif wins >= top25:  # Top 25% (8 or 9 wins out of 10 weeks)
    #         return 'background-color: goldenrod'
    #     elif wins <= bot25:  # Bottom 25% (0 to 2 wins out of 10 weeks)
    #         return 'background-color: tomato; color: white'
    #     elif wins <= bot10:  # Bottom 10% (0 to 1 wins out of 10 weeks)
    #         return 'background-color: red; color: white'
    #     else:  # Any other case
    #         return 'background-color: white'

    # # Apply the custom styling function to the 'Wins' column
    # styled_df = df.style.applymap(style_wins, subset=['Wins'])
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
    playoff_number = playoff_num(file)
    slice_ = df.columns[:playoff_number]
    styled_df = formatted_df.style.set_properties(**{'background-color': 'lightgray'}, subset=slice_)
    st.dataframe(styled_df)

    st.header('Louie Power Index Each Week')
    df = pd.read_excel(file, sheet_name="LPI By Week")
    df.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df = df.set_index("Teams")
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

    # st.header('Upset Factor of Previous Week')
    # st.write('This simply compares both the Expected Win total against the Strength of Schedule total to see which teams are best')
    # df = pd.read_excel(file, sheet_name="Louie Power Index")
    # df = df.iloc[: , 1:]
    # df.index += 1
    # df3 = df.style.background_gradient(subset=['Louie Power Index (LPI)'])
    # st.dataframe(df3)

app()