import sys
import os
from pathlib import Path
import json
from PyQt5 import QtWidgets, QtCore, QtGui
from search_window_universal import Ui_SearchWindowUniversal
from path_manager_logic import PathManager
from findstuff_V2 import results_as_dict
import findstuff_V2
from endings import endings

class SearchWindowUniversal(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SearchWindowUniversal()
        self.ui.setupUi(self)
        self.current_root_path = ""

        self.ui.pushButton.clicked.connect(self.search_files)
        self.ui.pushButton_2.clicked.connect(self.open_path_manager)
        self.ui.pushButton_2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.pushButton_2.customContextMenuRequested.connect(self.show_directory_context_menu)
        self.ui.lineEdit.returnPressed.connect(self.search_files)
        self.ui.treeWidget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.ui.treeWidget.itemActivated.connect(self.on_item_double_clicked)
        self.ui.treeWidget.setAlternatingRowColors(True)
        self.ui.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.treeWidget.customContextMenuRequested.connect(self.open_context_menu)

        self.other_checkboxes = [
            self.ui.checkBox_2,
            self.ui.checkBox_3,
            self.ui.checkBox_4,
            self.ui.checkBox_5,
            self.ui.checkBox_6,
            self.ui.checkBox_7,
            self.ui.checkBox_8,
            self.ui.checkBox_9,
        ]

        self.ui.checkBox.setChecked(True)
        for cb in self.other_checkboxes:
            cb.setChecked(True)

        self.ui.checkBox.stateChanged.connect(self.alles_state_changed)
        for cb in self.other_checkboxes:
            cb.stateChanged.connect(self.other_state_changed)

        self.ui.checkBox_10.stateChanged.connect(self.toggle_collapse)

        self.update_active_directory_label()

    def show_directory_context_menu(self, position):
        try:
            with open("directories.json", "r", encoding="utf-8") as f:
                directories = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            directories = {}

        if not directories:
            return

        menu = QtWidgets.QMenu()
        for dir_name in directories:
            action = menu.addAction(dir_name)
            action.triggered.connect(lambda checked, name=dir_name: self.set_active_directory(name))

        global_pos = self.ui.pushButton_2.mapToGlobal(position)
        menu.exec_(global_pos)

    def set_active_directory(self, dir_name):
        try:
            with open('active_path.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        data['active'] = dir_name
        with open('active_path.json', 'w') as f:
            json.dump(data, f, indent=4)

        self.update_active_directory_label()
        self.ui.treeWidget.clear()

    def toggle_collapse(self, state):
        if state == QtCore.Qt.Checked:
            self.ui.treeWidget.collapseAll()
            for i in range(self.ui.treeWidget.topLevelItemCount()):
                self.ui.treeWidget.topLevelItem(i).setExpanded(True)
        else:
            self.ui.treeWidget.expandAll()
        
        try:
            with open('active_path.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        data['collapse_state'] = self.ui.checkBox_10.isChecked()
        
        with open('active_path.json', 'w') as f:
            json.dump(data, f, indent=4)

    def update_active_directory_label(self):
        active_dir_name = 'Bilder' # Default
        try:
            active_path_file = Path(__file__).resolve().parent / "active_path.json"
            with open(active_path_file, "r", encoding="utf-8") as f:
                active_path_data = json.load(f)
                active_dir_name = active_path_data.get("active", 'Bilder')
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        self.ui.label_3.setText(active_dir_name)

    def alles_state_changed(self, state):
        is_checked = self.ui.checkBox.isChecked()
        for cb in self.other_checkboxes:
            cb.blockSignals(True)
            cb.setChecked(is_checked)
            cb.blockSignals(False)

    def other_state_changed(self, state):
        self.ui.checkBox.blockSignals(True)
        if all(cb.isChecked() for cb in self.other_checkboxes):
            self.ui.checkBox.setChecked(True)
        else:
            self.ui.checkBox.setChecked(False)
        self.ui.checkBox.blockSignals(False)

    def get_selected_file_formats(self):
        checkbox_mapping = {
            self.ui.checkBox_2: "pdf",
            self.ui.checkBox_5: "doc",
            self.ui.checkBox_6: "xls",
            self.ui.checkBox_7: "dwg",
            self.ui.checkBox_3: "pic",
            self.ui.checkBox_4: "vid",
            self.ui.checkBox_8: "aud",
            self.ui.checkBox_9: "msg",
        }

        selected_formats = []
        for checkbox, key in checkbox_mapping.items():
            if checkbox.isChecked():
                selected_formats.extend(endings[key])

        return selected_formats

    def search_files(self):
        findstuff_V2.file_formats = self.get_selected_file_formats()
        self.ui.treeWidget.clear()
        search_term = self.ui.lineEdit.text()
        results, self.current_root_path = results_as_dict(search_term)
        self.add_items(self.ui.treeWidget.invisibleRootItem(), results, [])
        self.toggle_collapse(self.ui.checkBox_10.checkState())

    def add_items(self, parent, elements, relative_components):
        for key, value in elements.items():
            # Build new relative path components
            new_rel = relative_components + [key]

            # If the first component duplicates last part of root_path, remove it
            if self.current_root_path:
                root_last = Path(self.current_root_path).parts[-1]
                if len(new_rel) > 1 and new_rel[0] == root_last:
                    stored_rel_path = new_rel[1:]
                else:
                    stored_rel_path = new_rel
            else:
                stored_rel_path = new_rel

            item = QtWidgets.QTreeWidgetItem(parent, [key])
            # Store relative components as tuple directly
            item.setData(0, 1000, tuple(stored_rel_path))

            # If the value is a non-empty dictionary, it's a folder.
            if isinstance(value, dict) and value:
                font = QtGui.QFont()
                font.setBold(True)
                item.setFont(0, font)
                self.add_items(item, value, new_rel)

    def on_item_double_clicked(self, item, column):
        rel_path_tuple = item.data(0, 1000)  # tuple of components
        if not self.current_root_path:
            return
        full_path = Path(self.current_root_path).joinpath(*rel_path_tuple)

        if full_path.exists():
            try:
                if sys.platform.startswith("darwin"):
                    import subprocess

                    subprocess.Popen(["open", str(full_path)])
                elif sys.platform.startswith("linux"):
                    import subprocess

                    subprocess.Popen(["xdg-open", str(full_path)])
                elif sys.platform.startswith("win"):
                    os.startfile(str(full_path))
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Fehler",
                    f"Konnte nicht geöffnet werden:\n{e}\n\nPfad: {full_path}",
                )
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "Nicht gefunden",
                f"Pfad existiert nicht:\n\n{full_path}",
            )

    def open_context_menu(self, position):
        item = self.ui.treeWidget.itemAt(position)
        if item:
            menu = QtWidgets.QMenu()
            copy_action = menu.addAction("Pfad kopieren")
            action = menu.exec_(self.ui.treeWidget.mapToGlobal(position))
            if action == copy_action:
                self.copy_item_path(item)

    def open_path_manager(self):
        dialog = PathManager()
        dialog.exec_()
        self.update_active_directory_label()

    def copy_item_path(self, item):
        rel_path_tuple = item.data(0, 1000)
        if rel_path_tuple and self.current_root_path:
            full_path = Path(self.current_root_path).joinpath(*rel_path_tuple)
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(str(full_path))
