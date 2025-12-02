from PyQt5 import QtWidgets, QtCore
from path_controller_widget import Ui_Form
import json
from pathlib import Path
import os
from scan_dialog_logic import ScanDialog
from edit_dir_name_dialog_logic import EditDirNameDialog

class PathController(QtWidgets.QWidget):
    radio_button_toggled = QtCore.pyqtSignal(bool, str)
    delete_requested = QtCore.pyqtSignal(str)
    name_changed = QtCore.pyqtSignal(str, str) # old_name, new_name

    def __init__(self, dir_name, dir_path, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.dir_name = dir_name
        self.dir_path = dir_path

        self.ui.radioButton.setText(self.dir_name)
        self.ui.label.setText(self.dir_path)
        self.ui.radioButton.toggled.connect(self.on_radio_button_toggled)
        self.ui.pushButton.clicked.connect(self.rescan_directory)
        self.ui.pushButton_2.clicked.connect(self.prompt_for_delete)
        self.ui.pushButton_3.clicked.connect(self.open_edit_dialog)
        self.load_metadata()

    def open_edit_dialog(self):
        dialog = EditDirNameDialog(self.dir_name, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_name = dialog.get_new_name().strip()
            if new_name and new_name != self.dir_name:
                self.change_dir_name(new_name)

    def change_dir_name(self, new_name):
        try:
            with open("directories.json", "r+", encoding="utf-8") as f:
                directories = json.load(f)
                if new_name in directories:
                    QtWidgets.QMessageBox.warning(self, "Fehler", f"Der Name '{new_name}' existiert bereits.")
                    return

                path = directories.pop(self.dir_name)
                directories[new_name] = path

                f.seek(0)
                f.truncate()
                json.dump(directories, f, indent=4)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            QtWidgets.QMessageBox.warning(self, "Fehler", f"Fehler beim Lesen/Schreiben von directories.json: {e}")
            return

        project_root = Path(__file__).resolve().parent.parent
        dirs_path = project_root / "dirs"
        old_json_path = dirs_path / f"{self.dir_name}.json"
        new_json_path = dirs_path / f"{new_name}.json"

        if old_json_path.exists():
            try:
                os.rename(old_json_path, new_json_path)
            except OSError as e:
                QtWidgets.QMessageBox.warning(self, "Fehler", f"Fehler beim Umbenennen der Datei: {e}")
                with open("directories.json", "r+", encoding="utf-8") as f:
                    directories = json.load(f)
                    path = directories.pop(new_name)
                    directories[self.dir_name] = path
                    f.seek(0)
                    f.truncate()
                    json.dump(directories, f, indent=4)
                return

        old_name = self.dir_name
        self.dir_name = new_name
        self.ui.radioButton.setText(self.dir_name)

        self.name_changed.emit(old_name, self.dir_name)

        QtWidgets.QMessageBox.information(self, "Erfolg", "Verzeichnis erfolgreich umbenannt.")


    def prompt_for_delete(self):
        reply = QtWidgets.QMessageBox.question(self, 'Verzeichnis löschen',
                                               f"Sind Sie sicher, dass Sie das Verzeichnis '{self.dir_name}' löschen möchten?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.delete_requested.emit(self.dir_name)

    def on_radio_button_toggled(self, checked):
        if checked:
            self.radio_button_toggled.emit(checked, self.dir_name)

    def load_metadata(self):
        project_root = Path(__file__).resolve().parent.parent
        dirs = project_root / "dirs"
        js_path = dirs / f"{self.dir_name}.json"
        try:
            with open(js_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            metadata = data.get("metadata")
            if metadata:
                self.ui.label_2.setText(f"letzter Scan: {metadata.get('last_parsed', 'N/A')}")
                self.ui.label_3.setText(f"Scandauer:  {metadata.get('parsetime', 'N/A')}s")
                self.ui.label_4.setText(f"Ordner: {metadata.get('parsed_dirs', 'N/A')}")
                self.ui.label_5.setText(f"Dateien: {metadata.get('parsed_files', 'N/A')}")
            else:
                self.set_default_labels()
        except (FileNotFoundError, json.JSONDecodeError):
            self.set_default_labels()
            
    def set_default_labels(self):
        self.ui.label_2.setText("letzter Scan: N/A")
        self.ui.label_3.setText("Scandauer: N/A")
        self.ui.label_4.setText("Ordner: N/A")
        self.ui.label_5.setText("Dateien: N/A")

    def rescan_directory(self):
        dialog = ScanDialog(self.dir_path, self.dir_name, self)
        dialog.finished.connect(self.on_scan_dialog_finished)
        dialog.open()

    def on_scan_dialog_finished(self, result):
        if result == QtWidgets.QDialog.Accepted:
            self.load_metadata()
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Verzeichnis erfolgreich neu gescannt!")
            msg.setWindowTitle("Scan abgeschlossen")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
