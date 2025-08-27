import pandas as pd
import os
import glob

# Path to the drafts folder
drafts_folder = "drafts"

# Initialize an empty list to store dataframes
dataframes = []

# Function to calculate letter grade based on average draft grade
def calculate_letter_grade(avg_grade):
    if avg_grade >= 90:
        return "A+"
    elif avg_grade >= 85:
        return "A"
    elif avg_grade >= 80:
        return "A-"
    elif avg_grade >= 75:
        return "B+"
    elif avg_grade >= 70:
        return "B"
    elif avg_grade >= 65:
        return "B-"
    elif avg_grade >= 60:
        return "C+"
    elif avg_grade >= 55:
        return "C"
    elif avg_grade >= 50:
        return "C-"
    elif avg_grade >= 45:
        return "D+"
    elif avg_grade >= 40:
        return "D"
    elif avg_grade >= 35:
        return "D-"
    else:
        return "F"


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

import pandas as pd
import os

# Path to the drafts folder
drafts_folder = "drafts"

# Function to determine final standings based on the Playoff Results sheet
def determine_final_standings(league_name, year):
    # Construct the file path for the league's Excel file
    file_path = os.path.join(drafts_folder, f"{league_name} {year}.xlsx")
    
    try:
        # Read the Playoff Results sheet
        playoff_results = pd.read_excel(file_path, sheet_name="Playoff Results")
        
        # Extract the winners from each round
        standings = []
        for round_name in ["Championship", "Semi Final", "Quarter Final"]:
            round_results = playoff_results[playoff_results["Round"] == round_name]
            for _, row in round_results.iterrows():
                if round_name == "Championship":
                    standings.append({"Team": row["Winner"], "Standing": "Champion"})
                elif round_name == "Semi Final":
                    standings.append({"Team": row["Winner"], "Standing": "2nd"})
                elif round_name == "Quarter Final":
                    standings.append({"Team": row["Winner"], "Standing": "3rd"})
        
        # Convert standings to a DataFrame
        standings_df = pd.DataFrame(standings)
        
        # Add teams that didn't make playoffs
        all_teams = playoff_results["Team 1"].dropna().unique().tolist() + playoff_results["Team 2"].dropna().unique().tolist()
        all_teams = list(set(all_teams))  # Remove duplicates
        for team in all_teams:
            if team not in standings_df["Team"].values:
                standings_df = pd.concat([standings_df, pd.DataFrame([{"Team": team, "Standing": "Didn't Make Playoffs"}])], ignore_index=True)
        
        # Add the league name and year
        standings_df["League Name"] = league_name
        standings_df["Year"] = year
        
        return standings_df
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return pd.DataFrame()

# Example usage
# Assuming `final_df` contains the aggregated draft grades with League Name and Year columns
final_standings = []
for _, row in final_df.iterrows():
    league_name = row["League Name"]
    year = league_name.split()[-1]  # Extract the year from the league name
    league_name = " ".join(league_name.split()[:-1])  # Extract the league name without the year
    
    standings_df = determine_final_standings(league_name, year)
    final_standings.append(standings_df)

# Combine all standings into a single DataFrame
final_standings_df = pd.concat(final_standings, ignore_index=True)

# Save the final standings to a CSV file
output_path = os.path.join(drafts_folder, "Final_Standings.csv")
final_standings_df.to_csv(output_path, index=False)

# Display the final standings
print(final_standings_df)