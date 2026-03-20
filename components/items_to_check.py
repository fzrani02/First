
import streamlit as st

def render_test_checkbox():
    col1, col2 = st.columns(2)

    with col1:
        st.checkbox("Agilent", key="ict_agilent")
        st.checkbox("Teradyne", key="ict_teradyne")
        st.checkbox("Genrad", key="ict_genrad")

    with col2:
        st.checkbox("Tri", key="ict_tri")
        st.checkbox("Tescon", key="ict_tescon")

def render_row(item, engineer_list):
    c1, c2, c3,c4 = st.columns([3,2,2,4])
    
    with c1:
        st.write(item)

    with c2:
        st.multiselect(
            "",
            engineer_list,
            key=f"pic_{item}",
            label_visibility="collapsed"
        )
    with c3: 
        st.text_input(
            "",
            key=f"target_{item}",
            label_visibility = "collapsed"
        )
    with c4:
        st.text_input(
            "",
            key=f"remark_{item}",
            label_visibility = "collapsed"
        )


SECTIONS = {
    "DOCUMENTATION": [
        "BOM",
        "Drawing",
        "Drawing Upload to SAP or SharePoint",
        "Process Control Plan"
    ],

    "SMT":[
        "Stencil",
        "Solder Paste",
        "SMT Program"
    ],
    "MI": [
        "MI Preparation",
        "Work Instruction"
    ],
    "BACK END": [
        "Assembly Jig",
        "Process Flow"
    ], 
    
    "TEST":[
        "ICT Program / Fixture"
    ],
    "QUALITY":[
        "Control Plan",
        "Quality Instruction"
    ],
    "MATERIAL AVAILABILITY":[
        "Material Status"
    ],
    "SHIPMENT PLAN":[
        "Shipment Schedule"
    ],
    "OTHERS":[
        "Other Requirements"
    ]
}

def render_items_to_check(df, item_check):

    st.markdown("## ITEMS TO CHECK")
    
    st.write ("NOTE: All documents/package from Design/Customer must be updated for every stage of the build including Mass Production")
    if not item_check:
        st.warning("No items parsed from PDF")

    for item in item_check:
        st.write(item)
        
    engineer_list = [""] + df["ER"].unique().tolist()
    st.markdown(
        """
        <style>
        
        div[data-testid="stExpander"] {
            background-color:#ffffff;
            border-radius:8px;
            border:1px solid #d0d7de;
        }
        
        div[data-testid="stExpander"] summary {
            font-weight:600;
            font-size:14px;
        }
        
        </style>
        """, unsafe_allow_html=True)
    with st.container(border=True, height=600):  

        col1,col2,col3,col4 = st.columns([3,2,2,4])

        col1.markdown("**Check Item**")
        col2.markdown("**PIC**")
        col3.markdown("**Target Finish**")
        col4.markdown("**Remarks**")
    
        st.markdown("---")
    
        for section, items in SECTIONS.items():
           with st.expander(section, expanded=False):
               for item in items:
                   if item == "ICT Program / Fixture":
                       c1,c2,c3,c4 = st.columns([3,2,2,4])
                       with c1:
                           st.write(item)
                           
                       with c2:
                           render_test_checkbox()
                           
                       with c3:
                           st.text_input("", key="target_test")
                           
                       with c4:
                           st.text_input("", key="remark_test")

                   else:
                       render_row(item, engineer_list)
                       
                    
