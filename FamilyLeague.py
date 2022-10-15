def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st

    st.header('Schedule Record Matrix')
    st.caption('What your record would be (right to left) against everyone elses schedule. Top to bottom shows what each teams record would be with your schedule')# league = "EBCLeague"
    league = "FamilyLeague"
    # league = "PennoniYounglings"
    file = league + ".xlsx"
    df = pd.read_excel(file, sheet_name="Schedule Grid")
    df.index += 1 
    pd.options.mode.chained_assignment = None
    st.dataframe(df, height=460, width=2000)

    st.header('Strength of Schedule')
    st.caption('The lower the number, the harder the schedule the team has had. If your average wins against schedule is 1, that means every team in the league would only average 1 win all season with your schedule')
    df = pd.read_excel(file, sheet_name="Avg Wins Against Schedule")
    df = df.iloc[: , 1:]
    df.index += 1 
    pd.options.mode.chained_assignment = None
    df3 = df.style.background_gradient(subset=['Avg Wins Against Schedule'])
    st.dataframe(df3, height=460)

    st.header('Expected Wins')
    st.caption('This is your average wins for the season across everyones schedule')
    st.caption('If the number is higher than your actual record, you have had an unlucky schedule, and if the number is lower than your record, than you have been getting lucky')
    df = pd.read_excel(file, sheet_name="Expected Wins")
    df = df.iloc[: , 1:]
    df.index += 1 
    pd.options.mode.chained_assignment = None
    df3 = df.style.background_gradient(subset=['Expected Wins'])
    st.dataframe(df3, height=460)

    st.header('The Louie Power Index (LPI)')
    st.caption('This simply compares both the Expected Win total against the Strength of Schedule total to see which teams are best')
    st.caption('It is not an exact science yet, but a negative score is a bad team, any score around 0 is average, and any score above 10 is a true contender')
    df = pd.read_excel(file, sheet_name="Louie Power Index")
    df = df.iloc[: , 1:]
    df.index += 1 
    pd.options.mode.chained_assignment = None
    df3 = df.style.background_gradient(subset=['Louie Power Index (LPI)'])
    st.dataframe(df3, height=460)