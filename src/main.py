import sys
from PyQt5 import QtWidgets, QtCore
from search_window_universal_logic import SearchWindowUniversal
from search_window_cross_logic import SearchWindowCross


class App(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.universal_window = SearchWindowUniversal()
        self.cross_window = SearchWindowCross()


        self.cross_window.ui.pushButton_switch.clicked.connect(self.switch_to_universal)

        self.current_window = self.universal_window
        self.current_window.show()

    def switch_to_universal(self):
        self.current_window.hide()
        self.current_window = self.universal_window
        self.universal_window.update_active_directory_label()
        self.current_window.show()

    def switch_to_cross(self):
        self.current_window.hide()
        self.current_window = self.cross_window
        self.current_window.show()


def main():
    app = App(sys.argv)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
