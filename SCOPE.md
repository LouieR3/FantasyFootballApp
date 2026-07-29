# FantasyFootballApp — Scope & Roadmap

Last updated: 2026-07-28

This document covers: (1) current state, (2) repo organization plan, (3) a review of the draft grade calculation with recommended fixes, (4) the feature backlog, and (5) a data-hosting migration plan.

---

## 1. Current state

- **App:** Streamlit multi-page app (`streamlit-app.py` home + 16 pages in `pages/`, one per league plus LPI Master List, Biggest Upsets, and Playoff Analysis). Every league page calls the shared `display_*` functions in `page_functions.py` and has a year filter.
- **Sections per page:** Playoff Results, Schedule Comparison, LPI, Playoff Odds, Record Predictions, Playoff Odds by Week, Betting Odds, Remaining Schedule Difficulty, LPI Each Week, Strength of Schedule, Expected Wins, Draft Results, Biggest LPI Upsets, Lifetime Record.
- **Data:** file-based. ~40 Excel files in `leagues/` (one per league-year), ~90 CSVs in `drafts/` (draft + free agent results per league-year), 14 Excel files in `odds/`, plus aggregate CSVs at the root (`Master_Draft_Data.csv`, `all_matchups.csv`, `all_playoffs.csv`, etc.).
- **Pipeline:** scripts run manually on a local machine (`ESPNWeeklyUpdateList.py`, `draft_data.py`, `create_betting_odds.py`, `all_matchups.py`, ...) → output files committed to git → Streamlit Cloud redeploys.
- **Leagues with multi-year history** (candidates for lifetime features): Game of Yards! (2019–25), EBC League (2021–25), Pennoni Younglings (2022–25), 0755 Fantasy Football (2022–25), Family Fantasy (2022–25), THE BEST OF THE BEST (2022–25), Brown Munde (2023–25).

### 🔴 Security issue — fix first

