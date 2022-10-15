import streamlit as st
import pandas as pd
import os
# import pydeck as pdk

from urllib.error import URLError

st.set_page_config(page_title="Map Test", layout="wide")
st.title('My Map')


@st.cache
def from_data_file(filename):
    url = (
        "http://raw.githubusercontent.com/streamlit/"
        "example-data/master/hello/v1/%s" % filename)
    return pd.read_json(url)

