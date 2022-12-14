def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st
    from calcPercent import percent
    import numpy as np

    st.header('Schedule Record Matrix')
    st.caption('What your record would be (right to left) against everyone elses schedule. Top to bottom shows what each teams record would be with your schedule')
    league = "EBC League 2021"
    # league = "FamilyLeague"
    # league = "PennoniYounglings"
    file = league + ".xlsx"
    print(league)
    df = pd.read_excel(file, sheet_name="Schedule Grid")
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

    # def highlight_cell(col, col_label, row_label):
    # # check if col is a column we want to highlight
    #     if col.name == col_label:
    #         # a boolean mask where True represents a row we want to highlight
    #         mask = (col.index == row_label)
    #         # return an array of string styles (e.g. ["", "background-color: yellow"])
    #         return ["background-color: gray" if val_bool else "" for val_bool in mask]
    #     else:
    #         # return an array of empty strings that has the same size as col (e.g. ["",""])
    #         return np.full_like(col, "", dtype="str")
    # count = 0
    # for team in names:
    #     df.style.apply(highlight_cell, col_label=team, row_label=count)
    #     count += 1
    # df2 = df.style.apply(highlight_cell, col_label="A", row_label="b")
    st.dataframe(df2, width=2000)

    st.header('Strength of Schedule')
    st.caption('The lower the number, the harder the schedule the team has had. If your average wins against schedule is 1, that means every team in the league would only average 1 win all season with your schedule')
    df = pd.read_excel(file, sheet_name="Wins Against Schedule")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Avg Wins Against Schedule'])
    st.dataframe(df3)

    st.header('Expected Wins')
    st.caption('This is your average wins for the season across everyones schedule')
    st.caption('If the number is higher than your actual record, you have had an unlucky schedule, and if the number is lower than your record, than you have been getting lucky')
    df = pd.read_excel(file, sheet_name="Expected Wins")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Expected Wins'])
    st.dataframe(df3)

    st.header('The Louie Power Index (LPI)')
    st.caption('This simply compares both the Expected Win total against the Strength of Schedule total to see which teams are best')
    st.caption('It is not an exact science yet, but a negative score is a bad team, any score around 0 is average, and any score above 10 is a true contender')
    df = pd.read_excel(file, sheet_name="Louie Power Index")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Louie Power Index (LPI)'])
    st.dataframe(df3)