# worker.py
from PySide2.QtCore import QObject, Signal

class ParseWorker(QObject):
    finished = Signal()
    progress = Signal(str)

    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path

    def run(self):
        from myparserfile import generate_bibliography  # Parser
        generate_bibliography()  # runs in backend
        self.finished.emit()
