import sys
import time
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QProgressBar, QPushButton, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QTimer  # Import QTimer from PyQt5.QtCore


class WorkerThread(QThread):
    progress_signal = pyqtSignal(int)

    def __init__(self, script_path, n):
        super().__init__()
        self.script_path = script_path
        self.n = n

    def run(self):
        for i in range(self.n):
            time.sleep(0.01)
            self.progress_signal.emit(i + 1)

        # Execute the Python script using subprocess
        try:
            subprocess.run(['python', self.script_path])
        except subprocess.CalledProcessError as e:
            print(f"Error executing script: {e}")

        # You can add additional cleanup or handling after the subprocess is complete


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(600)
        self.setWindowTitle('GCVM')  # Set the window title to 'GCVM'

        layout = QVBoxLayout()

        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        layout.addWidget(self.progressBar)

        self.button = QPushButton('Enable Virtual Mouse')
        self.button.setStyleSheet('font-size: 30px; height: 30px;')
        self.button.clicked.connect(self.start_subprocess)

        layout.addWidget(self.button)
        self.setLayout(layout)

        self.worker_thread = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gui)

    def start_subprocess(self):
        script_path = 'C:\\GCVM\\main.py'
        n = 500
        self.progressBar.setValue(0)

        # Start the subprocess in a separate thread
        self.worker_thread = WorkerThread(script_path, n)
        self.worker_thread.progress_signal.connect(self.update_progress)
        self.worker_thread.start()

        # Start the timer to periodically check for events
        self.timer.start(10)

    def update_progress(self, value):
        self.progressBar.setValue(value)

        # If subprocess is complete, stop the thread and timer
        if value == self.progressBar.maximum():
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.timer.stop()

    def update_gui(self):
        # Periodically check for events and update the GUI
        QApplication.processEvents()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    demo = AppDemo()
    demo.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')
