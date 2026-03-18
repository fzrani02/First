import pdfplumber
import re

def read_pdf(uploaded_file):

    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    return text

def parse_form(text):
    lines = text.split("\n")

    data = extract_project_data(lines)
    member_plant = extract_member_plant(lines)
    member_pcis = extract_member_pcis(lines)
    item_check = extract_item_check(lines)

    project_data = {
        "project_name": data.get("project_name",""),
        "customer": data.get("customer",""),
        "build_type": data.get("build_type",""),
        "pci": data.get("pci",""),
        "project_account": data.get("project_account",""),
        "product_type": data.get("product_type",""),
        "revision": data.get("revision","A"),
        "date_updated": data.get("date_updated","")
    }

    return {
        "project_data": project_data,
        "member_plant": member_plant,
        "member_pcis": member_pcis,
        "item_check": item_check
    }


def extract_project_data(lines):

    data = {}

    for line in lines:

        if "Project Name" in line and "Customer" in line:
            parts = line.split()
            data["project_name"] = parts[2]
            data["customer"] = parts[-1]

        if "Build Type" in line and "PCI FG" in line:
            parts = line.split()
            data["build_type"] = parts[2]
            data["pci"] = parts[-1]

        if "Project Account" in line and "Product Type" in line:
            parts = line.split()
            data["project_account"] = parts[2]
            data["product_type"] = parts[-1]

        if "Date Updated" in line:
            parts = line.split()
            data["date_updated"] = parts[2]

        if "Revision" in line:
            parts = line.split()
            if len(parts) > 2:
                data["revision"] = parts[-1]
            else:
                data["revision"] = "A"

    return data

def extract_member_plant(lines):

    members = []
    departments_master = [
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

    start = None
    end = None

    for i, line in enumerate(lines):

        if "PROJECT TEAM MEMBERS (PLANT)" in line:
            start = i

        if "PROJECT TEAM MEMBERS (PCIS)" in line:
            end = i
            break

    if start is not None and end is not None:

        for line in lines[start:end]:

            if "@" not in line:
                continue

            parts = line.split()

            email = next((p for p in parts if "@" in p), None)

            if not email:
                continue

            department = None
            for dept in departments_master:
                if dept in line:
                    department = dept
                    break

            if not department:
                continue

            remaining = line.replace(department, "").replace(email, "").strip()
            remaining_parts = remaining.split()

            if len(remaining_parts) == 2:
                name = remaining_parts[0]
                ext = remaining_parts[1]
            elif len(remaining_parts) == 1:
                name = remaining_parts[0]
                ext = ""
            else:
                name = ""
                ext = ""

            member = {
                "department": department,
                "name": name, 
                "email": email,
                "ext": ext,
                "M1": "✓" in line,
                "M2": False,
                "M3": False,
                "M4": False
            }

            members.append(member)
            
    return members

def extract_member_pcis(lines):

    members = []
    start = None
    end = None

    for i, line in enumerate(lines):

        if "PROJECT TEAM MEMBERS (PCIS)" in line:
            start = i

        if "ITEMS TO CHECK" in line:
            end = i
            break

    if start is not None and end is not None:

        for line in lines[start:end]:

            if "Engineer" in line or "Manager" in line:

                parts = line.split()
                
                email_index = None

                for i, p in enumerate(parts):
                    if "@" in p:
                        email_index = i
                        break

                if email_index is None:
                    continue

                email = parts[email_index]
                name = parts[email_index - 1] if email_index > 0 else ""
                department = " ".join(parts[:email_index - 1])

                member = {
                    "department": department.strip(),
                    "name": name.strip(),
                    "email": email.strip(),
                    "M1": "✓" in line,
                    "M2": False,
                    "M3": False,
                    "M4": False
                }

                members.append(member)

    return members

def extract_item_check(lines):

    items = []
    start = None

    for i, line in enumerate(lines):

        if "ITEMS TO CHECK" in line:
            start = i
            break

    if start is not None:

        for line in lines[start+1:]:

            parts = line.split()

            if len(parts) >= 2:

                item = {
                    "item": " ".join(parts[:-3]) if len(parts) > 3 else parts[0],
                    "pic": parts[-3] if len(parts) > 3 else "",
                    "target": parts[-2] if len(parts) > 2 else "",
                    "remark": parts[-1] if len(parts) > 1 else ""
                }

                items.append(item)

    return items



