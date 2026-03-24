from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.platypus import Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from components.items_to_check import SECTIONS, ICT_ROWS, normalize_key
import streamlit as st
import io
import json


def generate_pdf(project_data, departments, pcis_departments):
    st.write("SESSION STATE DEBUG:", st.session_state)
    

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    remark_style = styles["Normal"]
    cell_style = styles["Normal"]
    cell_style.fontSize = 8
    cell_style.leading = 10
    cell_style.wordWrap = 'CJK'   # penting buat wrap paksa
    remark_style.fontSize = 8
    remark_style.leading = 10   # jarak antar baris
    elements = []

    logo = Image("logo.png", width=120, height=40)

    title = Paragraph(
        "<para align=center><b>PRODUCT BUILD BRIEFING CHECKLIST</b></para>",
        styles['Title']
    )
    
    np_info = Paragraph(
        "<para align=right>NP-F-006<br/>20 Feb 2026</para>",
        styles['Normal']
    )
    
    header_table = Table(
        [[logo, title, np_info]],
        colWidths=[120, 320, 120]
    )
    
    header_table.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1,20))

    # =========================
    # TITLE
    # =========================

    
    # =========================
    # PROJECT INFO
    # =========================

    project_table = [
        ["Project Name", project_data["project_name"], "Customer", project_data["customer"]],
        ["Build Type", project_data["build_type"], "PCI FG P/N", project_data["pci"]],
        ["Project Account", project_data["project_account"], "Product Type", project_data["product_type"]],
        ["Date Updated", str(project_data["date_updated"]), "Revision", project_data["revision"]],
    ]

    t = Table(project_table, colWidths=[120,160,120,120])

    t.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),
        ("BACKGROUND",(2,0),(2,-1),colors.lightgrey),
    ]))

    elements.append(t)
    elements.append(Spacer(1,25))

    # =========================
    # TEAM MEMBERS
    # =========================

    elements.append(Paragraph("<b>PROJECT TEAM MEMBERS (PLANT)</b>", styles['Heading3']))
    elements.append(Spacer(1,10))

    team_data = [["Department","Name","Ext","Email","M1","M2","M3","M4"]]

    for dept in departments:

        team_data.append([
            dept,
            st.session_state.get(f"plant_{dept}_engineer",""),
            st.session_state.get(f"plant_{dept}_ext",""),
            st.session_state.get(f"plant_{dept}_email",""),
            "✓" if st.session_state.get(f"plant_{dept}_m1") else "",
            "✓" if st.session_state.get(f"plant_{dept}_m2") else "",
            "✓" if st.session_state.get(f"plant_{dept}_m3") else "",
            "✓" if st.session_state.get(f"plant_{dept}_m4") else "",
        ])

    team_table = Table(team_data, hAlign='LEFT')

    team_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("ALIGN",(4,1),(-1,-1),"CENTER")
    ]))

    elements.append(team_table)
    elements.append(Spacer(1,25))

    # =========================
    # PCIS TEAM
    # =========================

    elements.append(Paragraph("<b>PROJECT TEAM MEMBERS (PCIS)</b>", styles['Heading3']))
    elements.append(Spacer(1,10))

    pcis_data = [["Department","Name","Ext","Email","M1","M2","M3","M4"]]

    for dept in pcis_departments:

        pcis_data.append([
            dept,
            st.session_state.get(f"pcis_{dept}_engineer",""),
            st.session_state.get(f"pcis_{dept}_ext",""),
            st.session_state.get(f"pcis_{dept}_email",""),
            "✓" if st.session_state.get(f"pcis_{dept}_m1") else "",
            "✓" if st.session_state.get(f"pcis_{dept}_m2") else "",
            "✓" if st.session_state.get(f"pcis_{dept}_m3") else "",
            "✓" if st.session_state.get(f"pcis_{dept}_m4") else "",
        ])

    pcis_table = Table(pcis_data, hAlign='LEFT')

    pcis_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("ALIGN",(4,1),(-1,-1),"CENTER")
    ]))

    elements.append(pcis_table)
    elements.append(Spacer(1,25))

    # =========================
    # ITEMS TO CHECK
    # =========================

    elements.append(Paragraph("<b>ITEMS TO CHECK</b>", styles['Heading3']))
    elements.append(Spacer(1,10))

    item_table = [["Section", "Item", "**", "PIC", "Target", "Remark"]]
    section_row_indices = []

    for section, items in SECTIONS.items():
    
        # SECTION HEADER (biar kebaca di PDF)
        section_row_indices.append(len(item_table))  # simpan index sebelum append

        item_table.append([
            Paragraph(f"<b>{section}</b>", cell_style),
            "", "", "", "", ""
        ])
    
        for item in items:
    
            # ===== SPECIAL CASE: ICT =====
            if item == "ICT Program / Fixture":
    
                # main row
                pic = Paragraph(", ".join(st.session_state.get("pic_ict", [])), cell_style)
                target = st.session_state.get("target_ict", "")
                remark_text = st.session_state.get("remark_ict", "")
                remark = Paragraph(remark_text.replace("\n", "<br/>"), remark_style)
    
                item_table.append([
                    "",
                    Paragraph("ICT Program / Fixture", cell_style),
                    "",
                    pic,
                    target,
                    remark
                ])
    
                # sub rows
                for left, right in ICT_ROWS:
    
                    checked = st.session_state.get(f"ict_{normalize_key(left)}", False)
    
                    pic = Paragraph(", ".join(st.session_state.get(f"pic_ict_{normalize_key(left)}", [])), cell_style)
                    target = Paragraph(str(st.session_state.get(f"target_ict_{normalize_key(left)}", "")).replace("\n","<br/>"), cell_style)
                    remark_text = st.session_state.get(f"remark_ict_{normalize_key(left)}", "")

                    main_checked = st.session_state.get(f"ict_{normalize_key(left)}", False)

                    checkbox_data = {
                        "item": left,
                        "checked": main_checked
                    }

                    if right:
                        right_checked = st.session_state.get(f"ict_{normalize_key(right)}", False)
                        checkbox_data["pair"] = {
                            "label": right,
                            "checked": right_checked
                        }

                    checkbox_json = Paragraph(
                        json.dumps(checkbox_data, indent=1).replace("\n","<br/>"),
                        cell_style
                    )

                    ##########
                    
                    remark = Paragraph(remark_text.replace("\n", "<br/>"), remark_style)
    
                    item_table.append([
                        "",
                        Paragraph(left, cell_style),
                        checkbox_json,
                        pic,
                        target,
                        remark
                    ])
    
            # ===== NORMAL ITEM =====
            else:
                key_base = f"{normalize_key(section)}_{normalize_key(item)}"
    
                pic = Paragraph(", ".join(st.session_state.get(f"pic_{key_base}", [])), cell_style)
                target = Paragraph(str(st.session_state.get(f"target_{key_base}", "")).replace("\n","<br/>"), cell_style)
                remark_text = st.session_state.get(f"remark_{key_base}", "")


                remark = Paragraph(remark_text.replace("\n","<br/>"), remark_style)

                print(remark_text)
    
                item_table.append([
                    "",
                    Paragraph(item, cell_style),
                    "",
                    pic,
                    target,
                    remark
                ])

    ###############
    
    items = Table(item_table, colWidths=[50,120,80,70,60,105], hAlign='LEFT')

    table_style = TableStyle([
        ("LEFTPADDING",(0,0),(-1,-1),4),
        ("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),2),
        ("BOTTOMPADDING",(0,0),(-1,-1),2),
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
    ])
    
    # 🔥 dynamic section styling
    for row_idx in section_row_indices:
        table_style.add("SPAN", (0,row_idx), (5,row_idx))
        table_style.add("BACKGROUND", (0,row_idx), (5,row_idx), colors.lightgrey)
        table_style.add("FONTNAME", (0,row_idx), (5,row_idx), "Helvetica-Bold")
    
    items.setStyle(table_style)

    elements.append(items)

    doc.build(elements)

    buffer.seek(0)

    return buffer
