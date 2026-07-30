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
