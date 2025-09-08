import pandas as pd
import streamlit as st
from calcPercent import percent
from playoffNum import playoff_num
from st_aggrid import AgGrid
from lifetime_record import lifetime_record
from streamlit_echarts5 import st_echarts
from pyecharts.charts import Line
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts

def display_playoff_results(file):
    try:
        df = pd.read_excel(file, sheet_name="Playoff Results")
        st.header('Playoff Results')

        # Increment index to start at 1
        df.index += 1

        # Round the specified columns to the 100th
        columns_to_round = ["Score 1", "Total Points 1", "Score 2", "Total Points 2"]
        df[columns_to_round] = df[columns_to_round].round(2).astype(str)

        def style_gold_and_bold(df):
            """
            Styles the last row bright gold, the 2nd and 3rd to last rows muted gold,
            and bolds the winning team's columns.
            """
            def highlight_rows(row):
                # Index of the row in the DataFrame
                row_idx = row.name
                
                # Last row: bright gold
                if row_idx == len(df):
                    return ['background-color: #FFD700'] * len(row)
                # Second and third to last rows: muted gold
                elif row_idx == len(df) - 1 or row_idx == len(df) - 2:
                    return ['background-color: #ffe064'] * len(row)
                # Default: no styling
                return [''] * len(row)

            def bold_winner(row):
                # Determine the winner columns
                winner = row["Winner"]
                if winner == row["Team 1"]:
                    return ['font-weight: bold' if col.endswith("1") else '' for col in df.columns]
                elif winner == row["Team 2"]:
                    return ['font-weight: bold' if col.endswith("2") else '' for col in df.columns]
                return [''] * len(row)

            # Combine the row and column styles
            styled = df.style.apply(highlight_rows, axis=1).apply(bold_winner, axis=1)
            return styled

        # Apply the styling function
        styled_df = style_gold_and_bold(df)

        # Display the styled DataFrame
        st.dataframe(styled_df)
    except:
        print("No Playoffs Yet")

def display_schedule_comparison(file):
    st.header('Schedule Comparisson')
    st.write('What your record would be (right to left) against everyone elses schedule. Top to bottom shows what each teams record would be with your schedule')

    df = pd.read_excel(file, sheet_name="Schedule Grid")
    df.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    
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

    if len(names) <= 10:
        height = "auto"
    else:
        height = 460 + (len(names) - 12) * 40
    print("HEIGHT:", height)
    # df2 = df.style.apply(lambda x: ["background-color: white" if (int(x.split(" ")[0].split('-')[0]) >= top25 and int(x.split(" ")[0].split('-')[0]) < top10) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: gold" if (int(x.split(" ")[0].split('-')[0]) >= top10 and int(x.split(" ")[0].split('-')[0]) < count) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: goldenrod" if (int(x.split(" ")[0].split('-')[0]) == count) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot25 and int(x.split(" ")[0].split('-')[0]) > bot10) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: red; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot10 and int(x.split(" ")[0].split('-')[0]) > 0) else "" for x in x], axis=1, subset=names).apply(lambda x: ["background-color: maroon; color: white" if (int(x.split(" ")[0].split('-')[0]) == 0) else "" for x in x], axis=1, subset=names)
    # df2 = df.style.apply(lambda x: ["background-color: khaki" 
    #                         if (int(i.split(" ")[0]) >= top25 and int(i.split(" ")[0]) < top10) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: gold" if (int(i.split(" ")[0]) >= top10 and int(i.split(" ")[0]) < count) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: goldenrod" if (int(i.split(" ")[0]) == count) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(i.split(" ")[0]) <= bot25 and int(i.split(" ")[0]) > bot10) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: red; color: white" if (int(i.split(" ")[0]) <= bot10 and int(i.split(" ")[0]) > 0) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: maroon; color: white" if (int(i.split(" ")[0]) == 0) 
    #                         else "" for i in x], axis = 1, subset=names)
        # df2 = df.style.apply(lambda x: ["background-color: khaki" 
    #                         if (int(i.split(" ")[0]) >= top25 and int(i.split(" ")[0]) < top10) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: gold" if (int(i.split(" ")[0]) >= top10 and int(i.split(" ")[0]) < count) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: goldenrod" if (int(i.split(" ")[0]) == count) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(i.split(" ")[0]) <= bot25 and int(i.split(" ")[0]) > bot10) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: red; color: white" if (int(i.split(" ")[0]) <= bot10 and int(i.split(" ")[0]) > 0) 
    #                         else "" for i in x], axis = 1, subset=names).apply(lambda x: ["background-color: maroon; color: white" if (int(i.split(" ")[0]) == 0) 
    #                         else "" for i in x], axis = 1, subset=names)

    df2 = df.style.apply(lambda x: ["background-color: khaki" 
                            if (int(x.split(" ")[0].split('-')[0]) >= top25 and int(x.split(" ")[0].split('-')[0]) < top10) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: gold" if (int(x.split(" ")[0].split('-')[0]) >= top10 and int(x.split(" ")[0].split('-')[0]) < count) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: yellow" if (int(x.split(" ")[0].split('-')[0]) == count) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot25 and int(x.split(" ")[0].split('-')[0]) > bot10) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: tomato; color: white" if (int(x.split(" ")[0].split('-')[0]) <= bot10 and int(x.split(" ")[0].split('-')[0]) > 0) 
                            else "" for x in x], axis = 1, subset=names).apply(lambda x: ["background-color: red; color: white" if (int(x.split(" ")[0].split('-')[0]) == 0) 
                            else "" for x in x], axis = 1, subset=names)
    st.dataframe(df2, height=height, width=2000)

