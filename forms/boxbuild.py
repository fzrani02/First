import streamlit as st
import pandas as pd
from components.header import render_header
from components.project_form import render_project_form

from components.team_table import render_team_table
from components.items_to_check import render_items_to_check
from utils.revision_logic import get_editable_column
from utils.pdf_import import read_pdf, parse_form
from utils.revision_logic import get_next_revision
from datetime import datetime
from utils.pdf_export import generate_pdf

from datetime import date
from utils.database import load_database
from utils.autosave import autosave

def convert_to_dict(data_list):
    result = {}
    for item in data_list:
        dept = item.get("department")
        if dept:
            result[dept] = item
    return result

def render_boxbuild():
    member_plant = {}
    member_pcis = {}
    item_check = {}

    render_header()
        
    uploaded_pdf = st.file_uploader(
        "Upload Previous Briefing PDF",
        type=["pdf"]
    )
    parsed = None
    if uploaded_pdf and "parsed_data" not in st.session_state:
        text = read_pdf(uploaded_pdf)
        parsed = parse_form(text)
        st.session_state["parsed_data"] = parsed
    
        for key, value in parsed["project_data"].items(): 
             st.session_state[key] = value

    st.markdown("---")

    project_data = render_project_form()

    if "parsed_data" in st.session_state:
        parsed = st.session_state["parsed_data"]
    
        member_plant = convert_to_dict(parsed.get("member_plant", []))
        member_pcis = convert_to_dict(parsed.get("member_pcis", []))
        item_check = parsed.get("item_check", [])
    
        project_data.update(parsed["project_data"])
        st.write("PLANT:", member_plant)
        st.write("PCIS:", member_pcis)
        st.write("ITEM CHECK:", item_check)
        for dept, data in member_plant.items():
            st.write(dept, data)
            
        ##################
        
        revision = project_data.get("revision", "A")
        editable_col = get_editable_column(revision, uploaded_pdf)

    st.markdown("---")
    
    df = load_database()
    pci = project_data.get("pci","")
    initial = project_data["initial"]
    
    departments = [
        "Product Engineer",
        "Process Engineer (SMT)",
        "Process Engineer (Back End)",
        "Test Engineer (FCT)",
        "Test Engineer (ICT)",
        "Production Supervisor (SMT)",
        "Production Supervisor (Back End)",
        "QA Engineer",
        "QC Engineer (IPQC)",
        "QC Engineer (OQC)",
        "QC Engineer (IQC)",
        "Material Controller",
        "COB Engineer",
        "DFM Engineer",
        "Maintenance Engineer"
    ]

    pcis_departments = [
        "Test Development Engineer",
        "Program Manager",
        "Account Manager",
        "Demand Planner"
    ]

    editable_col =1

    revision = None
       
    if revision is None and uploaded_pdf is None:
        editable_col = 1
    
    elif revision is None and uploaded_pdf:
        editable_col = 2
    
    elif revision == "A":
        editable_col = 3
    
    elif revision == "B":
        editable_col = 4

   
    with st.expander("PROJECT TEAM MEMBERS (PLANT)", expanded=False):
        
        render_team_table(
            df,
            initial,
            departments,
            editable_col,
            member_plant,
            "PROJECT TEAM MEMBERS (PLANTS)",
            "plant"
        )

    with st.expander("PROJECT TEAM MEMBERS (PCIS)", expanded=False):
        render_team_table(
            df,
            initial,
            pcis_departments,
            editable_col,
            member_pcis,
            "PROJECT TEAM MEMBERS (PCIS)",
            "pcis"
        )
    autosave()

    st.markdown("---")
    render_items_to_check(df, item_check)
    st.markdown("---")

    from utils.revision_logic import get_next_revision

    if st.button("Export to PDF"):
        
        revision = get_next_revision(project_data.get("revision"))
        project_data["revision"] = revision
        project_data["date_updated"] = date.today()
    
        pdf_file = generate_pdf(project_data, departments, pcis_departments)

        pci = project_data.get("pci","")
        account = project_data.get("project_account","")
        date_updated = project_data.get("data_updated", date.today())
        revision = project_data.get("revision","")
        
        filename = f"Attendance - {pci} - {account} - {date_updated} - Rev {revision}.pdf"

        st.download_button(
            label="Download PDF",
            data=pdf_file,
            file_name=filename,
            mime="application/pdf"
        )
    
