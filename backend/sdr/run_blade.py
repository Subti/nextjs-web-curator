#!/usr/bin/env python3
###############################################################################
#
# Copyright (c) 2018-present Nuand LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################
#
# Basic example of using bladeRF Python bindings for full duplex TX/RX.
# Review the companion txrx.ini to adjust configuration options.
#
###############################################################################

import datetime as dt
import numpy as np
import os
import sigmf
import sys
import time
import yaml
from pathlib import Path

from configparser           import ConfigParser
from multiprocessing.pool   import ThreadPool
from pathlib                import Path
from sigmf                  import SigMFFile

try:
    from sdr.modules import global_vars
    from sdr.bladerf import _bladerf
    from sdr.modules.numpy_modules import convert_bytes_to_samples, convert_to_2xn, save_to_npy
except Exception as e:
    print(f"Exception with import on run_blade: {e} ")
    import modules.global_vars as global_vars
    from bladerf import _bladerf
    from modules.numpy_modules import convert_bytes_to_samples, convert_to_2xn, save_to_npy
# =============================================================================
# Close the device and exit
# =============================================================================
class ShutdownException(Exception):
    pass

def shutdown( error = 0, board = None ):
    print("Shutting down with error code: " + str(error) )
    if( board != None ):
        board.close()
    # sys.exit(error)
    raise ShutdownException("Shutdown initiated with error code: {}".format(error))

# =============================================================================
# Version information
# =============================================================================
def print_versions( device = None ):
    print("libbladeRF version:\t" + str(_bladerf.version()) )
    if( device != None ):
        try:
            print("Firmware version:\t" + str(device.get_fw_version()) )
        except:
            print("Firmware version:\t" + "ERROR" )
            raise

        try:
            print("FPGA version:\t\t"     + str(device.get_fpga_version()) )
        except:
            print("FPGA version:\t\t"     + "ERROR" )
            raise

    return 0


# =============================================================================
# Search for a bladeRF device attached to the host system
# Returns a bladeRF device handle.
# =============================================================================
def probe_bladerf():
    device = None
    print("Searching for bladeRF devices..." )
    try:
        devinfos = _bladerf.get_device_list()
        if( len(devinfos) == 1 ):
            device = "{backend}:device={usb_bus}:{usb_addr}".format(**devinfos[0]._asdict())
            print("Found bladeRF device: " + str(device) )
        if( len(devinfos) > 1 ):
            print("Unsupported feature: more than one bladeRFs detected." )
            print("\n".join([str(devinfo) for devinfo in devinfos]) )
            shutdown( error = -1, board = None )
    except _bladerf.BladeRFError:
        print("No bladeRF devices found." )
        pass

    return device


# =============================================================================
# Load FPGA
# =============================================================================
def load_fpga( device, image ):

    image = os.path.abspath( image )

    if( not os.path.exists(image) ):
        print("FPGA image does not exist: " + str(image) )
        return -1

    try:
        print("Loading FPGA image: " + str(image ) )
        device.load_fpga( image )
        fpga_loaded  = device.is_fpga_configured()
        fpga_version = device.get_fpga_version()

        if( fpga_loaded ):
            print("FPGA successfully loaded. Version: " + str(fpga_version) )

    except _bladerf.BladeRFError:
        print("Error loading FPGA." )
        raise

    return 0


