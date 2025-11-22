import pandas as pd
from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
# import xlsxwriter
from itertools import combinations
import itertools
import math
import numpy as np
import random
import openpyxl
from monte_carlo_odds import (
    calculate_team_stats, 
    simulate_remaining_season, 
    create_summary_dataframes,
    add_weekly_analysis_to_main,
    retrieve_odds_dfs
)


start_time = time.time()

louie_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
prahlad_s2 = "AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4"
la_s2 = "AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D"
hannah_s2 = "AEBy%2FXPWgz4DEVTKf5Z1y9k7Lco6fLP6tO80b1nl5a1p9CBOLF0Z0AlBcStZsywrAAdgHUABmm7G9Cy8l2IJCjgEAm%2BT5NHVNFPgtfDPjT0ei81RfEzwugF1UTbYc%2FlFrpWqK9xL%2FQvSoCW5TV9H4su6ILsqHLnI4b0xzH24CIDIGKInjez5Ivt8r1wlufknwMWo%2FQ2QaJfm6VPlcma3GJ0As048W4ujzwi68E9CWOtPT%2FwEQpfqN3g8WkKdWYCES0VdWmQvSeHnphAk8vlieiBTsh3BBegGULXInpew87nuqA%3D%3D"
ava_s2 = "AEBL5xTPsfrhYhP04Dc%2FHGojCvZAK7pmvEtoKwm%2FDUFjM86FeGyFUfomgi6VkRTlpDC0bXAOQyOy9UfdWQm%2FAbZUPauwvbn%2Bfn9pkW4BTpHapwqDSJyXSMWoH7GJyQjI8Oq7AF4bkD8A5Vm31unAN0dn6ar5h2YdSy7USKAbm8vH%2BVmQ3yAoT8QQ23V4mCQM7ztjkA3hkEYf%2BFfyB1ASlVb%2B0286sPBoPaaESQv45qLuCUG6883kq4SXq7PUACFpAUICO7ahS%2F06pr1Gg%2BzhO79cea6jXKNJsgRYQLQmHea7Yw%3D%3D"
matt_s2 = "AEApTMk4bKXLS%2ByFC85I7AlYVnFOTx28Qn8C5ElSPEEY3%2BV6Jn0RzRDIb1H39fmRU9ABSWxJBwDaxottGDrfteMllIgOnF6QDw%2Bv2v6ox%2FDJGV4DJav5ntyQn3oihvOstkQsXIvSGD5jFAQFTJcb6GOCe9jG0WuATob3%2BU5fi2fZdZJ%2Blpx65ty5SNBe8znFW3T52EfNFbEOrCFW13IHqmEUiO9%2BooinLTMwIhsD2Txzg7peD6bKhs%2BOQL7pqc2xE1x084MSLRZ33UZioi8aNJdJx%2FBO8BUaBy%2FB3VFUkB2S1CFUUnlY5S96e98QD9vgmLY%3D"
elle_s2 = "AECfQX9GAenUR7mbrWgFnjVxXJJEz4u%2BKEZUVBlsfc%2FnRHEmQJhqDOvGAxCjq%2BpWobEwQaiNR2L2kFAZRcIxX9y3pWjZd%2BHuV4KL0gq495A4Ve%2Fnza1Ap%2BGM5hQwgIpHqKL%2BosHEXvXVBfUxUmmX%2BG7HkNIir0lAZIX3CS68XAO6KXX5aEl%2BjUsc8pYqNAiaEiCEyLdULrUimPcog39bHlbmIuwYHXf2LsMHWUdQ1RrDGP%2BOIpKXx257vQLxnW%2FI72Eg7W%2Fg6Htwx1TpG5U9eMXEwQp0UEKHanE0YSgnTTELIw%3D%3D"
dave_s2 = "AEATfV13bzJs4HpWGw5IMP0Hoh9yD7FJ%2FWPkdfAC8pOMFdD9RT8wgdt%2BoACXFYuTYIBcpKSl1vPlVip8kDK8mqBlSh2ulGveo35%2BZMYhANuNP%2FfZCdttmqnrzzYjA7UedbVQfVpUcNgwrTD6Xn0dkyHQyDoOqrJbGGFbDkz%2F%2B8Tlas275RhFZ4jXhdZNgddmK0qiYgZABl13Ou8Gv2zzhgk77Pbf%2FhKvWxcN20pZHpN58x%2FwUAajmiZgEl2Nt4gbojRhLGTRqGBqYQ7C%2BqCpBw5KImrN72sLGJuqi5%2BgJHgaIw%3D%3D"
ayush_s2 = "AEAVdXHc27USh4ku3cV29OmfzPAysyGlSqIQuU0%2FX2OR2yXn4P51Fbq0rmxpRhWFjwLehTCw6uZ7a6RhnamZ2CKnsleRO0UZ9bnpbNSMC9NR%2BvLkrqEniQKURmJFcf9NnF9ee36YYaHJwKdzxzpcHJfuV8MXumVPBRhOJdLWRL4RsnxcDa0R8kztme9xMvULhkxtIeK9nZWI%2FcKD1lp%2B%2F2CqmeOAx5ddZssKEUT3l%2BORqAyEkH%2BvhicLfAzrLNsKQUpp%2FBuHavXfKvFSX%2BbE7DyBjC7XvvOjezSdMCpiHh0Ys5SdTeGXlPSN%2F4Tq%2FFZQJVs%3D"
# List of league configurations
year = 2025
leagues = [
    # Pennoni Younglings
    {"league_id": 310334683, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Pennoni Younglings"},
    # Family League
    {"league_id": 996930954, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Family League"},
    # EBC League
    {"league_id": 1118513122, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "EBC League"},
    # Pennoni Transportation
    {"league_id": 1339704102, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "0755 Fantasy Football"},
    # Game of Yards
    {"league_id": 1781851, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Game of Yards!"},
    # Brown Munde
    {"league_id": 367134149, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Brown Munde"},
    # Turf On Grade 2.0 League
    # {"league_id":1242265374, "year":year, "espn_s2":"AECbYb8WaMMCKHklAi740KXDsHbXHTaW5mI%2FLPUegrKbIb6MRovW0L4NPTBpsC%2Bc2%2Fn7UeX%2Bac0lk3KGEwyeI%2FgF9WynckxWNIfe8m8gh43s68UyfhDj5K187Fj5764WUA%2BTlCh1AF04x9xnKwwsneSvEng%2BfACneWjyu7hJy%2FOVWsHlEm3nfMbU7WbQRDBRfkPy7syz68C4pgMYN2XaU1kgd9BRj9rwrmXZCvybbezVEOEsApniBWRtx2lD3yhJnXYREAupVlIbRcd3TNBP%2F5Frfr6pnMMfUZrR9AP1m1OPGcQ0bFaZbJBoAKdWDk%2F6pJs%3D", "swid":'{4C1C5213-4BB5-4243-87AC-0BCB2D637264}', "name": "Turf On Grade 2.0"},
    # Las League
    {"league_id": 1049459, "year": year, "espn_s2": la_s2, "swid": "{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}", "name": "THE BEST OF THE BEST"},
    # Hannahs League
    {"league_id": 1399036372, "year": year, "espn_s2": hannah_s2, "swid": "{46993514-CB12-4CFA-9935-14CB122CFA5F}", "name": "The Girl's Room 💞🏈"},
    # Avas League
    {"league_id": 417131856, "year": year, "espn_s2": ava_s2, "swid": "{9B611343-247D-458B-88C3-50BB33789365}", "name": "Philly Extra Special"},
    # Matts League
    {"league_id": 261375772, "year": year, "espn_s2": matt_s2, "swid": "{F8FBCEF4-616F-45CD-BBCE-F4616FE5CD64}", "name": "BP- Loudoun 2025"},
    # Elles League
    {"league_id": 1259693145, "year": year, "espn_s2": elle_s2, "swid": "{B6F0817B-1DC0-4E29-B020-68B8E12B6931}", "name": "Operators Football League"},
    # Dave Work League
    {"league_id": 1675186799, "year": year, "espn_s2": dave_s2, "swid": "{AAD245A4-298A-4362-A70B-5F838E0D6F64}", "name": "OnP Fantasy"},
    # Dave Friend League
    {"league_id": 1924463077, "year": year, "espn_s2": dave_s2, "swid": "{AAD245A4-298A-4362-A70B-5F838E0D6F64}", "name": "The Mike Daisy Sports IQ League"},
    # Ayush League
    {"league_id": 558148583, "year": year, "espn_s2": ayush_s2, "swid": "{668E3A23-4B03-4D9E-9804-4C9D479F4E8F}", "name": "Ross' Fantasy League"},
]

def create_betting_odds(leagues, year):
    # Loop through each league configuration
    for league_config in leagues:
        try:
            league = League(
                league_id=league_config["league_id"],
                year=league_config["year"],
                espn_s2=league_config["espn_s2"],
                swid=league_config["swid"],
            )
            print(f"Processing league: {league_config['name']}")
        
            settings = league.settings

            leagueName = settings.name.replace(" 22/23", "")
            fileName = leagueName + " " + str(year) + " Betting Odds"
            file = leagueName + ".xlsx"

            # team_owners = [team.owners for team in league.teams]
            team_names = [team.team_name for team in league.teams]
            team_scores = [team.scores for team in league.teams] 
            team_scores_x = [team.scores for team in league.teams] 
            schedules = []
            for team in league.teams:
                schedule = [opponent.team_name for opponent in team.schedule]
                schedules.append(schedule)


            # Store data in DataFrames 
            scores_df = pd.DataFrame(team_scores, index=team_names)

            # Calculate current week
            zero_week = (scores_df == 0.0).all(axis=0)
            if zero_week.any():
                current_week = zero_week.idxmax() +1
            else:
                current_week = scores_df.shape[1]
            schedules_df = pd.DataFrame(schedules, index=team_names)
            records_df = pd.DataFrame(index=team_names, columns=team_names)

            # Fill diagonal with team names
            records_df.fillna('', inplace=True) 

            teams= league.teams
            reg_season_count = settings.reg_season_count
            num_playoff_teams = settings.playoff_team_count
            # Then use them step by step in your existing code
            team_stats = calculate_team_stats(teams, scores_df, current_week, reg_season_count)
            final_records, playoff_makes, last_place_finishes, seed_counts = simulate_remaining_season(
                teams, team_stats, current_week, reg_season_count, num_playoff_teams
            )
            summary_df, seed_df = create_summary_dataframes(
                team_stats, final_records, playoff_makes, last_place_finishes, seed_counts, num_playoff_teams, 1000, len(teams), reg_season_count
            )
            summary_df = (
                summary_df.sort_values('Playoff_Chance_Pct', ascending=False)
                .reset_index(drop=True)
                .set_index("Team")
            )
            num_teams = len(teams)

            make_playoff_odds_df, first_place_odds_df, last_place_odds_df = retrieve_odds_dfs(seed_df, num_teams, team_stats)

            writer = pd.ExcelWriter(f"odds/{fileName}.xlsx", engine='xlsxwriter')
            make_playoff_odds_df.to_excel(writer, sheet_name='Make Playoff Odds')
            first_place_odds_df.to_excel(writer, sheet_name='First Place Odds')
            last_place_odds_df.to_excel(writer, sheet_name='Last Place Odds')
            writer.close()
            # --------------------------------------------------------------------------------------
        except Exception as e:
            # Handle errors, such as the league not existing
            print(f"Error: League '{league_config['name']}' for year {league_config['year']} does not exist or could not be loaded.")
            print(f"Details: {str(e)}")
            continue  # Move to the next league

print("--- %s seconds ---" % (time.time() - start_time))