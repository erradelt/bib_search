from pathlib import Path

import filepathgen as fg

path = Path(
    r"D:\Planungsgruppe M+M AG\Standort Böblingen - Dokumente\Bereichsordner MLB\02_Bereich_MLB\Medizintechnik"
)


def bib_parser(path):
    with open("biboliste.txt", "w", encoding="utf-8") as f:
        for file in path.rglob("*"):
            if "0...00_ARCHIV_Unterlagen" not in file.parts:  # exclude archiv
                if file.suffix in (
                    ".pdf",
                    ".doc",
                    ".docx",
                    ".xls",
                    ".xlsx",
                    ".dwg",
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".exe",
                    ".mp4",
                    ".JPG",
                    ".mpg",
                    ".htm",
                    ".gif",
                ):
                    f.write(
                        f"{file}\n".strip(
                            "D:\Planungsgruppe M+M AG\Standort Böblingen - Dokumente\Bereichsordner MLB\02_Bereich_MLB\Medizintechnik"
                        )
                    )
