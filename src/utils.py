import pyaudio
from pydub import AudioSegment
from pydub.effects import high_pass_filter
from pydub.scipy_effects import low_pass_filter
from pydub.scipy_effects import high_pass_filter
from pydub.scipy_effects import band_pass_filter



class TransformableAudioSegment(AudioSegment):
	def equalize(self):
		transformed = cheap_eq(self, focus_freq=500, bandwidth=500, mode="peak", gain_dB=15)
		return transformed.high_pass_filter(1000)
	def overlay_using_start_time(self, seg, start_time):
		end_time = start_time + seg.duration_seconds
		return self.overlay(seg[start_time * 1000 : end_time * 1000])

class DeviceInputStream():
	def __init__(self, device):
		self.p = pyaudio.PyAudio()
		self.channels = int(device.get('maxInputChannels'))
		self.device_index = int(device.get('index'))
		self.rate = int(device.get('defaultSampleRate'))
		self.stream = self.p.open(
			format=pyaudio.paInt16,
			channels=self.channels,
			input=True,
			rate=self.rate,
			input_device_index=self.device_index
		)
	def read(self, chunk_size):
		data = self.stream.read(chunk_size)
		return TransformableAudioSegment(
			data=data,
			sample_width=2,
			frame_rate=self.rate,
			channels=self.channels
		)


class DeviceOutputStream():
	def __init__(self, device):
		self.p = pyaudio.PyAudio()
		self.channels = int(device.get('maxOutputChannels'))
		self.device_index = int(device.get('index'))
		self.rate = int(device.get('defaultSampleRate'))
		self.stream = self.p.open(
			format=pyaudio.paInt16,
			channels=self.channels,
			output=True,
			rate=self.rate,
			output_device_index=self.device_index
		)
	def play(self, seg):
		self.stream.write(seg._data)

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

def get_devices():
	p = pyaudio.PyAudio()
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')
	devices = []
	for i in range(0, numdevices):
		device = p.get_device_info_by_host_api_device_index(0, i)
		devices.append(device)
	return devices
