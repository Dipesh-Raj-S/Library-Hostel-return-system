import streamlit as st
import pandas as pd
from dashboard.api_client import fetch_api_data

@st.fragment(run_every=30) 
def render_trip_logs():
    data = fetch_api_data("trip_logs")
    
    if not data:
        st.info("No trip logs found.")
        return

    df = pd.DataFrame(data)
    
    # Convert and format Start Time
    df['Start'] = pd.to_datetime(df['start_time']).dt.strftime("%b %d, %I:%M %p")
    
    # Convert and format End Time (handling potential nulls)
    df['End'] = pd.to_datetime(df['end_time']).dt.strftime("%b %d, %I:%M %p")
    df['End'] = df['End'].fillna("In Progress")

    # Rename columns for the UI
    display_df = df[['student_name', 'direction', 'Start', 'End', 'status']].rename(columns={
        'student_name': 'Student',
        'direction': 'Route',
        'status': 'Result'
    })

    # Add a search filter
    search = st.text_input("🔍 Search Logs", placeholder="Type student name...")
    if search:
        display_df = display_df[display_df['Student'].str.contains(search, case=False)]

    st.dataframe(display_df, width='stretch', hide_index=True)
