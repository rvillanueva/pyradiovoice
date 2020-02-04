import pyaudio
import keyboard
from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import make_chunks
import time
from utils import cheap_eq, list_devices

enable_playback = True

CHUNK = 1024 * 2
CHANNELS = 2
RATE = 44100
FORMAT = pyaudio.paInt16
TALK_KEY = '`'

last_talk_release_time = 0
talk_release_is_pending = False
start_time = time.time()
burst_is_enabled = True

static_sound = AudioSegment.from_file("./assets/static.wav", format="wav")
burst_sound = AudioSegment.from_file("./assets/burst.wav", format="wav")

def main():
    global talk_release_is_pending
    p = pyaudio.PyAudio()

    input_stream = p.open(format=FORMAT,
        channels=CHANNELS,
        input=True,
        rate=RATE,
        input_device_index=1
    )

    primary_output_stream = p.open(format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
        output_device_index=7
    )

    playback_output_stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True
    )

    # Ensure keyboard talk release is recorded and delayed until end of burst
    keyboard.on_release_key(TALK_KEY, release_talk_callback, suppress=True)

    while True:
        talk_is_active = keyboard.is_pressed(TALK_KEY)
        burst_is_finished = time.time() > (last_talk_release_time + burst_sound.duration_seconds)
        audio_is_active = talk_is_active or burst_is_finished == False

        keyboard_needs_release = burst_is_enabled and talk_release_is_pending and burst_is_finished

        if audio_is_active:
            # Get sound from microphone
            mic_sound = get_mic_sound(input_stream)

            # Add overlays and transformations
            sound = transform_mic_audio(mic_sound)
            sound = overlay_static_sound(sound, static_sound)
            if(burst_is_enabled == True and burst_is_finished == False):
                sound = overlay_burst_sound(sound, burst_sound)

            # Play
            if(enable_playback):
                play(playback_output_stream, sound)
            play(primary_output_stream, sound)

        elif keyboard_needs_release:
            # Ensure
            keyboard.release(TALK_KEY)
            talk_release_is_pending = False


def release_talk_callback(keyboard_event):
    global last_talk_release_time
    global talk_release_is_pending
    last_talk_release_time = time.time()
    if burst_is_enabled == True:
        talk_release_is_pending = True

def transform_mic_audio(seg):
    transformed = cheap_eq(seg, focus_freq=500, bandwidth=500, mode="peak", gain_dB=15)
    transformed = transformed.high_pass_filter(1000)
    return transformed

def overlay_static_sound(seg, static):
    elapsed = start_time - time.time()
    start = elapsed % static.duration_seconds
    end = (elapsed + seg.duration_seconds) % static.duration_seconds + seg.duration_seconds
    transformed = (seg + 15).overlay(static[start * 1000: end * 1000] - 25)
    return transformed

def overlay_burst_sound(seg, burst):
    start = time.time() - last_talk_release_time
    end = start + seg.duration_seconds
    transformed = seg.overlay(burst[start * 1000: end * 1000] - 5)
    return transformed

def play(stream, sound):
    stream.write(sound._data)

def get_mic_sound(input_stream):
    data = input_stream.read(CHUNK)
    return AudioSegment(
        data=data,
        sample_width=2,
        frame_rate=44100,
        channels=2
    )


main()
