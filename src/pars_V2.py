from pathlib import Path
import json
import os
import time
import datetime

def write_dir_json(path: Path, file, indent_level=1, progress_callback=None, should_stop=None, total_counters=None):
    """Schreibt rekursiv die Verzeichnisstruktur, ohne alles in den RAM zu laden.

    `total_counters` is a mutable dict used to accumulate total counts across
    the entire scan run. If provided, progress_callback will be called with the
    running total of directories scanned (so the UI can display a cumulative
    counter). This avoids restarting the displayed count per subdirectory.
    """
    indent = "    " * indent_level
    entries = []

    if total_counters is None:
        total_counters = {"dirs": 0, "files": 0}

    for item in sorted(path.iterdir(), key=lambda p: p.name.lower()):
        # Symlinks ignorieren → verhindert Endlosrekursion
        if item.is_symlink():
            continue
        entries.append(item)

    for index, item in enumerate(entries):
        if should_stop and should_stop():
            # Return placeholders; totals are stored in total_counters
            return 0, 0
        is_last = index == len(entries) - 1

        # Ordner
        if item.is_dir():
            # update global total
            total_counters["dirs"] += 1
            if progress_callback:
                # report cumulative dirs and files
                progress_callback(total_counters["dirs"], total_counters["files"])
            file.write(f"{indent}{json.dumps(item.name)}: {{\n")
            # recurse, passing the same totals dict
            write_dir_json(item, file, indent_level + 1, progress_callback, should_stop, total_counters)
            file.write(f"{indent}}}")
        else:
            # Datei
            total_counters["files"] += 1
            file.write(f"{indent}{json.dumps(item.name)}: null")
            # report cumulative progress after counting a file as well
            if progress_callback:
                progress_callback(total_counters["dirs"], total_counters["files"])

        if not is_last:
            file.write(",\n")
        else:
            file.write("\n")
    return 0, 0


def generate_bibliography(passedpath, dir_name, progress_callback=None, should_stop=None):
    root_path = Path(passedpath)
    project_root = Path(__file__).resolve().parent.parent
    dirs = project_root / "dirs"
    dirs.mkdir(exist_ok=True)

    output_file = dirs / f"{dir_name}.json"
    temp_file_path = output_file.with_suffix(".tmp")

    start_time = time.time()

    totals = {"dirs": 0, "files": 0}
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write("{\n")
        f.write(f"    {json.dumps(root_path.name)}: {{\n")
        write_dir_json(root_path, f, 2, progress_callback, should_stop, totals)
        f.write("    }\n")
        f.write("}\n")

    if should_stop and should_stop():
        os.remove(temp_file_path)
        return None

    end_time = time.time()
    parsetime = round(end_time - start_time, 2)
    last_parsed = datetime.date.today().strftime("%d.%m.%Y")

    with open(output_file, "w", encoding="utf-8") as final_f:
        final_f.write("{\n")
        metadata = {
            "last_parsed": last_parsed,
            "parsetime": parsetime,
            "parsed_dirs": totals.get("dirs", 0),
            "parsed_files": totals.get("files", 0),
        }
        final_f.write(f'    "metadata": {json.dumps(metadata, indent=4)},\n')
        final_f.write('    "data": ')
        with open(temp_file_path, "r", encoding="utf-8") as temp_f:
            final_f.write(temp_f.read())
        final_f.write("\n}\n")

    os.remove(temp_file_path)

    return output_file
