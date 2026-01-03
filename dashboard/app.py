import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import cv2
from face_utils import get_face_encoding, register_student_api
from face_recognition import face_locations

if "cap" not in st.session_state:
    st.session_state.cap = None


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
page = st.sidebar.selectbox("Navigation", ["Active Timers", "Alerts", "Student Logs","Register Student"])

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
    
    st.autorefresh(interval=1000, key="active_timers")

    data = fetch_data("active_timers")
        
    with placeholder.container():
        if data:
            # Convert to DataFrame
            df = pd.DataFrame(data)
                
            # Calculate remaining time
            now = datetime.now()
            df['expected_end_time_dt'] = pd.to_datetime(df['expected_end_time'])
                
            def calculate_remaining(row):
                remaining = row['expected_end_time_dt'] - now
                if remaining.total_seconds() > 0:
                    mm, ss = divmod(remaining.seconds, 60)
                    return f"{int(mm):02d}:{int(ss):02d}"
                else:
                    return "Passed"
                
            df['Time Remaining'] = df.apply(calculate_remaining, axis=1)
                
            # Select and rename columns for display
            display_df = df[['student_name', 'student_block', 'start_time', 'expected_end_time', 'Time Remaining', 'status']]
            display_df.columns = ['Student Name', 'Block', 'Start Time', 'Expected Return', 'Time Remaining', 'Status']
                
            # Show as a table
            st.dataframe(
                display_df, 
                use_container_width=True,
                column_config={
                    "Student Name": st.column_config.TextColumn("Student Name", width="medium"),
                    "Block": st.column_config.TextColumn("Block", width="small"),
                    "Time Remaining": st.column_config.TextColumn("Timer", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                },
                hide_index=True
            )
        else:
            st.info("No students currently outside.")
        
       

elif page == "Alerts":
    st.header("🚨 Late Alerts")
    
    placeholder = st.empty()
    
    
    data = fetch_data("alerts")
    
    st.autorefresh(interval=5000, key="alerts")

        
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

elif page == "Register Student":
    st.header("🧑‍🎓 Register New Student")

    name = st.text_input("Student Name")
    block = st.text_input("Block", value="D")

    start_cam = st.button("Start Camera")
    capture = st.button("Capture & Register")
    stop_cam = st.button("Stop Camera")
    if start_cam and st.session_state.cap is None:
        st.session_state.cap = cv2.VideoCapture(0)
    frame_placeholder = st.empty()

    if st.session_state.cap:
        ret, frame = st.session_state.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = frame[:, :, ::-1]
            boxes = face_locations(rgb)

            for t, r, b, l in boxes:
                cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)

            frame_placeholder.image(frame, channels="BGR")
    if capture:
        if not name:
            st.error("Enter student name")
        elif st.session_state.cap is None:
            st.error("Start the camera first")
        else:
            ret, frame = st.session_state.cap.read()
            if ret:
                encoding = get_face_encoding(frame)

                if encoding is not None:
                    res, status = register_student_api(name, encoding, block)
                    if status == 201:
                        st.success(f"Student registered. ID: {res.get('student_id')}")
                    else:
                        st.error("Registration failed")
                else:
                    st.warning("No valid face detected")
    if stop_cam and st.session_state.cap:
        st.session_state.cap.release()
        st.session_state.cap = None




