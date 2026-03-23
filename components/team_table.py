import streamlit as st
from utils.database import get_engineers_by_department

def render_team_table(df, initial, departments, editable_col, attendance_data, member_data, title, key_prefix):

    # CSS
    st.markdown("""
    <style>

    div[data-testid="stCheckbox"] {
        display:flex;
        justify-content:center;
        align-items: center;
        width: 100%;
    }
    
    div[data-testid="stCheckbox"] label {
        display: flex;
        justify-content:center;
        align-items: center;
        width: 100%;
    }

    </style>
    """, unsafe_allow_html=True)

    # HEADER
    left, right = st.columns([3,2])

    with left:

        col1,col2,col3,col4 = st.columns([3,3,2,3])
        col1.markdown("**Department**")
        col2.markdown("**Name**")
        col3.markdown("**Ext. #**")
        col4.markdown("**Email**")

    with right:

        st.markdown("<h3 style='text-align: center;'>ATTENDANCES</h3>", unsafe_allow_html=True)


        col1,col2,col3,col4 = st.columns([1,1,1,1], gap="small")

        with col1:
            st.date_input("", key=f"{key_prefix}_mtg1", disabled=editable_col != 1, label_visibility="collapsed")

        with col2:
            st.date_input("", key=f"{key_prefix}_mtg2", disabled=editable_col != 2, label_visibility="collapsed")

        with col3:
            st.date_input("", key=f"{key_prefix}_mtg3", disabled=editable_col != 3, label_visibility="collapsed")

        with col4:
            st.date_input("", key=f"{key_prefix}_mtg4", disabled=editable_col != 4, label_visibility="collapsed")

    st.markdown("---")

    # ROW DATA
    for dept in departments:
        existing_member = attendance_data.get(dept, {})
        existing_name = existing_member.get("name", "")
        existing_email = existing_member.get("email", "")

        engineers = get_engineers_by_department(df, initial, dept)
        engineer_list = [""] + engineers["ER"].tolist()

        left, right = st.columns([3,2])

        with left:

            col1,col2,col3,col4 = st.columns([3,3,2,3])

            with col1:
                st.write(dept)

            with col2:
                default_index = 0
                if existing_name in engineer_list:
                    default_index = engineer_list.index(existing_name)

                selected = st.selectbox(
                    "",
                    engineer_list,
                    key=f"{key_prefix}_{dept}_engineer",
                    label_visibility="collapsed"
                )
                
                engineer_selected = selected != ""

            email_key = f"{key_prefix}_{dept}_email"
            
            email = ""
            
            if selected:
                email = engineers.loc[
                    engineers["ER"] == selected, "Email"
                ].values[0]

            else:
                email = existing_email

            st.session_state[email_key] = email

            with col3:
                st.text_input(
                    "",
                    value = existing_member.get("ext", ""),
                    key=f"{key_prefix}_{dept}_ext",
                    label_visibility="collapsed"
                )

            with col4:
                st.text_input(
                    "",
                    key=email_key,
                    disabled=True,
                    label_visibility="collapsed"
                )

        with right:

            col1,col2,col3,col4 = st.columns(4)

            with col1:
                checked = attendance_data.get(dept, {}).get("m1", False)
                st.checkbox("", value=checked, key=f"{key_prefix}_{dept}_m1", disabled=(editable_col != 1) or (not engineer_selected))

            with col2:
                checked = attendance_data.get(dept, {}).get("m2", False)
                st.checkbox("", value=checked, key=f"{key_prefix}_{dept}_m2", disabled=(editable_col != 2) or (not engineer_selected))

            with col3:
                checked = attendance_data.get(dept, {}).get("m3", False)
                st.checkbox("", value=checked, key=f"{key_prefix}_{dept}_m3", disabled=(editable_col != 3) or (not engineer_selected))

            with col4:
                checked = attendance_data.get(dept, {}).get("m4", False)
                st.checkbox("", value=checked, key=f"{key_prefix}_{dept}_m4", disabled=(editable_col != 4) or (not engineer_selected))