ESPN `espn_s2` cookies and `SWID`s (yours and several friends') were **hardcoded in committed source** across 54 files — and the repo is publicly linked from the live app. These cookies grant login-level read access to the private leagues.

1. ✅ **Done (2026-07-28):** all credentials moved to `.streamlit/secrets.toml` (gitignored); every file now reads them through `credentials.py` (`CRED["..."]`), which falls back to Streamlit Cloud secrets and `ESPN_*` env vars.
2. ✅ **Done:** `.streamlit/secrets.toml` added to `.gitignore`; `.streamlit/secrets.toml.example` committed as a template.
3. ✅ **Done:** paste the `[espn]` block from `.streamlit/secrets.toml` into the Streamlit Cloud app's Secrets settings **before pushing**, or the deployed app will fail on the next deploy.
4. ✅ **Done:** rotate the cookies (log out/in on ESPN regenerates them) — removing them from the tip of the branch does not remove them from git history.
5. Longer term: a single league-registry config module holding league IDs + credential references, so pages and pipeline scripts stop duplicating them.

### Repo hygiene — ✅ done

- Scratch files and superseded duplicates (`test.py`, `elo_claude.py`, `headToHead2.py`, `playoff_odds_gemini.py`, `season_results_test.py`, `monte_carlo_odds_test.py`, `espn.py`, `weekTest.py`, `intro.py`, `league_history.py`, `results.txt`, `player.json`, ...) moved to `archive/` with a README explaining each. `league.py` turned out to be a vendored copy of espn_api's own module — archived too.
- `todo.txt` superseded by this document (items folded into §4).

---

## 2. Repo organization — ✅ done 2026-07-28

Actual structure (see README for the annotated version). `streamlit-app.py` kept its name so the Streamlit Cloud entrypoint setting still resolves; `pages/` stays at the root because Streamlit requires it.

```
FantasyFootballApp/
├── streamlit-app.py            # Streamlit entrypoint
├── pages/                      # league pages (Streamlit requirement)
├── paths.py                    # repo-anchored data locations — ALL file I/O
├── credentials.py              # ESPN secrets loader
├── ffapp/
│   ├── ui/         page_functions, lifetime_record_owner, calcPercent, playoffNum
│   ├── metrics/    monte_carlo_odds, draft_grading, create_betting_odds, owner_overrides
│   └── espn/       draft_data, all_matchups, all_playoffs, season_results
├── pipeline/       ESPNWeeklyUpdateList, ESPNWeeklyUpdate, ESPN_Add_Old_Season,
│                   regrade_drafts, add_current_week_results, playoff_chances, ...
├── experiments/    one-off explorations (lpi, elo, printOwners, strengthOfSchedule, ...)
├── analysis/       offline studies
├── archive/        dead code; nothing imports it
└── data/           leagues/  drafts/  odds/  + cross-league aggregate CSVs
```

Two structural wins beyond the file moves:

- **`paths.py`** — every data read/write resolves against the repo root instead of the
  current directory. Previously a script run from anywhere but the repo root would
  crash or silently write files to the wrong place; now `python pipeline/anything.py`
  works from any directory. Verified by running the grading pipeline from `C:\Windows\Temp`.
- **Depth-independent bootstrap** — scripts outside the root walk up to find `paths.py`
  and put the repo root on `sys.path`, so they run as plain scripts (no `-m` needed).

Still open from the original plan:

1. A league-registry config module (league IDs + credential references are still duplicated across pipeline scripts and `pages/`). This is the single biggest remaining duplication.
2. Splitting `page_functions.py` (~36 KB, 15 functions) into per-section modules under `ffapp/ui/`.
3. `experiments/` deserves a triage pass — several of those scripts are probably dead rather than merely exploratory.

---

## 3. Draft grade review

The grade is computed in `draft_data.py` (and mirrored in `analysis/draft_analysis*.py`). Current design: a weighted sum of ratios → min-max scaled to 1–100 within the league-year → `10 * grade^0.51` transform → clip at 100 → letter grade.

### Problems found

**P1 — Free agent grades are computed from the wrong rows (bug).** In `freeAgentResults()`, the non-2024 branch grades `additions_df` using `draft_df['Points'] / max_points` and `draft_df['Avg Points'] / max_avg_points` (draft_data.py:346–347) — drafted players' stats, not the free agents'. Worse, `draft_df` was previously sorted by grade, so pandas index alignment pairs each free agent with an essentially random drafted player. The 2024 branch has the same alignment problem dividing `additions_df['Points']` by `draft_df['Projected Points']` (lines 331–332): mismatched indexes produce NaN/garbage. **Free agent grades for non-2024 years are effectively noise.**

**P2 — The draft-position term flips sign between year branches.** The 2024 formula rewards *later* picks: `(Total Pick − 1)/(max_pick − 1) × 0.4` (line 178). The other-years formula rewards *earlier* picks: `(max_pick − Total Pick)/max_pick × 0.4` (line 203). They can't both be right. More fundamentally, an additive position term measures nothing about steals — a last-round bust gets the same +0.4 credit as a last-round league-winner. "Steal-ness" is an interaction: performance *relative to what that slot usually returns* (see fix below).

**P3 — Mixed scales make the stated weights meaningless.** Most terms are 0–1 ratios, but `Position Value` (points ÷ positional mean) and `Round Value` (avg points ÷ round mean) are unbounded — a top QB or a late-round hit routinely scores 2–4+. With W5 = 0.5, Position Value alone can contribute more than every 0–1 term combined, so the effective weighting bears little relation to the intended one.

**P4 — Projection ratios are unstable.** `Points / Projected Points` explodes (or divides by zero) for players with tiny/zero projections — exactly the late-round fliers the grade should handle well. This is likely why the formula forked into a 2024-only branch.

**P5 — Per-league-year min-max scaling breaks comparability.** Forcing min = 1 and max = 100 within each league-year means someone always gets ~100 and someone ~1 regardless of absolute quality, a single outlier compresses everyone else into a narrow band, and grades can't be compared across leagues or years — which undermines the lifetime/draft-history features planned in §4.

**P6 — The `^0.51` curve + clip pins the top.** After min-max, the max is 100, and `10 × 100^0.51 ≈ 105` → clipped to 100. Several players pin at exactly 100, and the curve compresses differences among good picks (the region you care most about).

**P7 — Smaller issues.** `max_games = 14` is hardcoded while season points accrue over 17–18 weeks; the letter scale bottoms out at "F-" with no "F"; two divergent formulas (2024 vs. else) with different weight sets makes results era-dependent; weights W1–W8 are ad hoc with no validation against any ground truth.

### Recommended redesign — ✅ implemented 2026-07-28

**Team-level grades are standardized separately** (added same day): a capital-weighted mean of ~16 pick grades has sd 10/√16 ≈ 2.5, which squeezed every team into C-/C/C+ regardless of how they drafted. Team scores are now z-scored again across teams within the season, giving team grades their own 75 ± 10 spread (sd 9.95, range 52–100, full A+→F). Ordering and the −0.50 standings correlation are unchanged. `lifetime_record.py` / `lifetime_record_owner.py` read this via `draft_grading.team_draft_grade()` instead of averaging pick grades themselves.

⬜ **Open question — draft grade vs. end-of-season roster.** The draft grade intentionally measures *draft-day decisions only*: full-season points of the players you drafted, whether or not you kept them. It says nothing about in-season roster management (waiver hits, trades, drops). A separate **Roster Grade** blending draft grade with the free-agent `Performance Grade` (weighted by share of the team's actual scoring) would measure "how well did you build this roster all year" — see §4.2.

The redesign below now lives in `draft_grading.py` (shared by `draft_data.py` and runnable standalone: `python draft_grading.py` regrades every `drafts/` CSV and rebuilds `Master_Draft_Data.csv`, `Aggregated_Draft_Grades.csv`, and the grade columns of `Draft_Grades_with_Standings.csv`). Grade = 0.6·z(value over slot) + 0.4·z(points above replacement), standardized within season across all leagues, mapped to 75 ± 10 per z (clip 30–100). The expectation curve is keyed on the Nth-player-taken-at-a-position, so it transfers across 8–16 team drafts. Validation: all 26 top-12-pick sub-100-point busts grade F; late steals (pick ≥ 100, > 250 pts) average 85; team draft grade correlates with final standing at −0.50. Known gap: 26 `RRR On Premise` rows in `Draft_Grades_with_Standings.csv` have no standings/year (pre-existing — that league was never in the standings script's league list) and keep stale grades.

1. **Grade = value over slot expectation.** You already have the dataset for this: `Master_Draft_Data.csv` spans every league-year. Fit a curve of expected season points as a function of overall pick number (log/monotone spline, optionally per position). Then a pick's grade is `(actual points − expected points at that slot)`, standardized. This single term *is* the steal/bust measure — it replaces P2's additive position term, works identically for every year (kills the 2024 fork), and needs no projection data (fixes P4).
2. **Use points above replacement for positional value.** Instead of points ÷ positional mean (unbounded, P3), compute points above the replacement-level player at that position (replacement = the (starters × teams)-th ranked player). This is bounded-ish, league-size aware, and correctly values scarce positions.
3. **Standardize with z-scores or percentiles, not min-max.** Combine the (few) components as z-scores within a season across *all* leagues, then map to 0–100 via percentile. Grades become comparable across leagues and years (fixes P5, P6) — a prerequisite for "lifetime draft grade" features.
4. **Fix the free agent frame (P1)** — compute every component from `additions_df` with `reset_index(drop=True)` applied after any sort, before arithmetic that pairs frames. Consider grading FA pickups as points-above-replacement accrued *after acquisition date* rather than full-season points.
5. **Team draft grade:** weight pick grades by draft capital (early picks matter more) rather than a simple mean, and validate the formula: regress team draft grade against final standings / points-for across `Draft_Grades_with_Standings_Enhanced.csv` history and tune until the correlation is meaningful. That file exists precisely to make this testable.
6. Derive `max_games` from the league's actual season length instead of hardcoding 14.

---

## 4. Feature backlog

Items carried over from `todo.txt` are marked ⭐.

### 4.1 Lifetime / multi-year (for leagues with 2+ seasons)

- ⭐ **Owner career table:** Year, W, L, Points For, Points Against, Final Place, Draft Grade — one row per season, including playoff matchups in the totals.
- **Franchise trend charts:** wins, PF/PA, and season-end LPI by year (line charts); draft grade by year.
- **All-time records book:** highest single-week score, biggest blowout, closest game, longest win/loss streaks, best/worst season, most points in a loss / fewest in a win — all derivable from `all_matchups.csv`.
- **Head-to-head rivalry view:** pick two owners → lifetime record, average margin, playoff meetings, notable games.
- **Championship/podium tracker:** titles, finals appearances, playoff appearance rate per owner.
- ⭐ **Cross-season Elo** (`elo.py` exists — surface it): Elo carried across seasons with decay, charted over the franchise's life.
- **Owner-based identity** (`lifetime_record_owner.py` started this): key everything on Owner ID rather than team name so renames don't split history.
- ✅ **Co-owner attribution** (2026-07-28): ESPN returns a list of owners per team and the code took `owners[0]`, so a co-owned season landed on whoever ESPN listed first — splitting a franchise's history across two people. `owner_overrides.py` now defines the canonical owner per co-owned team-year, and every user-facing path resolves through it. First entry: Pennoni Younglings 2024 "Philadelphia Bills Mafia" (Henry Morris + Robbie Wilston) → **Robbie Wilston**, so Henry's history is 2022–2023 and Robbie's is 2024–2025. Add future cases to `PREFERRED_CO_OWNER`.

### 4.2 Draft & player analytics

- ⭐ **"Best possible team" button** — optimal lineup from that year's draft pool given the league's roster slots.
- ⭐ **Best pick of each round**; ⭐ **biggest steals / biggest busts** (falls straight out of the value-over-slot grade in §3).
- **Draft position tendencies per owner:** positional mix by round across years (e.g., "always takes a QB by round 3").
- **Round-by-round hit rate:** share of picks per round that returned starter-level value, per owner and league.
- **Draft grade vs. final standing scatter** across all league-years — does drafting well predict winning? (validates §3.5).
- **Player-level views:** most-drafted players by owner across years ("player loyalty"), points by acquisition type (drafted vs. FA vs. trade), best FA pickup of the year.
- **Roster Grade** (distinct from Draft Grade): blend the team's draft grade with its free-agent Performance Grades, weighted by each group's share of actual points scored, so the number reflects the roster the team *finished* with rather than draft day alone. Pairs naturally with a "draft grade vs. roster grade" delta column — big positive deltas identify the best in-season managers.
- **Post-draft roster churn:** % of drafted roster still on the team at season end.

### 4.3 Season page upgrades

- ⭐ **Playoff bracket visual** with each team's LPI next to their name.
- ⭐ **Final place added to year-by-year stats.**
- ⭐ **LPI change vs. last week** (arrow/delta column) on the LPI table.
- **Luck index:** actual record vs. all-play record (you already compute the all-play grid for Schedule Comparison — surface the gap as a single "luck" number).
- **Weekly margin chart:** per-team margin of victory/defeat by week.
- **Points distribution:** box/violin per team to show consistency vs. boom-bust (feeds intuition for the Monte Carlo odds).
- **Matchup explorer** (stub exists at the bottom of league pages): pick two teams → season series, scores, LPI at time of matchup.
- ⭐ **Predicted score shown on playoff matchups.**
- ⭐ **Monte Carlo playoff simulation → odds to win it all** (extend `monte_carlo_odds.py` through the bracket, not just seeding).
- **Performance:** wrap file loads in `@st.cache_data` — every section currently re-reads Excel on each rerun.

### 4.4 Pipeline / structural

- ⭐ **Backfill previous years** for each league: weekly update, playoff results, draft results, all matchups, draft grades with standings (`ESPN_Add_Old_Season.py` is the tool).
- ⭐ **Fill known data gaps:** Game of Yards! draft files 2019–2021; Turf On Grade 2.0 drafts 2023–24.
- **One config to rule them all:** single league registry consumed by pages and pipeline (see §2 step 3).
- **Automated weekly refresh** — see §5.

---

## 5. Data hosting: analysis & recommendation

### Today

CSV + Excel files committed to git; the app reads them with pandas/openpyxl on every page load. Manual local script runs push updates.

**Pain points:** Excel reads are slow (openpyxl) and uncached; filenames are the schema (league name + year string, emoji included — `The Girl's Room 💞🏈 2025.xlsx`), so joins across datasets are string-matching exercises; binary `.xlsx` diffs bloat git history; a weekly refresh requires you at your machine; no data validation ever runs; aggregate files (`Master_Draft_Data.csv`, `all_matchups.csv`) duplicate what's in the per-league files and drift.

### Options

| Option | Effort | What it buys | What it doesn't |
|---|---|---|---|
| **A. SQLite (or DuckDB) file in repo** | Low | One `app.db` replaces ~150 files; real schema + keys (league_id, owner_id, year, week); fast queries; joins for free; still zero-infrastructure on Streamlit Cloud | Still commit-to-deploy; concurrent writes N/A (fine here) |
| **B. Parquet files in repo** | Low | 10–50× faster reads than xlsx, typed columns, small diffs | Still file-per-dataset; no joins/constraints |
| **C. Hosted Postgres (Supabase / Neon free tier) + `st.connection`** | Medium | Data updates without git commits; app always current; enables on-demand refresh button in the app | External dependency; free-tier limits; secrets management required (needed anyway) |
| **D. GitHub Actions weekly cron** running the pipeline and committing outputs | Low–Medium | Kills the manual weekly run regardless of storage choice; ESPN cookies live in Actions secrets | Cookies expire (~1 year) and need occasional refresh |

### Recommendation (phased)

1. **Phase 1 — SQLite + caching (do this first).** Write a one-time importer that loads `leagues/`, `drafts/`, `odds/`, and the aggregate CSVs into `data/app.db` with proper tables (`seasons`, `teams`, `owners`, `matchups`, `draft_picks`, `weekly_odds`, ...). Add a `src/db.py` loader used by `page_functions.py`, wrapped in `@st.cache_data`. Keep writing the CSV/Excel alongside during one season as a safety net. This fixes speed, schema, and name-matching in one move with no new infrastructure.
2. **Phase 2 — GitHub Actions weekly refresh.** Tuesday-morning cron: pull ESPN → rebuild `app.db` → commit. Credentials from Actions secrets (depends on §1 security work).
3. **Phase 3 (optional) — Supabase/Neon** only if you want same-day updates without deploys or an in-app "refresh now" button. The schema from Phase 1 ports directly; SQLite may well be the permanent answer for this data size (~a few MB/season).

---

## 6. Suggested sequencing

| Priority | Work | Sections |
|---|---|---|
| 1 | Secrets out of source + rotate cookies | §1 |
| 2 | Fix free-agent grade bug; pick one draft formula | §3 P1–P2 |
| 3 | SQLite migration + `st.cache_data` | §5 Phase 1 |
| 4 | Draft grade redesign (value-over-slot + PAR) | §3 |
| 5 | Lifetime/owner career features (unlocked by 3 & 4) | §4.1 |
| 6 | GitHub Actions weekly refresh | §5 Phase 2 |
| 7 | Season-page upgrades & draft analytics backlog | §4.2–4.3 |
