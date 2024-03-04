import zmq
import numpy as np
import time
import argparse
from argparse import Namespace


# call sdr with something like python3 -m sdr.sdr_capture -s pluto -t inf -n 10000000 
# make sure n is sufficiently sall


import modules.global_vars as global_vars
from modules.numpy_modules import convert_to_2xn, save_to_npy, make_sigmf_meta_dict, save_to_sigmf


def zmq_subscriber(args):
    received_count = 0
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    
    # Specify the IP and port of the publisher
    socket.connect(f"tcp://{args.zmq_pub_host}:{args.zmq_port}")
    print(f"receiving on tcp://{args.zmq_pub_host}:{args.zmq_port}")
    # Subscribe to all messages (empty string means no filter on subscription)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    
    t_start = time.perf_counter()  

    while True:
        data = socket.recv()  # Receive serialized numpy array
        signal = np.frombuffer(data,dtype=np.complex64)  # Deserialize the data into a numpy array
        
        # Process or print the data as required
        # print(arr)
        received_count += 1
        t_end = time.perf_counter()  
        print(f"Received a total of ." + '\033[92m' +f"{received_count}." + '\033[0m' +f" examples." + "\033[0;35m" +f" Process_loop_time: {t_end-t_start}" + '\033[0m')

        if args.record:

            save_args = Namespace(
                num_samples=len(signal),
                center_freq=3775e6,
                sample_rate=20e6,
                metadata='../rx_meta.yaml',
                sdr="gnodeb"
            )
            print(save_args)
            if args.file_extension == "sigmf":
                anno = "Recorded IQ signal"
                sigmf_meta_dict = make_sigmf_meta_dict(save_args,anno,sdr=save_args.sdr)
                fullpath = save_to_sigmf(signal,save_args.center_freq,sigmf_meta_dict)
            else:
                samples = convert_to_2xn(signal)
                fullpath = save_to_npy(samples, save_args.num_samples, save_args.center_freq, save_args.sample_rate, save_args.metadata, sdr=save_args.sdr)

            t_save = time.perf_counter()  
            print("\033[96m" +f" Save_time: {t_save-t_end}" + '\033[0m')
            t_start = t_save
        else:
            t_start = t_end  



# To start listening and printing



def buffer_subscriber():
    try:
        import modules.global_vars as global_vars
    except:
        from sdr import global_vars

    print("Starting buffer subscriber.")

    while True:
        received_count = 0
        # Check if buffer has changed
        if not np.array_equal(global_vars.buffer, last_buffer) and global_vars.buffer.size > 0:
            print(global_vars.buffer.shape)
            data = global_vars.buffer.tobytes()  # Serialize numpy array
            # data = np.array(global_vars.buffer).tobytes()  # Serialize numpy array
            last_buffer = global_vars.buffer.copy()  # Store the latest buffer for next comparison
            received_count += 1
            global_vars.buffer_count += 1
            global_vars.buffer = np.array([])

            print(f"Removed a total of {global_vars.buffer_count} example from the buffer.")
            print(f"Received a total of {received_count} examples from buffer.")

            no_change_counter = 0  # Reset the no-change counter
            no_change_timeout = 5 if no_change_timeout > 5 else no_change_timeout
        else:
            no_change_counter += 1
            if no_change_counter >= no_change_timeout*10: # Multiplied by 10 due to 0.1s sleep
                break
            time.sleep(0.1)  # Sleep for 0.1 if no change detected






if __name__ == "__main__":
    # add argparse
    #parse arguments if theyre provided
    parser = argparse.ArgumentParser(description='example for subscribing from zmq or buffer')
    parser.add_argument("-p", "--zmq_port",
                        type=int, default=5556, 
                        help="Specify a port for subscribing from zmq")
    parser.add_argument("-a", "--zmq_pub_host",
                        type=str, default="localhost", 
                        help="Specify ip address of local host")
    parser.add_argument("--record", type=bool, default=False, help="to save recordings --record.", action=argparse.BooleanOptionalAction)
    parser.add_argument("--file_extension", '-x', type=str, default="npy", help="File extennsion - only used if saving recordings, default npy also supports sigmf.")
    args = parser.parse_args()


    zmq_subscriber(args)
    # buffer_subscriber()