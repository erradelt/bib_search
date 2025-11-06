from PyQt5 import QtWidgets
from path_manager_ui import Ui_Dialog

class PathManager(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
