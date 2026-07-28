"""Draft and free-agent grading engine.

Replaces the old weighted-ratio formula (see SCOPE.md section 3). Design:

Draft picks
  1. Expected points curve: pooled across every league-year on file, fit
     median season points as a function of (Position, Nth player taken at
     that position). Using position-rank instead of overall pick number makes
     the curve comparable across 8/10/12/16-team drafts. The curve is
     smoothed and forced monotone non-increasing.
  2. Value Over Slot (VOS) = actual points - expected points at that slot,
     scaled by the position's residual spread. This is the steal/bust
     measure: a late pick that outproduces its slot grades high, an early
     pick that busts grades low.
  3. Points Above Replacement (PAR) = points - replacement level at the
     position in that specific league-year (replacement = the
     (starters x teams)-th best season among all rostered players there).
     Rewards positional scarcity correctly instead of the old unbounded
     points/position-average ratio.
  4. Grade = 0.6 * z(VOS) + 0.4 * z(PAR), standardized within season across
     ALL leagues, mapped to a 30-100 scale centered at 75 (a C). Grades are
     therefore comparable across leagues and years - a 90 in the EBC League
     2022 means the same thing as a 90 in Game of Yards! 2025.

Free agents
  Graded on PAR alone (there is no draft slot), standardized within the
  season's free-agent pool, mapped with the same scale.

Team draft grade (aggregates)
  Weighted mean of pick grades, weighted by the expected points of each
  pick's slot, so early-round hits/misses move the team grade more than
  round-15 fliers.

Run directly to regrade every file in drafts/ and rebuild the aggregate
CSVs:  python draft_grading.py
"""
import glob
import os
import re

import numpy as np
import pandas as pd

DRAFTS_DIR = "drafts"
MASTER_CSV = "Master_Draft_Data.csv"
AGGREGATED_CSV = os.path.join(DRAFTS_DIR, "Aggregated_Draft_Grades.csv")
STANDINGS_CSV = os.path.join(DRAFTS_DIR, "Draft_Grades_with_Standings.csv")

# Typical starting-lineup slots per team, used for replacement level.
STARTERS = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "K": 1, "D/ST": 1}
MIN_CURVE_SAMPLES = 50      # below this a position gets a flat median curve
GRADE_CENTER, GRADE_PER_Z = 75.0, 10.0
GRADE_MIN, GRADE_MAX = 30.0, 100.0

DRAFT_FILE_RE = re.compile(r"^(?P<league>.+?)\s*Draft Results (?P<year>\d{4})\.csv$")
FA_FILE_RE = re.compile(r"^(?P<league>.+?)\s*FreeAgent Results (?P<year>\d{4})\.csv$")


def grade_to_letter(grade):
    if pd.isna(grade):
        return ""
    if grade >= 97: return "A+"
    if grade >= 93: return "A"
    if grade >= 90: return "A-"
    if grade >= 87: return "B+"
    if grade >= 83: return "B"
    if grade >= 80: return "B-"
    if grade >= 77: return "C+"
    if grade >= 73: return "C"
    if grade >= 70: return "C-"
    if grade >= 67: return "D+"
    if grade >= 63: return "D"
    if grade >= 60: return "D-"
    return "F"


def _zscore(series, fallback=None):
    """Standardize a series; degenerate groups fall back to the pooled stats."""
    sd = series.std(ddof=0)
    if len(series) >= 6 and sd > 1e-9:
        return (series - series.mean()) / sd
    if fallback is not None:
        mean, sd = fallback
        if sd > 1e-9:
            return (series - mean) / sd
    return pd.Series(0.0, index=series.index)


def _grouped_z(df, value_col, group_cols):
    """z-score value_col within group_cols, falling back to Year-wide stats."""
    out = pd.Series(np.nan, index=df.index)
    inner = [c for c in group_cols if c != "Year"]
    for year, ydf in df.groupby("Year"):
        fallback = (ydf[value_col].mean(), ydf[value_col].std(ddof=0))
        if not inner:
            out.loc[ydf.index] = _zscore(ydf[value_col], fallback)
            continue
        for _, gdf in ydf.groupby(inner):
            out.loc[gdf.index] = _zscore(gdf[value_col], fallback)
    return out


