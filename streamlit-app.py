import streamlit as st
import pandas as pd
# import pydeck as pdk
from bs4 import BeautifulSoup
import requests
import csv
import json
import re
import asyncio
# from operator import itemgetter
# from urllib.error import URLError
# from streamlit_observable import observable
# import pandas_profiling
# from streamlit_pandas_profiling import st_profile_report
import numpy as np
# import actors2
# import EBCleague2022
# import FamilyLeague2022
# import PennoniYounglings2022
# import PrahladFriendsLeague2022
# import PennoniTransportation2022
# import EBCLeague2021
from espn_api.football import League
# import LPIMasterList
# from streamlit_option_menu import option_menu
# from st_pages import Page, show_pages, add_page_title

st.set_page_config(page_title="Louie's Fantasy Football App", page_icon="🏈", layout="wide")

# PAGES = {
#     "🏈_Pennoni_Younglings_2022": PennoniYounglings2022,
#     "🎮 EBC League 2022": EBCleague2022,
#     "👪_Family_League_2022": FamilyLeague2022,
#     "🛠️_Pennoni_Transportation_2022": PennoniTransportation2022,
#     "🧑‍🤝‍🧑_Prahlad_Friends_League_2022": PrahladFriendsLeague2022,
#     "🎮_EBC League 2021": EBCLeague2021,
#     "LPI Master List": LPIMasterList,
# }
# st.sidebar.title('Navigation')
# selection = st.sidebar.radio("Leagues:", list(PAGES.keys()))
# page = PAGES[selection]

# # 1. as sidebar menu
# # with st.sidebar:
# #     selected = option_menu("Main Menu", ["🏈 Pennoni Younglings 2022", '🎮 EBC League 2022'], 
# #         icons=['house', 'gear'], menu_icon="cast", default_index=1)
# #     selected

# page.app()

# Main Description
st.markdown("## 🏈 Welcome to Louie's Fantasy Football App!")
st.markdown("Developed by __Louie Rodriguez__: https://github.com/LouieR3/FantasyFootballApp")
st.markdown("League's are labeled by league name and year on the side.")

# Description of the features. 
st.markdown(
    """
    ### Some info on analysis you will see on each page:

    - __Schedule Comparison__ - This shows you what your team's record would be against everyone elses schedule when reading from left to right. Looking at the records for your team top to bottom shows what each teams record would be with your schedule. A deep yellow color indicates a record in the top 10%, a lighter yellow color indicates a top 25% record, a light red color indicates a bottom 25% record, and a dark red color indicates a bottom 10% record.
    
    - __Strength of Schdeule__ - This table ranks each team's schedule from hardest to easiest based on the average number of wins all other teams would have against that schedule. The Avg Wins Against Schedule column shows the hypothetical average record every team would have with that schedule over the season. Lower averages indicate a tougher slate of opponents.

    - __Expected Wins__ - The Expected Wins column shows how many wins each fantasy football team could expect with an average schedule. Teams with a higher Expected Win value than their actual wins have overcome tough schedules. Teams with lower Expected Wins have benefitted from weaker schedules. A positive value in the Difference column means you should have that many more wins added onto your record, and a negative number means you are that many wins above what you really should have.

    - __*NEW* Playoff Odds__ - This chart shows what each team's odds are of getting each place in the league based on the history of each team's scores this year. It does not take projections or byes into account. It uses the team's scoring data to run 10,000 monte carlo simulations of each matchup given a team's average score and standard deviation.
    
    - __The Louie Power Index (LPI)__ - The Louie Power Index compares Expected Wins and Strength of Schedule to produce a strength of schedule adjusted score. Positive scores indicate winning against tough schedules. Negative scores mean losing with an easy schedule. Higher scores are better. Scores near zero are neutral. The LPI shows which direction teams should trend - high scores but worse records suggest improvement ahead. Low scores but better records indicate expected decline.
    
    """
)
