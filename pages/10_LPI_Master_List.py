def app():
    import pandas as pd
    from operator import itemgetter
    import glob
    import streamlit as st

    pd.options.mode.chained_assignment = None
    st.header('Master List of LPI')
    files = glob.glob('leagues/*.xlsx')

    appended_data = []
    leagueList = []
    for file in files:
        leagueName = file.split("leagues/")[1].split(".xlsx")[0]
        leagueList.append(leagueName)
        df = pd.read_excel(file, sheet_name="Louie Power Index")
        df["League"] = leagueName
        appended_data.append(df)

    dfFINAL = pd.concat(appended_data)
    dfFINAL = dfFINAL.iloc[: , 1:]
    # first_column = dfFINAL.pop('Owner') 
  
    # # insert column using insert(position,column_name, 
    # # first_column) function 
    # dfFINAL.insert(1, 'Owner', first_column) 
    df1 = dfFINAL.sort_values(by=['Louie Power Index (LPI)'], ascending=False)
    df1.index += 1

    option = st.selectbox(
        "Choose a year",
        ("All", "2025", "2024", "2023", "2022", "2021"),
        placeholder="Select year...",
    )
    st.write('You selected:', option)

    if option == "All":
        filtered_df = df1
    else:
        filtered_df = df1[df1['League'].str.contains(option)]
    
    filtered_df.index += 1
    filtered_df.drop(columns=['Owner'])
    df3 = filtered_df.reset_index(drop=True).style.background_gradient(subset=['Louie Power Index (LPI)']).apply(lambda x: ["background-color: purple; color: white" 
                            if i == leagueList[0]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: skyblue" if i == leagueList[1]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: goldenrod" if i == leagueList[2]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: gray; color: white" if i == leagueList[3]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: green; color: white" if i == leagueList[4]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: maroon; color: white" if i == leagueList[5]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: red; color: white" if i == leagueList[6]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: blue; color: white" if i == leagueList[7]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: yellow" if i == leagueList[8]
                            else "" for i in x], axis = 1).apply(lambda x: ["background-color: tan" if i == leagueList[9]
                            else "" for i in x], axis = 1)
    st.dataframe(df3, height=2150, hide_index=True)

app()