import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
from config import Config

# Configuration
API_BASE_URL = Config.API_BASE_URL
REFRESH_RATE = 1  # Seconds

st.set_page_config(
    page_title="Warden Dashboard",
    page_icon="👮",
    layout="wide"
)

# Helper for API calls
def fetch_data(endpoint):
    try:
        res = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=2)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        st.error(f"Backend Connection Error: {e}")
        return []

# Auto Refreshing Timers ---
@st.fragment(run_every=REFRESH_RATE)
def show_active_timers_fragment():
    data = fetch_data("active_timers")
    if not data:
        st.info("No students currently moving.")
        return

    df = pd.DataFrame(data)
    now = datetime.now()
    
    if 'expected_end_time' in df.columns:
        df['expected_end_time_dt'] = pd.to_datetime(df['expected_end_time'])
        
        def calculate_remaining(row):
            remaining = row['expected_end_time_dt'] - now
            if remaining.total_seconds() > 0:
                mm, ss = divmod(int(remaining.total_seconds()), 60)
                return f"{mm:02d}:{ss:02d}"
            return "Passed"
        
        df['Time Remaining'] = df.apply(calculate_remaining, axis=1)

    # Filter datasets
    hl_movers = df[df['direction'] == 'Hostel -> Library'].copy() if 'direction' in df.columns else pd.DataFrame()
    lh_movers = df[df['direction'] == 'Library -> Hostel'].copy() if 'direction' in df.columns else pd.DataFrame()

    col1, col2 = st.columns(2)
    
    cols_to_show = ['student_name', 'student_block', 'start_time', 'expected_end_time', 'Time Remaining', 'status']
    col_names = ['Name', 'Block', 'Start', 'Expected', 'Timer', 'Status']

    with col1:
        st.subheader("Hostel ➡️ Library")
        if not hl_movers.empty:
            st.dataframe(hl_movers[cols_to_show].rename(columns=dict(zip(cols_to_show, col_names))), width='content', hide_index=True)
        else:
            st.info("No movements.")

    with col2:
        st.subheader("Library ➡️ Hostel")
        if not lh_movers.empty:
            st.dataframe(lh_movers[cols_to_show].rename(columns=dict(zip(cols_to_show, col_names))),width='content', hide_index=True)
        else:
            st.info("No movements.")

# Auto Refreshing Alerts
@st.fragment(run_every=REFRESH_RATE)
def show_alerts_fragment():
    data = fetch_data("alerts")
    if data:
        df = pd.DataFrame(data)
        st.error(f"Total Late Students: {len(data)}")
        st.dataframe(df[['student_name', 'expected_end_time', 'status']], use_container_width=True, hide_index=True)
    else:
        st.success("No alerts. All students on time.")

def student_reg_df():
    res = requests.get("http://127.0.0.1:5000/get_encodings")
    data = res.json()
    rows = []
    for sid, info in data.items():
        rows.append([
            info["name"],
            info["block"],
            info["reg_no"]
        ])
    df = pd.DataFrame(rows,columns=["Name","Block","Reg No"])
    st.dataframe(df, use_container_width=True,hide_index=True)

# Main UI
st.title("Hostel Warden Dashboard")
page = st.sidebar.selectbox("Navigation", ["Active Timers", "Alerts", "Student Logs","Registered Students"])

if page == "Active Timers":
    st.header("Active Movements")
    show_active_timers_fragment()

elif page == "Alerts":
    st.header("🚨 Late Alerts")
    show_alerts_fragment()

elif page == "Student Logs":
    st.header("📜 All Student Logs")
    st.info("Log history feature coming soon.")

elif page == "Registered Students":
    st.header("Registered Students")
    student_reg_df()
    