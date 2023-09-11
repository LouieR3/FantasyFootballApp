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

st.set_page_config(page_title="Louie's Fantasy Football App", layout="wide")

# PAGES = {
#     "🏈 Pennoni Younglings 2022": PennoniYounglings2022,
#     "🎮 EBC League 2022": EBCleague2022,
#     "👪 Family League 2022": FamilyLeague2022,
#     "🛠️ Pennoni Transportation 2022": PennoniTransportation2022,
#     "🧑‍🤝‍🧑 Prahlad Friends League 2022": PrahladFriendsLeague2022,
#     "🎮 EBC League 2021": EBCLeague2021,
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
st.markdown("## 👋 Welcome to SurViZ, your best tool to compare and explore galaxy SurVeys!")
st.markdown("Developed by __Hubert Bretonnière__: https://github.com/Hbretonniere/SurViZ")
st.markdown("The app is still under development. Please reach me in the github repo if you have any comments or suggestions.")
st.markdown("For a more quantitative comparison of some of the surveys, you can visit and use galcheat (https://github.com/aboucaud/galcheat)")

# Description of the features. 
st.markdown(
    """
    ### Select on the left panel what you want to explore:

    - With 🔭 General info, you will have a short description of the telescopes, their scientific goals, instruments and surveys.
    
    - With 🎨 Filters, you will explore the spectral bands of each telescopes' instruments.

    - With 👁️ FOV, you will be able to explore the Field of View of each telescope.

    - With 📈characteristics, you will explore the capacity of the missions regarding filters, resolution and depth.
    
    - With 🌌 Galaxy, you will explore the surveys and instruments' image quality (resolution and PSF) in a TNG galaxy.

    - With ✨ Galaxy fields, you will explore the surveys and instruments' depths in a simulated galaxy field.

    - With 🗺️ Survey footprint, you will visualise the sizes and positions of the various surveys.

    - With 🪞 Mirror , you will explore the size of the telescopes' primary mirror.
    \n  
    
    More information can be found by clicking in the READMEs of each tab.
    """
)
