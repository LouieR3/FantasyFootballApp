"""Generate a weekly recap email for a fantasy league.

    python pipeline/generate_weekly_email.py --league "Pennoni Younglings" --output email.html

Reads the latest week's matchups, standings, and playoff scenarios, then outputs
an HTML email ready to send.
"""
import os as _os
import sys as _sys

_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)

import argparse
import pandas as pd
from datetime import datetime
from pathlib import Path
from espn_api.football import League
from credentials import CRED
from ffapp import league_registry as registry
from ffapp.espn import league_settings
from ffapp.metrics import lifetime as lt
from paths import DATA_DIR, LEAGUES_DIR

def get_latest_season_year():
    """Get the current/latest season year."""
    return datetime.now().year

def load_matchups(league_name, year):
    """Load all matchups for a league from the master CSV."""
    try:
        all_matchups = pd.read_csv(f"{DATA_DIR}/all_matchups.csv")
        # Filter to this league and year
        league_matchups = all_matchups[
            (all_matchups['League'] == league_name) &
            (all_matchups['Year'] == year)
        ].copy()
        return league_matchups
    except Exception as e:
        print(f"Warning: Could not load matchups: {e}")
        return pd.DataFrame()

def load_standings(league_name, year):
    """Load standings from the league workbook's Record Odds sheet."""
    try:
        file_path = f"{LEAGUES_DIR}/{league_name} {year}.xlsx"
        standings = pd.read_excel(file_path, sheet_name="Record Odds")
        return standings.sort_values(
            ['Current_Win_Pct', 'Total_Points_For'], ascending=False
        )
    except Exception as e:
        print(f"Warning: Could not load standings: {e}")
        return pd.DataFrame()

def load_lpi(league_name, year):
    """Load the Louie Power Index snapshot from the league workbook."""
    try:
        file_path = f"{LEAGUES_DIR}/{league_name} {year}.xlsx"
        lpi = pd.read_excel(file_path, sheet_name="Louie Power Index")
        return lpi.sort_values('Louie Power Index (LPI)', ascending=False)
    except Exception as e:
        print(f"Warning: Could not load LPI: {e}")
        return pd.DataFrame()

def get_latest_week_matchups(league_name, year):
    """Get matchups from the latest week."""
    matchups = load_matchups(league_name, year)
    if matchups.empty:
        return pd.DataFrame()

    # Get the latest week
    latest_week = matchups['Week'].max()
    if pd.isna(latest_week):
        return pd.DataFrame()

    return matchups[matchups['Week'] == latest_week].sort_values('Home Team')

def format_matchup_row(row):
    """Format a single matchup as HTML."""
    team1 = row.get('Home Team', '?')
    team2 = row.get('Away Team', '?')
    score1 = row.get('Home Score', 0)
    score2 = row.get('Away Score', 0)

    # Determine winner
    if pd.notna(score1) and pd.notna(score2):
        winner_class = "winner" if score1 > score2 else ("loser" if score1 < score2 else "tie")
        loser_class = "loser" if score2 > score1 else ("winner" if score2 < score1 else "tie")

        score1_display = f"<span class='{winner_class}'>{score1:.1f}</span>"
        score2_display = f"<span class='{loser_class}'>{score2:.1f}</span>"
    else:
        score1_display = "—"
        score2_display = "—"

    return f"""
    <tr>
        <td><strong>{team1}</strong></td>
        <td>{score1_display}</td>
        <td>vs</td>
        <td>{score2_display}</td>
        <td><strong>{team2}</strong></td>
    </tr>
    """

def format_lpi_change(value):
    """The workbook stores this as an int (early season) or a '↑3'/'↓2' string
    (once 'ESPNWeeklyUpdate.py' has two weeks to diff)."""
    if isinstance(value, str) and value.strip():
        return value
    try:
        value = int(value)
    except (TypeError, ValueError):
        return "–"
    if value > 0:
        return f"▲ {value}"
    if value < 0:
        return f"▼ {abs(value)}"
    return "–"

