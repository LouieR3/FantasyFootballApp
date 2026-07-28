from credentials import CRED
import pandas as pd
from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter

start_time = time.time()

espn_s2 = CRED["louie_s2"]

# Pennoni Younglings
year = 2025
# league = League(league_id=310334683, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])

# Family League
# league = League(league_id=996930954, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])

# EBC League
# league = League(league_id=1118513122, year=year, espn_s2=espn_s2, swid=CRED["louie_swid"])

# Pennoni Transportation
# league = League(league_id=1339704102, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Game of Yards
# league = League(league_id=1781851, year=year, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Brown Munde
# league = League(league_id=367134149, year=2022, espn_s2=CRED["prahlad_s2"], swid=CRED["prahlad_swid"])

# Turf On Grade League
# league = League(league_id=1242265374, year=2024, espn_s2=CRED["turf_s2"], swid=CRED["prahlad_swid"])

# Las League
# league = League(league_id=1049459, year=2025, espn_s2=CRED["la_s2"], swid=CRED["la_swid"])

# Hannahs League
hannah_s2 = CRED["hannah_s2"]
league = League(
    league_id=1399036372,
    year=2025,
    espn_s2=hannah_s2,
    swid=CRED["hannah_swid"],
)

ava_s2 = CRED["ava_s2"]
matt_s2 = CRED["matt_s2"]
elle_s2 = CRED["elle_s2"]
dave_s2 = CRED["dave_s2"]

# Avas League
# league = League(league_id=417131856, year=2025, espn_s2=ava_s2, swid=CRED["ava_swid"])
# Matts League
# league = League(league_id=261375772, year=2024, espn_s2=matt_s2, swid=CRED["matt_swid"])
# Elles League
# league = League(league_id=1259693145, year=2025, espn_s2=elle_s2, swid=CRED["elle_swid"])

# Dave Work League
# year = 2025
league = League(
    league_id=1675186799,
    year=year,
    espn_s2=dave_s2,
    swid=CRED["dave_swid"],
)
# league = League(league_id= 1924463077, year= year, espn_s2= dave_s2, swid= CRED["dave_swid"])


nolan_s2 = CRED["nolan_s2"]
league = League(
    league_id=496646254,
    year=year,
    espn_s2=nolan_s2,
    swid=CRED["nolan_swid"],
)


def test_league_data(league):
    print(league.settings)
    print(league.current_week)
    settings = league.settings
    print(settings.reg_season_count)
    print(settings.playoff_team_count)
    print(league.settings.tie_rule)

    # print(league.free_agents())
    # print(league.least_scored_week())
    # print(league.least_scorer())
    # print(league.load_roster_week(2))
    # print(league.most_points_against())
    # print(league.player_info(4036212))
    print(league.previousSeasons)
    # print(league.recent_activity())


test_league_data(league)


def test_matchup_data(league):
    playoff_round_1 = league.box_scores(week=1)
    for match in playoff_round_1:
        print(match)
        print(match.home_lineup)
        print(match.home_team)
        print(match.home_projected)
        print(match.home_score)
        print(match.away_team)
        print(match.away_projected)
        print(match.away_score)
        # print(match.matchup_type)
        print()


# test_matchup_data(league)

playoff_round_1 = league.box_scores(week=15)[0]
playoff_round_1.matchup_type


# player = playoff_round_1[0].home_lineup[0]
# print(player.points_breakdown)
def test_player_data(league):
    playoff_round_1 = league.box_scores(week=15)
    player = playoff_round_1[0].home_lineup[0]
    player = league.player_info(playerId=13983)
    print(player.playerId)
    print(player.name)
    print(player.position)
    print(player.proTeam)
    print(player.injuryStatus)
    print(player.projected_points)
    print(player.points)
    print(player.points_breakdown)
    print(player.acquisitionType)
    print(player.stats)
    print(player.avg_points)
    print(player.posRank)
    print()
    print(playoff_round_1[0].home_lineup)

    player_name = player.name
    player_stat = league.player_info(player_name)
    player_stats = player_stat.stats
    print(player_stats)


# test_player_data(league)


def test_team_data(league):
    team_names = [team.team_name for team in league.teams]
    print(team_names)

    team_owners = [team.owners[0]["id"] for team in league.teams]
    # print(team_owners)

    team_scores = [team.scores for team in league.teams]
    # print(team_scores)

    teams = league.teams
    schedules = [
        [opponent.owners[0]["id"] for opponent in team.schedule] for team in teams
    ]
    schedules = [team.schedule for team in teams]
    # print(schedules)
    scores_df = pd.DataFrame(team_scores, index=team_owners)

    current_week = (
        scores_df.apply(lambda row: row[row != 0.0].last_valid_index(), axis=1).max()
        + 1
    )
    print(current_week)

    team = teams[5]

    print(team.team_name)
    print(team.outcomes)
    print(team.acquisitions)


test_team_data(league)
