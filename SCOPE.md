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

## 2a. Streamlit display sweep — ✅ done 2026-07-28

- Home page rewritten: all 14 sections documented (it covered 5), dead commented blocks and unused imports removed, the italicized *NEW* dropped from Playoff Odds, typos fixed.
- Added the missing section descriptions for **Playoff Results**, **Draft Results** and **Biggest LPI Upsets** (the last had the LPI blurb pasted in by mistake, commented out). **Playoff Odds By Week** had a verbatim copy of the Playoff Odds text.
- **Corrected a factual error:** Schedule Comparison said to read "right to left". The grid is `records_df.at[team, opp]` — row = your team, column = the opponent whose schedule you borrow — so it reads **left to right** across your row.
- Layout: `width=2000` (wider than any viewport) → `use_container_width`; `st.markdown("---")` → `st.divider()`; 8 pages' title emoji now matches their sidebar icon.

### Page smoke test

`python tools/smoke_pages.py` executes every page in `pages/` plus `streamlit-app.py` with
streamlit, the `display_*` layer, espn_api and the chart libraries stubbed, so each page's
own logic (year selection, path building, ordering) runs for real. It exists because
`py_compile` passes on code that still blows up at runtime: an `UnboundLocalError` shipped
to production when a year-selector block landed *below* the `st.title()` that used
`selected_year`. Run it before pushing page changes.

It also caught a pre-existing crash in Playoff Analysis: `Index.map(...).round(3)` -
`Index` has no `.round()`, so that section failed on any pandas version.

### Page configuration bugs found during the sweep

