import pars_V2
import json

dir = input('directory name: ')
path = input ('path: ')

def parscaller(dir, path):
    try:
        with open("directories.json", "r", encoding="utf-8") as f:
            directories = json.load(f)
    except FileNotFoundError:
        directories = {}

    directories[dir] = path

    output_file = "directories.json"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"{json.dumps(directories)}")

    pars_V2.generate_bibliography(path, dir)

    return directories
