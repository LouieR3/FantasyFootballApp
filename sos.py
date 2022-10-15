def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from league import league

    st.header('Strength of Schedule')
    st.caption('The lower the number, the harder the schedule the team has had. If your average wins against schedule is 1, that means every team in the league would only average 1 win all season with your schedule')

    file = league()
    df = pd.read_excel(file, sheet_name="Strength of Schedule")
    df = df.iloc[: , 1:]
    df.index += 1 
    pd.options.mode.chained_assignment = None
    df3 = df.style.background_gradient(subset=['Avg Wins Against Schedule'])
    st.dataframe(df3)