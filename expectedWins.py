def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from league import league

    st.header('Expected Wins')
    st.caption('This is your average wins for the season across everyones schedule')
    st.caption('If the number is higher than your actual record, you have had an unlucky schedule, and if the number is lower than your record, than you have been getting lucky')

    file = league()
    df = pd.read_excel(file, sheet_name="Expected Wins")
    df = df.iloc[: , 1:]
    df.index += 1 
    pd.options.mode.chained_assignment = None

    st.dataframe(df)