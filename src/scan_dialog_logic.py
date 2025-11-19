from PyQt5 import QtWidgets, QtCore
from scan_dialog import Ui_Dialog
import pars_V2
import time

class ScanWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)
    scantime = QtCore.pyqtSignal(float)

    def __init__(self, path, name):
        super().__init__()
        self.path = path
        self.name = name
        self._should_stop = False
        self.start_time = 0

    def run(self):
        self.start_time = time.time()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_scantime)
        self.timer.start(100)
        
        pars_V2.generate_bibliography(
            self.path,
            self.name,
            progress_callback=self.progress.emit,
            should_stop=self.should_stop
        )
        self.timer.stop()
        self.finished.emit()

    def update_scantime(self):
        self.scantime.emit(time.time() - self.start_time)

    def should_stop(self):
        return self._should_stop

    def stop(self):
        self._should_stop = True

class ScanDialog(QtWidgets.QDialog):
    def __init__(self, dir_path, dir_name, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.dir_path = dir_path
        self.dir_name = dir_name
        self.scan_finished = False

        self.ui.buttonBox.rejected.connect(self.reject)

        self.thread = QtCore.QThread()
        self.worker = ScanWorker(self.dir_path, self.dir_name)
        self.worker.moveToThread(self.thread)

        self.worker.progress.connect(self.update_progress)
        self.worker.scantime.connect(self.update_scantime)
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.started.connect(self.worker.run)

        self.show_timer = QtCore.QTimer(self)
        self.show_timer.setSingleShot(True)
        self.show_timer.timeout.connect(self.show)

    def show(self):
        if not self.scan_finished:
            super().show()

    def open(self):
        self.thread.start()
        self.show_timer.start(1000) # 1 second delay
        return super().open()

    def update_progress(self, dir_count):
        self.ui.label_5.setText(str(dir_count))

    def update_scantime(self, scantime):
        self.ui.label_4.setText(f"{scantime:.2f}s")

    def on_scan_finished(self):
        self.scan_finished = True
        if self.show_timer.isActive():
            self.show_timer.stop()
        self.accept()

    def reject(self):
        self.worker.stop()
        super().reject()
