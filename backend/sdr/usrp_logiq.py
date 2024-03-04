
import argparse
import numpy as np
import uhd

# import time
from time import time

try:
    import modules.global_vars as global_vars
    from modules.numpy_modules import convert_to_2xn, save_to_npy, make_sigmf_meta_dict, save_to_sigmf
except:
    from sdr.modules import global_vars
    from sdr.modules.numpy_modules import convert_to_2xn, save_to_npy, make_sigmf_meta_dict, save_to_sigmf

#requires uhd python api https://files.ettus.com/manual/page_python.html

def force_srate_xseries(srate):
    #decimations from 1 to 1024 - might be better to calculate...
    # two_hundred_rates=[200.0e6, 100.0e6, 50.0e6, 33.33e6, 25.0e6, 20.0e6, 16.67e6, 14.286e6]
    # one_eighty_four_rates=[184.32e6, 92.16e6, 46.08e6, 30.72e6, 23.04e6, 18.432e6, 15.36e6, 13.166e6]
    two_hundred_rates=[200.0e6 / i for i in range(1, 201)] # down to 1MHz wide
    one_eighty_four_rates=[184.32e6/ i for i in range(1, 185)] # down to ~ 1MHz wide

    diff_two_hundred = min([abs(x - srate) for x in two_hundred_rates])
    diff_one_eighty_four = min([abs(x - srate) for x in one_eighty_four_rates])

    closest_list = "two_hundred_rates" if diff_two_hundred < diff_one_eighty_four else "one_eighty_four_rates"
    if closest_list == "one_eighty_four_rates":
        mcr_str = ",master_clock_rate=184.32e6"
        print("MCR set to 184.32 MHz")
    else:
        mcr_str =""
    return mcr_str

def usrp_args_load(id_args,srate):

    if id_args[0:4]=='name':
        usrp_args=id_args
    else:
        mcr_str = force_srate_xseries(srate)
        usrp_args=f"addr={id_args}"+mcr_str
    return usrp_args

def usrp_logiq(args):
    print("Connecting to USRP")
    # usrp = uhd.usrp.MultiUSRP(f"addr={args.ip_addr}")
    usrp_args = usrp_args_load(args.ip_addr,args.sample_rate)
    usrp = uhd.usrp.MultiUSRP(usrp_args)
    num_samps = args.num_samples # number of samples received

    print("Configuring USRP")
    usrp.set_rx_rate(args.sample_rate, args.channel)
    usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(args.center_freq), args.channel)
    if args.gain:
        usrp.set_rx_gain(args.gain, args.channel)
    else:
        usrp.set_rx_agc(True, args.channel)

    bwrange = usrp.get_rx_bandwidth_range(args.channel)
    gainrange = usrp.get_rx_gain_range(args.channel)
    print(f"USRP settings - bandwidth range: {bwrange} gain range: {gainrange}")
    bw = args.sample_rate
    if bw < bwrange.start():
        bw = bwrange.start()
    elif bw > bwrange.stop():
        bw = bwrange.stop()
    usrp.set_rx_bandwidth(bw, args.channel)

    # Set up the stream and receive buffer
    st_args = uhd.usrp.StreamArgs("fc32", "sc16")
    st_args.channels = [args.channel]
    metadata = uhd.types.RXMetadata()
    streamer = usrp.get_rx_stream(st_args)
    max_buffer_samps = streamer.get_max_num_samps()
    recv_buffer = np.zeros((1, max_buffer_samps), dtype=np.complex64)       
    print(f"Max buffer samples: {max_buffer_samps}")

    # Start Stream
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    stream_cmd.stream_now = True
    streamer.issue_stream_cmd(stream_cmd)

    # Receive Samples
    signal = np.zeros(num_samps, dtype=np.complex64)
    for i in range(num_samps//max_buffer_samps):
        streamer.recv(recv_buffer, metadata)
        signal[i*max_buffer_samps:(i+1)*max_buffer_samps] = recv_buffer[0]

    # Stop Stream
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont)
    streamer.issue_stream_cmd(stream_cmd)

    # Convert and save samples
    samples = convert_to_2xn(signal)
    global_vars.buffer = samples

    if args.file_extension == "sigmf":
        anno = "Recorded IQ signal"
        sigmf_meta_dict = make_sigmf_meta_dict(args,anno,sdr="USRPX300")
        fullpath = save_to_sigmf(signal,args.center_freq,sigmf_meta_dict)
    else:
        fullpath = save_to_npy(samples, num_samps, args.center_freq, args.sample_rate, args.metadata, sdr="USRPX300")



    return fullpath, samples
    


