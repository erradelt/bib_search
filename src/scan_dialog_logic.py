from PyQt5 import QtWidgets, QtCore
from scan_dialog import Ui_Dialog
import pars_V2
import time

class ScanWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    # progress emits two ints: (dirs_total, files_total)
    progress = QtCore.pyqtSignal(int, int)
    scantime = QtCore.pyqtSignal(float)

    def __init__(self, path, name):
        super().__init__()
        self.path = path
        self.name = name
        self._should_stop = False
        self.start_time = 0
        self._last_progress_emit = 0

    def run(self):
        # Record start time; UI will poll this value to update the displayed
        # scan time. Avoid relying on a QTimer inside this worker thread
        # because the worker thread does not run a Qt event loop.
        self.start_time = time.time()

        # Use a throttled progress callback to avoid emitting a Qt signal
        # for every directory scanned (which can be very frequent and slow
        # down the parsing due to thread-context switching and UI updates).
        def throttled_progress(dirs_count, files_count):
            now = time.time()
            # Emit at most every 250ms or when we've processed 20 directories
            if now - self._last_progress_emit >= 0.25 or dirs_count % 20 == 0:
                self._last_progress_emit = now
                # emit both cumulative directory and file counts
                self.progress.emit(dirs_count, files_count)

        pars_V2.generate_bibliography(
            self.path,
            self.name,
            progress_callback=throttled_progress,
            should_stop=self.should_stop,
        )

        self.finished.emit()

    def update_scantime(self):
        # Kept for compatibility if external callers still use it, but
        # ScanDialog now updates the UI by polling `worker.start_time`.
        try:
            elapsed = time.time() - self.start_time
        except Exception:
            elapsed = 0.0
        self.scantime.emit(elapsed)

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
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.started.connect(self.worker.run)

        # Timer in the UI thread to poll the worker's start_time and update
        # the displayed scan time. Using a timer in the UI thread avoids
        # needing an event loop inside the worker thread.
        self.poll_timer = QtCore.QTimer(self)
        # Poll every 1000 ms so we only show whole seconds
        self.poll_timer.setInterval(1000)
        self.poll_timer.timeout.connect(self._update_ui_scantime)
        # Start polling when the dialog is opened (so the UI shows elapsed
        # time immediately). Also stop polling when finished.
        self.worker.finished.connect(lambda: self.poll_timer.stop())

        self.show_timer = QtCore.QTimer(self)
        self.show_timer.setSingleShot(True)
        self.show_timer.timeout.connect(self.show)

    def show(self):
        if not self.scan_finished:
            super().show()

    def open(self):
        self.thread.start()
        # Ensure the UI shows an initial time immediately and start polling
        # the worker.start_time even if the thread.started signal timing varies.
        self.ui.label_4.setText("0s")
        self.poll_timer.start()
        self.show_timer.start(1000) # 1 second delay
        return super().open()

    def update_progress(self, dir_count, file_count):
        # Update both directory and file counters in the dialog
        try:
            self.ui.label_5.setText(str(dir_count))
            self.ui.label_6.setText(str(file_count))
        except Exception:
            pass

    def update_scantime(self, scantime):
        # Keep compatibility: show whole seconds or minutes+seconds
        try:
            secs = int(scantime)
            self.ui.label_4.setText(self._format_elapsed(secs))
        except Exception:
            self.ui.label_4.setText("0s")

    def _update_ui_scantime(self):
        # Read worker.start_time (set in worker.run) and update UI
        try:
            start = getattr(self.worker, "start_time", None)
            if start:
                elapsed = int(time.time() - start)
                self.ui.label_4.setText(self._format_elapsed(elapsed))
        except Exception:
            # Be defensive; if anything goes wrong, stop the poll timer
            self.poll_timer.stop()

    def _format_elapsed(self, secs: int) -> str:
        """Return a human-readable elapsed string: 'Xs' or 'Mm SSs'."""
        if secs < 60:
            return f"{secs}s"
        minutes = secs // 60
        seconds = secs % 60
        return f"{minutes}m {seconds:02d}s"

    def on_scan_finished(self):
        self.scan_finished = True
        if self.show_timer.isActive():
            self.show_timer.stop()
        # Ensure final elapsed time (whole seconds) is shown before closing
        try:
            start = getattr(self.worker, "start_time", None)
            if start:
                elapsed = int(time.time() - start)
                self.ui.label_4.setText(self._format_elapsed(elapsed))
        except Exception:
            pass
        self.accept()

    def reject(self):
        self.worker.stop()
        super().reject()
