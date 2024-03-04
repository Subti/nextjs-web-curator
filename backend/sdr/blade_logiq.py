### convert_bytes_to_samples taken from smith1401/bladerf-sdr-aio

import argparse

try:
    from sdr.modules import global_vars
    from sdr.run_blade import rx
    from sdr.modules.numpy_modules import convert_bytes_to_samples, convert_to_2xn, save_to_npy, make_sigmf_meta_dict, save_to_sigmf

except Exception as e:
    print(f"Exception with imports on blade_logiq: {e}")
    import modules.global_vars as global_vars
    from run_blade import rx
    from modules.numpy_modules import convert_bytes_to_samples, convert_to_2xn, save_to_npy, make_sigmf_meta_dict, save_to_sigmf



# def blade_to_npy(channel: int, freq: float, sample_rate: float, gain: int, num_samples: int, meta_file: str):
def blade_to_npy(args):
    

    print("Running receive")
    _bytes = rx(args.channel, args.center_freq, args.gain, args.sample_rate, args.num_samples)
    # _bytes = rx(channel, freq, gain, sample_rate, num_samples)
    print("\nFinished receive")

    print("\nWriting file")
    signal = convert_bytes_to_samples(_bytes)
    samples = convert_to_2xn(signal)
    global_vars.buffer =samples 
    # print(samples.shape)


    if args.file_extension == "sigmf":
        anno = "Recorded IQ signal"
        sigmf_meta_dict = make_sigmf_meta_dict(args,anno,sdr="BladeRF")
        fullpath = save_to_sigmf(signal,args.center_freq,sigmf_meta_dict)
    else:
        fullpath = save_to_npy(samples, len(samples[0]), args.center_freq, args.sample_rate, args.metadata, sdr="BladeRF")





    print("Finished writing file")


    return fullpath, samples


if __name__ == "__main__":
    # add argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", "-c",      type=int,   default=0,                   help="specify the channel of the bladeRF, 0 selectes ch1, 1 selects ch2. Default = 0")
    parser.add_argument("--num_samples", "-n",  type=int,   default=1000000,              help="Number of samples to capture. Default = 1,000,000")
    parser.add_argument("--center_freq", "-f",  type=float, default=2440e6,              help="Center frequency in Hz. Default 2440e6")
    parser.add_argument("--sample_rate", "-r",  type=float, default=40e6,                help="sample rate in Hz. Default is 40e6")
    parser.add_argument("--gain", "-g",         type=int,   default=32,                  help="Set gain in dB. Default is 32")
    parser.add_argument("--metadata",    "-m",  type=str,   default="logiq_meta.yaml", help = "Full path to metadata to add to the numpy file. Default is logiq_meta.yaml in modules folder")
    parser.add_argument("--file_extension", "-x",  type=str, default="npy",   help="file extenstion. Default = 'npy'. Also supports 'sigmf', but only in block capture mode.")
    args = parser.parse_args()

    # auto choose filename, use timestamp - use r22
    # save in recordings subfolder
    # blade_to_npy(channel=args.channel, freq=args.center_freq, sample_rate=args.sample_rate, gain=args.gain, num_samples=args.num_samples, meta_file=args.metadata)
    blade_to_npy(args)


    #TODO: Move stream_blade to here..