import subprocess
import os
import re
import zmq
import numpy as np
import time

try:
    import modules.global_vars as global_vars
except:
    from sdr.modules import global_vars

import argparse

def cli_parser():
    parser = argparse.ArgumentParser(description="SDR capture module, cross platform library provides a common interface for common testbed functions.")
    parser.add_argument("-i", "--ip_addr",      
                        type=str,   
                        default="find",       
                        help="Specify the IP address of the SDR. Default = 'find', which searches for an IP address. If the search fails, defaults of 192.168.40.2 are used for USRP and 192.168.3.1 for the pluto. ")
    parser.add_argument("-n", "--num_samples",  
                        type=int,
                        default=10000000,
                        help="Number of samples to capture. Default = 128,000")
    parser.add_argument("-f", "--center_freq",  
                        type=float, 
                        default=2440e6,              
                        help="Center frequency in Hz. Default 2440e6 except for RTL: 1700e6 (1.7GHz)")
    parser.add_argument("-r", "--sample_rate",  
                        type=float, 
                        default=50000000,                
                        help="sample rate in Hz. Default is 50000000 (50MHz)")
    parser.add_argument("-g", "--gain",         
                        type=int,   
                        default=32,
                        help="Set gain in dB. Default is 32")
    parser.add_argument("-m", "--metadata",     
                        type=str,   
                        default="./logiq_meta.yaml", 
                        help="Metadata to add to the numpy file. Default is ./logiq_meta.yaml")
    parser.add_argument("-c", "--channel", 
                        type=int,
                        default=0,
                        help="The channel for the usrp or blade. Default is 0")
    parser.add_argument("-s", "--sdr",
                        type=str,
                        default=None,
                        help="Choice of which sdr to receive signals from. If none is chosen, program will try usrp, then blade, then pluto, then rtl.")
    parser.add_argument("-x", "--file_extension",
                        type=str,
                        default="npy",
                        help="File extension to save - default npy, also supports sigmf (block capture only).")
    parser.add_argument("-t", "--stream_time",
                        type=stream_time_type,
                        default=0, 
                        help="Length of time to stream continuously. If 'inf' is given, program will stream indefinitely and not save any recordings. If none is given, program will not stream continuously and will receive signal from chosen sdr once.")
    parser.add_argument("-z", "--zmq",
                        type=int, default=None, 
                        help="Specify a port for publising on zmq (instead of stream buffer) Suggested port 5556. Default = None i.e use stream buffer")
    parser.add_argument("--equalize", "-e",  help="--equalize for equalization or no argument for none.")


    args = parser.parse_args()

    return args



def find_uhd_device_ip():
    try:
        result = subprocess.check_output(["uhd_find_devices"], universal_newlines=True)
        ip_search = re.findall(r"addr: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", result)        
        if ip_search:
            #take the highest n.n.x.n subnet (manually chosen)
            highest_subnet_ip = max(ip_search, key=lambda ip: int(ip.split('.')[2]))
            print(highest_subnet_ip)
            return highest_subnet_ip
        else:
            print("No IP address found in uhd_find_devices output.")
            return None
    except subprocess.CalledProcessError:
        print("Error executing uhd_find_devices.")
        return None
    

def find_adalm_pluto_ip():
    return print("not currentl implemented")

    
#TODO : put more appropriate handling
def argscleanup(args):
    if args.sdr is not None:
        if "usrp" in args.sdr:
            sdr_max = 6000000000
            sdr_min = 10000000
            srate_max = 200000000
        elif "blade" in args.sdr:
            sdr_max = 6000000000
            sdr_min = 47000000
            srate_max = 61000000
        elif "pluto" in args.sdr:
            sdr_max = 6000000000
            sdr_min = 70000000
            srate_max = 61000000
        elif "rtl" in args.sdr:
            sdr_max = 1700000000
            sdr_min = 24000000
            srate_max = 2560000
            if args.num_samples > 512000:
                print(f"num_samples of {args.num_samples} invalid for {args.sdr}. Forcing to {512000}")
                args.num_samples = 512000

        elif "hackrf" in args.sdr:
            sdr_max = 6000000000
            sdr_min = 10000000
            srate_max = 35000000 #I just copied the pluto for now, TODO update this -alec
        else: #synth case
            sdr_max = 6000000000
            sdr_min = 70000000
            srate_max = 20000000

        if args.sample_rate > srate_max:
            print(f"Sample rate of {args.sample_rate} invalid for {args.sdr}. Forcing to {srate_max}")
            args.sample_rate = srate_max

        if args.center_freq + args.sample_rate/2 > sdr_max:
            print(f"Centre frequency of {args.center_freq} invalid for {args.sdr}.")
            if "rtl" in args.sdr:
                print("!!!!!!!")
                print(f"Forcing to Forcing to {sdr_max}")
                args.center_freq = sdr_max
        if args.center_freq + args.sample_rate/2 < sdr_min:
            print(f"Centre frequency of {args.center_freq} invalid for {args.sdr}.")


        if args.ip_addr == 'find':
            if "usrp" in args.sdr:
                try:
                    args.ip_addr = find_uhd_device_ip()
                except Exception as e:
                    print(f"Error: {e}")
                    print("Defaulting to usrp ip address of '192.168.40.2'.")
                    args.ip_addr = '192.168.40.2'
            elif "pluto" in args.sdr:
                try:
                    args.ip_addr = '192.168.3.1'
                    # args.ip_addr = find_adalm_pluto_ip()
                except Exception as e:
                    print(f"Error: {e}")
                    print("Defaulting to pluto ip address to '192.168.3.1'.")
                    args.ip_addr = '192.168.3.1'
            print(f'IP ADDRESS: {args.ip_addr}')
        else:
            print(f'IP ADDRESS: {args.ip_addr}')


    return args



def stream_time_type(value):
    if value == 'inf':
        return float('inf')
    try:
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid value '{value}'. Expected an integer or 'inf'.")



def radio_zmq_publisher(zmqport=5556):
    print(f"PUB to ZMQ PORT:{zmqport}")
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://*:{zmqport}")

    last_buffer = None
    no_change_timeout = 30  # Number of seconds to wait for a change before exiting
    no_change_counter = 0
    published_count = 0

    while True:
        # Check if buffer has changed
        t_start = time.perf_counter()  
        if not np.array_equal(global_vars.buffer, last_buffer) and global_vars.buffer.size > 0:
            send_buffer_shape = global_vars.buffer.shape
            data = global_vars.buffer.tobytes()  # Serialize numpy array
            # data = np.array(global_vars.buffer).tobytes()  # Serialize numpy array
            socket.send(data)
            last_buffer = global_vars.buffer.copy()  # Store the latest buffer for next comparison
            published_count += 1
            global_vars.buffer_count += 1

            global_vars.buffer = np.array([])

            # print(f"Removed a total of {global_vars.buffer_count} example from the buffer.")
            # print(f"Published a total of {published_count} examples to ZMQ.")

            no_change_counter = 0  # Reset the no-change counter
            no_change_timeout = 5 if no_change_timeout > 5 else no_change_timeout
            t_end = time.perf_counter()  
            print(f"Sent buffer shape: {send_buffer_shape}."+ "\033[38;5;214m" +f" Pub time: {t_end-t_start}. "+ '\033[0m')
            t_start = t_end
        else:
            no_change_counter += 1
            if no_change_counter >= no_change_timeout*10: # Multiplied by 10 due to 0.1s sleep
                break
            time.sleep(0.1)  # Sleep for 0.1 if no change detected

    #needs code to pop the buffer

    print(f"No new data detected for {no_change_timeout} seconds. Exiting zmq_publisher.")
