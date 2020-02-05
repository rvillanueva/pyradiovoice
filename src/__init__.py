from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication, QThreadPool
from app import Window
from thread import VoiceChangerRunnable

def start_runnable(**kwargs):
    QThreadPool.globalInstance().start(runnable)

if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationDisplayName('Radio Voice Changer')
    runnable = VoiceChangerRunnable()

    window = Window(run_callback=start_runnable)
    window.show()
    app.exec_()
