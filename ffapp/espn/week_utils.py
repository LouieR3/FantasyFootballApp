"""Week-boundary helpers for the weekly update scripts.

The season-edge cases (first week, last regular-season week, first playoff week,
leagues whose playoffs start earlier or later) used to be handled inline in two
scripts that disagreed with each other, which is why they needed hand-editing
at the boundaries. The logic lives here once, with tests.

ESPN gives every team a `scores` list padded out to the full season, so
unplayed weeks show up as 0.0 for everyone. A week counts as played if *anyone*
scored in it.

Two numbering systems are in play, so every function says which it returns:

* **week number** - 1-based, what a human calls "week 5".
* **column index** - 0-based position in `scores_df` / `schedules_df`, which is
  how the scripts index them (`scores_df.loc[team, 4]` is week 5).
"""


def completed_weeks(scores_df):
    """How many weeks have actually been played (a week number).

    Counts columns where at least one team scored, rather than looking for the
    first all-zero column, so a gap can't cut the count short.
    """
    return int((scores_df != 0.0).any(axis=0).sum())


def current_week(scores_df):
    """The week now in progress / next to be played (a week number).

    Equals ``completed_weeks() + 1``. If the whole season is done this is one
    past the last week, which is what the "iterate completed weeks" loops want:
    ``for week in range(1, current_week(scores_df))``.
    """
    return completed_weeks(scores_df) + 1


def completed_week_numbers(scores_df):
    """Week numbers that have been played, e.g. [1, 2, 3] (1-based)."""
    return list(range(1, completed_weeks(scores_df) + 1))


def regular_season_over(scores_df, reg_season_count):
    """True once every regular-season week has been played.

    ``reg_season_count`` is ESPN's ``settings.reg_season_count`` and differs
    between leagues, which is what makes playoffs start at different weeks.
    """
    return completed_weeks(scores_df) >= reg_season_count


def completed_playoff_week_indices(scores_df, reg_season_count):
    """Column indices (0-based) of playoff weeks that have been *played*.

    Empty until the first playoff week is complete. This is the fix for the
    first-playoff-week failure: the old code iterated every remaining column,
    including unplayed ones, and then looked those weeks up in the "LPI By
    Week" sheet, which only has columns for completed weeks.

    Week ``reg_season_count + 1`` is the first playoff week, and its column
    index is ``reg_season_count``.
    """
    done = completed_weeks(scores_df)
    if done <= reg_season_count:
        return []
    last_index = min(done, len(scores_df.columns)) - 1
    return list(range(reg_season_count, last_index + 1))


def has_lpi_week(lpi_week_df, week_number):
    """Whether the LPI By Week sheet has a column for this week number."""
    return f"Week {week_number}" in lpi_week_df.columns
