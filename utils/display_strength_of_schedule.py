import pandas as pd
import streamlit as st

def display_strength_of_schedule(file):
    """
    Reads the 'Wins Against Schedule' sheet from the given Excel file
    and displays it with a gradient background in Streamlit.

    Parameters:
    - file (str): Path to the Excel file.
    """
    st.header('Strength of Schedule')
    st.write("This ranks each team's schedule from hardest to easiest based on the average number of wins all other teams would have against that schedule. The Avg Wins Against Schedule column shows the hypothetical average record every team would have with that schedule over the season. Lower averages indicate a tougher slate of opponents.")
    
    # Read the Excel sheet
    df = pd.read_excel(file, sheet_name="Wins Against Schedule")
    
    # Process the DataFrame
    df = df.iloc[:, 1:]
    df.index += 1
    
    # Apply gradient styling
    df_styled = df.style.background_gradient(subset=['Wins Against Schedule'])
    
    # Display the styled DataFrame
    st.dataframe(df_styled)