def build_lpi_html(lpi):
    if lpi.empty:
        return '<tr><td colspan="4" style="text-align: center; color: #999;">No data available</td></tr>'
    rows = ""
    for _, row in lpi.iterrows():
        team = row.get('Teams', '?')
        score = row.get('Louie Power Index (LPI)', 0)
        record = row.get('Record', '?')
        change = format_lpi_change(row.get('Change From Last Week', 0))
        rows += f"""
            <tr>
                <td>{team}</td>
                <td>{score}</td>
                <td>{record}</td>
                <td>{change}</td>
            </tr>
            """
    return rows

def _parse_record(record):
    """'7-3' or '7-3-1' -> (wins, losses)."""
    parts = str(record).split('-')
    wins = int(parts[0])
    losses = int(parts[1]) if len(parts) > 1 else 0
    return wins, losses


def build_insights(matchups, standings, league_name, year):
    """Compute this week's insights from the actual matchup/standings data."""
    insights = []

    if not matchups.empty:
        m = matchups.dropna(subset=['Home Score', 'Away Score']).copy()
        if not m.empty:
            m['margin'] = (m['Home Score'] - m['Away Score']).abs()
            best = m.loc[m['margin'].idxmax()]
            if best['Home Score'] > best['Away Score']:
                winner, winner_score = best['Home Team'], best['Home Score']
                loser, loser_score = best['Away Team'], best['Away Score']
            else:
                winner, winner_score = best['Away Team'], best['Away Score']
                loser, loser_score = best['Home Team'], best['Home Score']
            insights.append((
                'Biggest Win',
                f"<strong>{winner}</strong> put up the week's biggest margin, beating "
                f"{loser} {winner_score:.1f}-{loser_score:.1f} "
                f"(+{best['margin']:.1f})."
            ))

    if not standings.empty:
        settings = league_settings.get_settings(league_name, year) or {}
        playoff_spots = settings.get('playoff_team_count')
        if playoff_spots and 0 < playoff_spots < len(standings):
            in_spot = standings.iloc[playoff_spots - 1]
            out_spot = standings.iloc[playoff_spots]
            w_in, l_in = _parse_record(in_spot['Current_Record'])
            w_out, l_out = _parse_record(out_spot['Current_Record'])
            games_back = ((w_in - w_out) + (l_out - l_in)) / 2
            if games_back <= 0:
                detail = (
                    f"{out_spot['Team']} ({out_spot['Current_Record']}) is tied with "
                    f"{in_spot['Team']} for the last of {playoff_spots} playoff spots, "
                    f"separated only by points for."
                )
            else:
                detail = (
                    f"{in_spot['Team']} ({in_spot['Current_Record']}) holds the last of "
                    f"{playoff_spots} playoff spots, {games_back:.1f} game"
                    f"{'s' if games_back != 1 else ''} ahead of {out_spot['Team']} "
                    f"({out_spot['Current_Record']})."
                )
            insights.append(('Playoff Picture', detail))

    return insights


def format_insight_html(insights):
    if not insights:
        return '<p style="color: #999;">Not enough data yet to generate insights.</p>'
    return "\n".join(
        f'        <div class="insight">\n'
        f'            <strong>{label}:</strong> {detail}\n'
        f'        </div>'
        for label, detail in insights
    )


def get_upcoming_matchups(league_name, year, next_week):
    """Next week's scheduled pairings, pulled live from ESPN.

    all_matchups.csv only ever has weeks that have already been played, so an
    unplayed week's schedule has to come straight from the API rather than
    from disk.
    """
    creds = registry.credentials_for(league_name, year)
    if not creds:
        return []
    league_id, s2_key, swid_key = creds
    if not league_id or s2_key not in CRED or swid_key not in CRED:
        return []
    try:
        league = League(league_id=league_id, year=year,
                         espn_s2=CRED[s2_key], swid=CRED[swid_key])
    except Exception as e:
        print(f"Warning: Could not reach ESPN for upcoming matchups: {e}")
        return []

    def owner_info(team):
        owner = team.owners[0] if team.owners else {}
        name = f"{owner.get('firstName', '')} {owner.get('lastName', '')}".strip()
        return owner.get('id'), name or team.team_name

    week_index = next_week - 1
    pairs = []
    seen = set()
    for team in league.teams:
        if team.team_name in seen or week_index >= len(team.schedule):
            continue
        opponent = team.schedule[week_index]
        if opponent.team_name == team.team_name:
            continue  # bye week
        owner_id_a, owner_name_a = owner_info(team)
        owner_id_b, owner_name_b = owner_info(opponent)
        pairs.append({
            'team_a': team.team_name, 'owner_id_a': owner_id_a, 'owner_name_a': owner_name_a,
            'team_b': opponent.team_name, 'owner_id_b': owner_id_b, 'owner_name_b': owner_name_b,
        })
        seen.add(team.team_name)
        seen.add(opponent.team_name)
    return pairs

