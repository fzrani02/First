import streamlit as st
from datetime import date 

def render_project_form():
  col1, col2, col3 = st.columns(3)
  
  with col1:
    project_name = st.text_input("Project Name", key="project_name")
    build_type = st.text_input("Build Type", key="build_type")

    if "data_updated" not in st.session_state:
      st.session_state["data_updated"] = date.today()
      
    date_updated = st.date_input("Date Updated", key="data_updated")

  with col2:
    customer_map = {
      "CG": "COGNEX",
      "GE": "GEA",
      "OR": "ORBCOMM",
      "LF": "LIFE FITNESS",
    }
    pci = st.text_input("PCI FG P/N", key="pci")
    initial = pci[:2].upper() if pci else ""

    customer_auto = customer_map.get(initial, "")
    
    if customer_auto and st.session_state.get("customer") != customer_auto:
      st.session_state["customer"] = customer_auto
      
    customer = st.text_input("Customer", key="customer")
    
    project_account = st.text_input("Project Account", key="project_account")

  with col3:
    revision = st.text_input("Revision", key="revision", disabled=True)
    product_type = st.selectbox(
      "Product Type",
      ["Automotive","Medical","Military","Consumer"],
      key="product_type"
    )
  
  return {
    "project_name": project_name,
    "build_type": build_type,
    "data_updated": date_updated, 
    "pci": pci,
    "customer": customer,
    "initial": initial,
    "project_account": project_account,
    "revision": revision,
    "product_type": product_type
  }
  




