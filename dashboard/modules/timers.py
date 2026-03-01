import streamlit as st
from dashboard.api_client import fetch_api_data, process_timer_data, REFRESH_RATE

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