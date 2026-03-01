import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
from config import Config

# Configuration
API_BASE_URL = Config.API_BASE_URL
REFRESH_RATE = 3  # Seconds

st.set_page_config(
    page_title="Warden Dashboard",
    page_icon="👮",
    layout="wide"
)

# Helper for API calls
@st.cache_data(ttl=REFRESH_RATE)
def fetch_api_data(endpoint):
    # Cached API fetcher
    try:
        res = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=2)
        if res.status_code == 200:
            return res.json()
        return []
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
        df['expected_dt'] = pd.to_datetime(df['expected_end_time'])
        diff = (df['expected_dt'] - now).dt.total_seconds()
        
        # Vectorized string formatting: MM:SS or "Passed"
        df['Time Remaining'] = diff.apply(
            lambda x: f"{int(x//60):02d}:{int(x%60):02d}" if x > 0 else "🚨 Passed"
        )
    return df


@st.fragment(run_every=REFRESH_RATE)
def render_active_timers():
    data = fetch_api_data("active_timers")
    df = process_timer_data(data)

    if df.empty:
        st.info("No students currently moving.")
        return

    col1, col2 = st.columns(2)
    directions = {
        "Hostel -> Library": col1,
        "Library -> Hostel": col2
    }

    for direction, col in directions.items():
        with col:
            st.subheader(f"➡️ {direction}")
            subset = df[df['direction'] == direction]
            if subset.empty:
                st.caption("No movements in this direction.")
            else:
                for _, row in subset.iterrows():
                    # Color indicator for late students
                    label = f"{row['student_name']} | {row['Time Remaining']}"
                    with st.expander(label):
                        c1, c2 = st.columns(2)
                        c1.markdown(f"**Start:** {row['start_time']}")
                        c1.markdown(f"**Expected:** {row['expected_end_time']}")
                        c2.markdown(f"**Status:** {row['status']}")
                        c2.markdown(f"**Block:** {row['student_block']}")

@st.fragment(run_every=REFRESH_RATE)
def render_alerts():
    data = fetch_api_data("alerts")
    if data:
        st.error(f"Total Late Students: {len(data)}")
        st.dataframe(pd.DataFrame(data)[['student_name', 'expected_end_time', 'status']], width='stretch', hide_index=True)
    else:
        st.success("✅ All students on time.")

def del_student(regno):
    """Helper to call the delete API"""
    try:
        res = requests.delete(f"{API_BASE_URL}/delete-student/{regno}", timeout=3)
        if res.status_code == 200:
            st.success(f"Student {regno} deleted successfully!")
            st.rerun() # Refresh the UI
        else:
            st.error("Failed to delete student.")
    except Exception as e:
        st.error(f"Error: {e}")

@st.fragment(run_every=30) 
def render_registration_table():
    data = fetch_api_data("get_encodings")
    if not data:
        st.info("No students registered.")
        return

    # Convert to list for easier iteration
    rows = []
    for sid, info in data.items():
        rows.append({
            "Name": info["name"],
            "Block": info["block"],
            "Reg No": info["reg_no"]
        })
    
    # Header Row
    cols = st.columns([3, 2, 2, 1])
    cols[0].write("**Name**")
    cols[1].write("**Block**")
    cols[2].write("**Reg No**")
    cols[3].write("**Action**")
    st.divider()

    # Data Rows
    for row in rows:
        cols = st.columns([3, 2, 2, 1])
        cols[0].write(row["Name"])
        cols[1].write(row["Block"])
        cols[2].write(row["Reg No"])
        
        # Unique key for each button using Reg No
        if cols[3].button("🗑️", key=f"del_{row['Reg No']}"):
            del_student(row["Reg No"])

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

# --- Main Navigation ---
st.title("🛡️ Hostel Warden Dashboard")
page = st.sidebar.radio("Navigation", ["Active Timers", "Alerts", "Student Logs", "Registered Students"])

if page == "Active Timers":
    render_active_timers()

elif page == "Alerts":
    render_alerts()

elif page == "Student Logs":
    st.header("📜 All Student Logs")
    render_trip_logs()

elif page == "Registered Students":
    st.header("📋 Registered Students")
    render_registration_table()
