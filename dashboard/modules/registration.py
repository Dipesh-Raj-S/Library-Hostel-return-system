import streamlit as st
from dashboard.api_client import fetch_api_data, del_student_api

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
                    del_student_api(reg_no)
                if sub_c2.button("❌", key=f"canc_{reg_no}", help="Cancel"):
                    st.session_state.confirm_delete_id = None
                    st.rerun()
        else:
            # Show the delete icon
            if cols[3].button("🗑️", key=f"del_{reg_no}"):
                st.session_state.confirm_delete_id = reg_no
                st.rerun()
