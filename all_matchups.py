from espn_api.football import League
import pandas as pd
import os
from openpyxl import load_workbook

def get_all_matchups(leagues, years):    
    # Initialize an empty list to store all playoff data
    combined_matchups_dfs = []

    # Loop through each league
    for league_config in leagues:
        league_id = league_config['league_id']
        espn_s2 = league_config['espn_s2']
        swid = league_config['swid']
        league_name = league_config['name']

        for year in years:
            print(f"Processing league: {league_name}, year: {year}")

            # Instantiate the league object for the current year
            try:
                league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
                print(league.settings)
            except Exception as e:
                # print(f"Error initializing league {league_name} for year {year}: {e}")
                continue
            
            if year < 2025:
                weeks = league.current_week
            else:
                print("Getting weeks for current season")
                team_names = [team.team_name for team in league.teams]
                team_scores = [team.scores for team in league.teams] 
                scores_df = pd.DataFrame(team_scores, index=team_names)
                zero_week = (scores_df == 0.0).all(axis=0)
                if zero_week.any():
                    weeks = zero_week.idxmax()
                else:
                    weeks = scores_df.shape[1]
            print(weeks)
            for week in range(1, weeks + 1):
                try:
                    matchups = league.box_scores(week=week)
                except Exception as e:
                    # print(f"Error fetching box scores for league {league_name}, year {year}, week {week}: {e}")
                    continue
                print(f"Fetched {len(matchups)} matchups for week {week} of {league_name} ({year})")  
                # Prepare data for the current week's matchups
                matchup_data = []
                for matchup in matchups:
                    matchup_info = {
                        'League': league_name,
                        'Year': year,
                        'Week': week,
                        'Home Team': matchup.home_team.team_name if matchup.home_team else None,
                        'Home Score': matchup.home_score,
                        'Home Predicted Score': matchup.home_projected,
                        'Away Team': matchup.away_team.team_name if matchup.away_team else None,
                        'Away Score': matchup.away_score,
                        'Away Predicted Score': matchup.away_projected,
                    }
                    matchup_data.append(matchup_info)

                # Convert the current week's matchup data to a DataFrame
                week_df = pd.DataFrame(matchup_data)
                combined_matchups_dfs.append(week_df)
    # Concatenate all weekly DataFrames into a single DataFrame
    if combined_matchups_dfs:
        all_matchups_df = pd.concat(combined_matchups_dfs, ignore_index=True)
    else:
        all_matchups_df = pd.DataFrame()  # Return an empty DataFrame if no data was collected

    return all_matchups_df

