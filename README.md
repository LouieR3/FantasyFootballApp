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
| **Draft Results** | Every draft pick graded 30–100 with a letter grade: 60% value-over-slot (production vs. what that draft slot historically returns, fit from every league-year on file) + 40% points-above-replacement at the position. Grades are standardized within each season across all leagues, so they're comparable everywhere (see `draft_grading.py`) |
| **Biggest LPI Upsets** | Wins by teams with a large LPI deficit vs. their opponent |
| **Lifetime Record** | All-time results for the league across seasons |

## Repo layout

```
FantasyFootballApp/
├── streamlit-app.py          # App entry point / home page
├── page_functions.py         # Shared display_* functions used by every league page
├── pages/                    # One Streamlit page per league (+ LPI master list, upsets, playoff analysis)
├── leagues/                  # Per-league, per-year season data (Excel) consumed by the app
├── drafts/                   # Per-league, per-year draft + free agent results (CSV)
├── odds/                     # Per-league betting odds (Excel)
├── analysis/                 # Offline analysis scripts (draft grading studies, playoff chances)
│
│   # Data pipeline (run locally to refresh data, then commit):
├── ESPNWeeklyUpdate.py       # Weekly pull: standings, matchups, LPI inputs → leagues/*.xlsx
├── ESPNWeeklyUpdateList.py   # Same, looped over all configured leagues
├── ESPN_Add_Old_Season.py    # Backfill a past season
├── draft_data.py             # Pull draft + free agent results and compute draft grades → drafts/*.csv
├── monte_carlo_odds.py       # Playoff odds simulation engine
├── create_betting_odds.py    # Weekly matchup betting lines → odds/*.xlsx
├── all_matchups.py           # Build all_matchups.csv (every H2H matchup, all leagues/years)
├── all_playoffs.py           # Build playoff results dataset
├── lifetime_record.py        # Lifetime records per team/owner
└── ...                       # Metric modules (lpi.py, elo.py, strengthOfSchedule.py, playoff_chances.py, etc.)
```

## Running locally

```bash
pip install -r requirements.txt
streamlit run streamlit-app.py
```

The app reads from the committed files in `leagues/`, `drafts/`, and `odds/`, so it runs without ESPN credentials.

## Refreshing data (weekly, during the season)

1. Run `ESPNWeeklyUpdateList.py` to pull the latest week for all leagues into `leagues/`.
2. Run `create_betting_odds.py` to regenerate `odds/`.
3. After drafts (or to refresh grades): run `draft_data.py` → `drafts/`.
4. Commit and push — Streamlit Cloud redeploys from the repo.

ESPN private-league access requires `espn_s2` and `SWID` cookies. All code reads them via `credentials.py` (`CRED["louie_s2"]`, etc.), which loads from `.streamlit/secrets.toml` (gitignored — copy `.streamlit/secrets.toml.example` and fill it in), from Streamlit Cloud's secrets settings, or from `ESPN_*` environment variables. Never put cookie values in source.

## Roadmap

The full scope, feature backlog, draft-grade methodology review, and data-hosting migration plan live in **[SCOPE.md](SCOPE.md)**. Highlights:

- **Lifetime & franchise history** — owner career tables (year, W/L, PF/PA, place, draft grade), multi-year LPI and points charts, all-time records book, head-to-head rivalry views, cross-season Elo.
- **Draft analytics** — best-possible-team button, best pick per round, biggest steals/busts, value-over-slot grading, owner draft tendencies.
- **Season page upgrades** — playoff bracket visual with LPI, final placement in year stats, week-over-week LPI change, luck index, records vs. all-play.
- **Data platform** — migrate from committed CSV/Excel to SQLite/Parquet with a scheduled (GitHub Actions) refresh instead of manual local runs.
