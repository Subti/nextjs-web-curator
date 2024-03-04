#example logger for parent folder of sdr module.

#this import will ONLY work from the parent folder
from sdr.sdr_capture import sdr_module

import argparse
from argparse import Namespace

#set defaults
rec_args = Namespace(
    ip_addr='find',
    num_samples=200000,
    center_freq=2620e6,
    sample_rate=50e6,
    gain=32,
    channel=0,
    metadata='./logiq_meta.yaml',
    sdr='usrp', 
    stream_time=1
)

#call the module
filepath, samples = sdr_capture(rec_args)

print(rec_args)