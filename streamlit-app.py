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
import EBCleague
import FamilyLeague
import PennoniYounglings
import PennoniPlayoffs
import PrahladFriendsLeague
import PennoniTransportation
import EBCLeague2021
from espn_api.football import League
import LPIMasterList

st.set_page_config(page_title="Louie's Fantasy Football Page", layout="wide")

PAGES = {
    "EBC League": EBCleague,
    "Family League": FamilyLeague,
    "Pennoni Younglings": PennoniYounglings,
    "Pennoni Playoffs": PennoniPlayoffs,
    "EBC League 2021": EBCLeague2021,
    "Pennoni Transportation": PennoniTransportation,
    "Prahlad Friends League": PrahladFriendsLeague,
    "LPI Master List": LPIMasterList,
}
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()

# pr = df.profile_report()
# st_profile_report(pr)
