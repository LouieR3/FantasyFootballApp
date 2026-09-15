"""Apply record formatting to dataframes for display.

Usage:
    from ffapp.utils.record_display import clean_record_column

    df = load_standings()
    df = clean_record_column(df, 'Current_Record')  # or 'Record' or whatever column name
    st.dataframe(df)
"""
import pandas as pd
from ffapp.utils.format_record import format_record

def clean_record_column(df, column_name):
    """
    Format a record column to omit zero ties.

    Args:
        df: DataFrame
        column_name: Name of the record column (e.g., 'Current_Record', 'Record')

    Returns:
        DataFrame with formatted record column
    """
    if column_name not in df.columns:
        return df

    df = df.copy()
    df[column_name] = df[column_name].apply(format_record)
    return df
