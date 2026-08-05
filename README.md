# 🏈 Louie's Fantasy Football Analysis App

A multi-page Streamlit app that analyzes ESPN fantasy football leagues I (or friends) are in — with a page per league, a year filter on each page, and a stack of custom analytics headlined by the **Louie Power Index (LPI)**.

**Live app:** https://louier3-fantasy-football-page.streamlit.app/

## What's on each league page

Each league page has a year selector and renders the following sections (data permitting for that year):

| Section | What it shows |
|---|---|
| **Playoff Results** | Playoff bracket results for the season |
| **Schedule Comparison** | Grid of every team's record if they played every other team's schedule. Color-coded: deep yellow = top 10% record, light yellow = top 25%, light red = bottom 25%, dark red = bottom 10% |
| **The Louie Power Index (LPI)** | Combines Expected Wins and Strength of Schedule into a schedule-adjusted power score. Positive = winning against tough schedules; negative = losing with an easy one. High LPI + bad record suggests improvement ahead |
| **Playoff Odds** | Each team's odds of finishing in each place, from 10,000 Monte Carlo simulations of remaining matchups using each team's scoring mean and standard deviation |
| **Record Predictions** | Predicted final records based on simulated remaining schedule |
| **Playoff Odds by Week** | How each team's playoff odds have moved week over week |
| **Betting Odds** | Sportsbook-style lines for each weekly matchup (spread, over/under, moneyline) derived from the simulations |
| **Remaining Schedule Difficulty** | Ranks the difficulty of each team's remaining slate |
| **LPI Each Week** | LPI trend line week by week |
| **Strength of Schedule** | Schedules ranked hardest to easiest by the average record all other teams would have against them |
| **Expected Wins** | Wins each team would expect with an average schedule, and the difference vs. their actual record |
| **Draft Results** | Every draft pick graded 30–100 with a letter grade: 60% value-over-slot (production vs. what that draft slot historically returns, fit from every league-year on file) + 40% points-above-replacement at the position. Grades are standardized within each season across all leagues, so they're comparable everywhere (see `ffapp/metrics/draft_grading.py`) |
| **Biggest LPI Upsets** | Wins by teams with a large LPI deficit vs. their opponent |
| **Lifetime Record** | All-time results for the league across seasons |

## Repo layout

```
FantasyFootballApp/
├── streamlit-app.py          # App entry point / home page (Streamlit Cloud entrypoint)
├── pages/                    # One Streamlit page per league (+ LPI master list, upsets, playoff analysis)
├── paths.py                  # Repo-anchored data locations — all file I/O goes through this
├── credentials.py            # ESPN cookie/SWID loader (secrets, never in source)
│
├── ffapp/                    # the library
│   ├── ui/                   # what the pages call
│   │   ├── data_loader.py        # cached file/ESPN access — all app reads go through this
│   │   ├── page_functions.py     # every display_* section on a league page
│   │   ├── lifetime_record_owner.py
│   │   ├── calcPercent.py  playoffNum.py
│   ├── metrics/              # computation
│   │   ├── monte_carlo_odds.py   # playoff odds / record prediction simulations
│   │   ├── draft_grading.py      # draft + free agent grading engine
│   │   ├── create_betting_odds.py
│   │   └── owner_overrides.py    # canonical owner for co-owned team-seasons
│   └── espn/                 # pulling + shaping ESPN data
│       ├── draft_data.py  all_matchups.py  all_playoffs.py  season_results.py
│
├── pipeline/                 # runnable entry points (see below)
├── experiments/              # one-off explorations and manual tests (lpi, elo, printOwners, ...)
├── analysis/                 # offline studies (draft grading research, playoff chances)
├── archive/                  # dead code kept for reference; nothing imports it
└── data/
    ├── leagues/              # one xlsx per league-year — the app's main source
    ├── drafts/               # draft + free agent results csv per league-year
    ├── odds/                 # betting odds xlsx per league-year
    └── *.csv                 # cross-league aggregates (all_matchups, Master_Draft_Data, ...)
```

Anything under `pipeline/`, `experiments/`, or `analysis/` finds the repo root on its own, so you can run it from any directory and it will read and write into `data/` correctly.

## Running locally

```bash
pip install -r requirements.txt
streamlit run streamlit-app.py
```

The app reads the committed files under `data/`, so it runs without ESPN credentials.

### Data access in the app

All app-side reads go through `ffapp/ui/data_loader.py`, which caches them. Streamlit re-runs a page's whole script on every widget interaction, so uncached reads repeat on every dropdown change — a league page used to re-parse the same workbook 20 times per render (the Schedule Grid sheet alone 10 times) and rebuild an ESPN `League` object per season.

Use these instead of `pd.read_excel` / `pd.read_csv` / `League(...)` anywhere in the app path:

