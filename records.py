def app():
    import pandas as pd
    from operator import itemgetter
    from league import league
    import streamlit as st

    st.header('Schedule Record Matrix')
    st.caption('What your record would be (right to left) against everyone elses schedule. Top to bottom shows what each teams record would be with your schedule')

    file = league()
    df = pd.read_excel(file, sheet_name="Schedule Grid")

    pd.options.mode.chained_assignment = None

    st.dataframe(df, height=500, width=2000)