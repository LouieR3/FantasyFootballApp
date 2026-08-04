"""Rebuild the cross-league aggregate CSVs from the league workbooks.

    python pipeline/rebuild_aggregates.py

Runs entirely offline - no ESPN credentials needed - because the league workbooks
under ``data/leagues/`` are already the source of truth. Run it after any weekly
update so the cross-league pages see the latest season.

Why this exists: ``data/all_playoff_dfs.csv`` was built by a function that
*appended* and de-duplicated, and which needed a live ESPN League object it never
actually used. The result was a file frozen at its first pull - it still stopped at
2024 while 13 workbooks held finished 2025 brackets, so every cross-league playoff
view silently omitted the newest season.

Rebuilds:
    data/all_playoff_dfs.csv               every playoff game, all leagues/years
    data/all_playoffs_with_predictions.csv the same plus predicted scores

Not rebuilt here (needs live ESPN):
    data/drafts/Draft_Grades_with_Standings.csv - the `Standing` / final-finish
    column comes from ``league.standings()``, so refreshing it means running
    ``analysis/draft_analysis.py``. Draft *grades* themselves are always current
    in ``Aggregated_Draft_Grades.csv`` via ``pipeline/regrade_drafts.py``.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import runpy

from ffapp.espn.all_playoffs import rebuild_from_workbooks

if __name__ == "__main__":
    print("1/2  rebuilding playoff results from the league workbooks...")
    rebuild_from_workbooks()

    print("\n2/2  adding predicted scores...")
    runpy.run_path(_os.path.join(_d, 'pipeline', 'playoff_add_predicted.py'),
                   run_name='__main__')

    print("\nDone. Reminder: `Standing` / final finish still needs "
          "analysis/draft_analysis.py (live ESPN).")
