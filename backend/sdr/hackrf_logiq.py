from hackrf import HackRF
import argparse
import time
import math
import subprocess
import numpy
import sys
try:
    import modules.global_vars as global_vars
    from modules.numpy_modules import convert_bytes_to_samples, convert_to_2xn, save_to_npy, make_sigmf_meta_dict, save_to_sigmf, bytes_to_complex_array

except Exception as e:
    print(f"Exception with imports on hackrf_logiq: {e}") #note that this is triggered with ANY import statement
    from sdr.modules import global_vars
    from sdr.modules.numpy_modules import convert_bytes_to_samples, convert_to_2xn, save_to_npy, make_sigmf_meta_dict, save_to_sigmf


def hackrf_block(args):
    # print("Running recieve")
    with HackRF() as hrf:

        if(args.num_samples> 10000000):
            print("Number of samples out of range for block capture. Forcing to 10M.\n")
            args.num_samples = 10000000 #verified

        hrf.set_sample_rate(args.sample_rate)
    
        hrf.center_freq = args.center_freq
        
        (enable_amp,lna_gain,vga_gain)= distribute_hackrf_gain(args.gain)

        if(enable_amp):
            hrf.enable_amp()
        else:
            hrf.disable_amp()
        
        hrf.set_lna_gain(lna_gain)
        hrf.set_vga_gain(vga_gain)

        print("Running recieve")

        signal = hrf.read_samples(args.num_samples)
        print("\nFinished receive, writing file.")

        samples = convert_to_2xn(signal)
        global_vars.buffer =samples 


        if args.file_extension == "sigmf":
            anno = "Recorded IQ signal"
            sigmf_meta_dict = make_sigmf_meta_dict(args,anno,sdr="HackRF")
            fullpath = save_to_sigmf(signal,args.center_freq,sigmf_meta_dict)
        else:
            fullpath = save_to_npy(samples, len(samples[0]), args.center_freq, args.sample_rate, args.metadata, sdr="HackRF")
            
            print("Finished writing file")

            return fullpath,samples


        

def distribute_hackrf_gain(gain):
    #distributes the one gain value among 3 amplifiers on the hackrf
    #worth revisiting to see if this is the best distribution

    if(gain>116):
        print("HackRF: Gain out of range. Forcing to 116dB.")
    
    enable_amp =False
 
    if(gain>30): #14 dB preamp
        gain = gain-14
        enable_amp=True
        print("HackRF: 14dB amplifier enabled.")
    

    lna_gain = math.floor(gain*0.6)
    lna_gain = lna_gain-lna_gain%8
    if(lna_gain>40):
        lna_gain=40

    vga_gain = gain-lna_gain

    if vga_gain>62:
        vga_gain=62
        
    return (enable_amp,lna_gain,vga_gain)
    '''There is a 14 dB amplifier at the front of the HackRF that you can turn on or off. The default is off.
    The LNA gain setting applies to the IF signal. It can take values from 0 to 40 dB in 8 dB steps. The default value is 16 dB.
    The VGA gain setting applies to the baseband signal. It can take values from 0 to 62 dB in 2 dB steps. The default value is 16 dB.
    The LNA and VGA gains are set to the nearest step below the desired value. So if you try to set the LNA gain to 17-23 dB, 
    the gain will be set to 16 dB. The same applies for the VGA gain; trying to set the gain to 27 dB will result in 26 dB.'''
        

def old_stream_hackrf(args):
    with HackRF() as hrf:
        hrf.sample_rate = args.sample_rate
        hrf.center_freq = args.center_freq

        (enable_amp,lna_gain,vga_gain)= distribute_hackrf_gain(args.gain)

        if(enable_amp):
            hrf.enable_amp()
        else:
            hrf.disable_amp()
        
        hrf.set_lna_gain(lna_gain)
        hrf.set_vga_gain(vga_gain)

        print("Starting stream")

        start_time =time.time()

        while True:
            signal = hrf.read_samples(args.num_samples)
            global_vars.buffer = signal
            
            if args.stream_time != float('inf') and time.time() >= (start_time + args.stream_time):
                break
        
        print("Ending stream.")


def stream_hackrf(args):
    # Run hackrf_transfer command

    HACKRF_BUFFER_SIZE = 131072
    (enable_amp,lna_gain,vga_gain)= distribute_hackrf_gain(args.gain)
    
    command = [
        "hackrf_transfer",
        "-r", "-",  # Read from stdin
        "-f", str(args.center_freq),
        "-s", str(args.sample_rate),
        "-n", str(int(args.sample_rate * args.stream_time)),
        "-l", str(lna_gain),
        "-g", str(vga_gain),
        "-a", str(int(enable_amp))

    ]

    print("stream_hackrf(): expecting to publish "+ str(int(args.sample_rate*args.stream_time)/HACKRF_BUFFER_SIZE) + " zmq buffers." )

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Read and process the captured samples
        while True:

            #interleaved 8 bit integers
            raw_samples = process.stdout.read(HACKRF_BUFFER_SIZE*2)  # Assuming 16-bit IQ samples
            if not raw_samples:
                break

            
            

            # Convert raw bytes to numpy array of complex numbers
            samples = bytes_to_complex_array(raw_samples)
            
    

            # Process the samples as needed
            # Example: print the first 10 samples
            global_vars.buffer = samples
            

        process.communicate()

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        process.terminate()
        process.wait()
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    # add argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--num_samples", "-n",  type=int,   default=1000000,              help="Number of samples to capture. Default = 1,000,000")
    parser.add_argument("--center_freq", "-f",  type=float, default=2440e6,              help="Center frequency in Hz. Default 2440e6")
    parser.add_argument("--sample_rate", "-r",  type=float, default=20e6,                help="sample rate in Hz. Default is 20e6")
    parser.add_argument("--gain", "-g",         type=int,   default=32,                  help="Set gain in dB. Default is 32")
    parser.add_argument("--metadata",    "-m",  type=str,   default="logiq_meta.yaml", help = "Full path to metadata to add to the numpy file. Default is logiq_meta.yaml in modules folder")
    parser.add_argument("--file_extension", "-x",  type=str, default="npy",   help="file extenstion. Default = 'npy'. Also supports 'sigmf', but only in block capture mode.")
    parser.add_argument("--stream_time","-s",   type = float, default =5.0,            help = "Stream time.") #remove this later
    args = parser.parse_args()

    hackrf_block(args)