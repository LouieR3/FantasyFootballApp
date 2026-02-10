import pandas as pd
import os
import glob

from espn_api.football import League
# Path to the drafts folder
drafts_folder = "drafts"
leagues_folder = "leagues"

# Initialize an empty list to store dataframes
dataframes = []

# Function to calculate letter grade based on average draft grade
def calculate_letter_grade(grade):
    if grade >= 97: return "A+"
    elif grade >= 93: return "A"
    elif grade >= 90: return "A-"
    elif grade >= 87: return "B+"
    elif grade >= 83: return "B"
    elif grade >= 80: return "B-"
    elif grade >= 77: return "C+"
    elif grade >= 73: return "C"
    elif grade >= 70: return "C-"
    elif grade >= 67: return "D+"
    elif grade >= 63: return "D"
    elif grade >= 60: return "D-"
    else: return "F-"


drafts_folder = "drafts"
print(os.listdir(drafts_folder))
# Iterate through all files in the drafts folder
for file in os.listdir(drafts_folder):
    print(file)
    if "Draft Results" in file and file.endswith(".csv"):
        # Read the file
        file_path = os.path.join(drafts_folder, file)
        df = pd.read_csv(file_path)

        # Extract league name from the file name
        league_name = file.replace(" Draft Results", "").replace(".csv", "")

        # Group by Team and calculate the average Draft Grade
        team_grades = df.groupby("Team")["Draft Grade"].mean().reset_index()

        # Calculate the letter grade for each team
        team_grades["Letter Grade"] = team_grades["Draft Grade"].apply(calculate_letter_grade)
        
        # Add the League Name column
        team_grades["League Name"] = league_name

        # Append the dataframe to the list
        dataframes.append(team_grades)

# Combine all dataframes into a single dataframe
final_df = pd.concat(dataframes, ignore_index=True)
# Sort the final dataframe by Draft Grade in descending order
final_df = final_df.sort_values(by="Draft Grade", ascending=False)

# Display the aggregated dataframe
print(final_df)

# Optionally, save the final dataframe to a new Excel file
output_path = os.path.join(drafts_folder, "Aggregated_Draft_Grades.csv")
final_df.to_csv(output_path, index=False)

# Path to the drafts folder
drafts_folder = "drafts"

# Function to determine final standings based on the Playoff Results sheet
def determine_final_standings(league_name, year):
    year = int(year)
    
    espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"

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

    # List of league configurations

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
    # Find the league config by name and year
    league_config = next((l for l in leagues if l["name"] == league_name and l["year"] == year), None)
    print(league_config)
    if not league_config:
        print(f"League config not found for {league_name} {year}")
        return pd.DataFrame()
    league = League(
        league_id=league_config["league_id"],
        year=league_config["year"],
        espn_s2=league_config["espn_s2"],
        swid=league_config["swid"],
    )
    pr = league.standings()
    standings = [
        {
            "Team": team.team_name,
            "Standing": team.final_standing,
            "Points For": team.points_for,
            "Points Against": team.points_against,
            "Record": f"{team.wins}-{team.losses}-{team.ties}"
        }
        for team in pr
    ]
    standings_df = pd.DataFrame(standings)
    print(standings_df)
    standings_df["League Name"] = league_name
    standings_df["Year"] = year
    return standings_df

# Get unique league names (with year) from final_df
unique_leagues = final_df["League Name"].unique()

# Collect all standings for each league
all_standings = []
for league_name_with_year in unique_leagues:
    # Split out year and league name
    parts = league_name_with_year.split()
    year = int(parts[-1])
    league_name = " ".join(parts[:-1])
    standings_df = determine_final_standings(league_name, year)
    # Recombine league name and year for merging
    standings_df["League Name"] = league_name_with_year
    all_standings.append(standings_df)

# Combine all standings into one DataFrame
standings_all_df = pd.concat(all_standings, ignore_index=True)

# Merge standings onto final_df by Team and League Name
# final_df['League Name'] = final_df['League Name'].apply(lambda x: " ".join(x.split()[:-1]))  # Remove year from League Name
final_df_with_standings = pd.merge(final_df, standings_all_df, on=["Team", "League Name"], how="left")
final_df_with_standings['Draft Grade'] = final_df_with_standings['Draft Grade'].round(2)
final_df_with_standings['League Name'] = final_df_with_standings['League Name'].apply(lambda x: " ".join(x.split()[:-1]))  # Remove year from League Name
final_df_with_standings['Points For'] = final_df_with_standings['Points For'].round(2)
final_df_with_standings['Points Against'] = final_df_with_standings['Points Against'].round(2)

# Process the Louie Power Index (LPI) sheet for each league file
lpi_dataframes = []

for file in os.listdir(leagues_folder):
    if file.endswith(".xlsx"):
        # Extract league name and year from the file name
        league_name_with_year = file.replace(".xlsx", "")
        parts = league_name_with_year.split()
        year = int(parts[-1])
        league_name = " ".join(parts[:-1])

        # Read the Louie Power Index sheet
        file_path = os.path.join(leagues_folder, file)
        try:
            lpi_df = pd.read_excel(file_path, sheet_name="Louie Power Index")
            lpi_df.rename(columns={'Louie Power Index (LPI)': 'LPI'}, inplace=True)
            lpi_df = lpi_df[['Teams', 'LPI']]  # Keep only relevant columns
            lpi_df.rename(columns={'Teams': 'Team'}, inplace=True)

            # Add League Name and Year columns
            lpi_df['League Name'] = league_name
            lpi_df['Year'] = year

            # Append to the list of dataframes
            lpi_dataframes.append(lpi_df)
        except Exception as e:
            print(f"Error reading LPI sheet for {file}: {e}")

# Combine all LPI dataframes into one
lpi_all_df = pd.concat(lpi_dataframes, ignore_index=True)

# # Merge LPI data with final_df_with_standings
# final_df_with_standings = pd.merge(final_df_with_standings, lpi_all_df, on=["Team", "League Name", "Year"], how="left")

# Merge LPI data with final_df_with_standings
final_df_with_standings = pd.merge(final_df_with_standings, lpi_all_df, on=["Team", "League Name", "Year"], how="left")

# Use combine_first to preserve existing data
final_df_with_standings = final_df_with_standings.combine_first(final_df)

# Save or display as needed
print(final_df_with_standings)
final_df_with_standings.to_csv(os.path.join(drafts_folder, "Draft_Grades_with_Standings.csv"), index=False)