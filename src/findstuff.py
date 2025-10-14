import filepathgen as fg

def file_loader():
    """Loads lines from biboliste.txt. Returns an empty list if not found."""
    try:
        with open(fg.current_directory + "/biboliste.txt", "r", encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        return []

def file_finder(search_term, text_lines):
    """Finds search_term in text_lines and returns a list of matching lines."""
    if not search_term:
        return []
    
    results = []
    for item in text_lines:
        if search_term in item:
            results.append(item)
    return results