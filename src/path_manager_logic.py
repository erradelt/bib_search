import json
import os
from pathlib import Path
from PyQt5 import QtWidgets
from path_manager_ui import Ui_Dialog
from new_dir_path_dialog import Ui_Dialog as NewDirDialogUI
from pars_call import parscaller
from path_controller_logic import PathController
from scan_dialog_logic import ScanDialog

class PathManager(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.open_new_dir_dialog)

        # Prepare the scroll area
        self.scroll_layout = QtWidgets.QVBoxLayout(self.ui.scrollAreaWidgetContents)
        self.ui.scrollAreaWidgetContents.setLayout(self.scroll_layout)
        self.button_group = QtWidgets.QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.load_paths()

    def load_paths(self):
        # Clear existing widgets
        for i in reversed(range(self.scroll_layout.count())):
            widget_to_remove = self.scroll_layout.itemAt(i).widget()
            if widget_to_remove:
                if isinstance(widget_to_remove, PathController):
                    self.button_group.removeButton(widget_to_remove.ui.radioButton)
                widget_to_remove.setParent(None)

        try:
            with open("directories.json", "r", encoding="utf-8") as f:
                directories = json.load(f)
        except FileNotFoundError:
            directories = {}

        for dir_name, dir_path in sorted(directories.items()):
            path_widget = PathController(dir_name, dir_path)
            self.scroll_layout.addWidget(path_widget)
            self.button_group.addButton(path_widget.ui.radioButton)
            path_widget.radio_button_toggled.connect(self.on_path_selected)
            path_widget.delete_requested.connect(self.handle_delete_request)
            path_widget.name_changed.connect(self.handle_name_change)

            line = QtWidgets.QFrame()
            line.setFrameShape(QtWidgets.QFrame.HLine)
            line.setFrameShadow(QtWidgets.QFrame.Sunken)
            self.scroll_layout.addWidget(line)
        self.check_active_path()

    def handle_name_change(self, old_name, new_name):
        self.load_paths()
        # also update active path if the renamed one was active
        try:
            with open("active_path.json", "r", encoding="utf-8") as f:
                active_path_data = json.load(f)
            if active_path_data.get("active") == old_name:
                with open("active_path.json", "w", encoding="utf-8") as f:
                    json.dump({"active": new_name}, f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass # No active path file, nothing to do

    def handle_delete_request(self, dir_name):
        # 1. Update directories.json
        try:
            with open("directories.json", "r", encoding="utf-8") as f:
                directories = json.load(f)
            if dir_name in directories:
                del directories[dir_name]
            with open("directories.json", "w", encoding="utf-8") as f:
                json.dump(directories, f, indent=4)
        except FileNotFoundError:
            pass

        # 2. Delete the data file
        project_root = Path(__file__).resolve().parent.parent
        dirs_path = project_root / "dirs"
        json_file_to_delete = dirs_path / f"{dir_name}.json"
        if os.path.exists(json_file_to_delete):
            os.remove(json_file_to_delete)

        # 3. Refresh the UI
        self.load_paths()

    def check_active_path(self):
        try:
            with open("active_path.json", "r", encoding="utf-8") as f:
                active_path_data = json.load(f)
                active_dir_name = active_path_data.get("active")
        except (FileNotFoundError, json.JSONDecodeError):
            active_dir_name = None

        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if isinstance(widget, PathController) and widget.dir_name == active_dir_name:
                widget.ui.radioButton.setChecked(True)
                break

    def on_path_selected(self, checked, dir_name):
        if checked:
            with open("active_path.json", "w", encoding="utf-8") as f:
                json.dump({"active": dir_name}, f)

    def open_new_dir_dialog(self):
        dialog = QtWidgets.QDialog()
        ui = NewDirDialogUI()
        ui.setupUi(dialog)
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            dir_name = ui.dir_name.text()
            dir_path = ui.dir_path.text()
            if dir_name and dir_path:
                # Update directories.json immediately, but don't run the
                # potentially long parse synchronously. Start the parsing
                # inside the existing ScanDialog so the user sees progress.
                parscaller(dir_name, dir_path, run_parse=False)

                # Start a ScanDialog to run the parsing in the background
                scan_dialog = ScanDialog(dir_path, dir_name, parent=self)
                # When the scan finishes, refresh the path list
                scan_dialog.finished.connect(lambda res=None: self.load_paths())
                scan_dialog.open()
