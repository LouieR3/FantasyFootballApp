import pandas as pd
import re
# Provide the file paths to your Excel files
customer_file = r'C:\Users\louie.rodriguez\OneDrive - Pennoni\Desktop\repo\DeltekMapScirpts\Customer_List_by_Service_or_Misc_Charge ML.xlsx'
arcgis_file = r'C:\Users\louie.rodriguez\OneDrive - Pennoni\Desktop\repo\DeltekMapScirpts\arcgis_with_service_lines.xlsx'
property_date_file = r'C:\Users\louie.rodriguez\OneDrive - Pennoni\Desktop\repo\FantasyFootballApp\updated_arcgis_with_service_lines_processed.xlsx'

# Read the Excel files into DataFrames
customer_df = pd.read_excel(customer_file)
customer_df['Service Address'] = customer_df['Service Address'].str.replace(' MILLCREEK RD ', ' MILL CREEK RD ').str.replace(' KINGSCLERE RD ', ' KINGSCLERE DR ').str.replace(' DENNIS ROAD ', ' DENNIS RD ').str.replace(' LANE ', ' LN ').str.replace(' LA ', ' LN ').str.replace(' STEAMBOAT STA ', ' STEAMBOAT STATION ').str.replace(' E. ', ' E ').str.replace(' W. ', ' W ').str.replace(' ST PK ', ' STREET PIKE ').str.replace(' ST  PK ', ' STREET PIKE ')
customer_df['Service Address'] = customer_df['Service Address'].str.replace(' DRIVE ', ' DR ').str.replace(' DELL COURT ', ' DELL CT ').str.replace(' GRANTHAM COURT ', ' GRANTHAM CT ').str.replace(' GRAVEL HILL STAT ', ' GRAVEL HILL STA ').str.replace(' WILLOPENN DR ', ' WILLOWPENN DR ').str.replace(' VALLEY HILL TRAIL ', ' VALLEY HILL TRL ').str.replace(' STRATHMAN DR ', ' STRATHMANN DR ').str.replace(' STEAMBOAT STAT ', ' STEAMBOAT STATION ').str.replace(' SPRINGVIEW DR ', ' SPRING VIEW DR ').str.replace(' OAK TERRACE ', ' OAK TER ')
customer_df['Service Address'] = customer_df['Service Address'].str.replace(' STUMP ROAD ', ' STUMP RD ').str.replace(' MILLCREEK CIR ', ' MILL CREEK CIR ').str.replace(' MARIAN AVE ', ' MARIAN ST ').str.replace(' LONGFIELD DR ', ' LONGFIELD RD ').str.replace(' JAKOB PLACE ', ' JAKOB PL ').str.replace(' -A ', '  ').str.replace(' -B ', '  ')

customer_df['Service Address'] = customer_df['Service Address'].apply(
    lambda x: '464 SECOND STREET PIKE' if '--' in x else x
)

# customer_df['Address'] = customer_df['Service Address'].apply(lambda x: ' '.join(x.split()[:3]) if x.split()[0].isdigit() else x)
customer_df['ADDRESS'] = customer_df['Service Address'].apply(
    lambda x: re.split(r'\s+(?=SOUTHAMPTON|HUNTINGDON VALLEY|FEASTERVILLE|WARMINSTER|HUNTINGDON  VALLEY)', x)[0] if isinstance(x, str) else x
)

