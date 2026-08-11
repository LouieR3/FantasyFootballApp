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

## Cross-league pages

| Page | What it shows |
|---|---|
| **Playoff Analysis** | Every playoff bracket on file, all champions, seed-vs-outcome history |
| **Post-Season Draft Analysis** | One league-season's draft post-mortem: value over slot split into accuracy vs luck, steals and busts, value left on the board, and the best draft each manager could have had at their own pick slots (exact, slot-constrained) |
| **Lifetime League History** | Multi-year leagues: all-time table, careers (with Draft Grade + Transaction Grade side by side), head-to-head, playoff records, streaks, records book, and a league-wide transaction history showing who wins their trades |
| **All-Time Hall of Fame** | Every team-season across every league, ranked by league-relative metrics — best and worst ever, worst champions, best manager without a ring — plus all-time transaction feats (most lopsided/biggest/most mutual trades, best pickups, worst drops) |
| **Transaction Analysis** | Every add, drop and trade scored by started points above replacement: best pickups, drops that hurt, trade winners, and a manager scorecard (see `ffapp/metrics/transaction_analysis.py`) |
| **Live Draft Assistant** | Upload a rankings CSV and it tells you who's available, who's falling past their positional value, and — given your roster and your league's lineup — what to take next. Two modes: **manual** (no ESPN connection at all) or **live** (polls the draft feed). **Run locally during a live draft** — it polls with your `espn_s2` cookie |

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
│   │   ├── draft_analysis.py     # post-season draft post-mortem
│   │   ├── transaction_analysis.py  # scoring adds/drops/trades (SPAR)
│   │   ├── lifetime.py  hall_of_fame.py
│   │   ├── create_betting_odds.py
│   │   └── owner_overrides.py    # canonical owner for co-owned team-seasons
│   └── espn/                 # pulling + shaping ESPN data
│       ├── draft_data.py  all_matchups.py  all_playoffs.py  season_results.py
│       ├── transactions.py       # weekly roster snapshots + activity feed
│       ├── live_draft.py         # live draft board (raw API — espn_api can't)
│       ├── week_utils.py  league_settings.py
│
├── pipeline/                 # runnable entry points (see below)
├── experiments/              # one-off explorations and manual tests (lpi, elo, printOwners, ...)
├── analysis/                 # offline studies (draft grading research, playoff chances)
├── archive/                  # dead code kept for reference; nothing imports it
└── data/
    ├── leagues/              # one xlsx per league-year — the app's main source
    ├── drafts/               # draft + free agent results csv per league-year
    ├── odds/                 # betting odds xlsx per league-year
    ├── transactions/         # weekly roster snapshots + reconstructed moves per league-year
    ├── rankings/             # draft rankings CSVs for the Draft Assistant (gitignored — third-party sheets)
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
| `pipeline/backfill_transactions.py` | Weekly roster snapshots + add/drop/trade log for past seasons (~17 requests per league-season; 2019 is a hard floor) |
| `pipeline/refresh_standings.py` | Final standings (`Finish` on the Lifetime careers table) — needs ESPN's `final_standing`, so **run after each season ends**; without it Finish is blank for the newest year |

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

> ⚠️ **Transactions must be captured in-season.** `ESPNWeeklyUpdateList.py` now pulls them
> as part of the weekly run. ESPN serves its transaction log for the **current season only**
> and returns 404 for every completed one, so a season that is never run in-season can have
> its weekly roster snapshots backfilled but never its real move types or FAAB bids.
> To backfill snapshots for past seasons: `python pipeline/backfill_transactions.py --skip-existing`

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

`requirements.txt` is pinned with upper bounds so a new major release upstream cannot
silently take the app down. **One pin is load-bearing** and is documented in the file
itself:

> **`starlette>=0.46,<1.4`** — starlette 1.4.0 made `thread_minimum_size` a *required*
> keyword-only argument on `GZipResponder.__init__`. Streamlit subclasses that class in
> `streamlit/web/server/starlette/starlette_gzip_middleware.py` and constructs it
> without the argument, and Streamlit's own bound (`starlette<2,>=0.46.0`) is too loose
> to exclude it. Result:
> `TypeError: GZipResponder.__init__() missing 1 required keyword-only argument:
> 'thread_minimum_size'` on every gzip-accepting request. Every starlette up to 1.3.1
> is clean. Revisit once Streamlit supports starlette ≥ 1.4.

If something similar happens again:

1. Compare the resolved versions in the last **successful** Streamlit Cloud build log
   ("Installing dependencies") against the current build — the diff is usually one
   package.
2. To pin down a signature break exactly, download the suspect at several versions
   with `pip download <pkg>==<ver> --no-deps` and diff the function named in the
   traceback. That is how the starlette boundary above was found — guessing from the
   dependency list pointed at the wrong packages entirely.
3. Pin below the breaking version, redeploy, then **Reboot app**.

## Roadmap

The full scope, feature backlog, draft-grade methodology review, and data-hosting migration plan live in **[SCOPE.md](SCOPE.md)**. Highlights:

- **Lifetime & franchise history** — owner career tables (year, W/L, PF/PA, place, draft grade), multi-year LPI and points charts, all-time records book, head-to-head rivalry views, cross-season Elo.
- **Draft analytics** — best-possible-team button, best pick per round, biggest steals/busts, value-over-slot grading, owner draft tendencies.
- **Season page upgrades** — playoff bracket visual with LPI, final placement in year stats, week-over-week LPI change, luck index, records vs. all-play.
- **Data platform** — migrate from committed CSV/Excel to SQLite/Parquet with a scheduled (GitHub Actions) refresh instead of manual local runs.
