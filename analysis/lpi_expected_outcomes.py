"""What does a given end-of-season LPI actually predict?

Buckets every team-season on file (every league, every year) by its final LPI
in width-5 groups (1-5, 6-10, ... and the mirrored -5 to -1, -10 to -6, ...,
with 0 standing alone), then shows the average record and average final
standing for teams that landed in each bucket. Answers "if my LPI is 12 right
now, what does that typically turn into?" - once across every league, once
for Pennoni Younglings specifically.

Fully offline: reads data/leagues/*.xlsx and data/drafts/Draft_Grades_with_Standings.csv,
both already on disk from the weekly pipeline. No ESPN calls.

    python analysis/lpi_expected_outcomes.py

Output:
    analysis/lpi_expected_outcomes_all_leagues.png
    analysis/lpi_expected_outcomes_pennoni.png
"""
import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from paths import DRAFTS_DIR
from ffapp import league_registry as registry
from ffapp.metrics import hall_of_fame as hof

OUTPUT_DIR = _os.path.dirname(_os.path.abspath(__file__))
ALL_LEAGUES_PNG = _os.path.join(OUTPUT_DIR, 'lpi_expected_outcomes_all_leagues.png')
PENNONI_PNG = _os.path.join(OUTPUT_DIR, 'lpi_expected_outcomes_pennoni.png')
PENNONI_LEAGUE = "Pennoni Younglings"


def lpi_bucket(value):
    """Width-5 bucket for an LPI value: 1-5, 6-10, 11-15, ... and the mirrored
    -5 to -1, -10 to -6, ...; 0 stands alone since it splits neither evenly.

    Returns (label, sort_key) so buckets can be ordered worst-to-best.
    """
    v = int(round(value))
    if v == 0:
        return "0", 0
    sign = 1 if v > 0 else -1
    magnitude = abs(v)
    lo = ((magnitude - 1) // 5) * 5 + 1
    hi = lo + 4
    sort_key = sign * (lo + hi) / 2
    label = f"{lo}-{hi}" if sign > 0 else f"-{hi} to -{lo}"
    return label, sort_key


def build_team_seasons_with_standing():
    """Every team-season on file, with its end-of-season LPI bucket and,
    where available, its final league standing."""
    ts = hof.team_seasons()
    ts = ts.dropna(subset=['LPI']).copy()

    standings = pd.read_csv(f"{DRAFTS_DIR}/Draft_Grades_with_Standings.csv")
    standings['League'] = standings['League Name'].map(registry.canonical)
    standings['Year'] = standings['Year'].astype(int)
    standings['Team'] = standings['Team'].astype(str).str.strip()

    ts['Team_key'] = ts['Team'].astype(str).str.strip()
    ts = ts.merge(
        standings[['League', 'Year', 'Team', 'Standing']],
        left_on=['League', 'Year', 'Team_key'],
        right_on=['League', 'Year', 'Team'],
        how='left', suffixes=('', '_standing_match'),
    ).drop(columns=['Team_key', 'Team_standing_match'], errors='ignore')

    buckets = ts['LPI'].apply(lpi_bucket)
    ts['LPI Bucket'] = buckets.map(lambda t: t[0])
    ts['LPI Bucket Sort'] = buckets.map(lambda t: t[1])
    return ts


def summarize(ts):
    """One row per LPI bucket: sample size, average record, average standing."""
    rows = []
    for (label, sort_key), g in ts.groupby(['LPI Bucket', 'LPI Bucket Sort']):
        standing = g['Standing'].dropna()
        rows.append({
            'LPI Bucket': label,
            'Sort': sort_key,
            'Seasons': len(g),
            'Avg Win %': round(g['Win %'].mean(), 1),
            'Avg W': round(g['W'].mean(), 1),
            'Avg L': round(g['L'].mean(), 1),
            'Avg Standing': round(standing.mean(), 2) if len(standing) else np.nan,
            'Standing Seasons': len(standing),
        })
    out = pd.DataFrame(rows).sort_values('Sort').reset_index(drop=True)
    out['Avg Record'] = out.apply(lambda r: f"{r['Avg W']}-{r['Avg L']}", axis=1)
    return out


def plot(summary_df, title, out_path):
    n_buckets = len(summary_df)
    # Each bucket needs real horizontal room for its rotated label and
    # annotation - a fixed width squeezes everything into an unreadable
    # smear once there are 20+ buckets (the full-history, all-leagues case).
    width = max(14, n_buckets * 0.55)
    fig, axes = plt.subplots(2, 1, figsize=(width, 11))
    fig.suptitle(title, fontsize=16)

    colors = ['#d62728' if s < 0 else ('#7f7f7f' if s == 0 else '#2ca02c')
              for s in summary_df['Sort']]

    ax = axes[0]
    bars = ax.bar(summary_df['LPI Bucket'], summary_df['Avg Win %'], color=colors)
    for bar, record, n in zip(bars, summary_df['Avg Record'], summary_df['Seasons']):
        ax.annotate(f"{record}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     textcoords="offset points", xytext=(0, 14), ha='center',
                     va='bottom', fontsize=9, rotation=90)
        ax.annotate(f"n={n}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     textcoords="offset points", xytext=(0, 2), ha='center',
                     va='bottom', fontsize=8, color='#444444')
    ax.axhline(50, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
    ax.set_xlabel('End-of-season LPI')
    ax.set_ylabel('Average win %')
    ax.set_title('Expected record by LPI (bar label = avg W-L record, below it = sample size)')
    ax.set_ylim(0, summary_df['Avg Win %'].max() + 35)
    ax.set_xlim(-0.6, n_buckets - 0.4)
    ax.tick_params(axis='x', rotation=90)

    ax = axes[1]
    plot_df = summary_df.dropna(subset=['Avg Standing'])
    ax.plot(plot_df['LPI Bucket'], plot_df['Avg Standing'], marker='o', color='#1f77b4')
    for x, y, n in zip(plot_df['LPI Bucket'], plot_df['Avg Standing'], plot_df['Standing Seasons']):
        ax.annotate(f"n={n}", (x, y), textcoords="offset points", xytext=(0, 8),
                     ha='center', fontsize=8)
    ax.set_xlabel('End-of-season LPI')
    ax.set_ylabel('Average final standing (1 = best)')
    ax.set_title('Final finishing place by LPI')
    ax.invert_yaxis()
    ax.set_xlim(-0.6, n_buckets - 0.4)
    ax.tick_params(axis='x', rotation=90)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {out_path}")


def report(label, ts):
    summary = summarize(ts)
    print("=" * 88)
    print(f"{label} - {len(ts)} team-seasons")
    print("=" * 88)
    cols = ['LPI Bucket', 'Seasons', 'Avg Win %', 'Avg Record', 'Avg Standing', 'Standing Seasons']
    print(summary[cols].to_string(index=False))
    print()
    return summary


def main():
    ts = build_team_seasons_with_standing()

    all_summary = report("ALL LEAGUES", ts)
    plot(all_summary, 'Expected Record & Finish by End-of-Season LPI - All Leagues', ALL_LEAGUES_PNG)

    pennoni = ts[ts['League'] == PENNONI_LEAGUE]
    if pennoni.empty:
        print(f"No data found for {PENNONI_LEAGUE} - skipping its chart.")
        return
    pennoni_summary = report(PENNONI_LEAGUE, pennoni)
    plot(pennoni_summary, f'Expected Record & Finish by End-of-Season LPI - {PENNONI_LEAGUE}', PENNONI_PNG)


if __name__ == "__main__":
    main()
