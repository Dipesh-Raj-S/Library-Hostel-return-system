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
                    label = f"{row['student_name']} (Block {row['student_block']}) — {row['Time Remaining']}"
                    expanded = st.toggle(label, key=f"tog_{row['id']}")

                    if expanded:
                        with st.container(border=True):
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Departed", row['display_start'])
                            m2.metric("Expected", row['display_expected'])
                            
                            # Color code the remaining time
                            is_late = "Passed" in row['Time Remaining']
                            m3.metric("Remaining", row['Time Remaining'], 
                                    delta="LATE" if is_late else None,
                                    delta_color="inverse")
                            
                            st.caption(f"Status: {row['status']} | Direction: {row['direction']}")
                    
                    st.write("")


@st.fragment(run_every=REFRESH_RATE)
def render_alerts():
    data = fetch_api_data("alerts")
    if data:
        df = pd.DataFrame(data)
        
        # Beautify the expected time
        df['expected_dt'] = pd.to_datetime(df['expected_end_time'])
        df['Expected Arrival'] = df['expected_dt'].dt.strftime("%b %d, %I:%M %p")

        st.error(f"Total Late Students: {len(data)}")
        st.dataframe(df[['student_name', 'Expected Arrival', 'status']], width='stretch', hide_index=True,
            column_config={
                "student_name": "Student Name",
                "status": "Current Status"
            })
    else:
        st.success("✅ All students on time.")

def del_student(regno):
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

@st.fragment(run_every=30) 
def render_registration_table():
    data = fetch_api_data("get_encodings")
    if not data:
        st.info("No students registered.")
        return

    # Initialize state to track which student is being deleted
    if 'confirm_delete_id' not in st.session_state:
        st.session_state.confirm_delete_id = None

    # Header Row
    cols = st.columns([3, 2, 2, 2])
    cols[0].write("**Name**")
    cols[1].write("**Block**")
    cols[2].write("**Reg No**")
    cols[3].write("**Action**")
    st.divider()

    for sid, info in data.items():
        reg_no = info["reg_no"]
        cols = st.columns([3, 2, 2, 2])
        
        cols[0].write(info["name"])
        cols[1].write(info["block"])
        cols[2].write(reg_no)

        # confirm delete
        if st.session_state.confirm_delete_id == reg_no:
            # Show confirm/cancel buttons instead of the delete icon
            with cols[3]:
                sub_c1, sub_c2 = st.columns(2)
                if sub_c1.button("✅", key=f"conf_{reg_no}", help="Confirm Delete"):
                    del_student(reg_no)
                if sub_c2.button("❌", key=f"canc_{reg_no}", help="Cancel"):
                    st.session_state.confirm_delete_id = None
                    st.rerun()
        else:
            # Show the delete icon
            if cols[3].button("🗑️", key=f"del_{reg_no}"):
                st.session_state.confirm_delete_id = reg_no
                st.rerun()

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
