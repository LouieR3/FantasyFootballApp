def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from calcPercent import percent

    league = "Pennoni Younglings 2023"
    st.title("🏈 " + league)
    st.header('Schedule Comparisson')
    st.write('What your record would be (right to left) against everyone elses schedule. Top to bottom shows what each teams record would be with your schedule')
    # league = "EBCLeague"
    # league = "FamilyLeague"
    file = league + ".xlsx"
    df = pd.read_excel(file, sheet_name="Schedule Grid")
    df.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df['Teams'] = df['Teams'].replace({
        'PAI Athletic Director': 'PAI India Division Manager',
        'Team Corner Office': 'Pennoni Adjacent',
        "Rizzo's Crash Test Dummy": "Prahlad's Ghost",
        "Girth Brooks": "Bli Erinker"
    })
    df = df.rename(columns={
        'PAI Athletic Director': 'PAI India Division Manager',
        'Team Corner Office': 'Pennoni Adjacent',
        "Rizzo's Crash Test Dummy": "Prahlad's Ghost",
        "Girth Brooks": "Bli Erinker"
    })
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
    df2 = df.style.apply(lambda x: ["background-color: white" if (int(x.split(" ")[0].split('-')[0]) >= top25 and int(x.split(" ")[0].split('-')[0]) < top10) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: gold" if (int(x.split(" ")[0].split('-')[0]) >= top10 and int(x.split(" ")[0].split('-')[0]) < count) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: goldenrod" if (int(x.split(" ")[0].split('-')[0]) == count) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot25 and int(x.split(" ")[0].split('-')[0]) > bot10) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: red; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot10 and int(x.split(" ")[0].split('-')[0]) > 0) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: maroon; color: white" if (int(x.split(" ")[0].split('-')[0]) == 0) else "" for x in x], axis=1, subset=names)
    # df2= df
    st.dataframe(df2, height=460, width=2000)

    st.header('Strength of Schedule')
    st.write("This ranks each team's schedule from hardest to easiest based on the average number of wins all other teams would have against that schedule. The Avg Wins Against Schedule column shows the hypothetical average record every team would have with that schedule over the season. Lower averages indicate a tougher slate of opponents.")
    df = pd.read_excel(file, sheet_name="Wins Against Schedule")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Wins Against Schedule'])
    st.dataframe(df3, height=460)

    st.header('Expected Wins')
    st.write('The Expected Wins column shows how many wins each fantasy football team could expect with an average schedule.')
    st.write('Teams with a higher Expected Win value than their actual wins have overcome tough schedules. Teams with lower Expected Wins have benefitted from weaker schedules.')
    df = pd.read_excel(file, sheet_name="Expected Wins")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Expected Wins'])
    st.dataframe(df3, height=460)

    st.header('*NEW* Playoff Odds')
    st.write("This chart shows what each team's odds are of getting each place in the league based on the history of each team's scores this year. It does not take projections or byes into account. It uses the team's scoring data to run 10,000 monte carlo simulations of each matchup given a team's average score and standard deviation.")
    df = pd.read_excel(file, sheet_name="Playoff Odds")
    df = df.set_index("Teams")
    # df = df.iloc[: , 1:]
    # df.index += 1
    # df3 = df.style.background_gradient(subset=['Expected Wins'])
    st.dataframe(df, height=460)

    st.header('The Louie Power Index (LPI)')
    st.write('The Louie Power Index compares Expected Wins and Strength of Schedule to produce a strength of schedule adjusted score.')
    st.write('Positive scores indicate winning against tough schedules. Negative scores mean losing with an easy schedule. Higher scores are better. Scores near zero are neutral.')
    st.write('The LPI shows which direction teams should trend - high scores but worse records suggest improvement ahead. Low scores but better records indicate expected decline.')
    df = pd.read_excel(file, sheet_name="Louie Power Index")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Louie Power Index (LPI)'])
    st.dataframe(df3, height=460)

app()