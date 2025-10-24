from pathlib import Path
import filepathgen as fg
import json

root_path = Path(
    r"D:\Planungsgruppe M+M AG\Standort Böblingen - Dokumente\Bereichsordner MLB\02_Bereich_MLB\Medizintechnik")

def parse_dir_to_dict(path: Path) -> dict:
    structure = {}
    for item in path.iterdir():
        if item.is_dir():
            # Ordner → rekursiver Aufruf
            structure[item.name] = parse_dir_to_dict(item)
        else:
            # Datei → Wert kann None oder Info sein
            structure[item.name] = None
    return structure

def generate_bibliography():
    result = {root_path.name: parse_dir_to_dict(root_path)}
    output_file = 'bibo.json'
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    generate_bibliography()