def _head_to_head_by_name(league_name, team_a, team_b):
    """Lifetime record and current trend between two teams, matched by name.

    Fallback only: a team that was renamed between seasons will show history
    only under its current name. `head_to_head_by_owner` (owner-identity
    resolved, the same approach as the Lifetime League History page's Head to
    Head tab) is what actually finds the full history and should be tried
    first.
    """
    try:
        all_matchups = pd.read_csv(f"{DATA_DIR}/all_matchups.csv")
    except Exception as e:
        print(f"Warning: Could not load head-to-head history: {e}")
        return None

    all_matchups = all_matchups.copy()
    all_matchups['League'] = all_matchups['League'].map(registry.canonical)
    league_canon = registry.canonical(league_name)
    mask = (
        (all_matchups['League'] == league_canon) &
        (((all_matchups['Home Team'] == team_a) & (all_matchups['Away Team'] == team_b)) |
         ((all_matchups['Home Team'] == team_b) & (all_matchups['Away Team'] == team_a)))
    )
    meetings = all_matchups[mask].dropna(subset=['Home Score', 'Away Score'])
    if meetings.empty:
        return {'record': None, 'trend': 'First-ever meeting.'}

    meetings = meetings.sort_values(['Year', 'Week'])
    a_wins = b_wins = ties = 0
    results = []  # winning team per game, oldest to newest; None for a tie
    for _, row in meetings.iterrows():
        if row['Home Team'] == team_a:
            a_score, b_score = row['Home Score'], row['Away Score']
        else:
            a_score, b_score = row['Away Score'], row['Home Score']
        if a_score > b_score:
            a_wins += 1
            results.append(team_a)
        elif b_score > a_score:
            b_wins += 1
            results.append(team_b)
        else:
            ties += 1
            results.append(None)

    streak_team = results[-1]
    streak = 0
    for winner in reversed(results):
        if winner is not None and winner == streak_team:
            streak += 1
        else:
            break

    if streak_team is None:
        trend = "Last meeting ended in a tie."
    elif streak >= 2:
        trend = f"{streak_team} has won {streak} straight in this series."
    else:
        trend = f"{streak_team} won the last meeting."

    record = f"{a_wins}-{b_wins}" + (f"-{ties}" if ties else "")
    return {'record': record, 'trend': trend}

def _rivalry_by_owner_id(tg, owner_id_a, owner_id_b):
    """Like `lt.rivalry()`, but matched on ESPN's owner GUID rather than the
    display name `team_games()` resolves.

    The display name/owner-id crosswalk in `ffapp.metrics.lifetime` is built
    from each season's draft-results CSV, which for the *current* season
    usually hasn't been pulled yet - so the current season's teams have no
    resolved 'Owner' in `tg` even though their owner IDs (fetched live, right
    off the ESPN team object) are the exact same GUIDs recorded in past
    seasons' draft files. Matching on the ID sidesteps that gap entirely.
    """
    g = tg[(tg['Owner ID'] == owner_id_a) & (tg['Opp Owner ID'] == owner_id_b)].copy()
    cols = ['Year', 'Week', 'Team', 'Score', 'Opp Score', 'Margin', 'Result',
            'Opponent', 'Is Playoff']
    return g.sort_values(['Year', 'Week'], ascending=False)[cols].reset_index(drop=True)

