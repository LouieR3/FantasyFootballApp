"""Where does your team rank among everyone who owns the same star player?

Player_Stats_By_Record.py asks "which players sit on winning/losing teams."
This asks the inverse: for a given notable player (drafted in the top few
rounds, so true preseason draft capital rather than a hot waiver pickup),
every team *currently* rostering them across every 2026 league, and where
one specific team's win % falls in that distribution.

"Major player" = drafted in round 1-3 in at least one league this season
(--rounds to change the cutoff). Ownership and records are read live, so
trades/drops since the draft are reflected correctly - this is NOT the same
as "who drafted them."

    python pipeline/player_ownership_percentile.py
    python pipeline/player_ownership_percentile.py --league "Pennoni Younglings" --team "The Golden Receivers"
    python pipeline/player_ownership_percentile.py --rounds 2
    python pipeline/player_ownership_percentile.py --min-owners 5  # drop thin-sample players

Output:
    Console: for the chosen team, each major player they own, how many teams
    league-wide also own that player, and this team's win % percentile among them.
    pipeline/player_ownership_percentile.png: box-and-dot chart of the same.
"""
import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from espn_api.football import League

from ffapp import league_registry as registry
from ffapp.leagues_config import get_leagues_for_year

YEAR = 2026
DEFAULT_LEAGUE = "Pennoni Younglings"
DEFAULT_TEAM = "The Golden Receivers"
# `_d` above gets walked up to the repo root by the sys.path bootstrap, so it
# no longer points at this file's own directory - resolve that separately.
_SCRIPT_DIR = _os.path.dirname(_os.path.abspath(__file__))
OUTPUT_PNG = _os.path.join(_SCRIPT_DIR, "player_ownership_percentile.png")


def pull_league_wide_ownership(year=YEAR):
    """One row per (player, owning team, league) across every configured league.

    Draft round comes from ``league.draft`` (free - already fetched with the
    league object, no per-player calls needed). Current owner and record come
    from live rosters, so a trade since draft day is reflected correctly.
    """
    rows = []
    failed = []
    for cfg in get_leagues_for_year(year):
        try:
            league = League(league_id=cfg["league_id"], year=year,
                             espn_s2=cfg["espn_s2"], swid=cfg["swid"])
        except Exception as e:
            failed.append((cfg["name"], type(e).__name__))
            continue

        league_name = registry.canonical(league.settings.name) or cfg["name"]
        draft_round = {}
        try:
            for pick in league.draft:
                draft_round[pick.playerName] = pick.round_num
        except Exception:
            pass  # a league with no draft on file (e.g. mid-season add) just has none

        for team in league.teams:
            games = (team.wins or 0) + (team.losses or 0) + (team.ties or 0)
            win_pct = round(100 * (team.wins + 0.5 * team.ties) / games, 1) if games else np.nan
            for p in team.roster:
                rows.append({
                    "Player": p.name,
                    "Position": p.position,
                    "League": league_name,
                    "Team": team.team_name,
                    "Draft Round": draft_round.get(p.name),
                    "Team W": team.wins, "Team L": team.losses, "Team T": team.ties,
                    "Team Win %": win_pct,
                    "Team PPG": round(sum(team.scores[:games]) / games, 1) if games else np.nan,
                })

    df = pd.DataFrame(rows)
    if failed:
        print(f"Skipped {len(failed)} league(s) that could not be reached: "
              f"{', '.join(n for n, _ in failed)}")
    return df


def major_players(df, max_round):
    """Players drafted in round <= max_round in at least one league.

    A player's "tier" uses the best (lowest) round seen anywhere - a true
    first-rounder taken round 5 in one shallow league is still a first-rounder.
    """
    rounds = df.dropna(subset=["Draft Round"]).groupby("Player")["Draft Round"].min()
    return rounds[rounds <= max_round].sort_values()


def ownership_distribution(df, player):
    """Every team currently rostering `player`, with its win % and PPG."""
    return df[df["Player"] == player][
        ["League", "Team", "Draft Round", "Team W", "Team L", "Team T", "Team Win %", "Team PPG"]
    ].drop_duplicates(subset=["League", "Team"]).sort_values("Team Win %", ascending=False)


def percentile_of(value, series):
    """% of the distribution this value beats or ties - np.nan-safe."""
    s = series.dropna()
    if value is None or pd.isna(value) or len(s) <= 1:
        return np.nan
    return round(100 * (s <= value).mean(), 1)


