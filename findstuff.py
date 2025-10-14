import filepathgen as fg

with open(fg.current_directory+"/biboliste.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

search = input('was suchst?: ')

for item in lines:
    if search in item:
        print(item)