def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from league import league

    st.header('The Louie Power Index (LPI)')
    st.caption('This simply compares both the Expected Win total against the Strength of Schedule total to see which teams are best')
    st.caption('It is not an exact science yet, but a negative score is a bad team, any score around 0 is average, and any score above 10 is a true contender')

    file = league()
    df = pd.read_excel(file, sheet_name="Louie Power Index")

    pd.options.mode.chained_assignment = None

    st.dataframe(df, width=2000)