def build_expectation_curves(pool):
    """Fit expected-points-by-(position, position-rank) curves from all picks.

    Returns (curves, resid_sd): curves maps position -> np.array indexed by
    position rank (1-based rank -> index rank-1); resid_sd maps position ->
    std of (points - expected) for scaling.
    """
    pool = pool.copy()
    pool["PosRank"] = (
        pool.sort_values("Total Pick")
        .groupby(["League Name", "Year", "Position"])
        .cumcount()
        + 1
    )
    curves = {}
    for pos, pdf in pool.groupby("Position"):
        if len(pdf) < MIN_CURVE_SAMPLES:
            curves[pos] = np.array([pdf["Points"].median()])
            continue
        med = pdf.groupby("PosRank")["Points"].median()
        med = med.reindex(range(1, int(med.index.max()) + 1)).interpolate()
        smooth = med.rolling(window=5, center=True, min_periods=1).mean()
        curves[pos] = np.minimum.accumulate(smooth.to_numpy())

    def expected(row):
        curve = curves[row["Position"]]
        idx = min(int(row["PosRank"]), len(curve)) - 1
        return curve[idx]

    pool["Expected"] = pool.apply(expected, axis=1)
    resid_sd = (
        (pool["Points"] - pool["Expected"])
        .groupby(pool["Position"])
        .std(ddof=0)
        .clip(lower=1.0)
        .to_dict()
    )
    return curves, resid_sd


def _expected_points(df, curves):
    def expected(row):
        curve = curves.get(row["Position"])
        if curve is None or len(curve) == 0:
            return np.nan
        idx = min(int(row["PosRank"]), len(curve)) - 1
        return curve[idx]

    return df.apply(expected, axis=1)


def replacement_levels(draft_df, fa_df):
    """Replacement-level points per position for one league-year."""
    n_teams = draft_df["Team"].nunique()
    pool = draft_df[["Position", "Points"]]
    if fa_df is not None and len(fa_df):
        pool = pd.concat([pool, fa_df[["Position", "Points"]]], ignore_index=True)
    levels = {}
    for pos, pdf in pool.groupby("Position"):
        k = STARTERS.get(pos, 1) * n_teams
        pts = pdf["Points"].sort_values(ascending=False)
        levels[pos] = pts.iloc[min(k, len(pts)) - 1]
    return levels


def grade_all(draft_frames, fa_frames):
    """Grade every league-year at once.

    draft_frames / fa_frames: dict mapping (league, year) -> raw DataFrame
    with at least [Total Pick, Player, Position, Team, Points].
    Returns the same dicts with Draft Grade / Performance Grade and Letter
    Grade columns replaced.
    """
    pooled = []
    for (league, year), df in draft_frames.items():
        d = df.copy()
        d["League Name"], d["Year"] = league, year
        pooled.append(d)
    pool = pd.concat(pooled, ignore_index=True)
    curves, resid_sd = build_expectation_curves(pool)

    # --- draft picks ---
    pool["PosRank"] = (
        pool.sort_values("Total Pick")
        .groupby(["League Name", "Year", "Position"])
        .cumcount()
        + 1
    )
    pool["Expected"] = _expected_points(pool, curves)
    pool["VOS"] = (pool["Points"] - pool["Expected"]) / pool["Position"].map(resid_sd).fillna(1.0)

    par = pd.Series(np.nan, index=pool.index)
    for (league, year), gdf in pool.groupby(["League Name", "Year"]):
        levels = replacement_levels(gdf, fa_frames.get((league, year)))
        par.loc[gdf.index] = gdf["Points"] - gdf["Position"].map(levels)
    pool["PAR"] = par

    pool["zVOS"] = _grouped_z(pool, "VOS", ["Year", "Position"])
    pool["zPAR"] = _grouped_z(pool, "PAR", ["Year", "Position"])
    pool["raw"] = 0.6 * pool["zVOS"] + 0.4 * pool["zPAR"]
    pool["z"] = _grouped_z(pool, "raw", ["Year"])
    pool["Draft Grade"] = (GRADE_CENTER + GRADE_PER_Z * pool["z"]).clip(GRADE_MIN, GRADE_MAX).round(2)
    pool["Letter Grade"] = pool["Draft Grade"].apply(grade_to_letter)

    graded_drafts = {}
    for (league, year), gdf in pool.groupby(["League Name", "Year"]):
        original = draft_frames[(league, year)].copy()
        original = original.drop(columns=["Draft Grade", "Letter Grade"], errors="ignore")
        merged = original.merge(
            gdf[["Total Pick", "Draft Grade", "Letter Grade", "Expected"]],
            on="Total Pick",
            how="left",
        )
        merged = merged.sort_values("Draft Grade", ascending=False).reset_index(drop=True)
        graded_drafts[(league, year)] = merged

    # --- free agents: PAR-only, standardized within the season's FA pool ---
    fa_pooled = []
    for (league, year), df in fa_frames.items():
        if (league, year) not in draft_frames or df is None or not len(df):
            continue
        d = df.copy()
        d["League Name"], d["Year"] = league, year
        levels = replacement_levels(draft_frames[(league, year)], df)
        d["PAR"] = d["Points"] - d["Position"].map(levels)
        fa_pooled.append(d)

    graded_fas = {}
    if fa_pooled:
        fa_pool = pd.concat(fa_pooled, ignore_index=True)
        fa_pool["zPAR"] = _grouped_z(fa_pool, "PAR", ["Year", "Position"])
        fa_pool["z"] = _grouped_z(fa_pool, "zPAR", ["Year"])
        fa_pool["Performance Grade"] = (
            (GRADE_CENTER + GRADE_PER_Z * fa_pool["z"]).clip(GRADE_MIN, GRADE_MAX).round(2)
        )
        fa_pool["Letter Grade"] = fa_pool["Performance Grade"].apply(grade_to_letter)
        for (league, year), gdf in fa_pool.groupby(["League Name", "Year"]):
            original = fa_frames[(league, year)].copy()
            original = original.drop(columns=["Performance Grade", "Letter Grade"], errors="ignore")
            merged = original.merge(
                gdf[["Player", "Team", "Performance Grade", "Letter Grade"]],
                on=["Player", "Team"],
                how="left",
            )
            merged = merged.sort_values("Performance Grade", ascending=False).reset_index(drop=True)
            graded_fas[(league, year)] = merged

    return graded_drafts, graded_fas


