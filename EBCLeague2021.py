def app():
    import pandas as pd
    from operator import itemgetter
    import streamlit as st

    st.header('Schedule Record Matrix')
    st.caption('What your record would be (right to left) against everyone elses schedule. Top to bottom shows what each teams record would be with your schedule')
    league = "EBCLeague2021"
    # league = "FamilyLeague"
    # league = "PennoniYounglings"
    file = league + ".xlsx"
    print(league)
    df = pd.read_excel(file, sheet_name="Schedule Grid")
    df.index += 1 
    pd.options.mode.chained_assignment = None
    count = 14
    top20 = round(count * 0.8)
    bot20 = round(count * 0.2)
    # def highlight_cellsGood(val):
    #     val1 = str(val.split(" ")[0])
    #     print(val)
    #     val1 = int(val1)
    #     color = 'blue' if val1 >= top20 else ''
    #     print(val1 >= top20)
    #     return 'background-color: {}'.format(color)
    # def highlight_cellsBad(val):
    #     color = 'red' if val <= bot20 else ''
    #     return 'background-color: {}'.format(color)
    # df.style.applymap(highlight_cellsGood)
    # df3 = df.style.applymap(highlight_cellsBad)
    
    def highlight_cells(val):
        print(val)
        color = 'yellow' if val == "8 - 6 - 0" else ''
        return 'background-color: {}'.format(color)

    df.style.applymap(highlight_cells)
    def highlight_cols(val):
        val1 = str(val.split(" ")[0])
        if val1 >= top20:
            color = 'blue' # Dark purple
        elif val <= bot20:
            color = 'red' # Light purple
        return ['background-color: {}'.format(color) for c in val]

    df2 = df.style.apply(lambda x: ["background-color: blue" 
                          if (str(i.split(" ")[0]) >= top20) 
                          else "" for i in x], axis = 1)
    
    # df3 = df2.style.apply(lambda x: ["background-color: red" 
    #                       if (str(i.split(" ")[0]) <= bot20) 
    #                       else "" for i in x], axis = 1)
    st.dataframe(df2, width=2000)

    st.header('Strength of Schedule')
    st.caption('The lower the number, the harder the schedule the team has had. If your average wins against schedule is 1, that means every team in the league would only average 1 win all season with your schedule')
    df = pd.read_excel(file, sheet_name="Wins Against Schedule")
    df = df.iloc[: , 1:]
    df.index += 1 
    pd.options.mode.chained_assignment = None
    df3 = df.style.background_gradient(subset=['Avg Wins Against Schedule'])
    st.dataframe(df3)

    st.header('Expected Wins')
    st.caption('This is your average wins for the season across everyones schedule')
    st.caption('If the number is higher than your actual record, you have had an unlucky schedule, and if the number is lower than your record, than you have been getting lucky')
    df = pd.read_excel(file, sheet_name="Expected Wins")
    df = df.iloc[: , 1:]
    df.index += 1 
    pd.options.mode.chained_assignment = None
    df3 = df.style.background_gradient(subset=['Expected Wins'])
    st.dataframe(df3)

    st.header('The Louie Power Index (LPI)')
    st.caption('This simply compares both the Expected Win total against the Strength of Schedule total to see which teams are best')
    st.caption('It is not an exact science yet, but a negative score is a bad team, any score around 0 is average, and any score above 10 is a true contender')
    df = pd.read_excel(file, sheet_name="Louie Power Index")
    df = df.iloc[: , 1:]
    df.index += 1 
    pd.options.mode.chained_assignment = None
    df3 = df.style.background_gradient(subset=['Louie Power Index (LPI)'])
    st.dataframe(df3)