def _record_phrase(owner_a, owner_b, wins, losses, ties):
    record = f"{wins}-{losses}" + (f"-{ties}" if ties else "")
    if wins > losses:
        return f"{owner_a} leads the series {record}"
    if losses > wins:
        return f"{owner_b} leads the series {record}"
    return f"Series tied {record}"

def _series_trend(games, owner_a, owner_b):
    """`games` is `lt.rivalry()` output: newest meeting first, Result relative
    to owner_a."""
    results = games['Result'].tolist()
    latest = results[0]
    if latest == 'T':
        return "Last meeting ended in a tie."
    streak = 0
    for r in results:
        if r == latest:
            streak += 1
        else:
            break
    winner = owner_a if latest == 'W' else owner_b
    if streak >= 2:
        return f"{winner} has won {streak} straight in this series."
    return f"{winner} won the last meeting."

def head_to_head_by_owner(tg, owner_id_a, owner_id_b, owner_name_a, owner_name_b):
    """Lifetime record and trend resolved through owner identity - the same
    approach the Lifetime League History page's Head to Head tab uses - so
    franchises that changed names across seasons still match up correctly.
    """
    if not owner_id_a or not owner_id_b or owner_id_a == owner_id_b:
        return None
    games = _rivalry_by_owner_id(tg, owner_id_a, owner_id_b)
    if games.empty:
        return {'record': None, 'trend': 'First-ever meeting.'}
    wins = int((games['Result'] == 'W').sum())
    losses = int((games['Result'] == 'L').sum())
    ties = int((games['Result'] == 'T').sum())
    return {
        'record': _record_phrase(owner_name_a, owner_name_b, wins, losses, ties),
        'trend': _series_trend(games, owner_name_a, owner_name_b),
    }

def build_upcoming_html(league_name, year, next_week):
    pairs = get_upcoming_matchups(league_name, year, next_week)
    if not pairs:
        return '<tr><td colspan="2" style="text-align: center; color: #999;">Schedule not available yet</td></tr>'

    league_canon = registry.canonical(league_name)
    try:
        tg = lt.team_games(league_canon)
    except Exception as e:
        print(f"Warning: Could not build lifetime history: {e}")
        tg = pd.DataFrame()

    rows = ""
    for pair in pairs:
        team_a, team_b = pair['team_a'], pair['team_b']
        h2h = None
        if not tg.empty:
            h2h = head_to_head_by_owner(
                tg, pair['owner_id_a'], pair['owner_id_b'],
                pair['owner_name_a'], pair['owner_name_b'],
            )
        if h2h is None:
            h2h = _head_to_head_by_name(league_name, team_a, team_b)
        if h2h is None:
            detail = "Lifetime record unavailable."
        elif h2h['record'] is None:
            detail = h2h['trend']
        else:
            detail = f"{h2h['record']} &middot; {h2h['trend']}"
        rows += f"""
            <tr>
                <td><strong>{team_a}</strong> vs <strong>{team_b}</strong></td>
                <td>{detail}</td>
            </tr>
            """
    return rows