def team_grades(graded_drafts):
    """Team-level grades: pick grades weighted by the slot's expected points."""
    rows = []
    for (league, year), df in graded_drafts.items():
        weights = df["Expected"].clip(lower=1.0)
        for team, tdf in df.groupby("Team"):
            w = weights.loc[tdf.index]
            grade = float(np.average(tdf["Draft Grade"], weights=w))
            rows.append({
                "Team": team,
                "Draft Grade": round(grade, 2),
                "Letter Grade": grade_to_letter(grade),
                "League Name": f"{league} {year}",
            })
    out = pd.DataFrame(rows).sort_values("Draft Grade", ascending=False).reset_index(drop=True)
    return out


def _load_frames():
    draft_frames, fa_frames, paths = {}, {}, {}
    for path in sorted(glob.glob(os.path.join(DRAFTS_DIR, "*.csv"))):
        name = os.path.basename(path)
        m = DRAFT_FILE_RE.match(name)
        if m:
            key = (m.group("league").strip(), int(m.group("year")))
            draft_frames[key] = pd.read_csv(path)
            paths[("draft",) + key] = path
            continue
        m = FA_FILE_RE.match(name)
        if m:
            key = (m.group("league").strip(), int(m.group("year")))
            fa_frames[key] = pd.read_csv(path)
            paths[("fa",) + key] = path
    return draft_frames, fa_frames, paths


def regrade_all(verbose=True):
    """Regrade every drafts/ CSV in place and rebuild the aggregate files."""
    draft_frames, fa_frames, paths = _load_frames()
    if verbose:
        print(f"Grading {len(draft_frames)} drafts and {len(fa_frames)} free-agent files...")
    graded_drafts, graded_fas = grade_all(draft_frames, fa_frames)

    for key, df in graded_drafts.items():
        df.drop(columns=["Expected"]).to_csv(paths[("draft",) + key], index=False)
    for key, df in graded_fas.items():
        df.to_csv(paths[("fa",) + key], index=False)

    # Master_Draft_Data.csv = all draft picks with league/year columns
    master_parts = []
    for (league, year), df in graded_drafts.items():
        d = df.drop(columns=["Expected", "Owner ID"], errors="ignore").copy()
        d["League Name"], d["Year"] = league, year
        master_parts.append(d)
    master = pd.concat(master_parts, ignore_index=True)
    master.to_csv(MASTER_CSV, index=False)

    # Aggregated team grades (capital-weighted)
    teams = team_grades(graded_drafts)
    teams.to_csv(AGGREGATED_CSV, index=False)

    # Update grade columns in the standings file, leave standings/LPI intact
    unmatched = 0
    if os.path.exists(STANDINGS_CSV):
        standings = pd.read_csv(STANDINGS_CSV)
        key_frame = teams.copy()
        parts = key_frame["League Name"].str.rsplit(" ", n=1)
        key_frame["_league"] = parts.str[0]
        key_frame["_year"] = parts.str[1].astype(float)
        lookup = {
            (r["Team"], r["_league"], r["_year"]): (r["Draft Grade"], r["Letter Grade"])
            for _, r in key_frame.iterrows()
        }
        for i, row in standings.iterrows():
            hit = lookup.get((row["Team"], row["League Name"], row["Year"]))
            if hit:
                standings.at[i, "Draft Grade"], standings.at[i, "Letter Grade"] = hit
            else:
                unmatched += 1
        standings = standings.sort_values("Draft Grade", ascending=False).reset_index(drop=True)
        standings.to_csv(STANDINGS_CSV, index=False)

    if verbose:
        pool = pd.concat([df for df in graded_drafts.values()], ignore_index=True)
        print(f"Rewrote {len(graded_drafts)} draft files, {len(graded_fas)} FA files, "
              f"{len(master)} master rows, {len(teams)} team grades "
              f"({unmatched} standings rows had no matching team grade).")
        print("Letter distribution:", pool["Letter Grade"].value_counts().to_dict())
    return graded_drafts, graded_fas


if __name__ == "__main__":
    regrade_all()
