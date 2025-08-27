import os
import json
import pandas as pd
import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi
from st_aggrid import AgGrid, GridOptionsBuilder

# ----------------------------- #
# Authenticate with Kaggle API
# ----------------------------- #
# Get Kaggle API Key from Streamlit secrets
kaggle_username = st.secrets["kaggle"]["username"]
kaggle_api_key = st.secrets["kaggle"]["key"]

# Set the environment variables for Kaggle API
os.environ['KAGGLE_USERNAME'] = kaggle_username
os.environ['KAGGLE_KEY'] = kaggle_api_key

# Initialize the Kaggle API and authenticate
kaggle_api = KaggleApi()
kaggle_api.authenticate()
# Authentication Complete

# ----------------------------- #
# Get all active competitions
# ----------------------------- #
competitions = kaggle_api.competitions_list()

# Convert to DataFrame
competition_data = pd.DataFrame([c.__dict__ for c in competitions])

# Relevant columns to extract from the competition data
relevant_columns = [
    '_id', '_title', '_description', '_reward', '_category', 
    '_deadline', '_new_entrant_deadline', '_merger_deadline', 
    '_max_daily_submissions', '_user_has_entered', '_user_rank', 
    '_enabled_date'
]

# Create competition DataFrame with selected columns
competition_df = competition_data[relevant_columns]

# Rename columns for readability
competition_df.columns = [
    'Competition ID', 'Name', 'Description', 'Prize Money', 'Category', 
    'Deadline', 'New Entrant Deadline', 'Merger Deadline', 'Max Daily Submissions', 
    'User Has Entered', 'User Rank', 'Start Date'
]

# Convert date columns to datetime
competition_df['Deadline'] = pd.to_datetime(competition_df['Deadline'], errors='coerce')
competition_df['Start Date'] = pd.to_datetime(competition_df['Start Date'], errors='coerce')

# Clean the Prize Money column and ensure it's numeric
competition_df['Prize Money'] = competition_df['Prize Money'].str.replace('[^\d.]', '', regex=True)
competition_df['Prize Money'] = pd.to_numeric(competition_df['Prize Money'], errors='coerce')

# Format Prize Money with commas for better readability
competition_df['Prize Money'] = competition_df['Prize Money'].apply(
    lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
)

# ----------------------------- #
# Streamlit Configuration
# ----------------------------- #
st.set_page_config(page_title="Kaggle Competitions Dashboard", layout="wide")
st.title("Kaggle Competitions Dashboard")

# ----------------------------- #
# Sidebar: Filter for User Enrollment
# ----------------------------- #
with st.sidebar:
    st.subheader("Filter Competitions")
    
    # Filter by "User Has Entered"
    user_has_entered_filter = st.radio(
        "Select Competitions",
        ("All Competitions", "Competitions You've Entered"),
        index=0
    )

# ----------------------------- #
# Main Area: Displaying the Competitions Table
# ----------------------------- #
# Filter DataFrame based on "User Has Entered" field
if user_has_entered_filter == "Competitions You've Entered":
    filtered_df = competition_df[competition_df['User Has Entered'] == True].copy()
else:
    filtered_df = competition_df.copy()
filtered_df['User Has Entered'] = filtered_df['User Has Entered'].apply(lambda x: "Yes" if x else "No")

# Display filtered table of competitions
st.markdown("### Competitions")

# AgGrid for interactive table
grid_options = GridOptionsBuilder.from_dataframe(filtered_df)
grid_options.configure_default_column(groupable=True, editable=True, sortable=True, filterable=True)

# Enable pagination
grid_options.configure_pagination(paginationPageSize=10)  # Set the number of rows per page

grid_options = grid_options.build()
AgGrid(filtered_df, gridOptions=grid_options, height=400, width='100%', theme='streamlit')