def report_team(df, league_name, team_name, max_round, min_owners=1):
    league_name = registry.canonical(league_name)
    roster = df[(df["League"] == league_name) & (df["Team"] == team_name)]
    if roster.empty:
        print(f"No roster found for '{team_name}' in '{league_name}' - check spelling "
              f"(league names must match ESPN's, e.g. registry.canonical output).")
        return None

    team_row = roster.iloc[0]
    print(f"\n{'=' * 90}\n{team_name} ({league_name}): "
          f"{int(team_row['Team W'])}-{int(team_row['Team L'])}-{int(team_row['Team T'])}, "
          f"{team_row['Team Win %']}% win rate\n{'=' * 90}")

    tiers = major_players(df, max_round)
    owned_majors = roster[roster["Player"].isin(tiers.index)].sort_values(
        "Player", key=lambda s: s.map(tiers)
    )
    if min_owners > 1:
        enough_owners = {p for p in owned_majors["Player"]
                         if len(ownership_distribution(df, p)) >= min_owners}
        dropped = set(owned_majors["Player"]) - enough_owners
        owned_majors = owned_majors[owned_majors["Player"].isin(enough_owners)]
        if dropped:
            print(f"(dropped {len(dropped)} player(s) owned by fewer than {min_owners} "
                  f"teams league-wide: {', '.join(sorted(dropped))})")
    if owned_majors.empty:
        print(f"No round <= {max_round} players on this roster "
              f"{'with at least ' + str(min_owners) + ' owners' if min_owners > 1 else ''}.")
        return None

    results = []
    for _, row in owned_majors.iterrows():
        player = row["Player"]
        dist = ownership_distribution(df, player)
        pct = percentile_of(team_row["Team Win %"], dist["Team Win %"])
        results.append({
            "Player": player,
            "Pos": row["Position"],
            "Round": int(tiers[player]),
            "Owners league-wide": len(dist),
            "Median owner win %": round(dist["Team Win %"].median(), 1),
            "This team's win % percentile among owners": pct,
        })
        print(f"\n{player} ({row['Position']}, round {int(tiers[player])}) - "
              f"owned by {len(dist)} team(s) across the leagues on file:")
        print(dist.to_string(index=False))

    out = pd.DataFrame(results).sort_values(
        "This team's win % percentile among owners", ascending=False
    )
    print(f"\n--- Summary for {team_name} ---")
    print(out.to_string(index=False))
    return out


def plot_team(df, league_name, team_name, max_round, out_path, min_owners=1):
    league_name = registry.canonical(league_name)
    tiers = major_players(df, max_round)
    roster = df[(df["League"] == league_name) & (df["Team"] == team_name)]
    if roster.empty:
        return
    team_win_pct = roster.iloc[0]["Team Win %"]
    owned_majors = sorted(
        (p for p in roster["Player"] if p in tiers.index
         and len(ownership_distribution(df, p)) >= min_owners),
        key=lambda p: tiers[p],
    )
    if not owned_majors:
        print("Nothing to plot - no top-round players on this roster "
              f"{'with enough owners' if min_owners > 1 else ''}.")
        return

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(12, max(4, 0.6 * len(owned_majors) + 1)))
    fig.patch.set_facecolor("#0b1620")
    ax.set_facecolor("#0b1620")

    box_data, labels = [], []
    rng = np.random.default_rng(0)
    for i, player in enumerate(owned_majors):
        dist = ownership_distribution(df, player)["Team Win %"].dropna()
        box_data.append(dist.tolist())
        labels.append(f"{player} (rd {int(tiers[player])}, n={len(dist)})")

    positions = list(range(len(owned_majors), 0, -1))
    bp = ax.boxplot(box_data, positions=positions, vert=False, widths=0.5,
                     patch_artist=True, showfliers=False,
                     medianprops=dict(color="#2ee6d6", linewidth=2),
                     boxprops=dict(facecolor="#17323a", edgecolor="#2ee6d6"),
                     whiskerprops=dict(color="#2ee6d6"), capprops=dict(color="#2ee6d6"))

    for pos, dist in zip(positions, box_data):
        jitter = rng.uniform(-0.15, 0.15, size=len(dist))
        ax.scatter(dist, [pos + j for j in jitter], color="#9fb4bd", s=18,
                   zorder=3, alpha=0.8)

    # Highlight this team's own point on every row
    ax.scatter([team_win_pct] * len(positions), positions, color="#ff7f0e",
               marker="*", s=260, zorder=5, edgecolors="black", linewidths=0.6,
               label=f"{team_name}'s win %")

    ax.set_yticks(positions)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Win % among all teams that currently own this player")
    ax.set_title(f"{team_name} ({league_name}) vs. the field, by top-{max_round}-round player owned",
                 color="white")
    ax.legend(loc="lower right", facecolor="#17323a", edgecolor="#2ee6d6", labelcolor="white")
    ax.grid(axis="x", color="#2a4550", linewidth=0.5, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_color("#2a4550")

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"\nSaved {out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--league", default=DEFAULT_LEAGUE)
    parser.add_argument("--team", default=DEFAULT_TEAM)
    parser.add_argument("--rounds", type=int, default=3,
                         help="Treat round <= this as a 'major' player (default 3)")
    parser.add_argument("--min-owners", type=int, default=1,
                         help="Drop players owned by fewer than this many teams "
                              "league-wide - thin samples make a weak percentile (default 1, no filtering)")
    args = parser.parse_args()

    print("Pulling live rosters + draft boards for every 2026 league on file...")
    df = pull_league_wide_ownership(YEAR)
    print(f"{len(df)} roster rows across {df['League'].nunique()} leagues, "
          f"{df['Player'].nunique()} distinct players.\n")

    report_team(df, args.league, args.team, args.rounds, args.min_owners)
    plot_team(df, args.league, args.team, args.rounds, OUTPUT_PNG, args.min_owners)


if __name__ == "__main__":
    main()
