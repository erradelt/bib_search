endings = {
    "pdf": [".pdf"],
    "doc": [".doc", ".docx", ".odt"],
    "xls": [".xls", ".xlsx"],
    "dwg": [".dwg", ".dxf"],
    "pic": [".jpg", ".JPG", ".bmp", ".tiff", ".png"],
    "vid": [".mp4", ".mov"]}

# logic for extracting specific file-formats from endings
"""
filter = ["doc", "pic"]

term = []
for i in filter:
    for value in endings[i]:
        term.append(value)

print(term)
"""