import streamlit as st
from dashboard.modules import alerts, logs, registration, timers

st.set_page_config(
    page_title="Warden Dashboard",
    page_icon=":material/admin_panel_settings:",
    layout="wide"
)

st.title("🛡️ Hostel Warden Dashboard")
page = st.sidebar.radio("Navigation", ["Active Timers", "Alerts", "Student Logs", "Registered Students"])

if page == "Active Timers":
    timers.render_active_timers()

elif page == "Alerts":
    alerts.render_alerts()

elif page == "Student Logs":
    st.header("📜 All Student Logs")
    logs.render_trip_logs()

elif page == "Registered Students":
    st.header("📋 Registered Students")
    registration.render_registration_table()
