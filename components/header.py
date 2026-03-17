import streamlit as st

def render_header():

    col1, col2, col3 = st.columns([1,4,1])

    with col1:
        st.image("logo.png", width=120)

    with col2:
        st.markdown(
            """
            <h1 style='text-align:center'>
            PRODUCT BUILD BRIEFING CHECKLIST
            </h1>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div style='text-align:right'>
            NP-F-006<br>
            20 Feb 2026
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
