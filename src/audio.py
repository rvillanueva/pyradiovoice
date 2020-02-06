import pyaudio
import keyboard
from pydub import AudioSegment
import time
from utils import DeviceInputStream, DeviceOutputStream

class VoiceChanger():
    def __init__(self, input_device, output_device, playback_device=None, talk_key='`', enable_burst=True):
        self.chunk_size = 1024 * 2

        self.elapsed = time.time()

        self.last_talk_release_time = 0
        self.talk_release_is_pending = False
        self.start_time = time.time()

        self.p = pyaudio.PyAudio()

        self.static_sound = AudioSegment.from_file("../assets/static.wav", format="wav")
        self.burst_sound = AudioSegment.from_file("../assets/burst.wav", format="wav")

        self.input_device = input_device
        self.output_device = output_device
        self.playback_device = playback_device
        self.talk_key = talk_key
        self.enable_burst = enable_burst
        self.is_active = True

    def run(self):
        input_stream = DeviceInputStream(self.input_device)
        output_stream = DeviceOutputStream(self.output_device)
        if self.playback_device != None:
            playback_stream = DeviceOutputStream(self.playback_device)

        if self.enable_burst:
            keyboard.on_release_key(self.talk_key, self.handle_release_talk, suppress=True)

        while self.is_active:
            talk_is_active = keyboard.is_pressed(self.talk_key)
            burst_is_active = talk_is_active == False and (time.time() - self.last_talk_release_time) < self.burst_sound.duration_seconds
            audio_is_active = talk_is_active or burst_is_active

            keyboard_needs_release = self.talk_release_is_pending and burst_is_active == False

            if audio_is_active:
                # Get sound from microphone
                sound = input_stream.read(self.chunk_size)

                # Add overlays and transformations
                sound = (sound + 10).equalize().overlay_using_start_time(self.static_sound - 25, self.elapsed % self.static_sound.duration_seconds)
                if (self.enable_burst and burst_is_active):
                    sound = sound.overlay_using_start_time(self.burst_sound - 5, time.time() - self.last_talk_release_time)

                # Play
                if self.playback_device != None:
                    playback_stream.play(sound)
                output_stream.play(sound)

            elif keyboard_needs_release:
                # Trigger delayed talk key release
                keyboard.release(self.talk_key)
                talk_release_is_pending = False

    def handle_release_talk(self, keyboard_event):
        self.last_talk_release_time = time.time()
        if self.enable_burst == True:
            self.talk_release_is_pending = True

    def exit(self):
        self.is_active = False
