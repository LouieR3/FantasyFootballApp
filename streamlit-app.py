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
import PrahladFriendsLeague2022
import PennoniTransportation2022
import EBCLeague2021
from espn_api.football import League
import LPIMasterList

st.set_page_config(page_title="Louie's Fantasy Football App", layout="wide")

PAGES = {
    "🏈 Pennoni Younglings 2022": PennoniYounglings2022,
    "🎮 EBC League 2022": EBCleague2022,
    "🎮 EBC League 2021": EBCLeague2021,
    "👪 Family League 2022": FamilyLeague2022,
    "🛠️ Pennoni Transportation 2022": PennoniTransportation2022,
    "🧑‍🤝‍🧑 Prahlad Friends League 2022": PrahladFriendsLeague2022,
    "LPI Master List": LPIMasterList,
}
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Leagues:", list(PAGES.keys()))
page = PAGES[selection]
page.app()

# show_pages(
#     [
#         Page("example_app/PennoniTransportation2022.py", "Home", "🏠"),
#         # Can use :<icon-name>: or the actual icon
#         Page("example_app/PennoniYounglings2022.py", "Example One", ":books:"),
#         # Since this is a Section, all the pages underneath it will be indented
#         # The section itself will look like a normal page, but it won't be clickable
#         Section(name="Cool apps", icon=":pig:"),
#         # The pages appear in the order you pass them
#         Page("example_app/PrahladFriendsLeague2022.py", "Example Four", "📖"),
#         Page("example_app/LPIMasterList.py", "Example Two", "✏️"),
#         Section(name="Other apps", icon=":horse:"),
#         # Will use the default icon and name based on the filename if you don't
#         # pass them
#         Page("example_app/EBCLeague2021.py"),
#         # You can also pass in_section=False to a page to make it un-indented
#         Page("example_app/EBCleague2022.py", "Example Five", "🧰", in_section=False),
#     ]
# )

# pr = df.profile_report()
# st_profile_report(pr)
