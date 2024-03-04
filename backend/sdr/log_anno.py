import argparse

try:
    from sdr.modules.simple_anno import annotate_npy
except:
    from modules.simple_anno import annotate_npy





if __name__ == "__main__":


    # add argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", "-c",      type=int,   default=0,                   help="specify the channel of the bladeRF, 0 selectes ch1, 1 selects ch2. Default = 0")
    parser.add_argument("--num_samples", "-n",  type=int,   default=15000000,              help="Number of samples to capture. Default = 100,000")
    parser.add_argument("--center_freq", "-f",  type=float, default=2440e6,              help="Center frequency in Hz. Default 2400e6")
    parser.add_argument("--sample_rate", "-r",  type=float, default=60e6,                help="sample rate in Hz. Default is 40e6")
    parser.add_argument("--gain", "-g",         type=int,   default=32,                  help="Set gain in dB. Default is 32")
    parser.add_argument("--ip_addr", "-i",         type=str,   default="192.168.3.3",                  help="ip addr")
    parser.add_argument("--sdr", "-s",         type=str,   default="synth",                  help="SDR to use - default = synth")
    parser.add_argument("--file_extension", "-x",         type=str,   default="npy",                  help="File extension, default numpy but supports sigmf")
    parser.add_argument("--metadata",    "-m",  type=str,   default="logiq_meta.yaml", help = "Full path to metadata to add to the numpy file. Default is logiq_meta.yaml in modules folder")
    parser.add_argument("--loop_nfft", "-l",  type=bool, default=False, help="Run at various nfft's")
    parser.add_argument("--nfft_bins", "-b",         type=int,   default=2048,                  help="Number of FFT Bins, default = 2048")
    parser.add_argument("--threshold", "-t",  type=float, default=2, help="Threshold in Standard Deviations from the mean for mask creation")
    parser.add_argument("--clean", "-w",  type=bool, action=argparse.BooleanOptionalAction, help="--clean or -w to clean with erosion")
    parser.add_argument("--equalize", "-e",  type=bool, action=argparse.BooleanOptionalAction, help="--equalize for equalization or no argument for none.")
    parser.add_argument("--sweep_clean",  type=bool, action=argparse.BooleanOptionalAction, help="--sweep_clean for zeroing specmask based on time series response.")
    parser.add_argument("--bbox",  type=bool, action=argparse.BooleanOptionalAction, help="--bbox for bbox.")



    args = parser.parse_args()


    if args.sdr == 'usrp':

        try:
            from sdr.usrp_logiq import usrp_logiq
        except Exception:
            from usrp_logiq import usrp_logiq
        logiq = usrp_logiq
    elif args.sdr == 'blade':
        try:
            from sdr.blade_logiq import blade_to_npy
        except Exception:
            from blade_logiq import blade_to_npy
        logiq = blade_to_npy

    elif args.sdr =='pluto':
        try:
            from sdr.pluto_logiq import run_pluto_rx
        except Exception:
            from pluto_logiq import run_pluto_rx
        logiq = run_pluto_rx
    elif args.sdr =='rtl':
        try:
            from sdr.rtlsdr_logiq import rtlsdr_logiq
        except Exception:
            from rtlsdr_logiq import rtlsdr_logiq
        logiq = rtlsdr_logiq
    elif args.sdr =='thinkrf':
        try:
            from sdr.thinkrf_logiq import thinkrf_logiq
        except Exception:
            from thinkrf_logiq import thinkrf_logiq
        logiq = thinkrf_logiq
    else:
        try:
            from synth_logiq import synth_logiq
        except Exception:
            from sdr.synth_logiq import synth_logiq
        logiq = synth_logiq


    # auto choose filename, use timestamp - use r22
    # save in recordings subfolder
    args.filename,_ = logiq(args)
    args.plottime='full'
    args.nfft=args.nfft_bins
    args.compress = False

    if args.loop_nfft == True:
        nffts= [2048,1024,512,256,128]
        for nfft in nffts:
            args.nfft=nfft
            annotate_npy(args)
    else:
        annotate_npy(args)