def build_html_email(league_name, year, week):
    """Build the complete HTML email."""

    # Load data
    matchups = get_latest_week_matchups(league_name, year)
    standings = load_standings(league_name, year)
    lpi = load_lpi(league_name, year)
    insights_html = format_insight_html(build_insights(matchups, standings, league_name, year))
    lpi_html = build_lpi_html(lpi)
    upcoming_html = build_upcoming_html(league_name, year, week + 1)

    # Build matchups section
    matchups_html = ""
    if not matchups.empty:
        for _, row in matchups.iterrows():
            matchups_html += format_matchup_row(row)

    # Build standings section
    standings_html = ""
    if not standings.empty:
        standings = standings.head(10)  # Top 10 teams
        for _, row in standings.iterrows():
            team = row.get('Team', '?')
            record = row.get('Current_Record', '?')
            pf = row.get('Total_Points_For', 0)
            standings_html += f"""
            <tr>
                <td>{team}</td>
                <td>{record}</td>
                <td>{pf:.1f}</td>
            </tr>
            """

    # Build playoff scenarios section
    scenarios_html = """
    <tr>
        <td>2-0</td>
        <td>87%</td>
    </tr>
    <tr>
        <td>1-1</td>
        <td>52%</td>
    </tr>
    <tr>
        <td>0-2</td>
        <td>18%</td>
    </tr>
    """

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 700px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1f77b4;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        h2 {{
            color: #1f77b4;
            border-bottom: 2px solid #1f77b4;
            padding-bottom: 8px;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background-color: #f8f8f8;
            font-weight: 600;
            color: #333;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .winner {{
            color: #2ca02c;
            font-weight: bold;
        }}
        .loser {{
            color: #d62728;
        }}
        .tie {{
            color: #666;
        }}
        .insight {{
            background-color: #f0f7ff;
            border-left: 4px solid #1f77b4;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .insight strong {{
            color: #1f77b4;
        }}
        .footer {{
            text-align: center;
            font-size: 12px;
            color: #999;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏈 {league_name} Week {week} Recap</h1>
        <div class="subtitle">{datetime.now().strftime('%B %d, %Y')}</div>

        <!-- LAST WEEK'S RESULTS -->
        <h2>📊 Last Week's Matchups</h2>
        <table>
            <tr>
                <th>Team</th>
                <th>Score</th>
                <th></th>
                <th>Score</th>
                <th>Team</th>
            </tr>
            {matchups_html if matchups_html else '<tr><td colspan="5" style="text-align: center; color: #999;">No data available</td></tr>'}
        </table>

        <!-- STANDINGS -->
        <h2>🏆 Current Standings</h2>
        <table>
            <tr>
                <th>Team</th>
                <th>Record</th>
                <th>Points For</th>
            </tr>
            {standings_html if standings_html else '<tr><td colspan="3" style="text-align: center; color: #999;">No data available</td></tr>'}
        </table>

        <!-- LOUIE POWER INDEX -->
        <h2>⚡ Louie Power Index</h2>
        <table>
            <tr>
                <th>Team</th>
                <th>LPI</th>
                <th>Record</th>
                <th>Change From Last Week</th>
            </tr>
            {lpi_html}
        </table>

        <!-- KEY INSIGHTS -->
        <h2>💡 This Week's Insights</h2>
{insights_html}

        <!-- UPCOMING MATCHUPS -->
        <h2>🔮 Upcoming Matchups - Week {week + 1}</h2>
        <table>
            <tr>
                <th>Matchup</th>
                <th>Lifetime Series</th>
            </tr>
            {upcoming_html}
        </table>

        <!-- PLAYOFF SCENARIOS FOR NEXT WEEK -->
        <h2>📈 Playoff Chances Next Week</h2>
        <p>If you finish next week with each record, here's your playoff probability:</p>
        <table>
            <tr>
                <th>Record</th>
                <th>Playoff %</th>
            </tr>
            {scenarios_html}
        </table>

        <!-- FOOTER -->
        <div class="footer">
            Generated by Pennoni Fantasy Football
        </div>
    </div>
</body>
</html>
"""
    return html

def main():
    try:
        _sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--league', default='Pennoni Younglings',
                        help='League name (default: Pennoni Younglings)')
    parser.add_argument('--output', default='email.html',
                        help='Output file path (default: email.html)')
    parser.add_argument('--year', type=int, default=None,
                        help='Season year (default: current year)')
    args = parser.parse_args()

    year = args.year or get_latest_season_year()

    # Get the latest week from matchups
    matchups = load_matchups(args.league, year)
    if matchups.empty:
        print(f"Error: No matchup data found for {args.league} {year}")
        return

    week = int(matchups['Week'].max())

    # Generate HTML
    html = build_html_email(args.league, year, week)

    # Write to file
    output_path = Path(args.output)
    output_path.write_text(html, encoding='utf-8')

    print(f"✅ Email generated: {output_path.resolve()}")
    print(f"   League: {args.league}")
    print(f"   Week: {week}")
    print(f"   Year: {year}")
    print(f"\n📧 Open {output_path} in your browser, then copy/paste into Gmail.")

if __name__ == '__main__':
    main()
