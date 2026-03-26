import pdfplumber
import re
import json

def extract_revision_from_filename(filename):
    match = re.search(r"Rev[_\s]?([A-Z])", filename, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

def parse_checkbox_json(text):
    try:
        print("DEBUG BUFFER:", buffer)
        return json.loads(text)
    except:
        return None

def is_checked(val):
    return val in ["✓", "✔", "√", "v", "V", "x", "X", "3"]
    
def read_pdf(uploaded_file):

    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

            print("==== PDF TEXT ====")
            print(text[:2000])

    return text

def parse_form(text, uploaded_file):
  
    lines = text.split("\n")

    data = extract_project_data(lines)
    member_plant = extract_member_plant(lines)
    member_pcis = extract_member_pcis(lines)
    with pdfplumber.open(uploaded_file) as pdf:
        item_check = extract_item_check_from_tables(pdf)
        
    revision_from_file = extract_revision_from_filename(uploaded_file.name)

    project_data = {
        "project_name": data.get("project_name",""),
        "customer": data.get("customer",""),
        "build_type": data.get("build_type",""),
        "pci": data.get("pci",""),
        "project_account": data.get("project_account",""),
        "product_type": data.get("product_type",""),
        "revision": revision_from_file or data.get("revision", None),
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
                data["revision"] = None

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

            parts = line.split()

            email_index = None
            for i, p in enumerate(parts):
                if "@" in p:
                    email_index = i
                    break

            if email_index is None:
                continue

            email = parts[email_index]
            after_email = line.split(email)[-1]
            tokens = after_email.split()

            M1 = is_checked(tokens[0]) if len(tokens) > 0 else False
            M2 = is_checked(tokens[1]) if len(tokens) > 1 else False
            M3 = is_checked(tokens[2]) if len(tokens) > 2 else False
            M4 = is_checked(tokens[3]) if len(tokens) > 3 else False

            before_email = parts[:email_index]
            dept_words = department.split()

            if before_email[:len(dept_words)] == dept_words:
                remaining_parts = before_email[len(dept_words):]
            else:
                remaining_parts = before_email

            if len(remaining_parts) >= 2:
                name = " ".join(remaining_parts[:-1])
                ext = remaining_parts[-1]
                
            elif len(remaining_parts) == 1 :
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
                "m1": M1,
                "m2": M2,
                "m3": M3,
                "m4": M4
            }

            member["department"] = member["department"].strip()

            members.append(member)
            
    return members

def extract_member_pcis(lines):

    members = []
    start = None
    end = None

    for i, line in enumerate(lines):

        if "PROJECT TEAM MEMBERS (PCIS)" in line:
            start = i

        if "ITEM" in line.upper() and "CHECK" in line.upper():
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
                after_email = line.split(email)[-1]
                tokens = after_email.split()

                name = parts[email_index - 1] if email_index > 0 else ""
                department = " ".join(parts[:email_index - 1])
                
                M1 = is_checked(tokens[0]) if len(tokens) > 0 else False
                M2 = is_checked(tokens[1]) if len(tokens) > 1 else False
                M3 = is_checked(tokens[2]) if len(tokens) > 2 else False
                M4 = is_checked(tokens[3]) if len(tokens) > 3 else False

                member = {
                    "department": department.strip(),
                    "name": name.strip(),
                    "email": email.strip(),
                    "m1": M1,
                    "m2": M2,
                    "m3": M3,
                    "m4": M4
                }

                members.append(member)

    return members
    
def extract_item_check(lines):

    items = []

    buffer = ""
    bracket_count = 0
    capturing = False

    for line in lines:
        # count bracket 
        open_brace = line.count("{")
        close_brace = line.count("}")

        if open_brace > 0:
            capturing = True

        if capturing:
            buffer += line.strip() + " "
            bracket_count += open_brace
            bracket_count -= close_brace 

        if capturing and bracket_count == 0:
            capturing = False
            data = parse_checkbox_json(buffer.strip())

            if data:
                item_name = None
                checked = data.get("checked", False)

                pair_label = None
                pair_checked = False

                if "pair" in data:
                    pair_label = data["pair"].get("label")
                    pair_checked = data["pair"].get("checked", False)

                items.append({
                    "item": item_name,
                    "checked": checked,
                    "pair_label": pair_label,
                    "pair_checked": pair_checked
                })

            buffer = ""

    return items

def extract_item_check_from_tables(pdf):
    items = []
    for page in pdf.pages:
        tables = page.extract_tables()

        for table in tables:
            for row in table:
                if not row or len(row) < 5:
                    continue

                item_name = row[1]
                json_cell = row[2]
                pic = row[3]
                target = row[4]
                remark = row[5] if len(row) > 5 else ""

                if not json_cell or "{" not in json_cell:
                    continue

                try:
                    data = json.loads(json_cell)
                    checked = data.get("checked", False)
                    pair_label = None
                    pair_checked = False

                    if "pair" in data:
                        pair_label = data["pair"].get("label")
                        pair_checked = data["pair"].get("checked", False)

                        items.append({
                            "item": item_name,
                            "checked": checked,
                            "pair_label": pair_label,
                            "pair_checked": pair_checked,
                            "pic":pic,
                            "target": target,
                            "remark": remark
                        })

                except Exception as e:
                    print("JSON ERROR:", e)

    return items

              