bld_mapping = {
    # '598 BELMONT AVE BLD A': '101 A HAMPTON XING',
    '598 BELMONT AVE BLD B': '101 B HAMPTON XING',
    '598 BELMONT AVE BLD-C': '101 C HAMPTON XING',
    '598 BELMONT AVE BLD-D': '101 D HAMPTON XING',
    '598 BELMONT AVE BLD-E': '101 E HAMPTON XING',
    '598 BELMONT AVE BLD F': '101 F HAMPTON XING',
    '598 BELMONT AVE BLD G': '101 G HAMPTON XING',
    '598 BELMONT AVE BLD H': '101 H HAMPTON XING',
    '598 BELMONT AVE BLD I': '101 I HAMPTON XING',
    '598 BELMONT AVE BLD J': '101 J HAMPTON XING',
    '598 BELMONT AVE BLD-K': '101 K HAMPTON XING',
    '598 BELMONT AVE BLD L': '101 L HAMPTON XING',
    '598 BELMONT AVE BLD M': '101 M HAMPTON XING'
}

# Replace values in 'Service Address' based on the mapping
customer_df['ADDRESS'] = customer_df['ADDRESS'].apply(
    lambda x: bld_mapping.get(x, x)  # Directly fetch the replacement if available, else keep the original
)
customer_df['Street'] = customer_df['ADDRESS'].apply(lambda x: ' '.join(x.split()[1:]) if isinstance(x, str) and len(x.split()) > 1 else '')

arcgis_df = pd.read_excel(arcgis_file)

arcgis_df = arcgis_df[['PARCEL_NUM', 'ADDRESS', 'Match_addr', 'USER_File_Name']]
arcgis_df['File Address'] = arcgis_df['USER_File_Name'].apply(
    lambda x: re.sub(r'[_]', ' ', re.split(r'[-#]', x)[0]).strip() if pd.notnull(x) else None
)
# arcgis_df['ADDRESS'] = arcgis_df['ADDRESS'].str.replace(' INDUSTRIAL BLVD ', ' INDUSTRIAL HWY ')
# .str.replace(' E CUSHMORE ', ' CUSHMORE ')
property_date_df = pd.read_excel(property_date_file)

# Step 1: Create the Match_address column in arcgis_df from Match_addr (uppercase + Pennsylvania fix)
arcgis_df['Match_address'] = arcgis_df['Match_addr'].str.upper().str.replace(", PENNSYLVANIA,", ",PA")

arcgis_df['Match_address'] = arcgis_df['Match_address'].str.replace(',', '', n=1)


# Filter both dataframes for rows where Address equals '1141 CUSHMORE RD'
# customer_sub_df = customer_df[customer_df['ADDRESS'] == '1141 CUSHMORE RD']
# arcgis_sub_df = arcgis_df[arcgis_df['ADDRESS'] == '1141 CUSHMORE RD']

# # Print the rows where 'Address' equals '1141 CUSHMORE RD'
# print("Customer DataFrame row for '1141 CUSHMORE RD':")
# print(customer_sub_df)

# print("\nArcGIS DataFrame row for '1141 CUSHMORE RD':")
# print(arcgis_sub_df)

# # Check if the Address values are equal between the two DataFrames
# customer_address = customer_sub_df['ADDRESS'].values[0] if not customer_sub_df.empty else None
# arcgis_address = arcgis_sub_df['ADDRESS'].values[0] if not arcgis_sub_df.empty else None

# print(f"\nAre the addresses equal? {customer_address == arcgis_address}")

# # Attempt to merge the two filtered DataFrames
# merged_sub_df = pd.merge(customer_sub_df, arcgis_sub_df, how='left', left_on='ADDRESS', right_on='ADDRESS')

# # Print the merge result for these rows
# print("\nMerge result for '1141 CUSHMORE RD':")
# print(merged_sub_df)
# sfdsfd

# print(arcgis_df[['ADDRESS']])
# print(customer_df[['Address']])
# print()

# Step 2: Merge customer_df and arcgis_df based on 'Service Address' and 'Match_address'
merged_df = pd.merge(customer_df, arcgis_df, how='left', left_on='ADDRESS', right_on='ADDRESS')
# For those that couldn't merge, try merging on 'File Address'
merged_df = pd.merge(merged_df, arcgis_df, how='left', left_on='ADDRESS', right_on='File Address', suffixes=('', '_FileAddr'))


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
