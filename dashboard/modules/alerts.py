import streamlit as st
import pandas as pd
from dashboard.api_client import fetch_api_data, REFRESH_RATE

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

