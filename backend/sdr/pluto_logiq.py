import adi
import argparse
import datetime as dt
import numpy as np
import os
import time
import yaml

from pathlib import Path

try:
	from sdr.modules import global_vars
	from sdr.modules.numpy_modules import save_to_npy, convert_to_2xn, make_sigmf_meta_dict, save_to_sigmf

except: 
	import modules.global_vars as global_vars
	from modules.numpy_modules import save_to_npy, convert_to_2xn, make_sigmf_meta_dict, save_to_sigmf
# def run_pluto_rx(num_samples, freq, rate, gain, addr, meta_file: str = 'metadata.yaml'):
# def run_pluto_rx(num_samples, freq, rate, gain, addr, meta_file: str = 'metadata.yaml'):
# def steal(args):
# 	sdr = adi.Pluto("ip:"+ args.ip_addr)
# 	sdr.gain_control_mode_chan0 = 'manual'




def run_pluto_rx(args):
	print("Connecting to Pluto")
	sdr = adi.Pluto("ip:"+ args.ip_addr)
	# print("Connected to Pluto")
	print(f"Configuring Pluto with configs: {args} ")
	sdr.gain_control_mode_chan0 = 'manual'
	sdr.rx_hardwaregain_chan0 = args.gain # dB
	sdr.rx_lo = int(args.center_freq)
	sdr.sample_rate = int(args.sample_rate)
	sdr.rx_rf_bandwidth = int(args.sample_rate) # filter width, just set it to the same as sample rate for now
	sdr.rx_buffer_size = args.num_samples
	# print("Configuration complete")

	signal = sdr.rx() # receive samples off Pluto
	samples = convert_to_2xn(signal)
	global_vars.buffer = samples


	if args.file_extension == "sigmf":
		anno = "Recorded IQ signal"
		sigmf_meta_dict = make_sigmf_meta_dict(args,anno,sdr="pluto")
		fullpath = save_to_sigmf(signal,args.center_freq,sigmf_meta_dict)
	else:
		fullpath = save_to_npy(samples, len(samples[0]), args.center_freq, args.sample_rate, args.metadata, sdr="pluto")




	return fullpath, samples


def stream_pluto(args):
	sdr = adi.Pluto("ip:"+ args.ip_addr)
	sdr.gain_control_mode_chan0 = 'manual'
	sdr.rx_hardwaregain_chan0 = args.gain # dB
	sdr.rx_lo = int(args.center_freq)
	sdr.sample_rate = int(args.sample_rate)
	sdr.rx_rf_bandwidth = int(args.sample_rate) # filter width, set it to sample rate for now
	sdr.rx_buffer_size = args.num_samples

	# Receive Samples
	# infinite_stream = args.stream_time == float('inf')
	print("Starting stream")
	start_time = time.time()
	while True:
		signal = sdr.rx() # receive samples off Pluto
		# samples = convert_to_2xn(signal) # TODO: may need to remove this and switch to complex to achieve rtc
		# global_vars.buffer = samples
		global_vars.buffer = signal



		if args.stream_time != float('inf') and time.time() >= (start_time + args.stream_time):
			break


	return None # sends nothing once scrpt is done because the buffer halts execution if there is an interruption (may need to change)


if __name__ == "__main__":
	# add argparse
	parser = argparse.ArgumentParser(description="Capture IQ signals from a plutoSDR")
	# parser.add_argument("--address", "-a",      type=str,   default="192.168.3.1",       help="specify the IP address of the Pluto. Default = 192.168.3.1")
	parser.add_argument("-i", "--ip_addr",      type=str,   default="192.168.3.1",       help="specify the IP address of the Pluto. Default = 192.168.3.1")
	parser.add_argument("-n", "--num_samples",  type=int,   default=1000000,              help="Number of samples to capture. Default = 1,000,000")
	parser.add_argument("-f", "--center_freq",  type=float, default=2400e6,              help="Center frequency in Hz. Default 2400e6 (2.4GHz)")
	parser.add_argument("-r", "--sample_rate",  type=float, default=20e6,                help="sample rate in Hz. Default is 20e6 (20MHz)")
	parser.add_argument("-c", "--channel",  type=int, default=0,                help="channel to use. For pluto revC currently supports only channel 0")
	parser.add_argument("-g", "--gain",         type=int,   default=32,                  help="Set gain in dB. Default is 32")
	parser.add_argument("--metadata",    "-m",  type=str,   default="logiq_meta.yaml", help = "Full path to metadata to add to the numpy file. Default is logiq_meta.yaml in modules folder")
	parser.add_argument("--file_extension", "-x",  type=str, default="npy",   help="file extenstion. Default = 'npy'. Also supports 'sigmf', but only in block capture mode.")
	parser.add_argument("-z", "--zmq",type=int,default=None,help="Port for ZMQ streaming.")
	args = parser.parse_args()

	# savepath, samples = run_pluto_rx(args.num_samples, args.center_freq, args.sample_rate, args.gain, args.ip_addr, args.metadata)
	savepath, samples = run_pluto_rx(args)
	#savepath= pluto_to_npy(samples, args.center_freq, args.sample_rate, args.num_samples, args.metadata)

	print("Saved to", savepath)