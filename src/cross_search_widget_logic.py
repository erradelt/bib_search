import sys
import os
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui
from cross_search_widget import Ui_Form

class CrossSearchLogicWidget(QtWidgets.QWidget):
    def __init__(self, dir_name):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.dir_name = dir_name
        self.current_root_path = ""
        self.ui.checkBox.setText(dir_name)
        self.setMinimumHeight(250)

        self.ui.treeView.setAlternatingRowColors(True)
        self.ui.treeView.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.ui.treeView.itemActivated.connect(self.on_item_double_clicked)
        self.ui.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.open_context_menu)
        self.ui.treeView.setHeaderHidden(True)

    def display_results(self, results, root_path):
        self.current_root_path = root_path
        self.ui.treeView.clear()
        self.add_items(self.ui.treeView.invisibleRootItem(), results, [])
        self.ui.treeView.expandAll()


    def clear_results(self):
        self.ui.treeView.clear()

    def add_items(self, parent, elements, relative_components):
        for key, value in elements.items():
            new_rel = relative_components + [key]
            if self.current_root_path:
                root_last = Path(self.current_root_path).parts[-1]
                if len(new_rel) > 1 and new_rel[0] == root_last:
                    stored_rel_path = new_rel[1:]
                else:
                    stored_rel_path = new_rel
            else:
                stored_rel_path = new_rel

            item = QtWidgets.QTreeWidgetItem(parent, [key])
            item.setData(0, 1000, tuple(stored_rel_path))

            if isinstance(value, dict) and value:
                font = QtGui.QFont()
                font.setBold(True)
                item.setFont(0, font)
                self.add_items(item, value, new_rel)

    def on_item_double_clicked(self, item, column):
        rel_path_tuple = item.data(0, 1000)
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
        item = self.ui.treeView.itemAt(position)
        if item:
            menu = QtWidgets.QMenu()
            copy_action = menu.addAction("Pfad kopieren")
            action = menu.exec_(self.ui.treeView.mapToGlobal(position))
            if action == copy_action:
                self.copy_item_path(item)

    def copy_item_path(self, item):
        rel_path_tuple = item.data(0, 1000)
        if rel_path_tuple and self.current_root_path:
            full_path = Path(self.current_root_path).joinpath(*rel_path_tuple)
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(str(full_path))

    def toggle_collapse(self, state):
        if state == QtCore.Qt.Checked:
            self.ui.treeView.collapseAll()
            for i in range(self.ui.treeView.topLevelItemCount()):
                self.ui.treeView.topLevelItem(i).setExpanded(True)
        else:
            self.ui.treeView.expandAll()
