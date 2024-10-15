import pandas as pd

# File paths
template_path = r"C:\Users\louie.rodriguez\OneDrive - Pennoni\Desktop\repo\DeltekMapScirpts\usmam template revised.xlsx"
merged_output_path = r"C:\Users\louie.rodriguez\OneDrive - Pennoni\Desktop\repo\DeltekMapScirpts\usmam_merged_output.xlsx"

# Read the Excel files
df_template = pd.read_excel(template_path)
df_merged = pd.read_excel(merged_output_path)

# Sort df_merged by PARCEL_NUM
df_merged_sorted = df_merged.sort_values(by='PARCEL_NUM').copy()

# Create a helper column that counts the duplicates
df_merged_sorted['duplicate_count'] = df_merged_sorted.groupby('PARCEL_NUM').cumcount() + 1

# Append the suffix '_1', '_2', etc. to duplicates in PARCEL_NUM
df_merged_sorted['PARCEL_NUM'] = df_merged

# Filter df_template where 'Unique Service Line ID (Required)' is in 'PARCEL_NUM' of df_merged
filtered_df = df_template[df_template['Unique Service Line ID (Required)'].isin(df_merged_sorted['PARCEL_NUM'])]

# Show the first few rows of the filtered data

print(filtered_df)