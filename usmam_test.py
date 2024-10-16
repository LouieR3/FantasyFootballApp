import pandas as pd

# Read the template and merged Excel files
df_template = pd.read_excel("usmam template revised.xlsx")
df_merged = pd.read_excel("usmam_merged_output.xlsx")

# Rename the 'PARCEL_NUM' column in the template to match the merged data
df_template = df_template.rename(columns={'Unique Service Line ID (Required)': 'PARCEL_NUM'})

# Inner join the template and merged data based on PARCEL_NUM
merged_df = pd.merge(df_template, df_merged, on='PARCEL_NUM', how='inner')

# Sort the merged data by PARCEL_NUM
merged_df_sorted = merged_df.sort_values(by='PARCEL_NUM').copy()

# Create a helper column to count duplicates
merged_df_sorted['duplicate_count'] = merged_df_sorted.groupby('PARCEL_NUM').cumcount() + 1

# Append suffixes to duplicate PARCEL_NUMs
merged_df_sorted['PARCEL_NUM'] = merged_df_sorted.apply(
    lambda row: f"{row['PARCEL_NUM']}_{row['duplicate_count']-1}" if row['duplicate_count'] > 1 else row['PARCEL_NUM'],
    axis=1
)

# Drop the helper column
merged_df_sorted.drop(columns=['duplicate_count'], inplace=True)

# Print the merged data or save it to a new Excel file
print(merged_df_sorted)
merged_df_sorted.to_excel("usmam_output.xlsx", index=False)