import streamlit as st
from forms.boxbuild import render_boxbuild

st.set_page_config(layout="wide")

st.sidebar.title("Form Selection")

form_type = st.sidebar.radio(
    "Select Form",
    ["BoxBuild", "PCBA"]
)

if form_type == "BoxBuild":
    render_boxbuild()