| Instead of | Use |
|---|---|
| `pd.read_excel(f, sheet_name="X")` | `load_sheet(f, "X")` |
| `pd.read_excel(f, sheet_name=None)` | `load_all_sheets(f)` |
| `pd.read_csv(f)` | `load_csv(f)` |
| `League(league_id=..., year=...)` | `get_league(league_id, year, espn_s2, swid)` |

Cache keys include each file's modification time, so re-running the pipeline invalidates them automatically — no app restart needed. Loaders return copies, so page code can mutate results freely.

## Pipeline (run locally to refresh data, then commit)

| Script | What it does |
|---|---|
| `pipeline/ESPNWeeklyUpdateList.py` | **The main weekly run.** Loops every configured league: standings, matchups, LPI, playoff odds, betting odds → `data/leagues/`, `data/odds/` |
| `pipeline/ESPNWeeklyUpdate.py` | Same work for **one** league — edit the uncommented `league = League(...)` block near the top to pick it |
| `pipeline/ESPN_Add_Old_Season.py` | Backfill a **past** season for a league (weekly data, playoff results, drafts, matchups) |
| `pipeline/regrade_drafts.py` | Recompute all draft/free-agent grades across every season (needed after any grading change) |
| `pipeline/rebuild_aggregates.py` | Rebuild the cross-league playoff CSVs from the workbooks — **run weekly**, offline; without it the cross-league pages silently omit the newest season |
| `pipeline/add_current_week_results.py` | Append the current week into `data/all_matchups.csv` |
| `pipeline/playoff_chances.py`, `pipeline/playoff_add_predicted.py` | Playoff-odds datasets used by the Playoff Analysis page |

Typical in-season week:

```bash
python pipeline/ESPNWeeklyUpdateList.py
```

Then refresh the cross-league aggregates (offline, no credentials):

```bash
python pipeline/rebuild_aggregates.py
```

After a draft, or any time grading changes:

```bash
python pipeline/regrade_drafts.py
```

Then commit and push — Streamlit Cloud redeploys from the repo.

ESPN private-league access requires `espn_s2` and `SWID` cookies. All code reads them via `credentials.py` (`CRED["louie_s2"]`, etc.), which loads from `.streamlit/secrets.toml` (gitignored — copy `.streamlit/secrets.toml.example` and fill it in), from Streamlit Cloud's secrets settings, or from `ESPN_*` environment variables. Never put cookie values in source.

## Deploying to Streamlit Cloud

Push, and Cloud picks up the commit. One gotcha worth knowing:

> **If a deploy adds a new function to an existing module, reboot the app.**
> Streamlit re-executes the *page* script on every rerun but keeps already-imported
> modules in `sys.modules`. So new page code can run against an old copy of, say,
> `ffapp/league_registry.py`, and you get `ImportError: cannot import name ...` or
> `AttributeError: module ... has no attribute ...` even though the code on GitHub is
> correct. **Manage app → Reboot app** restarts the process and clears it. A rerun or
> "Clear cache" will not.
>
> Brand-new modules are fine — only additions to modules that were already imported
> are affected.

Before pushing page changes, run the page smoke test — it executes every page with
streamlit stubbed and catches runtime errors that `py_compile` cannot:

```bash
python tools/smoke_pages.py
```

### If the app breaks with no code change

Symptom: the live app fails after a deploy (or even without one) with an error from
deep inside a library you have never imported — for example
`TypeError: GZipResponder.__init__() missing 1 required keyword-only argument`.
`GZipResponder` is a Starlette internal; nothing in this repo touches Starlette.

That is a **dependency break, not a code break**. `requirements.txt` is now pinned
with upper bounds so a new major release upstream cannot silently take the app down.
If it happens again:

1. Open the last **successful** Streamlit Cloud build log and copy the resolved
   versions from the "Installing dependencies" step.
2. Pin the suspects to those versions. `streamlit-echarts` and `streamlit-echarts5`
   are the two left unconstrained and are the likeliest culprits — small third-party
   components are where an unexpected Starlette/FastAPI dependency comes from.
3. Redeploy, then **Reboot app**.

## Roadmap

The full scope, feature backlog, draft-grade methodology review, and data-hosting migration plan live in **[SCOPE.md](SCOPE.md)**. Highlights:

- **Lifetime & franchise history** — owner career tables (year, W/L, PF/PA, place, draft grade), multi-year LPI and points charts, all-time records book, head-to-head rivalry views, cross-season Elo.
- **Draft analytics** — best-possible-team button, best pick per round, biggest steals/busts, value-over-slot grading, owner draft tendencies.
- **Season page upgrades** — playoff bracket visual with LPI, final placement in year stats, week-over-week LPI change, luck index, records vs. all-play.
- **Data platform** — migrate from committed CSV/Excel to SQLite/Parquet with a scheduled (GitHub Actions) refresh instead of manual local runs.
