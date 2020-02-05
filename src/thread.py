from PyQt5.QtCore import QRunnable
from audio import VoiceChanger

class VoiceChangerRunnable(QRunnable):
    def run(self, **kwargs):
        self.voice_changer = VoiceChanger(**kwargs)
        self.voice_changer.run()
