import pyaudio
import wave
import sys
import keyboard
from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import make_chunks
from pydub.effects import high_pass_filter
from pydub.scipy_effects import low_pass_filter
from pydub.scipy_effects import high_pass_filter
from pydub.scipy_effects import band_pass_filter
import time

CHUNK = 2048
CHANNELS = 2
RATE = 44100
FORMAT = pyaudio.paInt16
TALK_KEY = '`'

last_cutoff = 0
talk_is_blocked = False

def cheap_eq(seg,focus_freq,bandwidth=100,mode="peak",gain_dB=0,order=5):
	'''
	Cheap EQ in PyDub
	Silence=-120dBFS
	I2/I1=2=>3dB SPL Gain
	'''
	if gain_dB>=0:
		if mode=="peak":
			sec=band_pass_filter(seg,focus_freq-bandwidth/2,focus_freq+bandwidth/2,order=order)
			pass
		if mode=="low_shelf":
			sec=low_pass_filter(seg,focus_freq,order=order)
			pass
		if mode=="high_shelf":
			sec=high_pass_filter(seg,focus_freq,order=order)
			pass
		seg=seg.overlay(sec-(3-gain_dB))
		pass
	if gain_dB<0:
		if mode=="peak":
			sec=band_pass_filter(seg,focus_freq-bandwidth/2,focus_freq+bandwidth/2,order=order)
			pass
		if mode=="low_shelf":
			sec=low_pass_filter(seg,focus_freq,order=order)
			pass
		if mode=="high_shelf":
			sec=high_pass_filter(seg,focus_freq,order=order)
			pass
		seg=(seg+gain_dB).overlay(sec-(3+gain_dB))-gain_dB
		pass
	return seg

def main():
    global talk_is_blocked
    global last_cutoff
    p = pyaudio.PyAudio()

    staticsound = AudioSegment.from_file("./assets/static.wav", format="wav")
    endsound = AudioSegment.from_file("./assets/radio-end.wav", format="wav")

    inputstream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    input=True,
                    rate=RATE,
                    input_device_index=1
                    )

    micoutputstream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    output_device_index=7
                    )
    playbackoutputstream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True
                    )
    elapsed = 0
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        print ("Input Device id " + str(i) + " - " + p.get_device_info_by_host_api_device_index(0, i).get('name'))


    def release_talk_callback(keyboard_event):
        global last_cutoff
        global talk_is_blocked
        last_cutoff = keyboard_event.time
        talk_is_blocked = True


    keyboard.on_release_key(TALK_KEY, release_talk_callback, suppress=True)


    while True:
        if(talk_is_blocked == True and last_cutoff < (time.time() - endsound.duration_seconds)):
            keyboard.release(TALK_KEY)
            talk_is_blocked = False

        if (keyboard.is_pressed(TALK_KEY) or last_cutoff > (time.time() - endsound.duration_seconds)):
            data = inputstream.read(CHUNK)
            micsound = AudioSegment(
                data=data,
                sample_width=2,
                frame_rate=44100,
                channels=2
            )
            transformed = cheap_eq(micsound, focus_freq=500, bandwidth=500, mode="peak", gain_dB=15)
            transformed = transformed.high_pass_filter(1000)

            staticsound_start = elapsed % staticsound.duration_seconds
            elapsed = elapsed + transformed.duration_seconds
            staticsound_end = elapsed % staticsound.duration_seconds

            transformed = (transformed + 15).overlay(staticsound[staticsound_start * 1000: staticsound_end * 1000] - 25)
            endsound_start = time.time() - last_cutoff
            endsound_end = endsound_start + transformed.duration_seconds
            if(endsound.duration_seconds > endsound_start):
                transformed = transformed.overlay(endsound[endsound_start * 1000: endsound_end * 1000] - 5)
            micoutputstream.write(transformed._data)
            playbackoutputstream.write(transformed._data)


main()
