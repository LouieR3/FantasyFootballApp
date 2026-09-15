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


def clean_all_record_columns(df):
    """
    Auto-detect and format all record columns in a dataframe.

    Looks for columns with 'Record', 'record' in the name and formats them
    to omit zero ties.

    Args:
        df: DataFrame

    Returns:
        DataFrame with all record columns formatted
    """
    df = df.copy()
    for col in df.columns:
        if 'record' in col.lower():
            df[col] = df[col].apply(format_record)
    return df
