from PyQt5 import QtWidgets, QtCore
from search_window_cross import Ui_MainWindow
from cross_search_widget_logic import CrossSearchLogicWidget
import json
import findstuff_V2
from findstuff_V2 import results_as_dict
from endings import endings

class SearchWindowCross(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Create a QScrollArea and a container widget
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.scroll_area.setSizePolicy(sizePolicy)
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        # Replace the treeWidget with our scroll area
        index = self.ui.verticalLayout.indexOf(self.ui.treeWidget)
        self.ui.verticalLayout.removeWidget(self.ui.treeWidget)
        self.ui.treeWidget.hide()
        self.ui.verticalLayout.insertWidget(index, self.scroll_area)

        self.populate_widgets()

        self.ui.pushButton.clicked.connect(self.search_files)
        self.ui.lineEdit.returnPressed.connect(self.search_files)

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

    def toggle_collapse(self, state):
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if isinstance(widget, CrossSearchLogicWidget):
                widget.toggle_collapse(state)

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
        search_term = self.ui.lineEdit.text()

        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if isinstance(widget, CrossSearchLogicWidget):
                if widget.ui.checkBox.isChecked():
                    results, root_path = results_as_dict(search_term, dict_name=widget.dir_name)
                    widget.display_results(results, root_path)
                else:
                    widget.clear_results()

    def populate_widgets(self):
        try:
            with open("directories.json", "r", encoding="utf-8") as f:
                directories = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            directories = {}

        for dir_name in sorted(directories.keys()):
            widget = CrossSearchLogicWidget(dir_name)
            self.scroll_layout.addWidget(widget)