def display_strength_of_schedule(file):
    """
    Reads the 'Wins Against Schedule' sheet from the given Excel file
    and displays it with a gradient background in Streamlit.

    Parameters:
    - file (str): Path to the Excel file.
    """
    st.header('Strength of Schedule')
    st.write("This ranks each team's schedule from hardest to easiest based on the average number of wins all other teams would have against that schedule. The Avg Wins Against Schedule column shows the hypothetical average record every team would have with that schedule over the season. Lower averages indicate a tougher slate of opponents.")
    
    # Read the Excel sheet
    df = pd.read_excel(file, sheet_name="Wins Against Schedule")
    
    # Process the DataFrame
    df = df.iloc[:, 1:]
    df.index += 1
    
    # Apply gradient styling
    df_styled = df.style.background_gradient(subset=['Wins Against Schedule'])
    df_names = pd.read_excel(file, sheet_name="Schedule Grid")
    # Display the styled DataFrame
    df_names.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df_names = df_names.set_index("Teams")
    pd.options.mode.chained_assignment = None
    names = []
    for col in df_names.columns:
        if col != "Teams":
            names.append(col)
    if len(names) <= 10:
        height = "auto"
    else:
        height = 460 + (len(names) - 12) * 40
    # Display the styled DataFrame
    st.dataframe(df_styled, height=height)

def display_expected_wins(file):
    """
    Reads the 'Expected Wins' sheet from the given Excel file
    and displays it with a gradient background in Streamlit.

    Parameters:
    - file (str): Path to the Excel file.
    """
    st.header('Expected Wins')
    st.write('The Expected Wins column shows how many wins each fantasy football team could expect with an average schedule.')
    st.write('Teams with a higher Expected Win value than their actual wins have overcome tough schedules. Teams with lower Expected Wins have benefitted from weaker schedules.')
    # Read the Excel sheet
    df = pd.read_excel(file, sheet_name="Expected Wins")
    
    # Process the DataFrame
    df = df.iloc[: , 1:]
    df.index += 1
    # Apply gradient styling
    df3 = df.style.background_gradient(subset=['Expected Wins'])
    
    df_names = pd.read_excel(file, sheet_name="Schedule Grid")
    # Display the styled DataFrame
    df_names.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df_names = df_names.set_index("Teams")
    pd.options.mode.chained_assignment = None
    names = []
    for col in df_names.columns:
        if col != "Teams":
            names.append(col)
    if len(names) <= 10:
        height = "auto"
    else:
        height = 460 + (len(names) - 12) * 40
    # Display the styled DataFrame
    st.dataframe(df3, height=height)


