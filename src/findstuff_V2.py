import filepathgen as fg
import re
import json

js_path = fg.current_directory + "/bibo.json"


def file_loader():
    """Loads lines from biboliste.txt. Returns an empty list if not found."""
    try:
        with open(js_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}


data = file_loader()

# list that contains functions to manipulate inputstring (searchterm)
replacements = [
    lambda s: s,
    lambda s: s.lower(),
    lambda s: s.capitalize(),
    lambda s: s.replace(" ", "-"),
    lambda s: s.replace(" ", "_"),
    lambda s: s.replace("-", "_"),
    lambda s: s.replace("-", " "),
    lambda s: s.replace("ä", "ae"),
    lambda s: s.replace("ü", "ue"),
    lambda s: s.replace("ö", "oe"),
    lambda s: s.replace("ae", "ä"),
    lambda s: s.replace("ue", "ü"),
    lambda s: s.replace("oe", "ö"),
    lambda s: re.sub(
        r"-(\w)",
        lambda m: "-" + m.group(1).upper(),
        ("HF" + s[2:] if s.lower().startswith("hf") else s),
    ),
    lambda s: re.sub(
        r"-(\w)",
        lambda m: "-" + m.group(1).upper(),
        ("OP" + s[2:] if s.lower().startswith("op") else s),
    ),
]


# generate list (set) that contains als variants of the searchterm. use set so no duplicates can exist
def search_variants(target):
    variants = set()
    for func in replacements:
        try:
            variants.add(func(target))
        except Exception:
            continue
    return variants


# find/confirm existance of searchterm
def find_doc(structure, target):
    variants = search_variants(target)
    for key, value in structure.items():
        for variant in variants:
            if variant.lower() in key.lower():
                return True
        if isinstance(value, dict):
            if find_doc(value, target):
                return True
    return False


# find all pathes of a given searchterm
def find_path(structure, target, current_path=None, pathlist=None):
    current_path = current_path or []
    pathlist = pathlist or []
    variants = search_variants(target)

    for key, value in structure.items():
        new_path = current_path + [key]
        if any(variant.lower() in key.lower() for variant in variants):
            # pathlist.append("/".join(new_path))
            pathlist.append(new_path)
        if isinstance(value, str):
            if any(variant.lower() in value.lower() for variant in variants):
                pathlist.append(new_path)
                # pathlist.append("/".join(new_path))
        if isinstance(value, dict):
            pathlist = find_path(value, target, new_path, pathlist)
    for p in pathlist:
        for item in p:
            if item.endswith((".jpg",".docx")):
                filtered_pathlist.append(p)
            
    return filtered_pathlist





# makes lists into dicts
def sort_results(tree, path):
    current = tree
    for part in path:
        current = current.setdefault(part, {})
    return tree


# passes the paths (variable "results") to def sort_results and an empty tree to start with
def results_as_dict(search_term):
    paths = find_path(data, search_term)
    tree = {}
    for p in paths:
        sort_results(tree, p)

    return tree
