
import argparse
import time

from rtlsdr import RtlSdr

try:
    from sdr.modules import global_vars
    from sdr.modules.numpy_modules import convert_to_2xn, save_to_npy, make_sigmf_meta_dict, save_to_sigmf
except:
    import modules.global_vars as global_vars
    from modules.numpy_modules import convert_to_2xn, save_to_npy, make_sigmf_meta_dict, save_to_sigmf



def rtlsdr_logiq(args):
    print("Connecting to RTL")
    if args.channel and args.channel > 0:
        sdr = RtlSdr(int(args.channel))
    else:
        sdr = RtlSdr()
    
    print("Configuring RTL")
    #Configure capture params
    sdr.sample_rate = args.sample_rate  
    sdr.center_freq = args.center_freq  
    #sdr.freq_correction = 0  # PPM correction is hardcoded

    if args.gain:
        sdr.gain = args.gain
    else:
        sdr.gain = 'auto'

    try:
        signal = sdr.read_samples(int(args.num_samples))  
    finally:
        sdr.close()

    samples = convert_to_2xn(signal)
    global_vars.buffer = samples
    print(samples.shape)

    if args.file_extension == "sigmf":
        anno = "Recorded IQ signal"
        sigmf_meta_dict = make_sigmf_meta_dict(args,anno,sdr="rtlsdr")
        fullpath = save_to_sigmf(signal,args.center_freq,sigmf_meta_dict)
    else:
        fullpath = save_to_npy(samples, args.num_samples, args.center_freq, args.sample_rate, args.metadata, sdr="rtlsdr")



    return fullpath, samples


def stream_rtlsdr(args):
    if args.channel and args.channel > 0:
        sdr = RtlSdr(int(args.channel))
    else:
        sdr = RtlSdr()

    #Configure capture params
    sdr.sample_rate = args.sample_rate  
    sdr.center_freq = args.center_freq  
    if args.gain:
        sdr.gain = args.gain
    else:
        sdr.gain = 'auto'

    print("Starting stream")
    start_time = time.time()
    while True:
        signal = sdr.read_samples(int(args.num_samples))
        # samples  = convert_to_2xn(samples)
        # global_vars.buffer = samples
        global_vars.buffer = signal


        if args.stream_time != float('inf') and time.time() >= (start_time + args.stream_time):
            break


    sdr.close() 
    # print("Stream finished, saving data to files")
    # filelist = []
    # for i, samples in enumerate(sample_list):
    #     filepath = save_to_npy(samples, args.num_samples, args.center_freq, args.sample_rate, args.metadata, i, sdr="rtlsdrv3")
    #     filelist.append(filepath)
    # print("Finished saving files")

    # return filelist, samples

    return None




if __name__ == "__main__":
    # add argparse
    #parse arguments if theyre provided
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_samples", "-n", type=int, default=128000, help="Number of samples to capture. Default = 128000. Max currently is 512000")
    parser.add_argument("--center_freq", "-f", type=float, default=1700e6, help="Center frequency in Hz. RTL is tunable from 24mhz to 1766mhz")
    parser.add_argument("--sample_rate", "-r", type=float, default=2560000, help="sample rate in Hz, default is 2.56e6, max is 3.2e6")
    parser.add_argument("--gain",        "-g", type=int, default=32, help="Set gain in dB from 0 to 50 dB, if unspecified, rtl will use auto")
    parser.add_argument("--channel",     "-c", type=int, default=0, help="specify which device to use, default = 0")
    parser.add_argument("--metadata",    "-m",  type=str,   default="logiq_meta.yaml", help = "Full path to metadata to add to the numpy file. Default is logiq_meta.yaml in modules folder")
    parser.add_argument("--file_extension", "-x",  type=str, default="npy",   help="file extenstion. Default = 'npy'. Also supports 'sigmf', but only in block capture mode.")
    args = parser.parse_args()


    rtlsdr_logiq(args)


#todo 
# # stream mode
# add to the driver