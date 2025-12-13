import streamlit as st
import requests
import pandas as pd
import time

# Configuration
API_BASE_URL = "http://localhost:5000"
REFRESH_RATE = 5 # Seconds

st.set_page_config(
    page_title="Warden Dashboard",
    page_icon="👮",
    layout="wide"
)

st.title("👮 Smart Hostel Warden Dashboard")

# Sidebar for navigation
page = st.sidebar.selectbox("Navigation", ["Active Timers", "Alerts", "Student Logs"])

def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return []

if page == "Active Timers":
    st.header("⏳ Active Library Trips")
    
    placeholder = st.empty()
    
    while True:
        data = fetch_data("active_timers")
        
        with placeholder.container():
            if data:
                df = pd.DataFrame(data)
                # Select relevant columns
                display_df = df[['student_name', 'start_time', 'expected_end_time', 'status']]
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No students currently outside.")
        
        time.sleep(REFRESH_RATE)

elif page == "Alerts":
    st.header("🚨 Late Alerts")
    
    placeholder = st.empty()
    
    while True:
        data = fetch_data("alerts")
        
        with placeholder.container():
            if data:
                df = pd.DataFrame(data)
                display_df = df[['student_name', 'expected_end_time', 'status']]
                
                # Highlight late students
                st.error(f"Total Late Students: {len(data)}")
                st.dataframe(display_df, use_container_width=True)
            else:
                st.success("No alerts. All students on time.")
        
        time.sleep(REFRESH_RATE)

elif page == "Student Logs":
    st.header("📜 All Student Logs")
    # For now, just showing active/alerts as we didn't make a full logs endpoint, 
    # but we can reuse active_timers or alerts or fetch all if we added that endpoint.
    # Let's just show a placeholder or fetch all if we add that endpoint later.
    st.info("Log history feature coming soon. (Requires /all_trips endpoint)")
