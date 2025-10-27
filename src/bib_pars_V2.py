from pathlib import Path
import json
import os

root_path = Path("P:\Projekte\BB18-900")


def write_dir_json(path: Path, file, indent_level=1):
    """Schreibt rekursiv die Verzeichnisstruktur, ohne alles in den RAM zu laden."""
    indent = "    " * indent_level
    entries = []

    # Wir sortieren, damit die Ausgabe stabil ist (optional)
    for item in sorted(path.iterdir(), key=lambda p: p.name.lower()):
        # Symlinks ignorieren → verhindert Endlosrekursion
        if item.is_symlink():
            continue
        entries.append(item)

    for index, item in enumerate(entries):
        is_last = (index == len(entries) - 1)

        # Ordner
        if item.is_dir():
            file.write(f'{indent}{json.dumps(item.name)}: {{\n')
            write_dir_json(item, file, indent_level + 1)
            file.write(f'{indent}}}')
        else:
            # Datei
            file.write(f'{indent}{json.dumps(item.name)}: null')

        if not is_last:
            file.write(",\n")
        else:
            file.write("\n")


def generate_bibliography():
    output_file = "bibo.json"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("{\n")
        f.write(f'    {json.dumps(root_path.name)}: {{\n')
        write_dir_json(root_path, f, 2)
        f.write("    }\n")
        f.write("}\n")


if __name__ == "__main__":
    generate_bibliography()
