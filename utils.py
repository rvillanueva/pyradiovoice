import pyaudio
from pydub.effects import high_pass_filter
from pydub.scipy_effects import low_pass_filter
from pydub.scipy_effects import high_pass_filter
from pydub.scipy_effects import band_pass_filter

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

def list_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        print ("Input Device id " + str(i) + " - " + p.get_device_info_by_host_api_device_index(0, i).get('name'))
