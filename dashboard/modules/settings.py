import streamlit as st
from dashboard.api_client import fetch_block_limits, update_block_limit

@st.fragment
def render_settings():
    # Initialize session states for tracking edits
    if 'edit_block' not in st.session_state:
        st.session_state.edit_block = None
    if 'new_limit_val' not in st.session_state:
        st.session_state.new_limit_val = 15

    limits = fetch_block_limits()

    if not limits:
        st.info("No block limits configured. Add one below.")
    else:
        # Header Row
        cols = st.columns([2, 2, 2])
        cols[0].write("**Block Name**")
        cols[1].write("**Limit (Mins)**")
        cols[2].write("**Actions**")
        st.divider()

        for item in limits:
            block = item['block']
            minutes = item['minutes']
            cols = st.columns([2, 2, 2])
            
            cols[0].write(f"**Block {block}**")

            # Check if this specific block is being edited
            if st.session_state.edit_block == block:
                # Show Input Field and Confirm/Cancel
                with cols[1]:
                    new_val = st.number_input(
                        "Mins", 
                        min_value=1, 
                        value=minutes, 
                        key=f"input_{block}",
                        label_visibility="collapsed"
                    )
                with cols[2]:
                    sub1, sub2 = st.columns(2)
                    if sub1.button(":material/check_circle:", key=f"save_{block}", help="Confirm Change"):
                        if update_block_limit(block, new_val):
                            st.toast(f"Block {block} updated!")
                            st.session_state.edit_block = None
                            st.rerun()
                    if sub2.button(":material/cancel:", key=f"stop_{block}", help="Cancel"):
                        st.session_state.edit_block = None
                        st.rerun()
            else:
                # Show Value and Edit Icon
                cols[1].write(f"{minutes} minutes")
                if cols[2].button(":material/edit:", key=f"edit_{block}"):
                    st.session_state.edit_block = block
                    st.rerun()

    st.divider()

    with st.expander(":material/add_2: Add New Block Configuration"):
        with st.container():
            c1, c2 = st.columns(2)
            new_b = c1.text_input("Block Name", placeholder="e.g., E").upper()
            new_m = c2.number_input("Minutes", min_value=1, value=15)
            
            if st.button("Add Block", type="primary"):
                if new_b:
                    if update_block_limit(new_b, new_m):
                        st.success(f"Block {new_b} added.")
                        st.rerun()
                else:
                    st.error("Please enter a block name.")