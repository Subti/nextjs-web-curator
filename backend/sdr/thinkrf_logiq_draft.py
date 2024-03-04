#####
# THINKRF FILE WORK IN PROGRESS

import sys
import traceback

import numpy as np
from time import time
from datetime import datetime
import pathlib
import argparse

import colorama
from colorama import Fore, Style


from pyrf.devices.thinkrf import WSA
from pyrf.util import collect_data_and_context



def thinkrf_logiq(args):


    #process arguments

    device_ip = args.ip_addr
    CENTER_FREQ = args.center_freq
    span_arg = float(40)*1e6            ##for trigger config
    SPP = 65504
    PPB =int(sys.argv[3]) # Packets per block --------> dynamically calculate


    #display configuration settings
    print("number of packets to record: ", PPB) 
    print("centre frequency: ", CENTER_FREQ)
    print("IP address: "+ sys.argv[1])
    print("Center frequency: "+ sys.argv[2]+ " MHz")

    # define some constants
    RFE_MODE = 'ZIF'
    DECIMATION = 1 # USE STREAM_LOGIQ FOR OTHER DECIMATIONS
    ATTENUATION = 0
    GAIN = 'HIGH'
    TRIGGER_SETTING = {'type': 'NONE',
                    'fstart': (CENTER_FREQ - 0.5*span_arg), # some value
                    'fstop': (CENTER_FREQ + 0.5*span_arg),  # some value
                    'amplitude': -100}

    # connect to wsa
    dut = WSA()
    dut.connect(sys.argv[1])


    #reset device
    dut.request_read_perm()
    dut.reset()
    dut.scpiset(":SYSTEM:FLUSH") 



    # setup data capture conditions
    dut.freq(CENTER_FREQ)
    dut.rfe_mode(RFE_MODE)
    if (RFE_MODE != 'DD'):
        dut.freq(CENTER_FREQ)
    dut.attenuator(ATTENUATION)
    dut.psfm_gain(GAIN)
    dut.trigger(TRIGGER_SETTING)
    dut.decimation(DECIMATION)

    # capture the desired data points
    #dut.capture(SPP, PPB)
    # configure and capture the required data
    dut.scpiset(":TRACE:SPP %s" % SPP) # dut.capture(SPP, PPB)
    dut.scpiset(":TRACE:BLOCK:PACKETS %s" % PPB)
    dut.scpiset(":TRACE:BLOCK:DATA?")

    print("Capture mode: ",dut.capture_mode())


    #initialize memory storage string
    # iqstring = np.empty([2,SPP*(PPB+1)],dtype="float16")
    iqarray = np.empty([PPB,SPP,2],dtype="float16")
    iqstring = np.empty([2,SPP*(PPB)],dtype="float16")


    idx = 0
    # while not dut.eof():
    #loop to capture then ofload data
    while idx <= PPB:
        pkt = dut.read()

        if pkt.is_context_packet():
            print(pkt)

        if pkt.is_data_packet():
            # print("index",idx)
            iqarray[idx] = pkt.data
            idx +=1

        if idx == PPB:
            break

    print("OUT OF CAPTURE LOOP")


    # print I/Q data into i and q
    for idx in range(PPB):
        for iqstring_address in range(SPP):
            iqstring[0,iqstring_address + idx*SPP] = iqarray[idx,iqstring_address,0]
            iqstring[1,iqstring_address + idx*SPP] = iqarray[idx,iqstring_address,1]
        # print(idx*SPP)

    # print("EXAMPLE I")
    # print(iqarray[9,:,0])
    # print("EXAMPLE Q ")
    # print(iqarray[9,:,1])
    # print("END OF EXAMPLE")

    print("IQSTRINGEXAMPLE")
    print(iqstring[0,:])
    print(iqstring[1,:])
    print("END IQSTRINGEXAMPLE")

    dut.disconnect()

    #print settings and other information
    # print("Shape of all IQ data: ",iqstring.shape)
    print("Recorded IQ ARRAY SHAPE:", iqarray.shape)
    print("Total recording length: ",len(iqstring[0,:]))
    # print("IQ data: ",iqarray)

    # manual garbage collection
    iqarray = None

  
    pltlen = len(iqstring[0,:])


    ### save decision input handling
    print("type 'y' to save this file, otherwise hit enter:")
    savecommand = input()
    now = str(int(time()))

    # ###folder / file handling  #old


    ###folder / file handling
    now = datetime.now() 
    month = str(now.strftime("%m"))
    day = str(now.strftime("%d"))
    time = now.strftime("%H%M%S")
    savelen = len(iqstring[0,:])
    folder_name = sys.argv[2] + "MHz" + month + day
    pathlib.Path(folder_name).mkdir(exist_ok=True) #check if folder exists then make it
    folder = pathlib.Path(folder_name)
    filename = "iq" + time + ".npy"
    fullpath = folder / filename


    ###recording metadata

    meta = np.array([sys.argv[2],pltlen,PPB,DECIMATION]) #save the available metadata


    if savecommand == "y":
        print("saving as: "+ filename)
        with open(fullpath, 'wb' ) as f:
            np.save(f,iqstring) 
            np.save(f,meta) 
    else:
        print("not saving")


