from PyQt5.QtCore import QRunnable
from audio import VoiceChanger

class VoiceChangerRunnable(QRunnable):
    def __init__(self, **kwargs):
        super().__init__()
        self.voice_changer = VoiceChanger(**kwargs)

    def run(self):
        self.voice_changer.run()

    def exit(self):
        self.voice_changer.exit()
