def get_editable_column(revision, uploaded_pdf):

    if revision is None and uploaded_pdf is None:
        return 1

    elif revision is None and uploaded_pdf:
        return 2

    elif revision == "A":
        return 3

    elif revision == "B":
        return 4

    else:
        return 1


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
    
