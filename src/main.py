import sys
import os
from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from search_window import Ui_MainWindow
from bib_pars_V2 import generate_bibliography, root_path
from findstuff_V2 import results_as_dict


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

    def search_files(self):
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

            if isinstance(value, dict):
                self.add_items(item, value, new_rel)

    def on_item_double_clicked(self, item, column):
        rel_path_tuple = item.data(0, 1000)  # tuple of components
        full_path = Path(root_path).joinpath(*rel_path_tuple).resolve(strict=False)

        # Debug prints
        print("[DEBUG] relative components:", rel_path_tuple)
        print("[DEBUG] concatenated full_path:", str(full_path))
        print("[DEBUG] exists:", full_path.exists())

        if full_path.exists():
            try:
                if sys.platform.startswith("darwin"):
                    import subprocess
                    subprocess.Popen(['open', str(full_path)])
                elif sys.platform.startswith("linux"):
                    import subprocess
                    subprocess.Popen(['xdg-open', str(full_path)])
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
