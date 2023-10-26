def app():
    import pandas as pd
    from operator import itemgetter
    import glob
    import streamlit as st

    pd.options.mode.chained_assignment = None
    st.header('Master List of LPI')
    files = glob.glob('*.xlsx')

    appended_data = []
    leagueList = []
    for file in files:
        leagueName = file.split(".xlsx")[0]
        leagueList.append(leagueName)
        df = pd.read_excel(file, sheet_name="Louie Power Index")
        df["League"] = leagueName
        appended_data.append(df)

    dfFINAL = pd.concat(appended_data)
    dfFINAL = dfFINAL.iloc[: , 1:]
    first_column = dfFINAL.pop('Owner') 
  
    # insert column using insert(position,column_name, 
    # first_column) function 
    dfFINAL.insert(1, 'Owner', first_column) 
    # dfFINAL.index += 1
    df1 = dfFINAL.sort_values(by=['Louie Power Index (LPI)'], ascending=False)
    
    df3 = df1.reset_index(drop=True).style.background_gradient(subset=['Louie Power Index (LPI)']).apply(lambda x: ["background-color: purple; color: white" 
                            if i == leagueList[0]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: skyblue" if i == leagueList[1]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: goldenrod" if i == leagueList[2]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: gray; color: white" if i == leagueList[3]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: green; color: white" if i == leagueList[4]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: maroon; color: white" if i == leagueList[5]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: red; color: white" if i == leagueList[6]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: blue; color: white" if i == leagueList[7]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: yellow" if i == leagueList[8]
                            else "" for i in x], axis = 1)
    st.dataframe(df3, height=2150)

app()