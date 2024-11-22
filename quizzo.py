import gspread
import pandas as pd

# Path to your Google API credentials file
credentials_file = 'path/to/your/credentials.json'

# Connect to Google Sheets using gspread
gc = gspread.service_account(filename=credentials_file)

# Open the Google Sheet by URL
sheet_url = "https://docs.google.com/spreadsheets/d/131-7lOU-7KsemJW_aXx1ecWNCwfub-Ziq7AeAjVAm5c/"
spreadsheet = gc.open_by_url(sheet_url)

# Select the first sheet (tab)
worksheet = spreadsheet.get_worksheet(0)

# Get all data from the worksheet
data = worksheet.get_all_records()

# Convert the data to a Pandas DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df)