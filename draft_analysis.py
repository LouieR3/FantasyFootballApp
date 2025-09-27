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
    louie_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"
    prahlad_s2 = "AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4"
    la_s2 = "AEC6x9TPufDhJAV682o%2BK6c8XdanPIkD8i3F4MF%2Fgtb1A4FD9SJMNrFoDt2sVHcppQpcYUIDF7kRotFrq8u%2Bkd4W94iy%2B952I9AG4ykEF3y2YRBvm75VMpecOvj7tZiv7iZ8R2K2SEqMExArEwMg3Bnbj161G3gMS6I%2F7YOKKMPTnC1VSTWuF5JlljFfFZz5hswmCr6IMZnZCzFmy%2FnPdwymI1NZ9IOAwJVn9pnBi9FpvyzcdcyYG2NOaarBmTLqyAd3%2BEdrDEpre%2F6Cfz6c3KcwO%2FFjPBkIFDxC1szNelynxfJZCupLm%2FEFFhXdbKnBeesbbOXJg%2BDLqZU1KGdCTU0FyEKr%2BcouwUy%2BnyDCuMYUog%3D%3D"
    hannah_s2 = "AEBy%2FXPWgz4DEVTKf5Z1y9k7Lco6fLP6tO80b1nl5a1p9CBOLF0Z0AlBcStZsywrAAdgHUABmm7G9Cy8l2IJCjgEAm%2BT5NHVNFPgtfDPjT0ei81RfEzwugF1UTbYc%2FlFrpWqK9xL%2FQvSoCW5TV9H4su6ILsqHLnI4b0xzH24CIDIGKInjez5Ivt8r1wlufknwMWo%2FQ2QaJfm6VPlcma3GJ0As048W4ujzwi68E9CWOtPT%2FwEQpfqN3g8WkKdWYCES0VdWmQvSeHnphAk8vlieiBTsh3BBegGULXInpew87nuqA%3D%3D"
    leagues = [
        {"league_id": 310334683, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Pennoni Younglings"},
        {"league_id": 996930954, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "Family Fantasy"},
        {"league_id": 1118513122, "year": year, "espn_s2": louie_s2, "swid": "{4656A2AD-A939-460B-96A2-ADA939760B8B}", "name": "EBC League"},
        {"league_id": 1339704102, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "0755 Fantasy Football"},
        {"league_id": 1781851, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Game of Yards!"},
        {"league_id": 367134149, "year": year, "espn_s2": prahlad_s2, "swid": "{4C1C5213-4BB5-4243-87AC-0BCB2D637264}", "name": "Brown Munde"},
        {"league_id": 1049459, "year": year, "espn_s2": la_s2, "swid": "{ACCE4918-2F2A-4714-B49E-576D9C1F4FBB}", "name": "THE BEST OF THE BEST"},
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

# Merge LPI data with final_df_with_standings
final_df_with_standings = pd.merge(final_df_with_standings, lpi_all_df, on=["Team", "League Name", "Year"], how="left")

# Save or display as needed
print(final_df_with_standings)
final_df_with_standings.to_csv(os.path.join(drafts_folder, "Draft_Grades_with_Standings.csv"), index=False)