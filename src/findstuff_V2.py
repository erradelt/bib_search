import re
from pathlib import Path
import json

def file_loader(dir_name):
    project_root = Path(__file__).resolve().parent.parent
    dirs = project_root / "dirs"
    js_path = dirs / f"{dir_name}.json"

    try:
        with open(js_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("data", {})
    except FileNotFoundError:
        return {}

data = {}
file_formats = []

def load_active_data():
    """
    Loads the data from the json file corresponding to the active path
    set in the PathManager. Also returns the root path for that directory.
    """
    global data
    active_dir_name = 'default' # Default value
    active_dir_path = ''

    # Get the active directory name
    try:
        active_path_file = Path(__file__).resolve().parent / "active_path.json"
        with open(active_path_file, "r", encoding="utf-8") as f:
            active_path_data = json.load(f)
            active_dir_name = active_path_data.get("active", 'Bilder')
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Get the path for the active directory
    try:
        dirs_file = Path(__file__).resolve().parent / "directories.json"
        with open(dirs_file, "r", encoding="utf-8") as f:
            dirs_data = json.load(f)
            active_dir_path = dirs_data.get(active_dir_name)
    except (FileNotFoundError, json.JSONDecodeError):
        active_dir_path = ""

    data = file_loader(active_dir_name)
    return active_dir_path

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
def find_path_recursive(structure, variants, current_path, pathlist, found_in_parent):
    """Helper that recursively finds file paths matching search criteria."""
    for key, value in structure.items():
        new_path = current_path + [key]
        key_matches = any(variant.lower() in key.lower() for variant in variants)

        if value is None:  # It's a file
            if found_in_parent or key_matches:
                pathlist.append(new_path)
        elif isinstance(value, dict):  # It's a directory
            find_path_recursive(
                value, variants, new_path, pathlist, found_in_parent or key_matches
            )


def find_path(structure, target):
    """
    Finds all FILE paths where the search term matches a component of the path
    (a folder or the filename).
    """
    variants = search_variants(target)
    pathlist = []
    find_path_recursive(structure, variants, [], pathlist, False)
    return pathlist


# makes lists into dicts
def sort_results(tree, path):
    current = tree
    for part in path:
        current = current.setdefault(part, {})
    return tree


# passes the paths (variable "results") to def sort_results and an empty tree to start with
def results_as_dict(search_term, dict_name=None):
    """
    Finds all file paths matching the search term, filters them by the selected
    file formats, and returns the results as a nested dictionary and the active dir path.
    """
    global data
    active_dir_path = ''

    if dict_name:
        data = file_loader(dict_name)
        try:
            dirs_file = Path(__file__).resolve().parent / "directories.json"
            with open(dirs_file, "r", encoding="utf-8") as f:
                dirs_data = json.load(f)
                active_dir_path = dirs_data.get(dict_name)
        except (FileNotFoundError, json.JSONDecodeError):
            active_dir_path = ""
    else:
        active_dir_path = load_active_data()

    # 1. Get all file paths where a component matches the search term.
    # This is efficient as it only traverses the data tree once.
    all_matching_files = find_path(data, search_term)

    # 2. Filter these file paths by the selected file formats.
    tree = {}
    if not file_formats:
        return tree, active_dir_path

    formats_tuple = tuple(file_formats)
    for path in all_matching_files:
        # The last component of the path is the filename.
        if path and path[-1].endswith(formats_tuple):
            sort_results(tree, path)

    return tree, active_dir_path
