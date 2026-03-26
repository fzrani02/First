import streamlit as st
import pandas as pd

from components.header import render_header
from components.project_form import render_project_form
from components.team_table import render_team_table
from components.items_to_check import render_items_to_check
from components.items_to_check import normalize_key
from components.items_to_check import SECTIONS

from utils.revision_logic import get_editable_column
from utils.pdf_import import read_pdf, parse_form
from utils.revision_logic import get_next_revision
from utils.pdf_export import generate_pdf
from utils.database import load_database
from utils.autosave import autosave

from datetime import date
from datetime import datetime

def convert_to_dict(data_list):
    result = {}
    for item in data_list:
        dept = item.get("department")
        if dept:
            result[dept] = item
    return result

def apply_checkbox_state(item_check):
    for item in item_check:
        
        left = item.get("item")
        
        if left:
            st.session_state[f"ict_{normalize_key(left)}"] = item.get("checked", False)

        right = item.get("pair_label")

        if right:
            st.session_state[f"ict_{normalize_key(right)}"] = item.get("pair_checked", False)

        key = normalize_key(left) if left else None

        if not key:
            continue

      
        st.session_state[f"target_ict_{key}"] = item.get("target", "")
        st.session_state[f"remark_ict_{key}"] = item.get("remark", "")

        if key:
            st.session_state[f"pic_ict_{key}"] = item.get("pic", "")

        pic_raw = item.get("pic", "")
        if pic_raw:
            st.session_state[f"pic_ict_{key}"] = [p.strip() for p in pic_raw.split(",")]

def render_boxbuild():
    import time
    start_total = time.time()
    
    member_plant = {}
    member_pcis = {}
    item_check = {}

    t_header = time.time()
    render_header()
    st.write("Header time:", time.time() - t_header)
        
    uploaded_pdf = st.file_uploader(
        "Upload Previous Briefing PDF",
        type=["pdf"]
    )
    parsed = None
    
    if uploaded_pdf and "parsed_data" not in st.session_state:

        t_pdf =time.time()
        
        text = read_pdf(uploaded_pdf)
        parsed = parse_form(text, uploaded_pdf)

        st.write("DEBUG item_check:", parsed.get("item_check"))

        st.session_state["parsed_data"] = parsed

        for member in parsed.get("member_plant", []):
            dept = member["department"]
            for m in ["m1","m2", "m3", "m4"]:
                st.session_state[f"plant_{dept}_{m}"] = member.get(m,False)

        for member in parsed.get("member_pcis", []):
            dept = member["department"]
            for m in ["m1","m2","m3", "m4"]:
                st.session_state[f"pcis_{dept}_{m}"] = member.get(m, False)

        for key, value in parsed["project_data"].items(): 
             st.session_state[key] = value
    
        apply_checkbox_state(parsed.get("item_check", []))

        st.write("PDF parse time:", time.time() - t_pdf)

        for item in parsed.get("item_check", []):

            name = item.get("item", "").lower()
            
            item_name = item.get("item", "")
            key_item = normalize_key(item_name)

            section_found = None
            for section, items in SECTIONS.items():
                if item_name in items:
                    section_found = section
                    break

            if not section_found:
                continue

            key_section = normalize_key(section_found)

            full_key = f"{key_section}_{key_item}"

            target_key = f"target_{full_key}"
            remark_key = f"remark_{full_key}"

            if target_key not in st.session_state:
                st.session_state[target_key] = item.get("target", "")

            if remark_key not in st.session_state:
                st.session_state[remark_key] = item.get("remark", "")

    st.markdown("---")

    project_data = render_project_form()

    if "parsed_data" in st.session_state:
        parsed = st.session_state["parsed_data"]
    
        member_plant = convert_to_dict(parsed.get("member_plant", []))
        member_pcis = convert_to_dict(parsed.get("member_pcis", []))
        item_check = parsed.get("item_check", [])

        t_form = time.time()
    
        project_data.update(parsed["project_data"])
        st.write("Form render time:", time.time() - t_form)
            
        ##################
        
        revision = project_data.get("revision", "A")
        editable_col = get_editable_column(revision, uploaded_pdf)

        st.write(parsed.get("item_check"))

    st.markdown("---")
    
    pci = project_data.get("pci","")
    initial = project_data["initial"]

    t_db = time.time()
    df = load_database()
    df_filtered = df[df["Initial"] == initial]
    st.write("Load DB time:", time.time() - t_db)
    
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

    revision = project_data.get("revision")
    editable_col = get_editable_column(revision, uploaded_pdf)
   
    with st.expander("PROJECT TEAM MEMBERS (PLANT)", expanded=False):
        t_table1 = time.time()
        
        render_team_table(
            df_filtered,
            initial,
            departments,
            editable_col,
            member_plant,
            member_plant,
            "PROJECT TEAM MEMBERS (PLANTS)",
            "plant"
        )
        st.write("Table PLANT time:", time.time() - t_table1)

    with st.expander("PROJECT TEAM MEMBERS (PCIS)", expanded=False):

        t_table2 = time.time()
        
        render_team_table(
            df_filtered,
            initial,
            pcis_departments,
            editable_col,
            member_pcis,
            member_pcis,
            "PROJECT TEAM MEMBERS (PCIS)",
            "pcis"
        )
        st.write("Table PCIS time:", time.time() - t_table2)
        
    autosave()

    st.markdown("---")
    
    t_items = time.time()
    render_items_to_check(df, item_check)
    st.write("Items check time:", time.time() - t_items)
             
    st.markdown("---")

    from utils.revision_logic import get_next_revision

    if st.button("Export to PDF"):
        t_export = time.time()
        
        current_revision = project_data.get("revision")

        if not uploaded_pdf:
            next_revision = "X"
        else:
            next_revision = get_next_revision(current_revision)

        # update data 
        project_data["revision"] = next_revision
        project_data["date_updated"] = date.today()
        
        pdf_file = generate_pdf(project_data, departments, pcis_departments)
        
        st.write("PDF generate time:", time.time() - t_export)

        pci = project_data.get("pci","")
        account = project_data.get("project_account","")
        date_updated = project_data.get("date_updated", date.today())
        
        filename = f"Attendance - {pci} - {account} - {date_updated} - Rev {next_revision}.pdf"

        st.download_button(
            label="Download PDF",
            data=pdf_file,
            file_name=filename,
            mime="application/pdf"
        )
        
    st.write("TOTAL time:", time.time() - start_total)
    