def display_playoff_odds(file, league_id, espn_s2, swid, year):
    """
    Displays the Playoff Odds table with formatting in Streamlit.

    Parameters:
    - file (str): Path to the Excel file.
    """
    st.header('*UNDER CONSTRUCTION* Playoff Odds')
    st.write("This chart shows what each team's odds are of getting each place in the league based on the history of each team's scores this year. It does not take projections or byes into account. It uses the team's scoring data to run 10,000 monte carlo simulations of each matchup given a team's average score and standard deviation.")
    
    # Read the Playoff Odds sheet
    df = pd.read_excel(file, sheet_name="Playoff Odds")
    df = df.set_index("Team")
    
    # Function to format and round the values
    def format_and_round(cell):
        if isinstance(cell, (int, float)):
            return f"{cell:.2f}"
        return cell

    # Apply the formatting function to the entire DataFrame
    formatted_df = df.applymap(format_and_round)
    
    # Get the number of playoff positions
    playoff_number = playoff_num(league_id, espn_s2, swid, year)
    slice_ = df.columns[:playoff_number]
    
    # Style the DataFrame
    styled_df = formatted_df.style.set_properties(**{'background-color': 'lightgray'}, subset=slice_)
    
    df_names = pd.read_excel(file, sheet_name="Wins Against Schedule")
    df_names.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    # Display the styled DataFrame
    df_names.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df_names = df_names.set_index("Teams")
    pd.options.mode.chained_assignment = None
    names = []
    for col in df_names.columns:
        if col != "Teams":
            names.append(col)
    if len(names) <= 10:
        height = "auto"
    else:
        height = 460 + (len(names) - 12) * 40
    # Display the styled DataFrame
    st.dataframe(styled_df, height=height)

def display_lpi_by_week(file):
    """
    Displays the Louie Power Index (LPI) by week in Streamlit.

    Parameters:
    - file (str): Path to the Excel file.
    """
    st.header('Louie Power Index Each Week')
    
    # Read the LPI By Week sheet
    df = pd.read_excel(file, sheet_name="LPI By Week")
    df.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df_names = pd.read_excel(file, sheet_name="Schedule Grid")
    # Display the styled DataFrame
    df_names.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df_names = df_names.set_index("Teams")
    pd.options.mode.chained_assignment = None
    names = []
    for col in df_names.columns:
        if col != "Teams":
            names.append(col)
    if len(names) <= 10:
        height = "auto"
    else:
        height = 460 + (len(names) - 12) * 40
    # Display the DataFrame
    st.dataframe(df, height=height, hide_index=True)

    # Create a new DataFrame excluding "Change From Last Week"
    df_chart = df.drop(columns=["Change From Last Week"])
    # Set the "Teams" column as the index for plotting
    # df_chart.set_index("Teams", inplace=True)

    # # Transpose the DataFrame so weeks are on the x-axis and teams are the lines
    # df_chart = df_chart.T

    # # Prepare data for pyecharts
    # x_axis = df_chart.index.tolist()  # Weeks (x-axis)
    # line_chart = Line().set_global_opts(
    #     title_opts=opts.TitleOpts(title="Louie Power Index By Week"),
    #     tooltip_opts=opts.TooltipOpts(trigger="axis"),
    #     xaxis_opts=opts.AxisOpts(type_="category", name="Weeks"),
    #     yaxis_opts=opts.AxisOpts(type_="value", name="LPI", min_=-100, max_=100),
    #     legend_opts=opts.LegendOpts(pos_top="5%"),
    # )

    # # Add each team's data as a line
    # for team in df_chart.columns:
    #     line_chart.add_yaxis(
    #         series_name=team,
    #         y_axis=df_chart[team].tolist(),
    #         is_smooth=True,  # Smooth the lines
    #         label_opts=opts.LabelOpts(is_show=False),
    #     )

    # # Render the chart in Streamlit
    # st_pyecharts(line_chart, height="500px")

    # Prepare data for the ECharts stacked line chart
    teams = df_chart["Teams"].tolist()
    weeks = df_chart.columns[1:]  # Exclude the "Teams" column
    series_data = []

    for _, row in df_chart.iterrows():
        print(f"Processing team: {row['Teams']}")
        print(f"Data: {row[1:].tolist()}")  # Exclude the "Teams" column
        series_data.append({
            "name": row["Teams"],
            "type": "line",
            "stack": "Total",
            "data": row[1:].tolist()  # Exclude the "Teams" column
        })

    # ECharts options
    options = {
        "title": {"text": ""},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": teams},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "toolbox": {"feature": {"saveAsImage": {}}},
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": weeks.tolist(),  # X-axis labels (Week 1, Week 2, ...)
        },
        "yAxis": {
            "type": "value",
            # "min": -100,  # Set the minimum value for the y-axis
            # "max": 100,   # Set the maximum value for the y-axis
        },
        "series": series_data
    }

    # Render the ECharts stacked line chart
    st_echarts(options=options, height="450px")

