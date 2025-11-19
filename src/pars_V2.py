from pathlib import Path
import json
import os
import time
import datetime

def write_dir_json(path: Path, file, indent_level=1, progress_callback=None, should_stop=None):
    """Schreibt rekursiv die Verzeichnisstruktur, ohne alles in den RAM zu laden."""
    indent = "    " * indent_level
    entries = []
    dir_count = 0
    file_count = 0

    for item in sorted(path.iterdir(), key=lambda p: p.name.lower()):
        # Symlinks ignorieren → verhindert Endlosrekursion
        if item.is_symlink():
            continue
        entries.append(item)

    for index, item in enumerate(entries):
        if should_stop and should_stop():
            return dir_count, file_count
        is_last = index == len(entries) - 1

        # Ordner
        if item.is_dir():
            dir_count += 1
            if progress_callback:
                progress_callback(dir_count)
            file.write(f"{indent}{json.dumps(item.name)}: {{\n")
            sub_dirs, sub_files = write_dir_json(item, file, indent_level + 1, progress_callback, should_stop)
            dir_count += sub_dirs
            file_count += sub_files
            file.write(f"{indent}}}")
        else:
            # Datei
            file_count += 1
            file.write(f"{indent}{json.dumps(item.name)}: null")

        if not is_last:
            file.write(",\n")
        else:
            file.write("\n")
    return dir_count, file_count


def generate_bibliography(passedpath, dir_name, progress_callback=None, should_stop=None):
    root_path = Path(passedpath)
    project_root = Path(__file__).resolve().parent.parent
    dirs = project_root / "dirs"
    dirs.mkdir(exist_ok=True)

    output_file = dirs / f"{dir_name}.json"
    temp_file_path = output_file.with_suffix(".tmp")

    start_time = time.time()

    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write("{\n")
        f.write(f"    {json.dumps(root_path.name)}: {{\n")
        dir_count, file_count = write_dir_json(root_path, f, 2, progress_callback, should_stop)
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
            "parsed_dirs": dir_count,
            "parsed_files": file_count,
        }
        final_f.write(f'    "metadata": {json.dumps(metadata, indent=4)},\n')
        final_f.write('    "data": ')
        with open(temp_file_path, "r", encoding="utf-8") as temp_f:
            final_f.write(temp_f.read())
        final_f.write("\n}\n")

    os.remove(temp_file_path)

    return output_file
