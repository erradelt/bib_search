import sys
import os
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui
from search_window import Ui_MainWindow
from bib_pars_V2 import generate_bibliography, root_path
from findstuff_V2 import results_as_dict
import findstuff_V2
from endings import endings


class BibliographyWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def run(self):
        generate_bibliography()
        self.finished.emit()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.search_files)
        self.ui.pushButton_3.clicked.connect(self.update_bibliography)
        self.ui.pushButton_2.clicked.connect(self.close)
        self.ui.lineEdit.returnPressed.connect(self.search_files)
        self.ui.treeWidget.itemDoubleClicked.connect(self.on_item_double_clicked)
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
        ]

        self.ui.checkBox.setChecked(True)
        for cb in self.other_checkboxes:
            cb.setChecked(True)

        self.ui.checkBox.stateChanged.connect(self.alles_state_changed)
        for cb in self.other_checkboxes:
            cb.stateChanged.connect(self.other_state_changed)

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
        results = results_as_dict(search_term)
        # We start recursive add with empty list as relative path
        self.add_items(self.ui.treeWidget.invisibleRootItem(), results, [])
        self.ui.treeWidget.expandAll()

    def add_items(self, parent, elements, relative_components):
        for key, value in elements.items():
            # Build new relative path components
            new_rel = relative_components + [key]

            # If the first component duplicates last part of root_path, remove it
            root_last = Path(root_path).parts[-1]
            if len(new_rel) > 1 and new_rel[0] == root_last:
                stored_rel_path = new_rel[1:]
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
        full_path = Path(root_path).joinpath(*rel_path_tuple)

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

    def copy_item_path(self, item):
        rel_path_tuple = item.data(0, 1000)
        if rel_path_tuple:
            full_path = Path(root_path).joinpath(*rel_path_tuple)
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(str(full_path))

    def update_bibliography(self):
        self.ui.pushButton_3.setEnabled(False)
        self.thread = QtCore.QThread()
        self.worker = BibliographyWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_bibliography_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_bibliography_finished(self):
        self.ui.pushButton_3.setEnabled(True)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Verzeichnis erfolgreich geladen!")
        msg.setWindowTitle("Verzeichnis geladen")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
