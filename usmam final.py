import pandas as pd

# File paths
template_path = r"usmam template revised.xlsx"
merged_output_path = r"usmam_merged_output.xlsx"

# Read the Excel files
df_template = pd.read_excel(template_path)
df_merged = pd.read_excel(merged_output_path)
print(df_merged)

# Sort df_merged by PARCEL_NUM
df_merged_sorted = df_merged.sort_values(by='PARCEL_NUM').copy()

# Sort df_merged by PARCEL_NUM
df_merged_sorted = df_merged.sort_values(by='PARCEL_NUM').copy()

# Create a helper column that counts the duplicates
df_merged_sorted['duplicate_count'] = df_merged_sorted.groupby('PARCEL_NUM').cumcount() + 1

# Append the suffix '_1', '_2', etc. to duplicates in PARCEL_NUM
df_merged_sorted['PARCEL_NUM'] = df_merged_sorted.apply(
    lambda row: f"{row['PARCEL_NUM']}_{row['duplicate_count']-1}" if row['duplicate_count'] > 1 else row['PARCEL_NUM'], 
    axis=1
)

# Drop the helper column since it's no longer needed
df_merged_sorted.drop(columns=['duplicate_count'], inplace=True)

# # Show the first few rows to confirm the changes
# print(df_merged_sorted)
# df_merged_sorted = df_merged_sorted[df_merged_sorted['PARCEL_NUM'].str.contains('48-025-005-001', na=False)]

# # Print the filtered dataframe
# print(df_merged_sorted[['PARCEL_NUM', 'Match_addr', 'Account Number']])

# Filter df_template where 'Unique Service Line ID (Required)' is in 'PARCEL_NUM' of df_merged
filtered_df = df_template[df_template['Unique Service Line ID (Required)'].isin(df_merged['PARCEL_NUM'])]

# Show the first few rows of the filtered data
print(filtered_df)