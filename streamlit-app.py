import streamlit as st

st.set_page_config(page_title="Louie's Fantasy Football App", page_icon="🏈", layout="wide")

st.markdown("## 🏈 Welcome to Louie's Fantasy Football App!")
st.markdown(
    "Custom analytics for the ESPN fantasy football leagues I (or a friend) am in. "
    "Pick a league from the sidebar — each league page has a **year selector** at "
    "the top. Below the league pages are the **cross-league deep dives**, which "
    "pool every league and every season on file."
)
st.caption(
    "Built by Louie Rodriguez · "
    "[source on GitHub](https://github.com/LouieR3/FantasyFootballApp)"
)

st.divider()

# ---------------------------------------------------------------- league pages
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
  against everyone else in that league, plus a season-by-season breakdown.
    """
)

st.divider()

# --------------------------------------------------------- cross-league pages
st.markdown("### Deep dives across every league")
st.markdown(
    "These pool every league and season on file rather than looking at one team's year."
)

a, b = st.columns(2)

with a:
    st.markdown(
        """
#### 🏟️ Playoff Analysis
Every bracket ever played, all champions, and how seeding has actually held up
against results.

#### 🔎 Post-Season Draft Analysis
A full post-mortem of one league's draft. Value over slot is split into
**Accuracy** (did you take a player the market already rated above that slot?)
and **Luck** (did they beat their own projection?) — the two add up exactly.
Also: the steals and busts, how much value was left on the board, and the best
draft each manager *could* have had, solved exactly against their own pick slots
and their league's real lineup rules.

#### 🔄 Transaction Analysis
Every add, drop and trade of a season, scored by **SPAR** — started points above
replacement. Points only count when the player was actually in your lineup, and
an add is worth what it *beat*, not what it scored. Best pickups, drops that came
back to haunt, who won each trade, and a manager scorecard.

#### 📋 Live Draft Assistant
For draft day. Upload your rankings sheet and it tells you who's still
available, who's **falling past their positional value**, how thin each position
is getting, and — given your roster and your league's real lineup — **what to
take next**. Works fully offline (tick players off as they go) or reads the live
ESPN draft feed. The positional path is adjustable: from pure best-available to
a strict RB-then-WR-then-TE/QB order.
        """
    )

with b:
    st.markdown(
        """
#### 🏛️ Lifetime League History
For leagues with more than one season: all-time standings, career records,
head-to-head between any two managers, playoff records, the clutch-and-choke
table, longest streaks, the record book — and a league-wide transaction history
showing who has actually won their trades.

#### 🏆 All-Time Hall of Fame
Every team-season from every league, ranked for bragging rights and humiliation
alike: best and worst teams ever, the best team to miss the playoffs, the worst
team to win it all, the best manager still without a ring. Plus the all-time
transaction feats — most lopsided trades, biggest trades, the genuinely mutual
ones, best waiver pickups and worst drops.

> **Comparing across leagues is the hard part.** Leagues differ in size, scoring
> and season length, so raw points mean different things. Cross-league rankings
> use **z-scores within each league-season** — "+2.0" means two standard
> deviations better than that league that year, which travels anywhere.
        """
    )

st.divider()

# ------------------------------------------------------------ add your league
st.markdown("### Want your league added?")

with st.expander("📥 How to add your league — what I need from you", expanded=False):
    st.markdown(
        """
Send me three things and I can pull your league's full history — every season
ESPN still has, usually back to 2019.

**1. Your league ID** — the easy one. Open your league on ESPN and look at the
address bar:

```
https://fantasy.espn.com/football/league?leagueId=1234567&seasonId=2025
                                                  ^^^^^^^
```

That number is the league ID. **If your league is public, that's all I need** —
skip the rest.

**2 & 3. `espn_s2` and `SWID`** — only needed for **private** leagues. These are
two cookies your browser already has once you're logged into ESPN:

1. Open your league on ESPN in Chrome or Edge, logged in
2. Press **F12** to open developer tools
3. Go to the **Application** tab (Firefox calls it **Storage**)
4. In the left sidebar: **Cookies → https://fantasy.espn.com**
5. Find these two rows and copy their **Value**:
   - `espn_s2` — a very long string with `%` signs in it
   - `SWID` — short, looks like `{1A2B3C4D-5E6F-...}`, curly braces included

Paste all three into a message and send them to me directly.
        """
    )
    st.warning(
        "**Send these to me privately — a text or DM, not through this site.** "
        "There is deliberately no form here to type them into. `espn_s2` and "
        "`SWID` are live session cookies: anyone holding them can read your ESPN "
        "fantasy account as you until they expire. Treat them like a password. "
        "A public web page that collects them is exactly what a credential-"
        "phishing page looks like, so this one doesn't — and you shouldn't type "
        "them into any other site that asks, either.",
        icon="🔒",
    )
    st.markdown(
        """
**Two things worth knowing:**

- They expire. Logging out of ESPN everywhere invalidates them immediately, so
  that's your off switch if you ever change your mind.
- I only ever read with them — standings, matchups, rosters, drafts and
  transactions. Nothing is ever written back to your league.

**What you get once it's in:** every section above for each season, plus your
league's own Lifetime History page, and your teams join the all-time Hall of Fame
rankings against everyone else's.
        """
    )

st.caption(
    "Something look wrong, or a section missing for a season you expected? "
    "Tell me which league and year — most gaps are just a season that hasn't "
    "been pulled yet."
)
