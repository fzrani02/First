def get_revision_week_map():
    return{
        "X": "m2",
        "A": "m3",
        "B": "m4"
    }
    
def get_editable_column(revision, uploaded_pdf):

    if not uploaded_pdf:
        return "m1" 

    revision_map = get_revision_week_map()
    return revisio_map.get(revision, None)

def get_next_revision(revision):

    if revision is None:
        return "A"

    if revision == "A":
        return "B"

    if revision == "B":
        return "C"

    if revision == "C":
        return "C" 

    return "A"
    
