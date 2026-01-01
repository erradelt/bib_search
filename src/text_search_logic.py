from PyQt5 import QtWidgets
from text_search_widget import Ui_Form
from doc_api import API

class TextSearchWidget(QtWidgets.QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.file_path = file_path
        self.setWindowTitle(f"Text Search - {self.file_path.name}")
        self.ui.pushButton.clicked.connect(self.press_search)

    def press_search(self):
        self.api_contact = API(self.file_path, self.ui.lineEdit.text())
        self.api_contact.key_finder()
