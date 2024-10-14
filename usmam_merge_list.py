import pandas as pd
import re
# Provide the file paths to your Excel files
customer_file = r'C:\Users\louie.rodriguez\OneDrive - Pennoni\Desktop\repo\DeltekMapScirpts\Customer_List_by_Service_or_Misc_Charge ML.xlsx'
arcgis_file = r'C:\Users\louie.rodriguez\OneDrive - Pennoni\Desktop\repo\DeltekMapScirpts\arcgis_with_service_lines.xlsx'
property_date_file = r'C:\Users\louie.rodriguez\OneDrive - Pennoni\Desktop\repo\FantasyFootballApp\updated_arcgis_with_service_lines_processed.xlsx'

# Read the Excel files into DataFrames
customer_df = pd.read_excel(customer_file)
customer_df['Service Address'] = customer_df['Service Address'].str.replace(' KINGSCLERE RD ', ' KINGSCLERE DR ').str.replace(' DENNIS ROAD ', ' DENNIS RD ').str.replace(' BEAVER RD ', ' BEAVER AVE ').str.replace(' LANE ', ' LN ').str.replace(' LA ', ' LN ').str.replace(' STEAMBOAT STA ', ' STEAMBOAT STATION ').str.replace(' E. ', ' E ').str.replace(' W. ', ' W ').str.replace(' ST PK ', ' STREET PIKE ').str.replace(' ST  PK ', ' STREET PIKE ')

# customer_df['Address'] = customer_df['Service Address'].apply(lambda x: ' '.join(x.split()[:3]) if x.split()[0].isdigit() else x)
customer_df['Address'] = customer_df['Service Address'].apply(
    lambda x: re.split(r'\s+(?=SOUTHAMPTON|HUNTINGDON VALLEY|FEASTERVILLE|WARMINSTER|HUNTINGDON  VALLEY)', x)[0] if isinstance(x, str) else x
)
customer_df['Street'] = customer_df['Address'].apply(lambda x: ' '.join(x.split()[1:]) if isinstance(x, str) and len(x.split()) > 1 else '')

arcgis_df = pd.read_excel(arcgis_file)

arcgis_df = arcgis_df[['PARCEL_NUM', 'ADDRESS', 'Match_addr', 'USER_File_Name']]
property_date_df = pd.read_excel(property_date_file)

# Step 1: Create the Match_address column in arcgis_df from Match_addr (uppercase + Pennsylvania fix)
arcgis_df['Match_address'] = arcgis_df['Match_addr'].str.upper().str.replace(", PENNSYLVANIA,", ",PA")

arcgis_df['Match_address'] = arcgis_df['Match_address'].str.replace(',', '', n=1)

# print(arcgis_df[['ADDRESS']])
# print(customer_df[['Address']])
# print()

# Step 2: Merge customer_df and arcgis_df based on 'Service Address' and 'Match_address'
merged_df = pd.merge(customer_df, arcgis_df, how='left', left_on='Address', right_on='ADDRESS')

# Step 3: Merge the result with the property_date_df on 'PARCEL_NUM' to bring in 'Property Date'
merged_df = pd.merge(merged_df, property_date_df[['PARCEL_NUM', 'Property Date']], how='left', on='PARCEL_NUM')

# Step 4: Populate 'Meter Photo' column based on non-null values in 'USER_File_Name'
merged_df['Meter Photo'] = merged_df['USER_File_Name'].notna().map({True: 'Yes', False: 'No'})

# Step 5: Populate 'Constructed 1964 or Later' based on 'Property Date'
# Check if 'Property Date' is >= 1964 (assuming 'Property Date' is a year or can be converted to one)
merged_df['Constructed 1964 or Later'] = merged_df['Property Date'].apply(lambda x: 'Yes' if pd.notna(x) and x >= 1964 else 'No')

# Output the length of original DataFrames and the merged result
print(f"Customer DataFrame Length: {len(customer_df)}")
print(f"ArcGIS DataFrame Length: {len(arcgis_df)}")
print(f"Property Date DataFrame Length: {len(property_date_df)}")
print(f"Merged DataFrame Length: {len(merged_df)}")

output_file = r'C:\Users\louie.rodriguez\OneDrive - Pennoni\Desktop\repo\DeltekMapScirpts\usmam_merged_output.xlsx'

merged_df.to_excel(output_file, index=False)
