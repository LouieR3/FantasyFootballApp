def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    import glob

    files = glob.glob('*.xlsx')
    dfFINAL = pd.DataFrame()
    for file in files:
        df = pd.read_excel(file, sheet_name="Louie Power Index")
        dfFINAL.append(df)

    dfFINAL = dfFINAL.iloc[: , 1:]
    dfFINAL.index += 1 
    pd.options.mode.chained_assignment = None
    df3 = dfFINAL.style.background_gradient(subset=['Louie Power Index (LPI)'])
    st.dataframe(df3)

