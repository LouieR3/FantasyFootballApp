"""Recompute draft + free agent grades for every season on file.

Run after pulling new draft data, or any time the grading formula changes.
Grades are pooled across all league-years, so every season must be regraded
together for them to stay comparable - that is why this is one command rather
than something draft_data.py does per league.

    python pipeline/regrade_drafts.py

Rewrites, in place:
    data/drafts/* Draft Results *.csv      per-pick Draft Grade / Letter Grade
    data/drafts/* FreeAgent Results *.csv  per-pickup Performance Grade
    data/Master_Draft_Data.csv             all picks, all leagues
    data/drafts/Aggregated_Draft_Grades.csv       team-level grades
    data/drafts/Draft_Grades_with_Standings.csv   grade columns only
"""
import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

from ffapp.metrics.draft_grading import regrade_all

if __name__ == "__main__":
    regrade_all()
