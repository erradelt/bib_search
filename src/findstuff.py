import filepathgen as fg
import re

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
    
    replacements = [
    lambda s: s,
    lambda s: s.lower(), # first character lower
    lambda s: s.capitalize(),
    lambda s: s.replace(' ', '-'),
    lambda s: s.replace(' ', '_'),
    lambda s: s.replace('-', '_'),
    lambda s: s.replace('-', ' '),
    lambda s: s.replace('ä', 'ae'),
    lambda s: s.replace('ü', 'ue'),
    lambda s: s.replace('ö', 'oe'),
    lambda s: s.replace('ae', 'ä'),
    lambda s: s.replace('ue', 'ü'),
    lambda s: s.replace('oe', 'ö'),
    lambda s: re.sub(r"-(\w)", lambda m: "-" + m.group(1).upper(), ('HF' + s[2:] if s.lower().startswith('hf') else s)),
    lambda s: re.sub(r"-(\w)", lambda m: "-" + m.group(1).upper(), ('OP' + s[2:] if s.lower().startswith('op') else s))
    ]
    
    results = []
    for item in text_lines:
        for func in replacements:
            if func(search_term) in item:
                results.append(item)
                break
        
    if not results:
            results.append(f'keine Suchergebnisse für {search_term} gefunden')
        
    return results