louie_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
prahlad_s2 = "AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4"
la_s2 = "AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D"
hannah_s2 = "AEBy%2FXPWgz4DEVTKf5Z1y9k7Lco6fLP6tO80b1nl5a1p9CBOLF0Z0AlBcStZsywrAAdgHUABmm7G9Cy8l2IJCjgEAm%2BT5NHVNFPgtfDPjT0ei81RfEzwugF1UTbYc%2FlFrpWqK9xL%2FQvSoCW5TV9H4su6ILsqHLnI4b0xzH24CIDIGKInjez5Ivt8r1wlufknwMWo%2FQ2QaJfm6VPlcma3GJ0As048W4ujzwi68E9CWOtPT%2FwEQpfqN3g8WkKdWYCES0VdWmQvSeHnphAk8vlieiBTsh3BBegGULXInpew87nuqA%3D%3D"
ava_s2 = "AEBL5xTPsfrhYhP04Dc%2FHGojCvZAK7pmvEtoKwm%2FDUFjM86FeGyFUfomgi6VkRTlpDC0bXAOQyOy9UfdWQm%2FAbZUPauwvbn%2Bfn9pkW4BTpHapwqDSJyXSMWoH7GJyQjI8Oq7AF4bkD8A5Vm31unAN0dn6ar5h2YdSy7USKAbm8vH%2BVmQ3yAoT8QQ23V4mCQM7ztjkA3hkEYf%2BFfyB1ASlVb%2B0286sPBoPaaESQv45qLuCUG6883kq4SXq7PUACFpAUICO7ahS%2F06pr1Gg%2BzhO79cea6jXKNJsgRYQLQmHea7Yw%3D%3D"
matt_s2 = "AEApTMk4bKXLS%2ByFC85I7AlYVnFOTx28Qn8C5ElSPEEY3%2BV6Jn0RzRDIb1H39fmRU9ABSWxJBwDaxottGDrfteMllIgOnF6QDw%2Bv2v6ox%2FDJGV4DJav5ntyQn3oihvOstkQsXIvSGD5jFAQFTJcb6GOCe9jG0WuATob3%2BU5fi2fZdZJ%2Blpx65ty5SNBe8znFW3T52EfNFbEOrCFW13IHqmEUiO9%2BooinLTMwIhsD2Txzg7peD6bKhs%2BOQL7pqc2xE1x084MSLRZ33UZioi8aNJdJx%2FBO8BUaBy%2FB3VFUkB2S1CFUUnlY5S96e98QD9vgmLY%3D"
elle_s2 = "AECfQX9GAenUR7mbrWgFnjVxXJJEz4u%2BKEZUVBlsfc%2FnRHEmQJhqDOvGAxCjq%2BpWobEwQaiNR2L2kFAZRcIxX9y3pWjZd%2BHuV4KL0gq495A4Ve%2Fnza1Ap%2BGM5hQwgIpHqKL%2BosHEXvXVBfUxUmmX%2BG7HkNIir0lAZIX3CS68XAO6KXX5aEl%2BjUsc8pYqNAiaEiCEyLdULrUimPcog39bHlbmIuwYHXf2LsMHWUdQ1RrDGP%2BOIpKXx257vQLxnW%2FI72Eg7W%2Fg6Htwx1TpG5U9eMXEwQp0UEKHanE0YSgnTTELIw%3D%3D"
# List of league configurations
year = 2025
leagues = [
    # # Pennoni Younglings
    # {"league_id": 310334683, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Pennoni Younglings"},
    # # Family League
    # {"league_id": 996930954, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Family League"},
    # # EBC League
    # {"league_id": 1118513122, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "EBC League"},
    # # Pennoni Transportation
    # {"league_id": 1339704102, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "0755 Fantasy Football"},
    # Game of Yards
    {"league_id": 1781851, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Game of Yards!"},
    # # Brown Munde
    # {"league_id": 367134149, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Brown Munde"},
    # Turf On Grade 2.0 League
    {"league_id":1242265374, "year":year, "espn_s2":"AECbYb8WaMMCKHklAi740KXDsHbXHTaW5mI%2FLPUegrKbIb6MRovW0L4NPTBpsC%2Bc2%2Fn7UeX%2Bac0lk3KGEwyeI%2FgF9WynckxWNIfe8m8gh43s68UyfhDj5K187Fj5764WUA%2BTlCh1AF04x9xnKwwsneSvEng%2BfACneWjyu7hJy%2FOVWsHlEm3nfMbU7WbQRDBRfkPy7syz68C4pgMYN2XaU1kgd9BRj9rwrmXZCvybbezVEOEsApniBWRtx2lD3yhJnXYREAupVlIbRcd3TNBP%2F5Frfr6pnMMfUZrR9AP1m1OPGcQ0bFaZbJBoAKdWDk%2F6pJs%3D", "swid":'{4C1C5213-4BB5-4243-87AC-0BCB2D637264}', "name": "Turf On Grade 2.0"},
    # # Las League
    # {"league_id": 1049459, "year": year, "espn_s2": la_s2, "swid": "{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}", "name": "THE BEST OF THE BEST"},
    # # Hannahs League
    # {"league_id": 1399036372, "year": year, "espn_s2": hannah_s2, "swid": "{46993514-CB12-4CFA-9935-14CB122CFA5F}", "name": "Hannahs League"},
    # # Avas League
    # {"league_id": 417131856, "year": year, "espn_s2": ava_s2, "swid": "{9B611343-247D-458B-88C3-50BB33789365}", "name": "Avas League"},
    # # Matts League
    # {"league_id": 261375772, "year": year, "espn_s2": matt_s2, "swid": "{F8FBCEF4-616F-45CD-BBCE-F4616FE5CD64}", "name": "Matts League"},
    # # Elles League
    # {"league_id": 1259693145, "year": year, "espn_s2": elle_s2, "swid": "{B6F0817B-1DC0-4E29-B020-68B8E12B6931}", "name": "Matts League"},
]

years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
years = [2019, 2020, 2021, 2022, 2023, 2024]
# years = [2025]

all_matchups_df = get_all_matchups(leagues, years)
print(all_matchups_df)
try:
    current_matchups = pd.read_csv("all_matchups.csv")
    all_matchups_df = pd.concat([current_matchups, all_matchups_df]).drop_duplicates().reset_index(drop=True)
    all_matchups_df["Home Predicted Score"] = all_matchups_df["Home Predicted Score"].round(2)
    all_matchups_df["Away Predicted Score"] = all_matchups_df["Away Predicted Score"].round(2)
    all_matchups_df["Predicted Winner"] = all_matchups_df.apply(lambda row: row["Home Team"] if row["Home Predicted Score"] > row["Away Predicted Score"] else (row["Away Team"] if row["Away Predicted Score"] > row["Home Predicted Score"] else "Tie"), axis=1)
    all_matchups_df["Actual Winner"] = all_matchups_df.apply(lambda row: row["Home Team"] if row["Home Score"] > row["Away Score"] else (row["Away Team"] if row["Away Score"] > row["Home Score"] else "Tie"), axis=1)
    print("Merged with existing all_matchups.csv")
    all_matchups_df.to_csv("all_matchups.csv", index=False)
except FileNotFoundError:
    print("No existing all_matchups.csv found, creating a new one.")

# all_matchups = pd.read_csv("all_matchups.csv")
# print(all_matchups)
# all_matchups["Predicted Winner"] = all_matchups.apply(lambda row: row["Home Team"] if row["Home Predicted Score"] > row["Away Predicted Score"] else (row["Away Team"] if row["Away Predicted Score"] > row["Home Predicted Score"] else "Tie"), axis=1)
# all_matchups["Actual Winner"] = all_matchups.apply(lambda row: row["Home Team"] if row["Home Score"] > row["Away Score"] else (row["Away Team"] if row["Away Score"] > row["Home Score"] else "Tie"), axis=1)
# print(all_matchups)
# all_matchups.to_csv("all_matchups.csv", index=False)

# prediction_accuracy = (all_matchups["Predicted Winner"] == all_matchups["Actual Winner"]).mean()
# print(f"Overall Prediction Accuracy: {prediction_accuracy:.2%}")
