import streamlit as st

st.set_page_config(page_title="Louie's Fantasy Football App", page_icon="🏈", layout="wide")

st.markdown("## 🏈 Welcome to Louie's Fantasy Football App!")
st.markdown(
    "Custom analytics for the ESPN fantasy football leagues I (or a friend) am in. "
    "Pick a league from the sidebar — each page has a **year selector** at the top, "
    "and leagues are labeled by name and season."
)
st.caption(
    "Built by Louie Rodriguez · "
    "[source on GitHub](https://github.com/LouieR3/FantasyFootballApp)"
)

st.divider()

st.markdown("### What you'll find on each league page")

st.markdown(
    """
Sections appear in this order. Some only show up once there's enough data —
odds and remaining-schedule views need a few weeks of scores, and the draft and
betting sections only exist for seasons where that data was collected.
"""
)

left, right = st.columns(2)

with left:
    st.markdown(
        """
#### Results & schedule

- **Playoff Results** — the bracket for that season: matchups, seeds, scores and
  who advanced, once the postseason has started.

- **Schedule Comparison** — a grid of every team's record played against every
  other team's schedule. Read **across your row** to see what your record would
  be with each other team's slate; read **down your column** to see what every
  other team would have done with *your* schedule. Deep yellow is a top-10%
  record, light yellow top 25%, light red bottom 25%, dark red bottom 10%.

- **Strength of Schedule** — schedules ranked hardest to easiest by the average
  number of wins all other teams would get against that slate. Lower average
  wins means a tougher schedule.

- **Expected Wins** — how many wins each team would expect with an average
  schedule. A positive **Difference** means you've been unlucky and "should"
  have that many more wins; negative means you're running ahead of your play.

- **Remaining Schedule Difficulty** — the average LPI of each team's remaining
  opponents. Higher means a tougher road ahead.
        """
    )

with right:
    st.markdown(
        """
#### Projections & power ratings

- **The Louie Power Index (LPI)** — my schedule-adjusted power rating, combining
  Expected Wins with Strength of Schedule. Positive means winning against tough
  schedules; negative means losing against easy ones. Near zero is neutral. High
  LPI with a bad record suggests improvement ahead; the reverse suggests decline.

- **Louie Power Index Each Week** — LPI charted week by week, so you can see who
  is actually trending up or down.

- **Playoff Odds** — each team's chance of finishing in each place, from 10,000
  Monte Carlo simulations of the remaining games using each team's scoring
  average and standard deviation. Projections and byes are not considered.

- **Record Predictions** — the same simulations expressed as a projected
  final record.

- **Playoff Odds By Week** — how those playoff odds have moved week to week.

- **Betting Odds** — sportsbook-style lines for making the playoffs, finishing
  first and finishing last, derived from the same simulations.
        """
    )

st.markdown(
    """
#### Draft & history

- **Draft Results** — every pick graded 30–100 with a letter grade. The grade is
  60% *value over slot* (how the player produced versus what that draft slot
  historically returns, fit from every league-season on file) and 40% *points
  above replacement* at their position. Grades are standardized within each
  season across all leagues, so a 90 means the same thing in any league or year.

- **Biggest LPI Upsets** — the season's biggest surprises: wins by teams that
  were heavy underdogs by LPI. The bigger the **LPI Difference**, the more
  unlikely the result.

- **Lifetime Record** — pick an owner to see their all-time head-to-head record
  against everyone else in that league, plus a season-by-season breakdown with
  record, points for and against, finish and draft grade.
    """
)
