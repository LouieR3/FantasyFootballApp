def app():
    import pandas as pd
    from operator import itemgetter
    import glob
    import streamlit as st

    pd.options.mode.chained_assignment = None
    st.header('Master List of LPI')
    files = glob.glob('*.xlsx')

    appended_data = []
    for file in files:
        df = pd.read_excel(file, sheet_name="Louie Power Index")
        appended_data.append(df)

    dfFINAL = pd.concat(appended_data)
    dfFINAL = dfFINAL.iloc[: , 1:]
    # dfFINAL.index += 1
    df1 = dfFINAL.sort_values(by=['Louie Power Index (LPI)'], ascending=False)
    
    df3 = df1.reset_index(drop=True).style.background_gradient(subset=['Louie Power Index (LPI)'])
    st.dataframe(df3, height=2150)

