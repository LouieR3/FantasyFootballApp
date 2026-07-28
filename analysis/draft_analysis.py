import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from credentials import CRED
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
    
    espn_s2 = CRED["louie_s2"]

    louie_s2 = CRED["louie_s2"]
    prahlad_s2 = CRED["prahlad_s2"]
    la_s2 = CRED["la_s2"]
    hannah_s2 = CRED["hannah_s2"]
    ava_s2 = CRED["ava_s2"]
    matt_s2 = CRED["matt_s2"]
    elle_s2 = CRED["elle_s2"]
    dave_s2 = CRED["dave_s2"]
    ayush_s2 = CRED["ayush_s2"]
    # List of league configurations
    year = 2025

    # List of league configurations

    leagues = [
        # Pennoni Younglings
        {"league_id": 310334683, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "Pennoni Younglings"},
        # Family League
        {"league_id": 996930954, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "Family League"},
        # EBC League
        {"league_id": 1118513122, "year": year, "espn_s2": louie_s2, "swid": CRED["louie_swid"], "name": "EBC League"},
        # Pennoni Transportation
        {"league_id": 1339704102, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "0755 Fantasy Football"},
        # Game of Yards
        {"league_id": 1781851, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "Game of Yards!"},
        # Brown Munde
        {"league_id": 367134149, "year": year, "espn_s2": prahlad_s2, "swid": CRED["prahlad_swid"], "name": "Brown Munde"},
        # Turf On Grade 2.0 League
        # {"league_id":1242265374, "year":year, "espn_s2":CRED["turf_s2"], "swid":CRED["prahlad_swid"], "name": "Turf On Grade 2.0"},
        # Las League
        {"league_id": 1049459, "year": year, "espn_s2": la_s2, "swid": CRED["la_swid"], "name": "THE BEST OF THE BEST"},
        # Hannahs League
        {"league_id": 1399036372, "year": year, "espn_s2": hannah_s2, "swid": CRED["hannah_swid"], "name": "The Girl's Room 💞🏈"},
        # Avas League
        {"league_id": 417131856, "year": year, "espn_s2": ava_s2, "swid": CRED["ava_swid"], "name": "Philly Extra Special"},
        # Matts League
        {"league_id": 261375772, "year": year, "espn_s2": matt_s2, "swid": CRED["matt_swid"], "name": "BP- Loudoun 2025"},
        # Elles League
        {"league_id": 1259693145, "year": year, "espn_s2": elle_s2, "swid": CRED["elle_swid"], "name": "Operators Football League"},
        # Dave Work League
        {"league_id": 1675186799, "year": year, "espn_s2": dave_s2, "swid": CRED["dave_swid"], "name": "OnP Fantasy"},
        # Dave Friend League
        {"league_id": 1924463077, "year": year, "espn_s2": dave_s2, "swid": CRED["dave_swid"], "name": "The Mike Daisy Sports IQ League"},
        # Ayush League
        {"league_id": 558148583, "year": year, "espn_s2": ayush_s2, "swid": CRED["ayush_swid"], "name": "Ross' Fantasy League"},
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