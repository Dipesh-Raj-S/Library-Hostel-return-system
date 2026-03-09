import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from config import Config

API_BASE_URL = Config.API_BASE_URL
REFRESH_RATE = 3

@st.cache_data(ttl=REFRESH_RATE)
def fetch_api_data(endpoint):
    try:
        res = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=2)
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        st.error(f"Backend Connection Error: {e}")
        return []

def process_timer_data(data):
    """Vectorized calculation for time remaining"""
    if not data: 
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    now = datetime.now()
    
    if 'expected_end_time' in df.columns:
        # Convert to datetime objects
        df['expected_dt'] = pd.to_datetime(df['expected_end_time'])
        df['start_dt'] = pd.to_datetime(df['start_time'])

        # Calculate remaining time (vectorized)
        diff = (df['expected_dt'] - now).dt.total_seconds()
        df['Time Remaining'] = diff.apply(
            lambda x: f"{int(x//60):02d}:{int(x%60):02d}" if x > 0 else "🚨 Passed"
        )

        # format for readability
        df['display_start'] = df['start_dt'].dt.strftime("%I:%M %p")
        df['display_expected'] = df['expected_dt'].dt.strftime("%I:%M %p")

    return df

def del_student_api(regno):
    """Helper to call the delete API"""
    try:
        res = requests.delete(f"{API_BASE_URL}/delete-student/{regno}", timeout=3)
        if res.status_code == 200:
            st.success(f"Student {regno} deleted.")
            st.session_state.confirm_delete_id = None
            st.rerun() # Refresh the UI
        else:
            st.error("Failed to delete.")
    except Exception as e:
        st.error(f"Error: {e}")

def fetch_block_limits():
    """Fetches block time limits from the DB"""
    try:
        res = requests.get(f"{API_BASE_URL}/admin/get_limits", timeout=2)
        return res.json() if res.status_code == 200 else []

    except Exception as e:
        st.error(f"Error fetching limits: {e}")
        return []

def update_block_limit(block, minutes):
    """Sends new limit to the API"""
    try:
        payload = {"block": block, "minutes": int(minutes)}
        res = requests.post(f"{API_BASE_URL}/admin/update_limit", json=payload, timeout=3)
        return res.status_code == 200

    except Exception as e:
        st.error(f"Error updating limit: {e}")
        return False