- **Year selectors were broken or absent.** Six leagues advertised four seasons but only have 2025 data, so any other year 404'd; the workaround had been to comment the selector out and pin the year. Years now come from `available_years()`, which reads what's on disk — working selector on every page, only real options, new seasons appear automatically, no annual edits.
- **Five pages pointed at the wrong ESPN league** (copy-pasted from Las League, `league_id`/credentials never updated). This is why `display_lifetime_record` — the one section needing a correct `league_id` — was commented out on several pages.

  | Page            | was                                                                     | now                                                |
  | --------------- | ----------------------------------------------------------------------- | -------------------------------------------------- |
  | The Girl's Room | 1049459 /`la_s2`                                                      | 1399036372 /`hannah_s2`                          |
  | Matts League    | 1049459 /`la_s2`                                                      | 261375772 /`matt_s2`                             |
  | Turf On Grade   | 1118513122 (EBC's id)                                                   | 1242265374 /`turf_s2`                            |
  | Avas League     | 1049459 /`la_s2` (Las League's id!), showed Operators Football League | 1259693145 /`elle_s2`, Operators Football League |
  | Elles League    | 1259693145 /`elle_s2`, showed Philly Extra Special                    | 417131856 /`ava_s2`, Philly Extra Special        |

  Both Avas/Elles pages were internally inconsistent — each displayed one league while holding a different league's id. Louie confirmed **Operators Football League is Ava's league**, so Avas League keeps that league and gets the matching id; Elles League keeps Philly Extra Special. Credential keys stay paired with the id known to read each league even though the key *names* no longer match the association (see §2c).

  Lifetime Record re-enabled on the Avas/Elles pages. ⬜ **Still commented out on 6 pages** (Family League, Turf On Grade, Dave Redbull, Dave Friend, Matts, The Girl's Room, Dukes) — their league IDs are now correct, so they can probably be switched back on, but that needs a live run to confirm rather than being enabled blind.
- ⬜ A **league registry** (§2 item 1) would have prevented this entire class of bug and is now clearly the highest-value remaining cleanup.

---

## 2b. Weekly-update season-boundary bugs — ✅ fixed 2026-07-28

The weekly scripts needed hand-editing at season boundaries. Root cause: week detection was duplicated inline in both scripts with *different* semantics, and neither was right at the edges. Logic now lives in `ffapp/espn/week_utils.py` with 12 unit-tested boundary cases (preseason, week 1, mid-season, last regular week, each playoff week, full season, and `reg_season_count` of 12/13/14/15 for leagues whose playoffs start earlier or later).

`current_week` now means *the next week to be played*, so `range(1, current_week)` is exactly the completed weeks. One definition, one assignment per script.

| #  | Bug                                                                                                                           | Symptom                                                                                                                        |
| -- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| 1  | `current_week = 19` hard-coded in `ESPNWeeklyUpdateList.py`, overriding detection                                         | every league treated as an 18-week season                                                                                      |
| 2  | `ESPNWeeklyUpdate.py` added `+ 1` after detecting the week                                                                | computed LPI for an unplayed week mid-season                                                                                   |
| 3  | `else: current_week = scores_df.shape[1]` (off by one)                                                                      | **the final week never got an LPI column** once the season completed                                                     |
| 4  | `if current_week > 1` then read `'Week ' + str(week-1)`                                                                   | **KeyError 'Week 0' after week 1** — the first-week crash                                                               |
| 5  | Playoff block gated on`current_week > reg_season_count`                                                                     | fired before the first playoff game finished, then asked "LPI By Week" for columns it didn't have → KeyError at playoff start |
| 6  | Playoff loop ran`range(reg_season_count, last_column_name+1)`                                                               | walked*unplayed* trailing weeks, inventing 0-0 matchups                                                                      |
| 7  | `lpi_week_df` read from the **previous run's** workbook                                                               | a league's first run has no file to read                                                                                       |
| 8  | `ESPNWeeklyUpdate.py`: `fileName` reassigned to a full path inside the playoff branch, then re-wrapped at the final write | wrote to`data/leagues/data/leagues/<name>.xlsx.xlsx` — **the workbook write crashed as soon as playoffs began**       |
| 9  | `ESPNWeeklyUpdate.py`: `lpi_df` (Louie Power Index) reassigned to LPI-By-Week data                                        | **"Louie Power Index" sheet silently corrupted during playoffs**                                                         |
| 10 | Playoff Results appended via openpyxl, then`pd.ExcelWriter(..., 'xlsxwriter')` recreated the workbook without it            | **the sheet was destroyed on every run**                                                                                 |
| 11 | A*second* `current_week` calculation inside the playoff block reassigned it                                               | Monte Carlo ran with a different week than the rest of the script                                                              |
| 12 | `ESPNWeeklyUpdate.py` never computed Remaining Schedule Difficulty, but truncates the workbook                              | running the single-league script**deleted** that sheet, breaking its page section                                        |

Byes and varying bracket sizes were already handled correctly (`opponent == team` → bye; round names derived from remaining team count) and were left alone.

⚠️ Not executed: these scripts need `espn_api` and live ESPN access, which the dev environment here lacks. Every change is a targeted edit verified by compile + static checks, and `week_utils` is unit-tested, but **the first real run of each script should be watched**.

---

## 2c. League registry — ✅ added 2026-07-28

`ffapp/league_registry.py` is now the single place that knows what each league is, whose it is, and how to reach it. Pages, the pipeline and the colour-coded cross-league pages should all read from here instead of repeating league IDs and credential keys — that duplication is what put five pages on the wrong ESPN league (§2a).

**Association is the important column:** nobody refers to these by their ESPN names. "Operators Football League" is *Ava's league*; that's the only handle that means anything. It drives the colour key on the LPI Master List and Biggest Upsets pages, and the league dropdowns are labelled with it.

| Association (whose league)                    | ESPN league name                | Seasons on file | League ID  | Credential key     | Page                                       |
| --------------------------------------------- | ------------------------------- | --------------- | ---------- | ------------------ | ------------------------------------------ |
| **Louie - Pennoni coworkers**           | Pennoni Younglings              | 2022–2025 (4)  | 310334683  | `louie_s2_pages` | `1_🏈_Pennoni_Younglings.py`             |
| **Louie - family**                      | Family Fantasy                  | 2022–2025 (4)  | 996930954  | `louie_s2_pages` | `1_👪_Family_League.py`                  |
| **Louie - EBC friends**                 | EBC League                      | 2021–2025 (5)  | 1118513122 | `louie_s2_pages` | `1_🎮_EBC_League.py`                     |
| **Prahlad - Pennoni Transportation**    | 0755 Fantasy Football           | 2022–2025 (4)  | 1339704102 | `prahlad_s2`     | `1_🛠️_Pennoni_Transportation.py`       |
| **Prahlad - friends**                   | Game of Yards!                  | 2019–2025 (7)  | 1781851    | `prahlad_s2`     | `3_🧑‍🤝‍🧑_Prahlad_Friends_League.py` |
| **Prahlad - Brown Munde**               | Brown Munde                     | 2023–2025 (3)  | 367134149  | `prahlad_s2`     | `3_🧑‍🤝‍🧑_Brown_Munde.py`            |
| **Prahlad - Turf On Grade**             | Turf On Grade 2.0               | 2023–2024 (2)  | 1242265374 | `turf_s2`        | `4_🧑‍🤝‍🧑_Turf_On_Grade.py`          |
| **Las league**                          | THE BEST OF THE BEST            | 2022–2025 (4)  | 1049459    | `la_s2`          | `5_🍝_Las_League.py`                     |
| **Hannah**                              | The Girl's Room 💞🏈            | 2025            | 1399036372 | `hannah_s2`      | `5_💅_The_Girls_Room.py`                 |
| **Ava**                                 | Operators Football League       | 2025            | 1259693145 | `elle_s2`        | `5_👱🏻‍♀️_Avas_League.py`            |
| **Elle**                                | Philly Extra Special            | 2025            | 417131856  | `ava_s2`         | `5_🦝_Elles_League.py`                   |
| **Dave - work (OnP)**                   | OnP Fantasy                     | 2025            | 1675186799 | `dave_s2`        | `5_🍹_Dave_Redbull_League.py`            |
| **Dave - friends**                      | The Mike Daisy Sports IQ League | 2025            | 1924463077 | `dave_s2`        | `5_🎮_Dave_Friend_League.py`             |
| **Jackson (Dukes)**                     | Ross' Fantasy League            | 2025            | 558148583  | `ayush_s2`       | `6_👑_Dukes_League.py`                   |
| **Matt**                                | BP- Loudoun 2025                | 2025            | 261375772  | `matt_s2`        | `5_👷🏻‍♀️_Matts-League.py`           |
| **Dave - older On Premise league ⚠️** | RRR On Premise                  | 2024            | —         | —                 | *(no page)*                              |
| **unknown ⚠️**                        | Board Fantasy Football          | 2025            | —         | —                 | *(no page)*                              |

⚠️ = association inferred rather than stated by Louie; worth confirming.

Notes:

- **Credential keys are historical labels and do not always match the association.** `elle_s2` reads Ava's league and `ava_s2` reads Philly Extra Special. The key names came from the variable names in the pre-secrets code; what matters is that each `league_id` stays paired with the cookie known to read it. Renaming the keys is safe but must be done in `.streamlit/secrets.toml`, Streamlit Cloud secrets and the registry together.
- **`Board Fantasy Football` and `RRR On Premise `** have data on disk but no page and no known owner — candidates for either a page or archiving. Note the trailing space in `RRR On Premise `, which is load-bearing for the filename match.
- Next step: have `pages/` and `pipeline/` import from the registry rather than hard-coding IDs. The pages still declare their own `league_id`/credentials; wiring them through the registry is the remaining half of this fix.

---

## 3. Draft grade review

The grade is computed in `draft_data.py` (and mirrored in `analysis/draft_analysis*.py`). Current design: a weighted sum of ratios → min-max scaled to 1–100 within the league-year → `10 * grade^0.51` transform → clip at 100 → letter grade.

### Problems found

**P1 — Free agent grades are computed from the wrong rows (bug).** In `freeAgentResults()`, the non-2024 branch grades `additions_df` using `draft_df['Points'] / max_points` and `draft_df['Avg Points'] / max_avg_points` (draft_data.py:346–347) — drafted players' stats, not the free agents'. Worse, `draft_df` was previously sorted by grade, so pandas index alignment pairs each free agent with an essentially random drafted player. The 2024 branch has the same alignment problem dividing `additions_df['Points']` by `draft_df['Projected Points']` (lines 331–332): mismatched indexes produce NaN/garbage.

**Corrected severity (measured after the fact):** an earlier draft of this document called those grades "effectively noise" — that was too strong. Two of the four terms (`Games Played`, `Position Value`) *were* computed from the free agent's own row, so the old grades still correlated with the free agent's actual points at **+0.65** on average within a league-year. The redesign raises that to **+0.77**. So the bug degraded the grades rather than randomising them.

**P2 — The draft-position term flips sign between year branches.** The 2024 formula rewards *later* picks: `(Total Pick − 1)/(max_pick − 1) × 0.4` (line 178). The other-years formula rewards *earlier* picks: `(max_pick − Total Pick)/max_pick × 0.4` (line 203). They can't both be right. More fundamentally, an additive position term measures nothing about steals — a last-round bust gets the same +0.4 credit as a last-round league-winner. "Steal-ness" is an interaction: performance *relative to what that slot usually returns* (see fix below).

**P3 — Mixed scales make the stated weights meaningless.** Most terms are 0–1 ratios, but `Position Value` (points ÷ positional mean) and `Round Value` (avg points ÷ round mean) are unbounded — a top QB or a late-round hit routinely scores 2–4+. With W5 = 0.5, Position Value alone can contribute more than every 0–1 term combined, so the effective weighting bears little relation to the intended one.

**P4 — Projection ratios are unstable.** `Points / Projected Points` explodes (or divides by zero) for players with tiny/zero projections — exactly the late-round fliers the grade should handle well. This is likely why the formula forked into a 2024-only branch.

**P5 — Per-league-year min-max scaling breaks comparability.** Forcing min = 1 and max = 100 within each league-year means someone always gets ~100 and someone ~1 regardless of absolute quality, a single outlier compresses everyone else into a narrow band, and grades can't be compared across leagues or years — which undermines the lifetime/draft-history features planned in §4.

**P6 — The `^0.51` curve + clip pins the top.** After min-max, the max is 100, and `10 × 100^0.51 ≈ 105` → clipped to 100. Several players pin at exactly 100, and the curve compresses differences among good picks (the region you care most about).

**P7 — Smaller issues.** `max_games = 14` is hardcoded while season points accrue over 17–18 weeks; the letter scale bottoms out at "F-" with no "F"; two divergent formulas (2024 vs. else) with different weight sets makes results era-dependent; weights W1–W8 are ad hoc with no validation against any ground truth.

### Status: can this be checked off?

**Yes for the grading itself** — verified against the current data on 2026-07-28:

| Check                                   | Result                                                                              |
| --------------------------------------- | ----------------------------------------------------------------------------------- |
| Draft picks graded                      | 6,772 / 6,772 rows, 0 NaN, all within 30–100                                       |
| Free agents graded                      | 1,710 / 1,710 rows, 0 NaN, all within 30–100                                       |
| Letter grades match their numeric grade | 0 mismatches across all 75 files                                                    |
| Grade spread (picks / FAs)              | sd 9.93 / 10.00 — full range in use, no pinning                                    |
| Team grades                             | 429 team-seasons, sd 9.95, range 51.7–100, full A+→F                              |
| Predictive validity                     | team grade vs final standing**r = −0.51**, vs points-for **r = +0.53** |
| FA grade vs that FA's own points        | **+0.77** mean within league-year (was +0.65)                                 |
| P1–P7 from above                       | all addressed; one formula for every season                                         |

⬜ **Three things remain open** (none of them block using the grades):

1. **Free agent grades use full-season points, not points after acquisition.** A player picked up in week 12 is credited with everything they scored from week 1. Fixing this needs transaction dates, which the current pull doesn't collect (`league.recent_activity()` would provide them). This is the most substantive remaining inaccuracy.
2. **26 `RRR On Premise` rows in `Draft_Grades_with_Standings.csv` keep stale grades.** They have no Year or Standing, so the regrade can't match them. That league has no page and no known league_id in the registry — needs its id/credentials, or those rows should be dropped.
3. **Availability no longer factors in.** The old formula gave credit for Games Played; the new one is purely points-based (value over slot + points above replacement). A 10-game monster now grades above a 17-game merely-good player. That's defensible but it is a behaviour change worth being aware of.

One operational note: `pull_draft_data()` writes raw stats with **blank** grades on purpose, because grades are pooled across all league-seasons. Any pull must be followed by `python pipeline/regrade_drafts.py`, or the new season's CSVs will have empty grade columns.

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

## 3b. Post-season draft analysis — ✅ built 2026-07-28

New page `pages/13_🔎_Draft_Analysis.py` over `ffapp/metrics/draft_analysis.py`. Pick a league and season and get a full draft post-mortem, in seven tabs.

**The core idea — accuracy vs luck.** Each pick is measured against **Expected** (what that draft slot historically returns, from the position-rank curve fit across all 39 league-seasons), then split:

|              |                                                                                                    |
| ------------ | -------------------------------------------------------------------------------------------------- |
| `ACCURACY` | Projected − Expected — you took a player the market already rated above the slot. Your decision. |
| `LUCK`     | Actual − Projected — breakouts, injuries, situation. Not your decision.                          |
| `VALUE`    | Actual − Expected = ACCURACY + LUCK                                                               |

Verified exact (`max residual 0.000000000`) across all 39 league-seasons.

Two measurement problems found and fixed while building it:

- **Raw accuracy/luck were badly biased.** ESPN projections assume a full healthy season, so they sit **~46 points per pick** above the median outcomes the slot curve is fit on. Uncentred, *every* manager looked highly accurate and desperately unlucky. Both are now centred on the league-season mean, so 0 = average drafter. Centring is a constant shift, so the identity survives.
- **It is called "accuracy", not "skill", on purpose.** Measured over 102 consecutive-season owner pairs: accuracy repeats year over year at **r = +0.08** — indistinguishable from zero at that sample size (luck +0.03, total value +0.24). The metric describes how a draft was *built* relative to the market; it is not evidence of durable talent. The UI says so too.

### Table display: decimals and heights — ✅ 2026-07-28

`ffapp/ui/tables.py` centralises two display fixes that were affecting every styled table in the app.

- **Decimals.** pandas' `styler.format.precision` defaults to **6**, so any styled table rendered 1954.3 as `1954.300000`. Fixed with a Styler format (not a cast to string — strings would break the colour gradients and column sorting). `apply_display_defaults()` sets precision to 1 for the session; explicit `.format()` calls still win, and `show_table(..., formats={'LPI': '{:.0f}'})` handles per-column overrides. Verified: **0 cells with 4+ decimals** across all 12 tables on the Draft Analysis page and 6 sampled league-page sections.
- **Heights.** `table_height(n_rows)` returns `35·rows + 35 header + 3` so nothing scrolls. This replaces `460 + (len(names) - 12) * 40`, which was pasted 9 times and only right at 12 teams (it also fell back to `height="auto"` for ≤10). The new formula reproduces it — 458px vs 460px at 12 teams, confirming 35px rows — and now handles every league size: 8→318, 10→388, 12→458, 14→528, 16→598. Long tables (every pick in a draft) pass `max_rows` to cap the height and scroll past that point.

One ordering gotcha worth remembering: a later `Styler.format()` overrides an earlier one, so a general precision applied *after* a per-column format silently clobbers it. `show_table` applies general precision first, then `formats`, and callers must pass column overrides through the parameter rather than pre-formatting.

### Best lineup you could have drafted — slot-constrained, exact

Headline of the Best lineup tab. Each manager is held to **their own draft slots**: at pick 9 you may have anyone who really went 9th or later. A 4th-round breakout was reachable by everyone, so the question becomes who reached.

Why not full hindsight ("best 9 in the draft, order ignored")? Tried it: for Pennoni Younglings 2025 it yields one lineup worth 2860.9 and hands **every** manager that identical number. It ranks nobody. Kept only as an all-star-of-the-draft curiosity.

**Exact, not greedy.** Only starters score, so this is "pick players to fill the lineup, each assigned to one of your own pick slots, maximise points". A player drafted at overall pick `a` is reachable at your slot `p` iff `a >= p`, so reachable sets nest as `p` grows — meaning an optimal assignment never needs to cross, and walking players in actual-pick order against slots in order is provably optimal. That reduces to a DP over (player, slot, slots filled). Cross-checked against brute force on a reduced pool: **837.32 both**. ~2.7 s per league-season, cached.

Verified across 429 team-seasons: every chosen player was reachable at the slot used, no player or slot reused, slot caps respected, positions legal for their slot, reconstructed lineup total equals the DP optimum, and the ceiling never falls below what the manager actually achieved.

**Result: the ceiling is nearly flat** (2516–2574 across 12 managers, ~2% spread) — in hindsight, draft position barely limits what was *reachable*. So the leaderboard is **Efficiency %** — how much of your own reachable ceiling you captured — which spreads properly: 57.7% to 77.5%.

Simplification stated rather than hidden: every *other* manager's picks stay as they really were, so taking a player somebody else drafted later does not ripple through their draft.

**League lineup settings are now captured.** `ffapp/espn/league_settings.py` stores `league.settings.roster` per league-season in `data/league_settings.json`; the draft pull and both weekly scripts write it. Bench/IR are dropped, flex slots (`RB/WR/TE`, `OP` superflex) expand to the positions they accept. Until a season is captured the UI says the lineup is **assumed** rather than pretending otherwise.

> A bug worth remembering: the first version of the roster parser split every slot name containing `/`, which turned **`D/ST`** into a flex accepting "D" or "ST" — neither a real position — so the defence slot could never be filled and every lineup silently lost ~187 points. Caught because a hardcoded fallback and the parsed roster disagreed on the same league (2566.7 vs 2379.7) despite identical slot composition. Positions whose own name contains a slash are now special-cased, and a flex is only accepted when every part is a recognised position.

**Tabs:** Owner scorecard (value, accuracy/luck, hit rate, accuracy-vs-luck scatter) · Steals & busts · By round (best pick of each round, how each round performed league-wide) · By position (value by owner × position, position-taken-each-round tendencies) · Best available (hindsight points left on the board per pick and per owner) · Best lineup (optimal starting lineup from a manager's own picks, bench points forgone) · Retention.

**Data gaps, handled explicitly rather than fudged:**

1. **2023 has no projections** (~16% coverage), so the accuracy/luck split is hidden for those 8 league-seasons with a visible warning. Value Over Slot is still exact.
2. **Draft retention needed data that did not exist.** The free-agent file only lists players *nobody* drafted, so it cannot say how much of a manager's own draft survived. `draft_data.py` now writes `data/drafts/<league> Final Roster <year>.csv`; the tab fills in from the next pull onward. Past seasons cannot be reconstructed — ESPN only exposes current rosters.
3. ⬜ **"Best possible *record* from simulation" still not built.** Simulating a counterfactual roster's record needs *weekly* player scores; only season totals and averages are stored. Adding weekly player scores to the pull would unlock it, along with start/sit analysis ("points left on your bench each week"). That is the natural next step.

---

## 3c. Lifetime league history — ✅ built 2026-07-28

New page `pages/14_🏛️_Lifetime_League_History.py` over `ffapp/metrics/lifetime.py`. Appears only for the **8 leagues with 2+ seasons** on file. Computed entirely from data already on disk — no ESPN round trip.

### 🔴 Stale aggregate CSVs hid the newest season — ✅ fixed 2026-07-28

Symptom: no 2025 playoff results and no 2025 draft grades on the cross-league pages, even though the workbooks clearly had both.

Cause: those pages read one-off **aggregate** CSVs that were never rebuilt.

| File                                            | Was                                                         | Now                                                                      |
| ----------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------ |
| `data/all_playoff_dfs.csv`                    | 160 rows,**stopped at 2024**, last written 2025-09-30 | 264 rows, 2019–2025                                                     |
| `data/all_playoffs_with_predictions.csv`      | 128 rows, stopped at 2024                                   | 212 rows, incl. 77 for 2025 and 11 championship games                    |
| `data/drafts/Draft_Grades_with_Standings.csv` | stops at 2024 (needs live ESPN standings)                   | unchanged — grades now read from`Aggregated_Draft_Grades.csv` instead |

Three separate problems behind it:

1. **`create_playoff_df` appended and de-duplicated** rather than rebuilding, so any season whose workbook changed after its first pull stayed frozen. 13 workbooks held finished 2025 brackets that never made it in.
2. **It required a live ESPN `League` object it never used** — instantiated only to print settings — so refreshing the aggregate needed credentials it had no real dependency on. Same in `playoff_add_predicted.py`, which imported `espn_api` and never called it. Both imports are now lazy/removed, and `rebuild_from_workbooks()` regenerates from the workbooks offline.
3. **Draft grades were read from the standings file**, which lags because `Standing` requires `league.standings()`. Grades live in `Aggregated_Draft_Grades.csv`, which `regrade_drafts` rewrites in full every run. `lifetime.owner_careers` now takes grades from there and only `Finish` from the standings file — so grades are current and the page says explicitly which years lack a finish and how to fill it.

**`python pipeline/rebuild_aggregates.py`** now does the playoff rebuild plus predictions, offline. Add it to the weekly routine after the update script.

Rebuilding also exposed a latent crash in Playoff Analysis: the oldest Playoff Results sheets predate the `Record` columns, and two places did `Record.str.split('-')[0].astype(int)` → `ValueError: cannot convert float NaN to integer`. The old aggregate happened to exclude those workbooks, so it had never fired. Both spots now drop record-less games from that comparison only and say so.

### Streamlit Cloud stale-module trap (bitten twice)

Streamlit re-executes the page script on every rerun but keeps already-imported modules in `sys.modules`. A deploy that **adds a symbol to an existing module** can therefore run new page code against the old module, producing `ImportError: cannot import name 'available_years'` or `AttributeError: module 'ffapp.league_registry' has no attribute 'canonical'` while the committed code is perfectly correct. **Manage app → Reboot app** is the fix; a rerun or cache clear is not. New modules are unaffected.

`ffapp/metrics/lifetime.py` now guards for this explicitly and raises a message naming the fix, so the next occurrence is self-diagnosing rather than a puzzle. Documented in the README's deploy section.

### The identity layer is the whole trick

Team names change constantly, so a name is not a manager. Three sources get stitched:

1. **Draft files carry `Owner ID`** for all 39 league-seasons — the stable key.
2. **`all_matchups.csv` carries only team names**, and stores whatever the team was called *when that week was pulled*. Two separate failure modes fixed:
   - names in the matchups but not the draft → matched by elimination when exactly one is unclaimed on each side;
   - a team renamed **mid-season** appears under *both* names, so set arithmetic finds nothing. Those merge when the two names play in non-overlapping weeks, never play each other, and their game counts add to one season. (Pennoni Younglings 2025: "Daddy's Home" 3 games + "Daddy's Finally Home" 14 = 17.)
3. **LPI sheets** supply human owner names (155 resolved); falls back to the most recent team name.

Result: **100% owner resolution on all 8 leagues** (was 92% before the rename passes). Anything still unmatched is listed in a warning on the page rather than silently dropped.

> **League names drift too.** 2025 has 18 games filed under "Family League" and 87 under "Family Fantasy" — the same league, renamed mid-season. Without folding them together that franchise's history splits in two. `league_registry.ALIASES` + `canonical()` handle it; add future renames there.

Regular season vs playoffs comes from the **playoff bracket data**, keyed on (year, team, score), not a week cutoff — leagues start their postseason in different weeks, so a cutoff would be wrong per league.

### Tabs

- **All-time** — standings by win %, with reg-season and playoff records split out, points for/against, best week.
- **Careers** — season by season per manager (record, playoff record, PF/PA, finish, draft grade) plus franchise trend lines for points or wins.
- **Head to head** — full owner×owner win matrix, plus a rivalry picker showing every meeting, record, average margin and playoff meetings.
- **Playoffs** — playoff W/L, win %, **titles**, finals appearances, average playoff score. Plus **clutch or choke**: playoff scoring against that manager's *own* regular-season average, so it measures showing up when it counts rather than just being good. Managers under two playoff games are excluded — one bad game is not a pattern.
- **Record book** — highest/lowest score, most lopsided win, narrowest win, most points in a loss, fewest in a win, highest/lowest playoff score, most lopsided playoff win, most over/under projection. Plus best and worst seasons.
- **Streaks & feats** — longest winning and losing runs, carrying across season boundaries.

Verified across all 8 leagues: margins cancel to zero, W count equals L count, all-time wins reconcile to the game log, the head-to-head matrix sums to total wins with a zero diagonal, and every career owner appears in the all-time table. 12s for all 8 leagues; cached per league in the app.

⬜ Still open: cross-season Elo (`experiments/elo.py` exists but is not wired in), and championship/podium tracking beyond titles and finals (needs final standings for every season, which `Draft_Grades_with_Standings.csv` only partly covers).

---

## 3d. All-Time Hall of Fame — ✅ built 2026-07-28

New page `pages/15_🏆_All_Time_Hall_of_Fame.py` over `ffapp/metrics/hall_of_fame.py`. **403 team-seasons across 14 leagues, 2019–2025, 34 championships** — every team-season ever, ranked for bragging rights.

### Cross-league comparability was the design problem

Leagues differ in size, scoring and season length, so raw points are meaningless between them. Rankings default to **PPG z** — points per game z-scored *within its own league-season*, so `+2.0` means "two standard deviations better than that league that year" and travels across leagues and eras. `Win %` and `LPI` are also league-relative (LPI is already scaled by league size). Raw points are displayed but never used to rank. A metric selector offers all four.

**Luck** = actual wins − Expected Wins, pulled from the Expected Wins sheet (present in all 42 workbooks).

Manager views pool across leagues, because ESPN owner IDs are account SWIDs — the same person carries the same ID everywhere. 19 owner IDs appear in 2+ leagues.

### The lists

Best / worst team-seasons ever · best season that never won a title · best teams to miss the playoffs · worst teams to make them · worst teams to reach a final · **worst champions** · luckiest and unluckiest seasons · **best managers without a ring** · heartbreak index (most playoff trips, no title) · dynasties · iron men (most seasons) · biggest turnarounds and collapses year over year.

Sample findings: Harshit Aggarwal's 2024 Game of Yards at **+2.36 PPG z** is the best season on record; a 0-14 Furnace Party season sits near the bottom; Lawrence Rosello went **12-5 in 2022 with −0.98 PPG z and +5.4 luck** — simultaneously the luckiest season and the worst playoff team by scoring; Prahlad Singh is the iron man at 18 seasons across 4 leagues with 3 titles; Utkarsh Gupta leads the heartbreak index with 7 playoff trips and no ring.

### Verified

All four metrics exercised across all seven team views plus the manager views. Invariants asserted: PPG z centres on 0 per league-season, at most one champion per league-season, finalists come in 0 or 2, every champion is also a finalist, every finalist made the playoffs, manager titles sum to the championship count (34), and manager seasons sum to the team-season count (403).

Build time went **40s → 4s** by memoising `owner_crosswalk` / `owner_display_names` / the raw matchup read in `lifetime.py` — without it, `owner_display_names` re-read all 42 workbooks once per league (588 Excel reads).

⬜ **`BP- Loudoun 2025` (Matt's league) is excluded** — it has 202 team-games but no draft file, so its teams cannot be tied to a manager. It is commented out in `draft_data.py`'s league list; uncomment it, run the draft pull, and it joins automatically. The page says so rather than silently omitting it.

> Data note: two Game of Yards workbooks spell a playoff round **"Quater Final"**. Normalised on read; the typo is baked into those files, not current code.

---

## 3e. Transaction analysis — ✅ built 2026-08-06

New page `pages/16_🔄_Transaction_Analysis.py` over `ffapp/espn/transactions.py` (pull + reconstruct) and `ffapp/metrics/transaction_analysis.py` (scoring). Grades the season *after* the draft: the waiver wire and the trade market.

### The finding that shaped the design: the transaction log is effectively forward-only

`league.recent_activity()` gives exact move types and FAAB bids, but it is only **reliably** available for the season in progress. Probed directly across both endpoint shapes the library uses:

| Season     | `/seasons/{year}/…/communication/`                   | `/leagueHistory/…` |
| ---------- | ------------------------------------------------------- | --------------------- |
| 2021–2025 | **404** "This Communication Group does not exist" | 404                   |
| 2026       | **200** (0 topics — season not started)          | 404                   |

Retention past the current season is real but erratic and cannot be planned around: of 38 backfilled league-seasons exactly **one** — Game of Yards! 2024 — still served its log (379 genuine messages, December 2024 dates), while EBC League 2024 did not, and repeat calls for the same league-year have disagreed. Treat historical availability as a bonus. **The only dependable capture is in-season**, which is why both weekly scripts call `build_season` every run.

**But `box_scores(week=N)` works for every season back to 2019**, despite the library docstring claiming it is current-season only. Each call returns every team's full roster — bench included — with lineup slot and points. So weekly snapshots are the substrate and the activity feed is only a labelling layer.

What a backfilled season loses: FAAB bids (permanently), churn inside one week (added Tuesday, dropped Friday), and the trade/waiver distinction when a move has no same-week return leg. Every move carries a `Source` column (`activity` vs `snapshot`) so the UI never implies more certainty than it has.

⚠️ **Consequence: the current season must be captured in-season.** Both weekly-update scripts now call `transactions.build_season()` after writing the workbook. A week missed there can still have its *snapshots* backfilled, but never its real labels.

### Trade detection needs same-pair matching

The obvious heuristic — "a team both gained and lost a player this week" — labelled **37 trades in a season that had 2**, because any team active on the waiver wire trips it. Correct version requires a genuine two-way swap between the *same pair* in the same week. Pennoni Younglings 2024 then yields 222 adds, 223 drops, 4 traded players (2 trades), and 34 `TEAM->TEAM` moves left honestly ambiguous.

### Scoring: started points above replacement (SPAR)

- **Started, not rostered** — points only count in weeks the player occupied a lineup slot. Raw rostered points reward hoarding a bench.
- **Above replacement** — an add is worth what it beat. Replacement = the 25th percentile of points among everyone rostered at that position that week, approximating the fringe player then available free. It must be estimated from rostered players because ESPN keeps no weekly scores for unowned players, which makes SPAR mildly conservative.
- **Drops scored separately** by what the player went on to start *for someone else*; points scored while unrostered are ignored.

Adds are deliberately **not** paired against the specific player dropped for them: at weekly granularity a team making three moves at once gives nine possible pairings and no way to choose. Replacement level sidesteps the pairing problem.

### Bug caught in build: the championship week was being dropped

The pull originally ended at `current_week - 1`, which reads as obviously correct and is not. On a **finished** season ESPN parks `current_week` at the final scoring period, so 2024 — which has scores in all 17 weeks — stopped at 16, losing the championship week and 191 player-weeks per league. Same family as the twelve season-boundary bugs in §2b, and the fix is to use the module written for it: `week_utils.completed_weeks()`, which counts weeks where *anyone* scored. Pinned by a regression test that asserts `completed_weeks > current_week - 1` on a finished season.

### ⚠️ Measured: this grades transactions, not managers

`tools/check_transactions.py` runs 33 correctness assertions against synthetic rosters with hand-computed answers, then measures the metric itself. Over **423 team-seasons from 38 league-seasons**:

|                          |                                                             |
| ------------------------ | ----------------------------------------------------------- |
| corr(Moves, SPAR)        | **+0.69** — SPAR substantially tracks sheer activity |
| corr(SPAR, Wins)         | **+0.01** (n=361) — nothing                          |
| corr(SPAR per Add, Wins) | **−0.06** — volume-adjusting does not rescue it     |
| corr(Moves, Wins)        | +0.09                                                       |
| YoY SPAR, same team      | +0.27 (n=153) — mostly persistence of*being active*      |

Compare the draft grade at **r = −0.51** against final standing. The reason is baseline, not a bug: a team that drafted well has little to gain from the wire and scores low for a good reason, while a team patching a broken draft can post a huge SPAR and still lose. So the column is named **Transaction Grade**, and the module docstring and the page both state these numbers — the same treatment the draft page's ACCURACY got after its persistence measured r = +0.08.

> An earlier draft of this section quoted r = +0.66 / −0.06 / **+0.12** from a 12-league-season sample. On the full backfill `SPAR per Add` vs wins is **−0.06**, which flips the claim that volume-adjusting helps. Numbers above are the full-sample ones.

⬜ **To make this predict wins** you need the counterfactual the snapshots cannot supply alone: what the team *would* have started standing pat. That is a lineup simulation over the drafted roster — reuse the slot-constrained DP in `draft_analysis.py` — and is a follow-on, not a fix.

### Data — 38 league-seasons, 12 leagues, 2.9 MB

`data/transactions/<League> Weekly Rosters <Year>.csv.gz` (gzipped: 24 MB → 2 MB across a full backfill, 11.5×; pandas infers the codec) and `<League> Moves <Year>.csv` (plain, small, worth diffing). Backfill with `python pipeline/backfill_transactions.py --skip-existing` — ~17 requests per league-season; 2019 is a hard floor.

⚠️ **The `.csv.gz` snapshots must be committed.** `.gitignore` carries `*.csv.gz` with an explicit `!data/transactions/*.csv.gz` exception. Drop that exception and the page deploys empty in a way that looks like the backfill never ran: the `Moves` files are plain `.csv` and push normally, but they hold no points, so nothing can be scored. The page now detects exactly this state — move logs present, snapshots absent — and says so instead of telling you to re-run the backfill you already ran.

| League                                                                        | Seasons    |
| ----------------------------------------------------------------------------- | ---------- |
| Game of Yards!                                                                | 2019–2025 |
| EBC League                                                                    | 2021–2025 |
| 0755 Fantasy Football, Pennoni Younglings, THE BEST OF THE BEST               | 2022–2025 |
| RRR On Premise*(Ava's, renamed Philly Extra Special in 2025)*               | 2021–2024 |
| Brown Munde                                                                   | 2023–2025 |
| Family Fantasy                                                                | 2024–2025 |
| OnP Fantasy, Operators Football League, Ross' Fantasy League, The Girl's Room | 2025       |

⬜ **4 real gaps — credentials, not missing leagues.** `THE BEST OF THE BEST` 2019–2021 and `The Girl's Room` 2024 return `ESPNAccessDenied`: the stored cookie cannot read them. The backfill script now separates these from `ESPNInvalidLeague` (league genuinely did not exist), because lumping them together hid the distinction entirely.

### Two crashes found in the build

**The championship week was silently dropped** — see above.

**An emoji killed an entire league.** `The Girl's Room 💞🏈` raised `UnicodeEncodeError` on the cp1252 Windows console. Because `build_season` prints its header *before* fetching anything, the exception fired ahead of the first request and the league was recorded as failed with no data — not a logging nuisance but total data loss for that league. Fixed with an encode-safe `transactions.say()` rather than reconfiguring global stdout, which a library has no business doing. Any script printing ESPN league names is exposed to this.

Beyond this page, the weekly snapshots are the missing input for **best-possible-record simulation** and **start/sit analysis** — both previously blocked on not having weekly player scores.

---

## 3f. Transaction feats on the Hall of Fame — ✅ built 2026-08-06

`ffapp/metrics/transaction_hall_of_fame.py`, surfaced as three new tabs on `pages/15_🏆_All_Time_Hall_of_Fame.py`. Kept in its own module rather than bolted onto `hall_of_fame.py` because it reads a different data source and must degrade independently — a league that was never backfilled should empty those three tabs, not the whole page.

**Trades** — most lopsided · biggest (most value moved) · most mutually beneficial. The mutual list ranks on what the **weaker** side got, not the total; ranking on the total just resurfaces blockbusters where one team was fleeced.

**Wire & drops** — best pickups off the waiver wire · worst drops (what the player did for whoever claimed them). Trades are excluded from "best adds" by default: left in, they take every slot, because a trade returns an established star and a waiver claim almost never does.

**Transaction feats** — most SPAR in a season · best SPAR per add (min 5 adds) · best and worst single-season Transaction Grades · best managers by career average grade, pooled across leagues on SWID.

### Three different normalisations, deliberately

| Ranking               | Basis                                   | Why                                                            |
| --------------------- | --------------------------------------- | -------------------------------------------------------------- |
| Team-season, manager  | **SPAR z** (within league-season) | where a league advantage would compound over a career          |
| Trades                | **raw margin**                    | both sides sit in the same league-season — already comparable |
| Individual adds/drops | **raw SPAR**                      | the headline of "best pickup ever"*is* the raw number        |

⚠️ The third case is the one place a scoring-settings bias survives — a PPR league is over-represented among big receiver and back pickups. Stated on the page rather than quietly normalised away.

### Performance

A full cross-league build recomputed `stints()` six times per league-season (impacts, drops, trades, plus twice inside `owner_summary`). All five scoring functions now accept a pre-computed stints frame: **46.7s → 18.7s**.

`transaction_seasons()` and `all_moves()` are deliberately **not** `lru_cache`d. The page caches them with `st.cache_data` keyed on the transactions directory mtime; a process-level cache underneath would keep serving last week's numbers after a weekly run — the same stale-state trap that bit `lifetime.py` twice.

### Weekly update → historical pages, asserted

`tools/check_weekly_flow.py` drives a fake two-team league through the exact call the weekly scripts make and asserts the whole chain with no ESPN access: files land where `paths.py` says → `available_seasons()` discovers them → the Transaction Analysis page scores them → the Hall of Fame picks them up → a re-run is idempotent → and the league name the weekly scripts derive matches both the backfill's name and the discovery regex. That last one matters because the name is set in three separate files and nothing else enforces agreement.

### Is `Source` needed?

Yes in the data, mostly not on screen. It varies — 194 of 7,242 acquisitions carry `activity` — but only **1 of 38** league-seasons is mixed, and all 84 trades are `snapshot`. So a constant "snapshot" column was pure noise on nearly every view while being the most important column in the table from 2026, once the live feed starts confirming move types. `tables.hide_constant()` now drops `Source` (and `FAAB Bid`, all-zero for the same reason) when it carries one value, and keeps it the moment it discriminates.

---

## 3g. Lifetime transactions, Finish fix, front page — ✅ 2026-08-06

### League-wide transaction history (Lifetime page, new **Transactions** tab)

Headline totals for the league — moves, SPAR split into **from the wire** vs **from trades**, average trade margin, total drop regret — then a per-owner table with total/avg SPAR, SPAR per add, trade count, **avg trade margin signed from that owner's side**, and a won-lost trade record. Best and worst trader are called out explicitly.

Deliberately **not** z-scored, unlike the Hall of Fame views: everyone in one league played the same scoring, so raw SPAR is already comparable and is the more legible number. Normalising here would obscure rather than help.

> Trade counts per league are small (EBC League: 7 across 5 seasons), so one lopsided deal can decide both "best" and "worst trader". The page says so rather than implying a stable ranking.

### 🔴 Finish was blank for all of 2025 — ✅ fixed

`Draft_Grades_with_Standings.csv` had stalled at **2024**. The old producer could not refresh it: `analysis/draft_analysis.py`'s `determine_final_standings(league_name, year)` reassigns `year = 2025` on its third line, discarding the argument, then matches its league config on that year — so it only ever resolved one season and silently returned an empty frame for any other.

**Deriving it offline was tried and rejected.** Reconstructing ESPN's `final_standing` from playoff brackets plus regular-season records matches on only **62%** of team-seasons (champion 23/24, but the middle of the table diverges — ESPN's consolation brackets and tiebreakers are not reproducible from what we store). A number wrong for four teams in ten is worse than a blank.

New `pipeline/refresh_standings.py` does the real thing: one League init per league-season, read `team.final_standing`, merge current draft grades, write the file. **277 rows → 465, now 2019–2025, 164 team-seasons of 2025 Finish across 14 leagues.**

Unplayed seasons are skipped — ESPN reports an existing-but-unstarted season as `final_standing 0, 0-0-0` for everyone, and writing those put a **Finish of 0** on 2026 rows, which reads as "finished first" at a glance.

⬜ 7 league-seasons still refuse (`ESPNAccessDenied`) — THE BEST OF THE BEST 2019–21, The Girl's Room 2024, BP- Loudoun 2024, OnP Fantasy 2026, Mike Daisy 2024. Cookie scope, not missing data.

### Transaction Grade on the careers table, and only there

Added to `lifetime.owner_careers()`. It is a per-season per-manager number, and the careers table is the one place it lines up with the **Draft Grade** for the same team-year — the season's story start to finish. Both curve within their own league-season, so 75 is average either way. Deliberately absent from the all-time table and the head-to-head views, where a per-season grade would have to be averaged into something meaningless.

Loaded lazily and wrapped in `try`, so a league with no transaction backfill still renders its careers table.

### Front page rewritten

Now covers the five cross-league pages (Playoff Analysis, Draft Analysis, Transaction Analysis, Lifetime History, Hall of Fame) alongside the per-league sections, and explains the z-score-within-league-season idea once, up front.

**Added: "Want your league added?"** — an expander with the real steps for finding a league ID and the `espn_s2` / `SWID` cookies in devtools.

🔒 **No input form, deliberately.** A public page that collects live session cookies is structurally identical to a credential-phishing page. Anyone holding `espn_s2` + `SWID` can read that ESPN account until the cookies expire, and Streamlit widget values would pass through server memory and session state on a hosted app. The expander says to send them privately instead, notes that logging out of ESPN everywhere revokes them, and states that the pipeline only ever reads.

---

## 3h. Live Draft Assistant — ✅ built 2026-08-10

`pages/17_📋_Draft_Assistant.py` over `ffapp/espn/live_draft.py` (ESPN reads) and `ffapp/metrics/draft_board.py` (rankings join + value). Upload a rankings CSV, watch the live board, see who is falling past their value and how long until you are up.

### `espn_api` cannot read a live draft — this is why the module exists

`base_league._fetch_draft` opens with:

```python
if not data.get('draftDetail', {}).get('drafted'):
    return
```

ESPN only flips `drafted` to True when the draft **completes**, so `league.draft` is empty for the entire window you need it, and `refresh_draft()` calls the same function. `live_draft.py` therefore talks to the `mDraftDetail` view directly with `requests` — no espn_api dependency at all.

### What the raw endpoint gives you (verified against real leagues)

- **The full pick order exists before anyone picks.** An undrafted 2026 league already returns every slot with `overallPickNumber`, `roundId`, `teamId` and `playerId = -1`. So the snake order — including the back-to-back turns at the wrap — is known up front, which makes "picks until you're up" arithmetic rather than guesswork.
- A pick landing just sets that slot's `playerId`. Taken vs available is one scan; no event log to replay, nothing to miss.
- **Polling is cheap:** ~0.45s per call, 5/5 clean. The page offers off / 5s / 10s / 30s via `st.fragment(run_every=...)`, so only the board re-runs.
- ESPN's own rank and ADP come from `kona_player_info` with `sortDraftRanks` (PPR / STANDARD / SUPERFLEX / ELIMINATION).

### Three findings that shaped the design

**1. Naive rank-diff is garbage.** The first value pass surfaced `49ers D/ST +235`, `Jake Elliott +221`, `Panthers D/ST +217` — because ESPN ranks defences and kickers near 400 while sheets rank them near 190, so the difference swamps every real edge. **All value is now position-relative**: `Pos VALUE` = ADP position-rank − ECR position-rank.

**2. ADP beats editorial rank for value.** A sheet's rank is an opinion about who is better; ADP is evidence about where players actually go. `VALUE` is ECR-vs-ADP — who the room is letting slide — with ESPN's rank carried alongside as a second opinion.

**3. Name matching was the real integration risk, and it is solved.** 11% of names differ by suffix or punctuation alone. Normalisation treats the two kinds differently on purpose: periods and apostrophes are **deleted** (`A.J. Brown` → `aj brown`), hyphens become **spaces** (`Amon-Ra St. Brown` → `amon ra st brown`). Deleting hyphens instead yields `amonra`, which matches neither spelling — caught by a test, not in production. Three passes (exact → spacing-insensitive → last-name+position), fallbacks only when unambiguous so it can never pick the wrong Josh Allen.

**Result: 200/200 matched** against the live ESPN pool on a real sheet. Unmatched players are always listed on the page, never dropped.

### Also handled

- **K/DST still appear in the draft log.** Sheets omit them but people draft them; reading the log off the matched board alone would skip picks. The log resolves from the ESPN pool instead.
- `recent_picks` reads `state['taken']` — the same source `board()` uses — rather than re-scanning `slots`. Two functions deriving "what's been picked" from different fields can disagree, and a log contradicting the board is worse than no log.
- Sparse `Round` columns are forward-filled into a per-player **Target Round** (sheets set it only on each round's first player, making it a tier marker).
- Flexible column aliases, because these sheets are hand-built: `Name`/`Player`, `FantasyPros`/`ECR`/`Rk`/`Rank`/`Consensus`, etc. Fails loudly with the actual column list when it cannot find them.

### Tabs

Best available · 💰 Value · 📉 Reaches (going earlier than they're worth) · By position · Scarcity (how many of each position remain within N ECR of the best one left) · Draft log.

### Data + safety

⚠️ **`data/rankings/*.csv` is gitignored.** A rankings sheet is somebody else's product; pushing one to a public repo redistributes their work. Only `data/rankings/README.md` is tracked. Upload is the intended path on a deployed app.

⚠️ **Run it locally during a draft.** It polls ESPN with your `espn_s2`, so on the public app anyone with the URL sees your board. Stated on the page. The module only ever reads — it cannot make a pick.

⬜ **FantasyPros has no free API.** Their API needs a paid key, so ingestion is CSV upload. ECR barely moves once you are drafting, so live fetching buys almost nothing and adds a ToS problem. Their current export terms are worth checking before relying on it.

`tools/check_draft_board.py` — 46 assertions: normalisation (including the must-NOT-collapse cases), column aliasing, matching, value maths, K/DST logging, roster needs and caps, recommendation ordering, dropoff, plus a live replay that freezes a completed draft at picks 0/24/100 and asserts the board shrinks.

### Two tracking modes — the CSV alone is enough

**Manual (default)** — no ESPN connection, no credentials, no network. Tick players off as they go, mark which are yours, type your next pick number. The sheet supplies ECR, ADP and ESPN rank from its own columns, which are already a snapshot of ESPN's API on the day it was built.

**Live ESPN draft** — polls `mDraftDetail` so picks land automatically. Still uses the sheet for all rankings; ESPN is only consulted for *who has been picked* and to map its numeric `playerId` to a name. Falls back with a message pointing at manual mode if credentials expire mid-draft.

`add_value` treats **ECR as the only required column**. ADP and ESPN rank are optional — a sheet with neither still gives a usable ranked board. Requiring them meant a valid two-column sheet raised `KeyError` instead of degrading.

### Roster construction: "what should I take at each pick"

Needs are **flex-aware and greedy in the right order** — dedicated slots fill before flex ones, so a third back soaks the flex rather than leaving WR2 looking open. Driven by the league's real `settings.roster` when stored, otherwise a lineup editor on the page.

**The positional path is measured, not asserted.** `positional_dropoff` compares the best ECR available now against the best likely to survive to your next turn (ADP as the estimate). A big gap means waiting is expensive. That adapts — if the room has ignored TE, it says so — where a hardcoded RB > WR > TE/QB order cannot.

`Adjusted ECR = ECR ÷ position score`, where position score = dropoff × need × your lean. A **lean slider (0–3)** exponentiates the priority weights: 0 drafts pure ECR, 1 is a mild RB-first path, 3 follows the path almost regardless of ECR. The lean is deliberately allowed to lose to a big ECR gap; at a middle slot the default takes a receiver ranked 14 spots higher over filling an empty backfield, and whether that's right is taste, not arithmetic.

Also: **Draft plan** projects the rest of your draft pick by pick, carrying each assumed selection into the next turn's needs.

### Four bugs found by simulating full drafts

Simulating 12-team snake drafts from every slot — not unit tests — caught all of these:

1. **Value-over-ADP inverted player quality.** Using it as a tie-break inside the score offered Tyrone Tracy (ECR 131) ahead of D'Andre Swift (ECR 60) at pick 24, because deep players fall furthest past their ADP. "Which position" and "which player" are now separate calculations.
2. **The lean was decorative.** At 1.15 vs 1.10 an RB-first and a WR-first setting produced *identical* drafts. Weights widened and the exponent slider added.
3. **Need didn't scale with count.** Needing two backs scored the same as needing one receiver, so the RB hole stayed open while the pool drained. Now `+0.30` per additional unfilled starter.
4. **Hard leans built illegal rosters.** At lean 3 a 13-round sim took **nine backs and no quarterback**. Caps are now derived from the league's own slots (startable + bench allowance → RB 6, WR 6, TE 3, QB 2, K 1, D/ST 1), so a position drops out once it's full.

---

## 4. Feature backlog

Items carried over from `todo.txt` are marked ⭐.

### 4.1 Lifetime / multi-year (for leagues with 2+ seasons)

- ✅ **Owner career table** — §3c, Careers tab.
- 🟡 **Franchise trend charts** — points and wins by year done in §3c; season-end LPI and draft grade by year still open.
- ✅ **All-time records book** — §3c, Record book + Streaks tabs.
- ✅ **Head-to-head rivalry view** — §3c, Head to head tab.
- 🟡 **Championship/podium tracker** — titles, finals and playoff appearances done in §3c; podium (2nd/3rd) still needs full final standings.
- ⭐ **Cross-season Elo** (`elo.py` exists — surface it): Elo carried across seasons with decay, charted over the franchise's life.
- ⭐**League wide Transaction History** - best trader, best adder, best worst trade and transaction grade next to draft grade and final standing
- ✅ **Owner-based identity** — solved offline in §3c (100% resolution incl. mid-season renames), no ESPN call needed.
- ✅ **Co-owner attribution** (2026-07-28): ESPN returns a list of owners per team and the code took `owners[0]`, so a co-owned season landed on whoever ESPN listed first — splitting a franchise's history across two people. `owner_overrides.py` now defines the canonical owner per co-owned team-year, and every user-facing path resolves through it. First entry: Pennoni Younglings 2024 "Philadelphia Bills Mafia" (Henry Morris + Robbie Wilston) → **Robbie Wilston**, so Henry's history is 2022–2023 and Robbie's is 2024–2025. Add future cases to `PREFERRED_CO_OWNER`.

### 4.2 Draft & player analytics

- ✅ **"Best possible team"** — optimal lineup from a manager's own picks (§3b, Best lineup tab).
- ✅ **Best pick of each round**, **biggest steals / busts** — §3b.
- ✅ **Draft position tendencies per owner** — §3b, By position tab (single season; across-years view still open).
- **Round-by-round hit rate:** share of picks per round that returned starter-level value, per owner and league.
- **Draft grade vs. final standing scatter** across all league-years — does drafting well predict winning? (validates §3.5).
- **Player-level views:** most-drafted players by owner across years ("player loyalty"), points by acquisition type (drafted vs. FA vs. trade), best FA pickup of the year.
- **Roster Grade** (distinct from Draft Grade): blend the team's draft grade with its free-agent Performance Grades, weighted by each group's share of actual points scored, so the number reflects the roster the team *finished* with rather than draft day alone. Pairs naturally with a "draft grade vs. roster grade" delta column — big positive deltas identify the best in-season managers.
- 🟡 **Post-draft roster churn** — built in §3b; waiting on the new Final Roster capture to have data.

### 4.3 Season page upgrades

- ⭐ **Playoff bracket visual** with each team's LPI next to their name.
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

### ✅ Phase 1 done 2026-07-28 — caching (measured, and it was the real bottleneck)

Benchmarked before choosing a storage format, which changed the conclusion: the data is only **3.0 MB** total, so size was never the problem. The problem was that **nothing was cached** and Streamlit re-runs the whole page script on every widget interaction.

Measured, per league page render: 20 separate `read_excel` calls (Schedule Grid parsed **10 times**) = **~350–480 ms**, plus one live ESPN `League` construction per season in the Lifetime Record loop (6 network round trips for a 5-year league) — all repeated on every dropdown change.

Format comparison for one page render — note parquet was measurably *worse* here (tables too small; per-file overhead dominates, and files got **bigger**: 89 KB vs 17 KB per league-year):

|                                | time            | vs. before      |
| ------------------------------ | --------------- | --------------- |
| before: 20 ×`read_excel`    | 450 ms          | 1×             |
| parquet, 20 reads              | 88 ms           | 5×             |
| sqlite, 20 queries             | 25 ms           | 18×            |
| **cached (what we did)** | **~4 ms** | **~80×** |

`ffapp/ui/data_loader.py` now serves all app reads. Results:

|                                        | before      | after                   |
| -------------------------------------- | ----------- | ----------------------- |
| League page, first load                | ~350 ms     | ~9 ms                   |
| League page, every later interaction   | ~350 ms     | **~4 ms (~80×)** |
| LPI Master List (42 files), first load | ~1.2–1.5 s | ~1.2 s (break-even)     |
| LPI Master List, later                 | ~1.2–1.5 s | ~50 ms (**~40×**)     |
| Biggest Upsets after Master List       | ~2.6 s      | ~60 ms (**~41×**)     |

Design choices worth remembering:

- Caches a `pd.ExcelFile` and parses **individual sheets on demand**, rather than `read_excel(sheet_name=None)`. The pages that pull one sheet from all 42 league files would otherwise parse ~11 sheets per file to use one — measured 2.6× faster on that pattern, identical for a league page. ~20 MB for all 42 workbooks.
- Workbook **bytes are read into memory** so no OS file handle stays cached — a held handle stopped the pipeline from rewriting those same xlsx files on Windows (found by test, fixed).
- Cache keys include file mtime, so a pipeline run invalidates them with no restart. Credential args are underscore-prefixed so Streamlit never hashes them into a key.
- Loaders return copies — page code mutates results in place (renames columns, shifts the index).

### Today (storage, unchanged)

CSV + Excel files committed to git. Manual local script runs push updates.

**Pain points:** Excel reads are slow (openpyxl) and uncached; filenames are the schema (league name + year string, emoji included — `The Girl's Room 💞🏈 2025.xlsx`), so joins across datasets are string-matching exercises; binary `.xlsx` diffs bloat git history; a weekly refresh requires you at your machine; no data validation ever runs; aggregate files (`Master_Draft_Data.csv`, `all_matchups.csv`) duplicate what's in the per-league files and drift.

### Options

| Option                                                                              | Effort      | What it buys                                                                                                                                                        | What it doesn't                                                                    |
| ----------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **A. SQLite (or DuckDB) file in repo**                                        | Low         | One`app.db` replaces ~150 files; real schema + keys (league_id, owner_id, year, week); fast queries; joins for free; still zero-infrastructure on Streamlit Cloud | Still commit-to-deploy; concurrent writes N/A (fine here)                          |
| **B. Parquet files in repo**                                                  | Low         | 10–50× faster reads than xlsx, typed columns, small diffs                                                                                                         | Still file-per-dataset; no joins/constraints                                       |
| **C. Hosted Postgres (Supabase / Neon free tier) + `st.connection`**        | Medium      | Data updates without git commits; app always current; enables on-demand refresh button in the app                                                                   | External dependency; free-tier limits; secrets management required (needed anyway) |
| **D. GitHub Actions weekly cron** running the pipeline and committing outputs | Low–Medium | Kills the manual weekly run regardless of storage choice; ESPN cookies live in Actions secrets                                                                      | Cookies expire (~1 year) and need occasional refresh                               |

### Recommendation (phased)

1. ✅ **Phase 1 — caching. Done** (see above). This was the whole performance problem; storage format was a red herring.
2. ⬜ **Phase 2 — SQLite, when the lifetime features get built. For query power, not speed.** Prototyped: the full corpus builds in **2.8 s → 14,381 rows, 2.0 MB, 13 tables**, and a cross-league aggregate query runs in **0.6 ms**. Today the same question means opening all 42 workbooks and string-matching league names out of filenames. Every §4.1 item (all-time records book, rivalry views, franchise trends) is one SQL query with it and a 42-file loop without it.
   - Build it as a **cached artifact, gitignored** (`@st.cache_resource`, ~3 s once per container), keeping the CSV/Excel files as the committed source of truth. A 2 MB binary rewritten weekly would bloat git — `.git` is already 70 MB from xlsx churn.
   - Two schema problems to fix during the migration, both found while prototyping: **mixed-type columns** (`Playoff Results.Seed 2`, `Score 2`, `LPI 2`, `Total Points 2` each hold both numbers and strings — parquet refused them outright), and **`Schedule Grid` is a team×team matrix**, so unioning it across leagues produced a 299-column table. It needs reshaping to long form (`team`, `opponent_schedule`, `record`), which would also simplify Schedule Comparison and the luck index.
3. ⬜ **Phase 3 — GitHub Actions weekly refresh.** Tuesday cron: pull ESPN → commit updated data. Credentials from Actions secrets.
4. ❌ **Skip parquet** — measurably wrong at this scale: slower than SQLite (88 vs 25 ms) and *larger* files (89 vs 17 KB per league-year).
5. ❌ **Skip hosted Postgres** (Supabase/Neon) for now. At 3 MB with one writer it adds a network hop, an outage dependency, and more secrets to manage for no gain. Revisit only for same-day updates without a redeploy.

---

## 6. Suggested sequencing

| Priority | Work                                                         | Sections       |
| -------- | ------------------------------------------------------------ | -------------- |
| 1        | ✅ Secrets out of source + rotate cookies                    | §1            |
| 2        | ✅ Fix free-agent grade bug; pick one draft formula          | §3 P1–P2     |
| 3        | ✅ Caching in`data_loader.py` (~80x on page interactions)  | §5 Phase 1    |
| 4        | Draft grade redesign (value-over-slot + PAR)                 | §3            |
| 5        | Lifetime/owner career features (unlocked by 3 & 4)           | §4.1          |
| 6        | SQLite for cross-league queries, then GitHub Actions refresh | §5 Phase 2–3 |
| 7        | Season-page upgrades & draft analytics backlog               | §4.2–4.3     |
