endings = {
    "pdf": [".pdf"],
    "doc": [".doc", ".docx", ".odt"],
    "xls": [".xls", ".xlsx"],
    "dwg": [".dwg", ".dxf"],
    "pic": [".jpg", ".JPG", ".bmp", ".tiff", ".png"],
    "vid": [".mp4", ".mov"],
    "aud": [".mp3", ".wav", ".ogg", ".m4a"],
    "msg": [".msg"]}

# logic for extracting specific file-formats from endings
"""
filter = ["doc", "pic"]

term = []
for i in filter:
    for value in endings[i]:
        term.append(value)

print(term)
"""
