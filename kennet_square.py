from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd
import re

# Load the Excel file into a DataFrame
xlsx_df = pd.read_excel("Lead Service Line- Residential.xlsx")
xlsx_df = xlsx_df.dropna(subset=['Location Id'])


# Connect to ArcGIS Online (public access, no authentication needed)
gis = GIS()

# Access the Feature Layer
url = "https://services.arcgis.com/G4S1dGvn7PIgYd6Y/ArcGIS/rest/services/Parcels_owners/FeatureServer/0"
layer = FeatureLayer(url)

# Define the query with multiple MUNI values and select specific columns
query = layer.query(where="(MUNI = 3 OR MUNI = 61 OR MUNI = 62)", 
                    out_fields="UPI, PIN_MAP, MUNI, LOC_ADDRESS, OWN1, OWN2, ADDR1, ADDR2, ZIP1, LEGAL1, LEGAL2, BOOK, PAGE, LOT")

# Convert the query result to a DataFrame and filter only the needed columns
arcgis_df = query.sdf[["UPI", "PIN_MAP", "LOC_ADDRESS", "OWN1", "OWN2", "ADDR1", "ADDR2", "ZIP1"]]

# Clean Property Location by removing text within parentheses and taking the text before any '-'
def clean_address(address):
    # Check if address is null
    if pd.isna(address):
        return address  # Leave as is or return "" if you'd prefer an empty string
    # Remove anything in parentheses
    address = re.sub(r'\(.*?\)', '', address).strip().replace("  ", " ")

    # Split on '-' and take only the first part
    return address.split('-')[0].strip()

xlsx_df["Property Location"] = xlsx_df["Property Location"].apply(clean_address)
xlsx_df["Property Location"] = (
    xlsx_df["Property Location"]
    .str.replace(" CRT", " CT", regex=False)
    .str.replace(" MEADOW CREEK", " MEADOWCREEK", regex=False)
    .str.replace(" LN", " LA", regex=False)
    .str.replace(" WAY", " WY", regex=False)
    .str.replace(" HARVEY CIR", " HARVEY CI", regex=False)
    .str.replace(" AVE", " AV", regex=False)
    .str.replace("HADLEYS MILL RUN", "HADLEYS MILL RN", regex=False)
)
xlsx_df['Block/Lot/Qual'] = xlsx_df['Block/Lot/Qual'].str.rstrip('.')

# Filter to show rows with '--' in Block/Lot/Qual before cleaning
contains_double_hyphen = xlsx_df[xlsx_df["Block/Lot/Qual"].str.contains('--', na=False)]

# Define a function to clean Block/Lot/Qual values
def clean_block_lot_qual(value):
    if pd.isna(value):
        return value  # Leave as is if it's null
    # Remove trailing periods
    value = value.rstrip('.')
    # Replace multiple hyphens with a single one
    value = re.sub(r'-+', '-', value)
    # Replace .- with -
    value = value.replace('.-', '-')
    value = value.replace('.01D', '1D')
    return value
# Apply the cleaning function
xlsx_df["Block/Lot/Qual"] = xlsx_df["Block/Lot/Qual"].apply(clean_block_lot_qual)

# Check again after cleaning
contains_double_hyphen_after = xlsx_df[xlsx_df["Block/Lot/Qual"].str.contains('--', na=False)]

# Filter and print rows in arcgis_df where LOC_ADDRESS contains "627 MAGNOLIA"
# arcgis_magnolia = arcgis_df[arcgis_df["LOC_ADDRESS"].str.contains("411 HESSIAN", case=False, na=False)]
# print("Rows in arcgis_df with '411 HESSIAN' in LOC_ADDRESS:")
# print(arcgis_magnolia)
# # Filter and print rows in xlsx_df where Property Location contains "627 MAGNOLIA"
# xlsx_magnolia = xlsx_df[xlsx_df["Property Location"].str.contains("411 HESSIAN", case=False, na=False)]
# print("\nRows in xlsx_df with '411 HESSIAN' in Property Location:")
# print(xlsx_magnolia)



# Create the result DataFrame
result_df = xlsx_df.copy()  # Efficiently create a copy

# First, merge on Block/Lot/Qual to UPI
matched_by_blocklotqual = result_df[result_df['Block/Lot/Qual'].notna()].merge(
    arcgis_df,
    how='left',
    left_on='Block/Lot/Qual',
    right_on='UPI'
)
print(matched_by_blocklotqual)
print("====")
print()
# Merge matched data back into result_df, keeping only necessary columns with suffixes
result_df = result_df.merge(
    matched_by_blocklotqual,
    how='left',
    on='Utm Id',
    suffixes=('', '_matched')
)

# Identify rows where UPI is still NaN (unmatched rows) for the second pass
unmatched_df = result_df[result_df['UPI'].isna()]

print(unmatched_df)
print()
# Second merge: match Property Location to LOC_ADDRESS for unmatched rows
unmatched_df = unmatched_df.merge(
    arcgis_df,
    how='left',
    left_on='Property Location',
    right_on='LOC_ADDRESS',
    suffixes=('', '_arcgis')
)
print(unmatched_df)
print(unmatched_df.columns)
print("============================")
print()

# Add columns from the second merge back into result_df with appropriate suffixes
result_df = result_df.merge(
    unmatched_df,
    how='left',
    on='Utm Id'
)
print(result_df)
print(result_df.columns)
print()

# Fill in UPI and LOC_ADDRESS where new matches were found
result_df['UPI'].fillna(result_df['UPI_arcgis'], inplace=True)
result_df['LOC_ADDRESS'].fillna(result_df['LOC_ADDRESS_arcgis'], inplace=True)

# Drop temporary columns used for merging to keep result_df clean
result_df.drop(columns=['UPI_arcgis', 'LOC_ADDRESS_arcgis'], inplace=True)

print("========")
print("result_df")
print(result_df[["Block/Lot/Qual", "UPI", "Property Location", "LOC_ADDRESS"]])
print()
# Fill remaining unmatched columns with NaN
result_df = result_df.fillna(pd.NA)

# Rename columns and combine address fields as before
result_df.rename(columns={"OWN1": "Owner 1", "OWN2": "Owner 2"}, inplace=True)
result_df["Owner Address"] = result_df["ADDR1"].fillna('') + " " + result_df["ADDR2"].fillna('') + " " + result_df["ZIP1"].fillna('')
result_df.drop(columns=["ADDR1", "ADDR2", "ZIP1", "LOC_ADDRESS"], inplace=True)

# Sort the DataFrame by 'Utm Id'
result_df = result_df.sort_values(by='Utm Id')

# Drop duplicates, keeping the last occurrence
result_df = result_df.drop_duplicates(subset='Utm Id', keep='last')

print(result_df)

result_df.to_excel("kennet_square.xlsx", index=False)