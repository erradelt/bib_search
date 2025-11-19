import pars_V2
import json

def parscaller(dir, path):
    try:
        with open("directories.json", "r", encoding="utf-8") as f:
            directories = json.load(f)
    except FileNotFoundError:
        directories = {}

    directories[dir] = path

    output_file = "directories.json"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(directories, indent=4))

    pars_V2.generate_bibliography(path, dir)

    return directories
