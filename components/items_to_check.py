
import streamlit as st

def normalize_key(text):
    return text.lower().replace(" ", "_").replace("/", "_")

ICT_ROWS = [
    ("Agilent", "Tri"),
    ("Teradyne", "Tescon"),
    ("Genrad", "")
]

def render_row(item, engineer_list, section):
    c1, c2, c3,c4,c5 = st.columns([3,2,2,2,4])
    
    with c1:
        st.write(item)

    with c2:
        pass

    with c3:
        st.multiselect(
            "",
            engineer_list,
            key=f"pic_{normalize_key(section)}_{normalize_key(item)}",
            label_visibility="collapsed"
        )
    with c4:
        key_target = f"target_{normalize_key(section)}_{normalize_key(item)}"
        value_target = st.session_state.get(key_target, "")
        
        st.text_area(
            "",
            key=key_target,
            height=100 if len(value_target) > 50 else 60,
            label_visibility = "collapsed"
        )
        
    with c5:
        key_remark = f"remark_{normalize_key(section)}_{normalize_key(item)}"
        value_remark = st.session_state.get(key_remark, "")
        
        st.text_area(
            "",
            key=key_remark,
            height=120 if len(value_remark) > 50 else 80,
            label_visibility = "collapsed"
        )


SECTIONS = {
    "DOCUMENTATION": [
        "BOM",
        "Drawing",
        "Drawing Upload to SAP or SharePoint",
        "Process Control Plan",
        "Customer Procedure",
        "Customer Specific Requirements (CSR)",
        "Metal Assessment (Steel/Iron/Aluminum/Others)",
        "Others"
    ],

    "SMT":[
        "XY or Customer’s CAD data",
        "Component Review",
        "Golden Sample (2 panels form for AOI)",
        "PCA DFM Review",
        "Refresh PCA",
        "Loading List / Work Instruction",
        "Label Pasting Location",
        "Special Instruction",
        "Others"
    ],
    
    "MI": [
        "Robotic Soldering Jig",
        "Lead Protrusion Review",
        "Lead Cutting Jig",
        "Lead Protrusion Checking",
        "Chip Wave",
        "MI Work Instruction",
        "Others"
    ],
    
    "BACK END": [
        "Battery Handling Instruction",
        "Packing Work Instruction (Box Build)",
        "Packing Work Instruction (PCBA)",
        "Conformal Coating Machine Allocation",
        "Washing",
        "Label Pasting Location",
        "Special Instruction",
        "Others"
    ], 
    
    "TEST":[
        "ICT Program / Fixture",
        "Flying Probe Test Program",
        "Board Level Test Program / Fixture",
        "Final Test Program / Fixture",
        "Test Work Instructions",
        "Off-board / On-board Programming"
    ],
    
    "QUALITY":[
        "OQC Inspection Procedure",
        "Others"
    ],
    
    "MATERIAL AVAILABILITY":[
        "Indirect Materials Full Kit Date",
        "Refresh Production Order",
        "Others"
    ],
    
    "SHIPMENT PLAN":[
        "Packaging Requirement",
        "Pack Plan",
        "Others"
    ],
    
    "OTHERS":[
        "NPI Buy-Off Checklist",
        "Build Timeline (Gantt Chart)",
        "RTDC Set-up / Spectrum Pro (For traceability system)"
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

        col1,col2,col3,col4, col5 = st.columns([3,2,2,2,4])

        col1.markdown("**Check Item**")
        col2.markdown("**")
        col3.markdown("**PIC**")
        col4.markdown("**Target Finish**")
        col5.markdown("**Remarks**")
    
        st.markdown("---")
    
        for section, items in SECTIONS.items():
           with st.expander(section, expanded=False):
               for item in items:
                   if item == "ICT Program / Fixture":
                        c1,c2,c3,c4,c5 = st.columns([3,2,2,2,4])
                    
                        with c1:
                            st.write("ICT Program / Fixture")
                            
                        with c3:
                            st.multiselect("", engineer_list, key="pic_ict", label_visibility="collapsed")
                            
                        with c4:
                            st.text_area("", key="target_ict", label_visibility="collapsed")
                            
                        with c5:
                            st.text_area("", key="remark_ict", label_visibility="collapsed")
                    
                        for left, right in ICT_ROWS:
                            c1,c2,c3,c4,c5 = st.columns([3,2,2,2,4])
                    
                            with c1:
                                st.checkbox(left, key=f"ict_{normalize_key(left)}")
                    
                            with c2:
                                if right:
                                    st.checkbox(right, key=f"ict_{normalize_key(right)}")
                    
                            with c3:
                                st.multiselect(
                                    "",
                                    engineer_list,
                                    key=f"pic_ict_{normalize_key(left)}",
                                    label_visibility="collapsed"
                                )
                    
                            with c4:
                                key_target = f"target_ict_{normalize_key(left)}"
                                value_target = st.session_state.get(key_target, "")

                                st.text_area(
                                    "",
                                    key=key_target,
                                    height=100 if len(value_target) > 50 else 60,
                                    label_visibility="collapsed"
                                )
                    
                            with c5:
                                key_remark = f"remark_ict_{normalize_key(left)}"
                                value_remark = st.session_state.get(key_remark, "")
                                
                                st.text_area(
                                    "",
                                    key=key_remark,
                                    height=120 if len(value_remark) > 50 else 80,
                                    label_visibility="collapsed"
                                )
                           
                   else:
                       render_row(item, engineer_list, section)
                       
                      
                        

                       
                    