#TODO - pls fix streaming mode.
def thinkrf_stream(args):
    
    # set the VRT packet size
    SPP = 65504
    CENTER_FREQ = float(sys.argv[2]) * 1e6
    RFE_MODE = 'SH'
    DEC_RATE = int(sys.argv[4])   #not 2 
    STARTID = 1234
    PACKETS_TO_RECORD = int(sys.argv[3])
    # define the RTSA device
    dut = WSA()
    # connect to RTSA device with a given IP address
    dut.connect(sys.argv[1])
    # reset device to default settings
    dut.request_read_perm()
    dut.reset()
    dut.scpiset(":SYSTEM:FLUSH") # dut.flush()
    # set RFE mode to ZIF, which yields I14Q14 data
    dut.scpiset(":INPUT:MODE %s" % RFE_MODE) # dut.rfe_mode(RFE_MODE)
    # does some device configuration, such as set frequency
    dut.scpiset(":FREQ:CENTER %s" % CENTER_FREQ) # dut.freq(CENTER_FREQ)
    # configure the VRT packet size
    dut.scpiset(":TRACE:SPP %s" % SPP) # dut.spp(SPP)
    # set the decimation rate to slow down the capture rate
    dut.scpiset(":SENSE:DECIMATION %d" % DEC_RATE) # dut.decimation(DEC_RATE)
    # dut.scpiset(":SENSE:DEC %d" % DEC_RATE) # dut.decimation(DEC_RATE)
    # Start the stream capture
    dut.scpiset(":TRACE:STREAM:START %d" % STARTID)

    print(dut.capture_mode())
    # loop to get the start ID that mark the beginning of this stream
    while True:
        packet = dut.read()
        print(packet)
        if packet.is_context_packet() and packet.fields.get('streamid') == STARTID:
            print('Start ID received. Start data capture next.')
            break
    # read the stream data and any context packets from the R55x0/R57x0


    total_pkts = 0
    overflow_count = 0

    #initialize memory storage string
    iqstring = np.empty([2,SPP*(PACKETS_TO_RECORD+1)])
    iqstring_address = 0
    while True:
        try:
            if total_pkts > PACKETS_TO_RECORD:
                dut.stream_stop()
                print(dut.capture_mode())
                dut.flush()

                print("\nStopping stream: max packet limit reached")
                break
            packet = dut.read()
            print(packet)

            # print I/Q data int
            if DEC_RATE > 1:
                for i, q in packet.data:
                    iqstring[0,iqstring_address] = i
                    iqstring[1,iqstring_address] = q
                    iqstring_address = iqstring_address + 1
            # else:
            #     data, context = collect_data_and_context(dut)


            if packet.is_data_packet() and packet.sample_loss:
                print(Fore.RED +"overflow detected")
                overflow_count = overflow_count + 1
            # optional, just to indicate the stream capture is still running
            total_pkts = total_pkts + 1
            if total_pkts % 100 == 0:
                print('.')
        # Add your conditional code here so to stop the stream
        # capture or just Ctrl+C to exit the program. For example:
        # when detect a key stroke, exit
        except:
            dut.scpiset(":TRACE:STREAM:STOP")  # dut.stream_stop()
            print(dut.capture_mode())
            dut.flush()
            print("Stopping stream: exception")
            print(traceback.format_exc())
            break


    ### save decision input handling
    print("type 'y' to save this file, otherwise hit enter:")
    savecommand = input()



    ###folder / file handling
    now = datetime.now() 
    month = str(now.strftime("%m"))
    day = str(now.strftime("%d"))
    time = now.strftime("%H%M%S")
    savelen = len(iqstring[0,:])
    folder_name = sys.argv[2] + "MHz" + month + day
    pathlib.Path(folder_name).mkdir(exist_ok=True) #check if folder exists then make it
    folder = pathlib.Path(folder_name)
    filename = "iq" + time + ".npy"
    fullpath = folder / filename

    ###recording metadata 

    meta = np.array([sys.argv[2],savelen,PACKETS_TO_RECORD,DEC_RATE]) #save the available metadata

    if savecommand == "y":
        print("saving as: "+ filename)
        with open(fullpath, 'wb' ) as f:
            np.save(f,iqstring) 
            np.save(f,meta) 
    else:
        print("not saving")




    print("Total packets captured: %d" % total_pkts)
    print("Total overflow detected: %d" % overflow_count)


if __name__ == "__main__":
	# add argparse
	parser = argparse.ArgumentParser()
	# parser.add_argument("--address", "-a",      type=str,   default="192.168.3.1",       help="specify the IP address of the Pluto. Default = 192.168.3.1")
	parser.add_argument("-i", "--ip_addr",      type=str,   default="192.168.3.1",       help="specify the IP address of the Pluto. Default = 192.168.3.1")
	parser.add_argument("-n", "--num_samples",  type=int,   default=1000000,              help="Number of samples to capture. Default = 1,000,000")
	parser.add_argument("-f", "--center_freq",  type=float, default=2400e6,              help="Center frequency in Hz. Default 2400e6 (2.4GHz)")
	parser.add_argument("-r", "--sample_rate",  type=float, default=20e6,                help="sample rate in Hz. Default is 20e6 (20MHz)")
	parser.add_argument("-c", "--channel",  type=int, default=0,                help="channel to use. For pluto revC currently supports only channel 0")
	parser.add_argument("-g", "--gain",         type=int,   default=32,                  help="Set gain in dB. Default is 32")
    parser.add_argument("--metadata",    "-m",  type=str,   default="logiq_meta.yaml", help = "Full path to metadata to add to the numpy file. Default is logiq_meta.yaml in modules folder")
	parser.add_argument("--file_extension", "-x",  type=str, default="npy",   help="file extenstion. Default = 'npy'. Also supports 'sigmf', but only in block capture mode.")
	args = parser.parse_args()

	savepath, samples = thinkrf_logiq(args)

	print("Saved to", savepath)