# =============================================================================
# RECEIVE
# =============================================================================
def receive(device, channel : int, freq : int, rate : int, gain : int, rx_done = None,
            num_samples : int = 1024):

    if( device == None ):
        print("RX: Invalid device handle." )
        return -1

    if( channel == None ):
        print("RX: Invalid channel." )
        return -1

    # Configure BladeRF
    ch             = device.Channel(channel)
    ch.frequency   = freq
    ch.sample_rate = rate
    ch.gain        = gain
    bw = rate
    if bw < 200000:
        bw = 200000
    elif bw > 56000000:
        bw = 56000000
    ch.bandwidth = bw

    print(ch)

    # Setup synchronous stream
    device.sync_config(layout         = _bladerf.ChannelLayout.RX_X1,
                       fmt            = _bladerf.Format.SC16_Q11,
                       num_buffers    = 16,
                       buffer_size    = 8192,
                       num_transfers  = 8,
                       stream_timeout = 3500)

    # Enable module
    print("RX: Start" )
    ch.enable = True

    # Create receive buffer and read in samples to buffer
    bytes_per_sample = 4
    buf = bytearray(num_samples*bytes_per_sample)
    device.sync_rx(buf, num_samples)

    # Disable module
    print("RX: Stop" )
    ch.enable = False

    if( rx_done != None ):
        rx_done.set()

    print("RX: Done" )

    return 0, buf


# =============================================================================
# STREAM BLADE
# =============================================================================
# def stream_blade(channel:int, freq:int, rate:int, gain:int, num_samples:int = 1024, 
#                    stream_time:int=60, meta_file:str='metadata.yaml'):
def stream_blade(args):
    channel = args.channel
    freq = args.center_freq
    gain = args.gain
    rate = args.sample_rate
    num_samples = args.num_samples
    stream_time = args.stream_time
    meta_file = args.metadata



    uut = probe_bladerf()
    if( uut == None ):
        print("No bladeRFs detected. Exiting.")
        shutdown(error = -1, board = None)

    device     = _bladerf.BladeRF( uut )
    board_name = device.board_name
    fpga_size  = device.fpga_size

    if( config.getboolean(board_name + '-load-fpga', 'enable') ):
        print("Loading FPGA..." )
        try:
            status = load_fpga(device, config.get(board_name + '-load-fpga', 'image_' + str(fpga_size) + 'kle' ) )
        except:
            print("ERROR loading FPGA." )
            raise

        if( status < 0 ):
            print("ERROR loading FPGA." )
            shutdown(error = status, board = device)
    else:
        print("Skipping FPGA load due to configuration setting." )

    status = print_versions(device=device)
    
    # Configure BladeRF
    ch             = device.Channel(_bladerf.CHANNEL_RX(channel))
    ch.frequency   = freq
    ch.sample_rate = rate
    ch.gain        = gain
    bw = rate
    if bw < 200000:
        bw = 200000
    elif bw > 56000000:
        bw = 56000000
    ch.bandwidth = bw

    print(ch)

    # Setup synchronous stream
    device.sync_config(layout         = _bladerf.ChannelLayout.RX_X1,
                       fmt            = _bladerf.Format.SC16_Q11,
                       num_buffers    = 16,
                       buffer_size    = 8192,
                       num_transfers  = 8,
                       stream_timeout = 3500)


    # NEW STREAM CODE
    # Enable module
    print("RX: Start" )
    ch.enable = True
    bytes_per_sample = 4

    print("Starting stream")
    start_time = time.time()

    while True:
        # Create receive buffer and read in samples to buffer
        # Add them to a list to convert and save after stream is finished
        buf = bytearray(num_samples*bytes_per_sample)
        device.sync_rx(buf, num_samples)
        signal = convert_bytes_to_samples(buf)
        # samples = convert_to_2xn(signal)
        # global_vars.buffer = samples
        global_vars.buffer = signal
        if args.stream_time != float('inf') and time.time() >= (start_time + args.stream_time):
            break

    # Disable module
    print("RX: Stop" )
    ch.enable = False

    return None # sends nothing once scrpt is done because the buffer halts execution if there is an interruption (may need to change)


    # # OLD STREAM CODE - LEAVE ALONE FOR NOW
    # # Enable module
    # print("RX: Start" )
    # ch.enable = True
    # bytes_per_sample = 4

    # print("Starting stream")
    
    # samp_array = []
    # end_time = time.time() + stream_time
    # while time.time() < end_time:
    #     # Create receive buffer and read in samples to buffer
    #     # Add them to a list to convert and save after stream is finished
    #     buf = bytearray(num_samples*bytes_per_sample)
    #     device.sync_rx(buf, num_samples)
    #     samples = convert_bytes_to_samples(buf)
    #     samples = convert_to_2xn(samples)
    #     samp_array.append(samples)
    #     global_vars.buffer = samples

    # # Disable module
    # print("RX: Stop" )
    # ch.enable = False

    # print("Stream finished, saving data to files")
    # filelist = []
    # for i, samples in enumerate(samp_array):
    #     filepath = save_to_npy(samples, freq, rate, num_samples, meta_file, i, sdr="BladeRF")
    #     filelist.append(filepath)
    # print("Finished saving files")

    # return filelist, samples


