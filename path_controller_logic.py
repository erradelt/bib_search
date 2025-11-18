from PyQt5 import QtWidgets, QtCore
from path_controller_widget import Ui_Form
import json
from pathlib import Path
import pars_V2

class RescanWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, path, name):
        super().__init__()
        self.path = path
        self.name = name

    def run(self):
        pars_V2.generate_bibliography(self.path, self.name)
        self.finished.emit()

class PathController(QtWidgets.QWidget):
    radio_button_toggled = QtCore.pyqtSignal(bool, str)
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
        self.load_metadata()

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
                self.ui.label_2.setText(f"last parsed: {metadata.get('last_parsed', 'N/A')}")
                self.ui.label_3.setText(f"parsetime: {metadata.get('parsetime', 'N/A')}s")
                self.ui.label_4.setText(f"parsed dirs: {metadata.get('parsed_dirs', 'N/A')}")
                self.ui.label_5.setText(f"parsed files: {metadata.get('parsed_files', 'N/A')}")
            else:
                self.set_default_labels()
        except (FileNotFoundError, json.JSONDecodeError):
            self.set_default_labels()

    def set_default_labels(self):
        self.ui.label_2.setText("last parsed: N/A")
        self.ui.label_3.setText("parsetime: N/A")
        self.ui.label_4.setText("parsed dirs: N/A")
        self.ui.label_5.setText("parsed files: N/A")

    def rescan_directory(self):
        self.ui.pushButton.setEnabled(False)
        self.thread = QtCore.QThread()
        self.worker = RescanWorker(self.dir_path, self.dir_name)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_rescan_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_rescan_finished(self):
        self.ui.pushButton.setEnabled(True)
        self.load_metadata()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Verzeichnis erfolgreich neu gescannt!")
        msg.setWindowTitle("Scan abgeschlossen")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
