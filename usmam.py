import pandas as pd
import math

# Load the Excel file
file_path = 'updated_arcgis_with_service_lines.xlsx'
df = pd.read_excel(file_path)

# List of streets that require the automatic "1951-1960" assignment for SO Installation Date Range
special_streets = ["BRISTOL RD", "STEET RD", "COUNTY LINE RD", "DAVIS VILLE RD", "MAPLE AVE", 
                   "SECOND STREET PIKE", "CHURCHVILLE RD", "GRAVEL HILL RD", 
                   "BUSTLETON PIKE", "STUMP RD"]

# Function to determine the SO Installation Date Range
def get_so_installation_date_range(row):
    if row['ADDRESS'] in special_streets:
        return 'G) 1951-1960'
    else:
        return get_installation_date_range_based_on_property_date(row['Property Date'])

# Function to determine the CO Installation Date Range based solely on Property Date
def get_co_installation_date_range(row):
    return get_installation_date_range_based_on_property_date(row['Property Date'])

# Helper function to determine installation date range based on Property Date
def get_installation_date_range_based_on_property_date(property_date):
    if property_date and not math.isnan(property_date):
        property_date = int(property_date)
        if property_date < 1901:
            return 'A) Pre-1901'
        elif 1901 <= property_date <= 1910:
            return 'B) 1901-1910'
        elif 1911 <= property_date <= 1920:
            return 'C) 1911-1920'
        elif 1921 <= property_date <= 1930:
            return 'D) 1921-1930'
        elif 1931 <= property_date <= 1940:
            return 'E) 1931-1940'
        elif 1941 <= property_date <= 1950:
            return 'F) 1941-1950'
        elif 1951 <= property_date <= 1960:
            return 'G) 1951-1960'
        elif 1961 <= property_date <= 1970:
            return 'H) 1961-1970'
        elif 1971 <= property_date <= 1980:
            return 'J) 1971-1980'
        elif 1981 <= property_date <= 1990:
            return 'K) 1981-1990'
        elif 1991 <= property_date <= 2000:
            return 'L) 1991-2000'
        elif 2001 <= property_date <= 2010:
            return 'M) 2001-2010'
        elif 2011 <= property_date <= 2020:
            return 'O) 2011-2020'
        else:
            return 'P) 2021-2030'
    else:
        return None

# Apply the function to create SO Installation Date Range and CO Installation Date Range
df['SO Installation Date Range'] = df.apply(get_so_installation_date_range, axis=1)
df['CO Installation Date Range'] = df.apply(get_co_installation_date_range, axis=1)

# Function to determine Interior Contains Lead Solder
def check_lead_solder(row):
    if row['Property Date'] and not math.isnan(row['Property Date']):
        if int(row['Property Date']) > 1964:
            return 'No'
        else:
            return 'Not Sure'
    else:
        return 'Not Sure'


# Apply the function to create the Interior Contains Lead Solder column
df['Interior Contains Lead Solder'] = df.apply(check_lead_solder, axis=1)

# Save the updated dataframe to a new Excel file
output_path = 'updated_arcgis_with_service_lines_processed.xlsx'
df.to_excel(output_path, index=False)

print("Processing complete. Data saved to 'updated_arcgis_with_service_lines_processed.xlsx'")