# =============================================================================
# Load Configuration
# =============================================================================

path = Path(__file__)
ROOT_DIR = path.parent.absolute()
config_path = os.path.join(ROOT_DIR, "rx.ini")

config = ConfigParser()
config.read(config_path)

# Set libbladeRF verbosity level
verbosity = config.get('common', 'libbladerf_verbosity').upper()
if  ( verbosity == "VERBOSE" ):  _bladerf.set_verbosity( 0 )
elif( verbosity == "DEBUG" ):    _bladerf.set_verbosity( 1 )
elif( verbosity == "INFO" ):     _bladerf.set_verbosity( 2 )
elif( verbosity == "WARNING" ):  _bladerf.set_verbosity( 3 )
elif( verbosity == "ERROR" ):    _bladerf.set_verbosity( 4 )
elif( verbosity == "CRITICAL" ): _bladerf.set_verbosity( 5 )
elif( verbosity == "SILENT" ):   _bladerf.set_verbosity( 6 )
else:
    print("Invalid libbladerf_verbosity specified in configuration file:",
           verbosity )
    shutdown( error = -1, board = None )


# =============================================================================
# BEGIN !!!
# =============================================================================
def rx(channel: int, frequency: float, gain: float, sample_rate: float, num_samples: int):
    uut = probe_bladerf()

    if( uut == None ):
        print("No bladeRFs detected. Exiting." )
        shutdown( error = -1, board = None )

    b          = _bladerf.BladeRF( uut )
    board_name = b.board_name
    fpga_size  = b.fpga_size


    if( config.getboolean(board_name + '-load-fpga', 'enable') ):
        print("Loading FPGA..." )
        try:
            status = load_fpga( b, config.get(board_name + '-load-fpga',
                                            'image_' + str(fpga_size) + 'kle' ) )
        except:
            print("ERROR loading FPGA." )
            raise

        if( status < 0 ):
            print("ERROR loading FPGA." )
            shutdown( error = status, board = b )
    else:
        print("Skipping FPGA load due to configuration setting." )

    status = print_versions( device = b )
    samples = None

    # TODO: can we have >1 rx/tx pool workers because 2x2 MIMO?
    rx_pool = ThreadPool(processes=1)

    for s in [ss for ss in config.sections() if board_name + '-' in ss]:

        if( s == board_name + "-load-fpga" ):
            # Don't re-loading the FPGA!
            continue

        if( config.getboolean(s, 'enable') ):

            print("\nRUNNING" )
            if( s == board_name + '-rx' ):
                rx_ch   = _bladerf.CHANNEL_RX(channel)

                # Make this blocking for now ...
                status, samples = rx_pool.apply_async(receive,
                                            (),
                                            { 'device'        : b,
                                            'channel'       : rx_ch,
                                            'freq'          : int(frequency),
                                            'rate'          : int(sample_rate),
                                            'gain'          : int(gain),
                                            'rx_done'       : None,
                                            'num_samples'   : int(num_samples)
                                            }).get()
                if( status < 0 ):
                    print("Receive operation failed with error " + str(status) )
        else:
            print("SKIPPED [ Disabled ]" )

    b.close()
    print("Done!" )
    return samples