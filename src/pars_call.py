import pars_V2
import json

def parscaller(dir, path, run_parse=True):
    """Add or update an entry in `directories.json`.

    If `run_parse` is True (default), `pars_V2.generate_bibliography` is called
    synchronously. Call with `run_parse=False` if the caller will start the
    parsing in a background thread or dialog (so the UI can show a progress
    dialog for the initial scan).
    """
    try:
        with open("directories.json", "r", encoding="utf-8") as f:
            directories = json.load(f)
    except FileNotFoundError:
        directories = {}

    directories[dir] = path

    output_file = "directories.json"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(directories, indent=4))

    if run_parse:
        pars_V2.generate_bibliography(path, dir)

    return directories
