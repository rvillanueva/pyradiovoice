from PyQt5.QtWidgets import QApplication, QErrorMessage
from PyQt5.QtCore import QCoreApplication, QThreadPool
from app import Window
from thread import VoiceChangerRunnable
import sys

runnables = []

def start_runnable(**kwargs):
    runnable = VoiceChangerRunnable(**kwargs)
    QThreadPool.globalInstance().start(runnable)
    runnables.append(runnable)
    return runnable

if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationDisplayName('Radio Voice Changer')

    window = Window(run_callback=start_runnable)
    window.show()
    app.exec_()
    for runnable in runnables:
        runnable.exit()
