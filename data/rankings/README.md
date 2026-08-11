# Draft rankings sheets

Drop rankings CSVs here and the **Draft Assistant** page (`pages/17_📋_Draft_Assistant.py`)
offers them in a dropdown. The page also takes a direct upload, which is the
intended path when it is deployed — upload the version closest to your draft so
you get the latest updates.

The CSVs themselves are **gitignored on purpose**. A rankings sheet is somebody
else's product; committing one to a public repo redistributes their work. Only
this README is tracked.

## What the parser needs

Two required columns, matched case-insensitively:

| Field | Accepted column names |
|---|---|
| **Name** | `Name`, `Player`, `Player Name` |
| **Rank** | `FantasyPros`, `ECR`, `FP`, `Rank`, `Rk`, `Overall Rank`, `Consensus` |

Optional, used when present: `Pos`, `Team`, `ADP`, `Bye`, `Tier`, `Round`,
`ESPN`, `Landmine`/`Notes`. A leading unnamed index column is ignored.

`Round` is treated as a tier marker: sheets tend to set it only on the first
player of each round, so it is forward-filled into a per-player **Target Round**.

## Name matching

ESPN carries generational suffixes and ranking sheets usually strip them, so
about 11% of names differ on spelling alone. The matcher normalises both sides —
`James Cook` ↔ `James Cook III`, `A.J. Brown` ↔ `AJ Brown`,
`Amon-Ra St. Brown` ↔ `Amon Ra St Brown` — then falls back to spacing-insensitive
and last-name-plus-position, each only when unambiguous.

Anything still unmatched is **listed on the page**, never silently dropped.
Verified at 200/200 against a real sheet; see `tools/check_draft_board.py`.
