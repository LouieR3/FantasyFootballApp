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
import EBCleague2022
import FamilyLeague2022
import PennoniYounglings2022
import PennoniPlayoffs
import PrahladFriendsLeague2022
import PennoniTransportation2022
import EBCLeague2021
from espn_api.football import League
import LPIMasterList

st.set_page_config(page_title="Louie's Fantasy Football App", layout="wide")

PAGES = {
    "Pennoni Younglings 2022": PennoniYounglings2022,
    "Pennoni Transportation 2022": PennoniTransportation2022,
    "Prahlad Friends League 2022": PrahladFriendsLeague2022,
    "EBC League 2022": EBCleague2022,
    "EBC League 2021": EBCLeague2021,
    "Family League 2022": FamilyLeague2022,
    "LPI Master List": LPIMasterList,
}
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Leagues:", list(PAGES.keys()))
selection2 = st.sidebar.radio("Leagues 2:", list(PAGES.keys()))
page = PAGES[selection]
page.app()

# pr = df.profile_report()
# st_profile_report(pr)
