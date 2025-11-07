import filepathgen as fg
import os

def file_loader():
    """Loads lines from biboliste.txt. Returns an empty list if not found."""
    try:
        with open(fg.current_directory + "/biboliste.txt", "r", encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        return []

source = file_loader()

for item in source:
    if ".doc" in item:
        print(os.path.basename(item))