def display_lpi(file):
    """
    Reads the 'Louie Power Index' sheet from the given Excel file
    and returns the DataFrame.

    Parameters:
    - file (str): Path to the Excel file.

    Returns:
    - pd.DataFrame: The Louie Power Index DataFrame.
    """
    st.header('The Louie Power Index (LPI)')
    st.write('The Louie Power Index compares Expected Wins and Strength of Schedule to produce a strength of schedule adjusted score.')
    st.write('Positive scores indicate winning against tough schedules. Negative scores mean losing with an easy schedule. Higher scores are better. Scores near zero are neutral.')
    st.write('The LPI shows which direction teams should trend - high scores but worse records suggest improvement ahead. Low scores but better records indicate expected decline.')
    df = pd.read_excel(file, sheet_name="Louie Power Index")
    
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['Louie Power Index (LPI)'])
    df_names = pd.read_excel(file, sheet_name="Schedule Grid")
    # Display the styled DataFrame
    df_names.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df_names = df_names.set_index("Teams")
    pd.options.mode.chained_assignment = None
    names = []
    for col in df_names.columns:
        if col != "Teams":
            names.append(col)
    if len(names) <= 10:
        height = "auto"
    else:
        height = 460 + (len(names) - 12) * 40
    st.dataframe(df3, height=height)

def display_draft_results(draft_file):
    try:
        df = pd.read_csv(draft_file)
        st.header('Draft Results')
        df = df.drop(columns=['Owner ID'])
        # Increment index to start at 1
        df.index += 1
        AgGrid(df)
    except:
        print("No Draft Results Yet")

def display_biggest_lpi_upsets(file):
    st.header('Biggest LPI Upsets')
    # st.write('The LPI shows which direction teams should trend - high scores but worse records suggest improvement ahead. Low scores but better records indicate expected decline.')
    df = pd.read_excel(file, sheet_name="Biggest Upsets")
    df = df.iloc[: , 1:]
    df.index += 1
    df3 = df.style.background_gradient(subset=['LPI Difference'])
    df_names = pd.read_excel(file, sheet_name="Schedule Grid")
    # Display the styled DataFrame
    df_names.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df_names = df_names.set_index("Teams")
    pd.options.mode.chained_assignment = None
    names = []
    for col in df_names.columns:
        if col != "Teams":
            names.append(col)
    if len(names) <= 10:
        height = "auto"
    else:
        height = 460 + (len(names) - 12) * 40
    st.dataframe(df3, height=height)

def display_lifetime_record(file, league_id, espn_s2, swid, year_options):
    df = pd.read_excel(file, sheet_name="Schedule Grid")
    df.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df = df.set_index("Teams")
    names = []
    for col in df.columns:
        if col != "Teams":
            names.append(col)

    st.header('Lifetime Record')
    st.write('Select a team and see their record vs all other teams over every year and every game of that league')
 
    selected_team = st.selectbox("Select Team", names)
    def convert_to_int_list(original_list):
        """
        Converts all elements in a list to integers.

        Parameters:
        - original_list (list): A list of elements that can be converted to integers.

        Returns:
        - list: A new list with all elements as integers.
        """
        return [int(item) for item in original_list]

    # Convert to integers
    years = convert_to_int_list(year_options)
    print(years)
    lifetime_record_df, year_df, all_matchups_df = lifetime_record(league_id, espn_s2, swid, years, selected_team)
    
    df4 = lifetime_record_df.style.background_gradient(subset=['Win Percentage'])
    df_names = pd.read_excel(file, sheet_name="Schedule Grid")
    # Display the styled DataFrame
    df_names.rename(columns={'Unnamed: 0': 'Teams'}, inplace=True)
    df_names = df_names.set_index("Teams")
    pd.options.mode.chained_assignment = None
    names = []
    for col in df_names.columns:
        if col != "Teams":
            names.append(col)
    if len(names) <= 10:
        height = "auto"
    else:
        height = 460 + (len(names) - 12) * 40
    st.dataframe(df4, height=height, hide_index=True)

    # df5 = year_df.style.background_gradient(subset=['Win Percentage'])
    st.write("Here is this team's record by year:")
    st.dataframe(year_df, hide_index=True)

# st.header('Upset Factor of Previous Week')
# st.write('This simply compares both the Expected Win total against the Strength of Schedule total to see which teams are best')
# df = pd.read_excel(file, sheet_name="Louie Power Index")
# df = df.iloc[: , 1:]
# df.index += 1
# df3 = df.style.background_gradient(subset=['Louie Power Index (LPI)'])
# st.dataframe(df3)