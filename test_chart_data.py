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

file = "leagues/EBC League 2024.xlsx"


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

# Create a new DataFrame excluding "Change From Last Week"
df_chart = df.drop(columns=["Change From Last Week"])
print(df_chart)
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