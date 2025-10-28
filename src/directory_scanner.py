import sqlite3
import os

def create_database(db_name):
    """Creates a SQLite database and a table to store directory information."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS directory_structure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            is_file BOOLEAN NOT NULL,
            FOREIGN KEY (parent_id) REFERENCES directory_structure (id)
        )
    ''')
    conn.commit()
    conn.close()

def scan_and_save(directory_path, db_name):
    """Scans a directory and saves its structure to the database."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Add the root directory
    root_name = os.path.basename(os.path.abspath(directory_path))
    c.execute("INSERT INTO directory_structure (name, parent_id, is_file) VALUES (?, ?, ?)",
              (root_name, None, False))
    root_id = c.lastrowid
    conn.commit()

    dir_map = {directory_path: root_id}

    for dirpath, dirnames, filenames in os.walk(directory_path):
        parent_id = dir_map[dirpath]

        for dirname in dirnames:
            c.execute("INSERT INTO directory_structure (name, parent_id, is_file) VALUES (?, ?, ?)",
                      (dirname, parent_id, False))
            new_dir_id = c.lastrowid
            dir_map[os.path.join(dirpath, dirname)] = new_dir_id

        for filename in filenames:
            c.execute("INSERT INTO directory_structure (name, parent_id, is_file) VALUES (?, ?, ?)",
                      (filename, parent_id, True))
    
    conn.commit()
    conn.close()

def print_structure(db_name, parent_id=None, indent=""):
    """Prints the directory structure from the database."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    if parent_id is None:
        c.execute("SELECT id, name, is_file FROM directory_structure WHERE parent_id IS NULL")
    else:
        c.execute("SELECT id, name, is_file FROM directory_structure WHERE parent_id = ?", (parent_id,))
    
    items = c.fetchall()
    conn.close()

    for id, name, is_file in items:
        print(f"{indent}{name}{' (file)' if is_file else ''}")
        if not is_file:
            print_structure(db_name, id, indent + "  ")


if __name__ == "__main__":
    db_name = "directory_scan.db"
    scan_directory = "/home/robert/Python/09_bib_search"

    # Clear the database file if it exists
    if os.path.exists(db_name):
        os.remove(db_name)

    create_database(db_name)
    scan_and_save(scan_directory, db_name)
    print(f"Directory structure of '{scan_directory}' saved to '{db_name}'.")
    print("\n--- Database Contents ---")
    print_structure(db_name)
