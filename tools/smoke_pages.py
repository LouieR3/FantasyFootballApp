"""Execute every Streamlit page with stubs, to catch runtime errors py_compile can't.

Stubs streamlit and the display_* layer, so each page's own logic runs for real:
year selection, path building, titles, ordering. That is exactly where an
UnboundLocalError / NameError / bad path lives.
"""
import functools
import glob
import io
import os
import sys
import traceback
import types

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

# ---------------------------------------------------------------- streamlit stub
class _Ctx:
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def __getattr__(self, name): return lambda *a, **k: None

st = types.ModuleType("streamlit")
st.cache_data = lambda **kw: (lambda fn: functools.lru_cache(maxsize=None)(fn))
st.cache_resource = st.cache_data
st.secrets = {}
st.session_state = {}
for fn in ("header subheader write caption error warning info success markdown title "
           "divider dataframe table json metric plotly_chart altair_chart pyplot "
           "bar_chart line_chart area_chart image set_page_config progress spinner "
           "toast balloons text code latex").split():
    setattr(st, fn, lambda *a, **k: None)
st.columns = lambda spec, **k: [_Ctx() for _ in (spec if isinstance(spec, list) else range(spec))]
st.expander = st.container = st.form = st.sidebar = lambda *a, **k: _Ctx()
st.tabs = lambda labels, **k: [_Ctx() for _ in labels]
st.selectbox = lambda label, opts, index=0, **k: (list(opts)[index] if opts else None)
st.multiselect = lambda *a, **k: []
st.radio = lambda label, opts, index=0, **k: (list(opts)[index] if opts else None)
st.slider = lambda l, lo=0, hi=10, value=None, **k: (value if value is not None else lo)
st.checkbox = lambda *a, **k: False
st.button = lambda *a, **k: False
st.text_input = lambda *a, **k: ""
st.number_input = lambda l, *a, **k: 0
st.__getattr__ = lambda name: (lambda *a, **k: None)  # any other st.* is a no-op
sys.modules["streamlit"] = st

# ------------------------------------------------- third-party rendering stubs
for name in ("st_aggrid", "streamlit_echarts5", "streamlit_echarts",
             "pyecharts", "pyecharts.charts", "pyecharts.options",
             "plost", "vega_datasets", "altair"):
    m = types.ModuleType(name)
    m.__getattr__ = lambda n: (lambda *a, **k: None)
    sys.modules.setdefault(name, m)
sys.modules["st_aggrid"].AgGrid = lambda *a, **k: None
sys.modules["streamlit_echarts5"].st_echarts = lambda *a, **k: None
sys.modules["streamlit_echarts"].st_pyecharts = lambda *a, **k: None
sys.modules["pyecharts.charts"].Line = object
sys.modules["pyecharts.options"].__getattr__ = lambda n: (lambda *a, **k: None)

# --------------------------------------------------------------- espn_api stub
espn = types.ModuleType("espn_api")
football = types.ModuleType("espn_api.football")
class _League:
    def __init__(self, **kw):
        self.year = kw.get("year")
        self.teams = []
        self.settings = types.SimpleNamespace(name="stub", reg_season_count=14,
                                              playoff_team_count=6)
    def standings(self): return []
    def standings_weekly(self, w): return []
football.League = _League
espn.football = football
sys.modules["espn_api"] = espn
sys.modules["espn_api.football"] = football

# ------------------------------- stub the display layer: pages' own code is the target
pf = types.ModuleType("ffapp.ui.page_functions")
CALLS = []
def _mk(name):
    def f(*a, **k):
        CALLS.append(name)
    return f
for name in ("display_playoff_results display_schedule_comparison display_strength_of_schedule "
             "display_expected_wins display_playoff_odds display_playoff_odds_by_week "
             "display_remaining_schedule_difficulty display_betting_odds "
             "display_betting_odds_full_width display_lpi_by_week display_lpi "
             "display_draft_results display_biggest_lpi_upsets display_lifetime_record "
             "owner_df_creation").split():
    setattr(pf, name, _mk(name))
sys.modules["ffapp.ui.page_functions"] = pf

# ------------------------------------------------------------------------- run
pages = sorted(glob.glob('pages/*.py')) + ['streamlit-app.py']
fails = []
for p in pages:
    CALLS.clear()
    ns = {'__name__': '__main__', '__file__': os.path.abspath(p)}
    try:
        exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), ns)
        print(f"  OK   {os.path.basename(p):44s} sections rendered: {len(CALLS)}")
    except Exception as e:
        fails.append((p, e))
        print(f"  FAIL {os.path.basename(p):44s} {type(e).__name__}: {e}")
        tb = traceback.format_exc().strip().split('\n')
        for line in tb[-4:]:
            print("        " + line)

print()
print(f"{len(pages) - len(fails)}/{len(pages)} pages executed cleanly")
sys.exit(1 if fails else 0)