def stream_usrp(args):
    print("Connecting to USRP")
    # usrp = uhd.usrp.MultiUSRP(f"addr={args.ip_addr}")
    usrp_args = usrp_args_load(args.ip_addr,args.sample_rate)
    usrp = uhd.usrp.MultiUSRP(usrp_args)

    print("Configuring USRP")
    usrp.set_rx_rate(args.sample_rate, args.channel)
    usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(args.center_freq), args.channel)
    if args.gain:
        usrp.set_rx_gain(args.gain, args.channel)
    else:
        usrp.set_rx_agc(True, args.channel)

    bwrange = usrp.get_rx_bandwidth_range(args.channel) 
    gainrange = usrp.get_rx_gain_range(args.channel)
    print(f"USRP settings - bandwidth range: {bwrange} gain range: {gainrange}")
    bw = args.sample_rate
    if bw < bwrange.start():
        bw = bwrange.start()
    elif bw > bwrange.stop():
        bw = bwrange.stop()
    usrp.set_rx_bandwidth(bw, args.channel)

    # Set up the stream and receive buffer
    st_args = uhd.usrp.StreamArgs("fc32", "sc16")
    st_args.channels = [args.channel]
    metadata = uhd.types.RXMetadata()
    streamer = usrp.get_rx_stream(st_args)
    max_buffer_samps = streamer.get_max_num_samps()
    print(f"Max buffer samples: {max_buffer_samps}")
    recv_buffer = np.zeros((1, max_buffer_samps), dtype=np.complex64)     

    # Start Stream
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    stream_cmd.stream_now = True
    streamer.issue_stream_cmd(stream_cmd)

    # NEW STREAM CODE
    # Receive Samples
    print("Starting stream")
    start_time = time()
    while True:
        samples = np.zeros(args.num_samples, dtype=np.complex64)
        for i in range(args.num_samples//max_buffer_samps):
            streamer.recv(recv_buffer, metadata)
            samples[i*max_buffer_samps:(i+1)*max_buffer_samps] = recv_buffer[0]
        global_vars.buffer = samples

        if args.stream_time != float('inf') and time() >= (start_time + args.stream_time):
            break

    # Stop Stream
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont)
    streamer.issue_stream_cmd(stream_cmd)

    return None

    # # OLD STREAM CODE
    # # Receive Samples
    # print("Starting stream")
    # sample_list = []
    # end_time = time() + args.stream_time
    # while time() < end_time:
    #     samples = np.zeros(args.num_samples, dtype=np.complex64)
    #     for i in range(args.num_samples//max_buffer_samps):
    #         streamer.recv(recv_buffer, metadata)
    #         samples[i*max_buffer_samps:(i+1)*max_buffer_samps] = recv_buffer[0]
    #     sample_list.append(samples)
    #     global_vars.buffer = samples

    # # Stop Stream
    # stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont)
    # streamer.issue_stream_cmd(stream_cmd)

    # print("Stream finished, saving data to files")
    # filelist = []
    # for i, samples in enumerate(sample_list):
    #     samples = convert_to_2xn(samples)
    #     filepath = save_to_npy(samples, args.num_samples, args.center_freq, args.sample_rate, args.metadata, i, sdr="USRPX300")
    #     filelist.append(filepath)
    # print("Finished saving files")

    # return filelist, samples


if __name__ == "__main__":
    # add argparse
    #parse arguments if theyre provided
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_samples", "-n",  type=int,   default=2000000, help="Number of samples to capture. Default = 10,000")
    parser.add_argument("--center_freq", "-f",  type=float, default=2440e6, help="Center frequency in Hz. Default 2400e6")
    parser.add_argument("--sample_rate", "-r",  type=float, default=20e6, help="sample rate in Hz, default is 20e6")
    parser.add_argument("--gain",        "-g",  type=int,   default=32, help="Set gain in dB, if unspecified, usrp will use 32")
    parser.add_argument("--channel",     "-c",  type=int,   default=0, help="specify the channel of the usrp, default = 0")
    parser.add_argument("--ip_addr",     "-i",  type=str,   default='192.168.40.2', help="specify the ip address of the usrp OR name ID, default = 192.168.40.2. For name 'type name=<device name>'")
    parser.add_argument("--metadata",    "-m",  type=str,   default="logiq_meta.yaml", help = "Full path to metadata to add to the numpy file. Default is logiq_meta.yaml in modules folder")
    parser.add_argument("--stream_time", "-t",  type=int,   default=20, help="Stream time for stream_usrp")
    parser.add_argument("--file_extension", "-x",  type=str, default="npy",   help="file extenstion. Default = 'npy'. Also supports 'sigmf', but only in block capture mode.")
    args = parser.parse_args()


    usrp_logiq(args)
    # stream_usrp(args)


    #TODO:
    # safe load
    # sample rate configuration