"""Repo-anchored data locations.

Every data read/write goes through these constants instead of a bare relative
path. They resolve against this file's location, so scripts work no matter
which directory you run them from - previously anything but the repo root
silently wrote files to the wrong place (or crashed).

Layout::

    data/
      leagues/       one xlsx per league-year (the app's main source)
      drafts/        draft + free agent results csv per league-year
      odds/          betting odds xlsx per league-year
      transactions/  weekly roster snapshots + reconstructed moves per league-year
      *.csv          cross-league aggregates (all_matchups, Master_Draft_Data, ...)

Usage::

    from paths import LEAGUES_DIR, league_file
    df = pd.read_excel(league_file("EBC League", 2025))
"""
import os

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(REPO_ROOT, "data")
LEAGUES_DIR = os.path.join(DATA_DIR, "leagues")
DRAFTS_DIR = os.path.join(DATA_DIR, "drafts")
ODDS_DIR = os.path.join(DATA_DIR, "odds")
TRANSACTIONS_DIR = os.path.join(DATA_DIR, "transactions")

# Cross-league aggregate files that used to sit at the repo root.
MASTER_DRAFT_DATA = os.path.join(DATA_DIR, "Master_Draft_Data.csv")
ALL_MATCHUPS = os.path.join(DATA_DIR, "all_matchups.csv")
ALL_PLAYOFF_DFS = os.path.join(DATA_DIR, "all_playoff_dfs.csv")
ALL_PLAYOFFS = os.path.join(DATA_DIR, "all_playoffs.csv")
ALL_PLAYOFFS_WITH_PREDICTIONS = os.path.join(DATA_DIR, "all_playoffs_with_predictions.csv")

# Grade/standings aggregates live alongside the draft files.
AGGREGATED_DRAFT_GRADES = os.path.join(DRAFTS_DIR, "Aggregated_Draft_Grades.csv")
DRAFT_GRADES_WITH_STANDINGS = os.path.join(DRAFTS_DIR, "Draft_Grades_with_Standings.csv")


def league_file(league_name, year):
    """data/leagues/<league> <year>.xlsx"""
    return os.path.join(LEAGUES_DIR, f"{league_name} {year}.xlsx")


def draft_file(league_name, year):
    """data/drafts/<league> Draft Results <year>.csv"""
    return os.path.join(DRAFTS_DIR, f"{league_name} Draft Results {year}.csv")


def free_agent_file(league_name, year):
    """data/drafts/<league> FreeAgent Results <year>.csv"""
    return os.path.join(DRAFTS_DIR, f"{league_name} FreeAgent Results {year}.csv")


def odds_file(league_name, year):
    """data/odds/<league> <year> Betting Odds.xlsx"""
    return os.path.join(ODDS_DIR, f"{league_name} {year} Betting Odds.xlsx")


def weekly_roster_file(league_name, year):
    """data/transactions/<league> Weekly Rosters <year>.csv.gz

    Gzipped because this is the one bulk dataset here: ~3k player-week rows per
    league-season, which is 24 MB of CSV across a full backfill versus 2 MB
    compressed (11.5x). pandas infers the codec from the extension, so nothing
    else changes. The Moves files stay plain CSV - they are small and are the
    ones worth reading by hand or diffing on GitHub.
    """
    return os.path.join(TRANSACTIONS_DIR, f"{league_name} Weekly Rosters {year}.csv.gz")


def moves_file(league_name, year):
    """data/transactions/<league> Moves <year>.csv"""
    return os.path.join(TRANSACTIONS_DIR, f"{league_name} Moves {year}.csv")


def data_file(name):
    """Any other file under data/."""
    return os.path.join(DATA_DIR, name)


def ensure_dirs():
    """Create the data directories if they don't exist yet."""
    for d in (DATA_DIR, LEAGUES_DIR, DRAFTS_DIR, ODDS_DIR, TRANSACTIONS_DIR):
        os.makedirs(d, exist_ok=True)
