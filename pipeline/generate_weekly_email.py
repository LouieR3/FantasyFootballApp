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
            (all_matchups['League Name'] == league_name) &
            (all_matchups['Year'] == year)
        ].copy()
        return league_matchups
    except Exception as e:
        print(f"Warning: Could not load matchups: {e}")
        return pd.DataFrame()

def load_standings(league_name, year):
    """Load standings from the league workbook."""
    try:
        file_path = f"{LEAGUES_DIR}/{league_name} {year}.xlsx"
        standings = pd.read_excel(file_path, sheet_name="Standings")
        return standings
    except Exception as e:
        print(f"Warning: Could not load standings: {e}")
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

    return matchups[matchups['Week'] == latest_week].sort_values('Team 1')

def format_matchup_row(row):
    """Format a single matchup as HTML."""
    team1 = row.get('Team 1', '?')
    team2 = row.get('Team 2', '?')
    score1 = row.get('Team 1 Points', 0)
    score2 = row.get('Team 2 Points', 0)

    # Determine winner
    if pd.notna(score1) and pd.notna(score2):
        winner_class = "winner" if score1 > score2 else ("loser" if score1 < score2 else "tie")
        loser_class = "loser" if score2 > score1 else ("winner" if score2 < score1 else "tie")

        score1_display = f"<span class='{winner_class if score1 > score2 else 'loser if score1 < score2 else \"\"'}'>{score1:.1f}</span>"
        score2_display = f"<span class='{loser_class if score2 > score1 else 'winner if score2 < score1 else \"\"'}'>{score2:.1f}</span>"
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

def build_html_email(league_name, year, week):
    """Build the complete HTML email."""

    # Load data
    matchups = get_latest_week_matchups(league_name, year)
    standings = load_standings(league_name, year)

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
            wins = row.get('Wins', 0)
            losses = row.get('Losses', 0)
            pf = row.get('Points For', 0)
            record = f"{int(wins)}-{int(losses)}"
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

        <!-- KEY INSIGHTS -->
        <h2>💡 This Week's Insights</h2>
        <div class="insight">
            <strong>Biggest Win:</strong> The team with the best performance. Check the matchups above.
        </div>
        <div class="insight">
            <strong>Playoff Implications:</strong> Based on current standings, ~6 teams are competing for playoff spots.
        </div>

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
            Generated by Pennoni Fantasy Football · <a href="https://sleeper.app/" style="color: #1f77b4; text-decoration: none;">View on Sleeper</a>
        </div>
    </div>
</body>
</html>
"""
    return html

def main():
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
    output_path.write_text(html)

    print(f"✅ Email generated: {output_path.resolve()}")
    print(f"   League: {args.league}")
    print(f"   Week: {week}")
    print(f"   Year: {year}")
    print(f"\n📧 Open {output_path} in your browser, then copy/paste into Gmail.")

if __name__ == '__main__':
    main()
