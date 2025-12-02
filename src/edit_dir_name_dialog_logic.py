from PyQt5 import QtWidgets
from edit_dir_name_dialog import Ui_EditDirNameDialog

class EditDirNameDialog(QtWidgets.QDialog):
    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.ui = Ui_EditDirNameDialog()
        self.ui.setupUi(self)

        self.ui.lineEdit_new_name.setPlaceholderText(current_name)

    def get_new_name(self):
        return self.ui.lineEdit_new_name.text()
