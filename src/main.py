import sys
from PyQt5 import QtWidgets
from search_window import Ui_MainWindow
from bib_pars_V2 import generate_bibliography
from findstuff_V2 import results_as_dict
import json


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.search_files)
        self.ui.pushButton_3.clicked.connect(self.update_bibliography)
        self.ui.pushButton_2.clicked.connect(self.close)
        self.ui.lineEdit.returnPressed.connect(self.search_files)
        self.ui.treeWidget.itemClicked.connect(self.on_item_clicked)

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
        from bib_pars_V2 import root_path
        self.add_items(self.ui.treeWidget.invisibleRootItem(), results, [str(root_path)])
        self.ui.treeWidget.expandAll()

    def add_items(self, parent, elements, path_components):
        for key, value in elements.items():
            new_path_components = path_components + [key]
            item = QtWidgets.QTreeWidgetItem(parent, [key])
            item.setData(0, 1000, new_path_components)
            if isinstance(value, dict):
                self.add_items(item, value, new_path_components)

    def on_item_clicked(self, item, column):
        path_components = item.data(0, 1000)
        print("\\".join(path_components))

    def update_bibliography(self):
        generate_bibliography()
        # Optional: show a message to the user
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Bibliography updated successfully!")
        msg.setWindowTitle("Update complete")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
