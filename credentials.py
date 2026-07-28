"""Central ESPN credential store.

Real values live OUTSIDE of source control, looked up in this order:
  1. .streamlit/secrets.toml (gitignored) - local runs, app and pipeline scripts
  2. Streamlit secrets (st.secrets["espn"]) - Streamlit Cloud (paste the same
     [espn] block into the app's Secrets settings)
  3. Environment variables - ESPN_<NAME>, e.g. ESPN_LOUIE_S2

Usage:  from credentials import CRED
        league = League(league_id=..., espn_s2=CRED["louie_s2"], swid=CRED["louie_swid"])
"""
import os
import re

_SECRETS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".streamlit", "secrets.toml")


def _from_toml_file():
    if not os.path.exists(_SECRETS_PATH):
        return None
    try:
        import tomllib  # Python 3.11+
        with open(_SECRETS_PATH, "rb") as fh:
            return dict(tomllib.load(fh).get("espn", {}))
    except ImportError:
        pass
    # minimal fallback parser for the flat  key = "value"  lines in [espn]
    creds, in_espn = {}, False
    with open(_SECRETS_PATH, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("["):
                in_espn = line == "[espn]"
            elif in_espn:
                m = re.match(r'(\w+)\s*=\s*"(.*)"', line)
                if m:
                    creds[m.group(1)] = m.group(2)
    return creds or None


def _from_streamlit():
    try:
        import streamlit as st
        if "espn" in st.secrets:
            return dict(st.secrets["espn"])
    except Exception:
        pass
    return None


class _Credentials(dict):
    def __missing__(self, key):
        env = os.environ.get("ESPN_" + key.upper())
        if env:
            return env
        raise KeyError(
            f"ESPN credential '{key}' not found. Add it under [espn] in "
            f"{_SECRETS_PATH} (see .streamlit/secrets.toml.example), in Streamlit "
            f"Cloud secrets, or set the ESPN_{key.upper()} environment variable."
        )


CRED = _Credentials(_from_toml_file() or _from_streamlit() or {})
