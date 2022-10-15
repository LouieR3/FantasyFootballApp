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
import unidecode
import espl
from espn_api.football import League

st.set_page_config(page_title="Louie's Fantasy Football Page", layout="wide")

PAGES = {
    "Schedule Grid": intro,
    "Strength of Schedule": actors,
    "Expected Wins": director,
    "Louie Power Index (LPI)": length
}
st.sidebar.title('EBC League')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()

# pr = df.profile_report()
# st_profile_report(pr)
