import sys
import os
import re
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

        # Button-Aktionen
        self.ui.pushButton.clicked.connect(self.search_files)
        self.ui.pushButton_3.clicked.connect(self.update_bibliography)
        self.ui.pushButton_2.clicked.connect(self.close)
        self.ui.lineEdit.returnPressed.connect(self.search_files)

        # TreeView Doppelklick
        self.ui.treeWidget.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Checkboxen
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

    # ----------------------------------------------------------------------
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

    # ----------------------------------------------------------------------
    def search_files(self):
        """Sucht nach Einträgen und füllt den Tree."""
        self.ui.treeWidget.clear()
        search_term = self.ui.lineEdit.text()
        results = results_as_dict(search_term)
        self.add_items(self.ui.treeWidget.invisibleRootItem(), results, [str(root_path)])
        self.ui.treeWidget.expandAll()

    def add_items(self, parent, elements, path_components):
        """Rekursiv Tree füllen."""
        for key, value in elements.items():
            new_path_components = path_components + [key]
            item = QtWidgets.QTreeWidgetItem(parent, [key])
            item.setData(0, 1000, new_path_components)
            if isinstance(value, dict):
                self.add_items(item, value, new_path_components)

    # ----------------------------------------------------------------------
    def on_item_double_clicked(self, item, column):
        """Beim Doppelklick: Datei oder Ordner öffnen."""
        path_components = item.data(0, 1000)
        print("[DEBUG] raw path_components:", path_components)

        # 1️⃣ Säubere Komponenten
        cleaned = []
        for c in path_components:
            s = str(c).strip().strip('"').strip("'")
            if s:
                cleaned.append(s)

        # 2️⃣ Entferne doppelten root_path, falls schon in components
        root_str = str(root_path).rstrip("\\/")
        filtered = []
        for comp in cleaned:
            if comp.startswith(root_str):
                print(f"[DEBUG] Entferne doppelten Rootanteil: {comp}")
                continue
            filtered.append(comp)

        print("[DEBUG] nach Rootfilter:", filtered)

        # 3️⃣ Vollständigen Pfad bauen
        full_path = Path(root_path, *filtered).resolve(strict=False)
        print("[DEBUG] final path:", full_path)
        print("[DEBUG] exists():", full_path.exists())

        # 4️⃣ Prüfen, ob Ordner oder Datei
        if full_path.exists():
            try:
                if full_path.is_dir():
                    # Explorer für Ordner
                    os.startfile(str(full_path))
                else:
                    # Standard-App für Datei
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
                f"Pfad existiert nicht:\n\n{full_path}\n\nKomponenten:\n{filtered}",
            )

    # ----------------------------------------------------------------------
    def update_bibliography(self):
        """Startet den Worker-Thread, um Bibliographie neu zu laden."""
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


# ----------------------------------------------------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

