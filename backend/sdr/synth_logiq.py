import argparse
import numpy as np
import math

import time 

try:
    import modules.global_vars as global_vars
    from modules.numpy_modules import convert_to_2xn, save_to_npy, make_sigmf_meta_dict, save_to_sigmf
except:
    from sdr.modules import global_vars
    from sdr.modules.numpy_modules import convert_to_2xn, save_to_npy, make_sigmf_meta_dict, save_to_sigmf


import numpy as np
import sys
import psutil

def add_noise(symbols, variance=0.1):
    """Add Gaussian noise to symbols."""
    noise = np.sqrt(variance) * (np.random.randn(symbols.size) + 1j * np.random.randn(symbols.size))
    return symbols + noise

def generate_bpsk_symbols(num_symbols, variance=0.1):
    """Generate BPSK symbols."""
    symbols = np.random.choice([1, -1], num_symbols)
    return add_noise(symbols, variance)

def generate_qpsk_symbols(num_symbols, variance=0.1):
    """Generate QPSK symbols."""
    symbols = np.random.choice([1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j], num_symbols)
    return add_noise(symbols, variance)

def generate_8psk_symbols(num_symbols, variance=0.1):
    """Generate 8PSK symbols."""
    angles = np.linspace(0, 2 * np.pi, 8, endpoint=False)
    symbols = np.exp(1j * angles[np.random.randint(8, size=num_symbols)])
    return add_noise(symbols, variance)

def generate_pam4_symbols(num_symbols, variance=0.1):
    symbols = np.random.choice(np.linspace(-3, 3, 4), num_symbols)
    return add_noise(symbols, variance)

def generate_qam16_symbols(num_symbols, variance=0.1):
    """Generate QAM16 symbols."""
    re_vals = np.array([-1.5, -0.5, 0.5, 1.5]) / np.sqrt(10)
    im_vals = np.array([-1.5, -0.5, 0.5, 1.5]) / np.sqrt(10)
    symbols = np.random.choice(re_vals, num_symbols) + 1j * np.random.choice(im_vals, num_symbols)
    return add_noise(symbols, variance)

def generate_qam64_symbols(num_symbols, variance=0.1):
    """Generate QAM64 symbols."""
    re_vals = np.array([-7, -5, -3, -1, 1, 3, 5, 7]) / np.sqrt(42)
    im_vals = np.array([-7, -5, -3, -1, 1, 3, 5, 7]) / np.sqrt(42)
    symbols = np.random.choice(re_vals, num_symbols) + 1j * np.random.choice(im_vals, num_symbols)
    return add_noise(symbols, variance)

def generate_qam256_symbols(num_symbols, variance=0.1):
    """Generate QAM256 symbols."""
    re_vals = np.array([-15, -13, -11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13, 15]) / np.sqrt(170)
    im_vals = np.array([-15, -13, -11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13, 15]) / np.sqrt(170)
    symbols = np.random.choice(re_vals, num_symbols) + 1j * np.random.choice(im_vals, num_symbols)
    return add_noise(symbols, variance)


generate_functions = {'bpsk':generate_bpsk_symbols,'qpsk':generate_qpsk_symbols,'8psk':generate_8psk_symbols,'pam4': generate_pam4_symbols ,'qam16':generate_qam16_symbols,'qam64':generate_qam64_symbols, "qam256":generate_qam256_symbols}

def add_noise_floor(signal, noise_floor_db=-100):
    """
    Adds a noise floor to the given signal.

    Parameters:
    - signal: The original signal
    - noise_floor_db: Desired power of the noise floor relative to the signal power, in dB. 
      Typically a negative value, e.g., -100 dB.

    Returns:
    - Signal with the noise floor added
    """
    signal_power = np.mean(np.abs(signal)**2)
    noise_power = signal_power * 10**(noise_floor_db/10) 
    noise = np.sqrt(noise_power) * (np.random.randn(*signal.shape) + 1j * np.random.randn(*signal.shape)) / np.sqrt(2)
    return signal + noise


def raised_cosine(t, beta, T):
    """
    Raised cosine function for pulse shaping.
    t : time array
    beta : roll-off factor [0, 1]
    T : symbol duration
    """
    if beta == 0:
        rc = np.sinc(t / T)
    else:
        rc = (np.sinc(t / T) * np.cos(np.pi * beta * t / T)) / (1 - (2 * beta * t / T)**2)
    return rc


# def generate_signal(mod_type, num_symbols, samples_per_symbol, fc, variance=0.01):
def generate_signal(mod_type, num_symbols, samples_per_symbol, fc, variance=0.01, beta=0.3, pct=10):
    """Generate modulated signal based on modulation type."""
    num_transmit_symbols = int(num_symbols * pct / 100)
    symbols = generate_functions[mod_type](num_transmit_symbols, variance)

    baseband_sequence = np.zeros(num_symbols, dtype=complex)

    num_groups = np.random.randint(5, num_transmit_symbols/10)
    group_endpoints = sorted([np.random.randint(1, num_transmit_symbols) for _ in range(num_groups-1)])
    group_endpoints = [0] + group_endpoints + [num_transmit_symbols]

    last_end_pos = 0

    for i in range(num_groups):
        group_length = group_endpoints[i+1] - group_endpoints[i]
        remaining_symbol_length = group_endpoints[-1] - group_endpoints[i+1]
        remaining_tape_length = len(baseband_sequence) - last_end_pos
        useful_whitespace_length = remaining_tape_length - remaining_symbol_length
      
        #0.25 forces it in the first quarter of remaining possible spaces, sqrt adds a distribution
        bias = np.sqrt(np.random.rand())
        start_pos = np.random.randint(last_end_pos,last_end_pos+math.ceil(0.25*bias*(useful_whitespace_length-group_length)))
        end_pos = start_pos + group_length
        
        baseband_sequence[start_pos:end_pos] = symbols[group_endpoints[i]:group_endpoints[i+1]]
        last_end_pos = end_pos
      
    # # no pulse shaping
    # t = np.arange(0, num_symbols * samples_per_symbol)
    # baseband_signal = np.repeat(baseband_sequence, samples_per_symbol)
    # carrier = np.exp(1j * 2 * np.pi * fc * t / samples_per_symbol)

    # Pulse shape method
    t_rc = np.linspace(-samples_per_symbol, samples_per_symbol, 2*samples_per_symbol + 1)
    rc_pulse = raised_cosine(t_rc, beta, samples_per_symbol)
    baseband_signal = np.convolve(np.repeat(baseband_sequence, samples_per_symbol), rc_pulse, mode='same')

    t = np.arange(0, num_symbols * samples_per_symbol)
    carrier = np.exp(1j * 2 * np.pi * fc * t / samples_per_symbol)

    generated_signal = baseband_signal * carrier

    generated_signal= add_noise_floor(generated_signal, noise_floor_db=-100)

    return generated_signal



def synth_logiq(args,nsigs=9,stream=False):

    spslist = [10, 20, 30, 50]
    fclist = [x for x in range(-6,7,1)]
    modslist = ['bpsk','qpsk','8psk','pam4','qam16','qam64','qam256']
    n_signals = np.random.randint(1,nsigs) if nsigs > 1 else nsigs
    signals = []

    for i in range(n_signals):
        amplitude = float(np.random.randint(10,100))/100
        pct = float(np.random.randint(0,70)) # no signal on more than 70% of the time
        sps = np.random.choice(spslist)
        mod_type = np.random.choice(modslist)
        if sps >20:
            fc = np.random.choice(fclist[1:-1])
        else:
            fc = np.random.choice(fclist)
        num_symbols = int(args.num_samples / sps)

        generated_signal = amplitude*generate_signal(mod_type,num_symbols, sps, fc,pct)

        if len(generated_signal)<args.num_samples:
            padding_length = args.num_samples - len(generated_signal)
            generated_signal = np.concatenate([generated_signal, np.zeros(padding_length, dtype=complex)])

        signals.append(generated_signal)
        print(f"Signal {i} - Amplitude:{amplitude}, pct:{pct}, sps:{sps}, modulation:{mod_type}, fc: {fc}  ")

    signal = sum(signals)


    #add more noise again
    nf_level = -np.random.randint(5,40)
    signal = add_noise_floor(signal, noise_floor_db=nf_level)

    #normalize
    max_magnitude = np.max(np.abs(signal))
    signal = signal / max_magnitude

    samples = convert_to_2xn(signal)



    if stream == True:
        return "", signal
    else:
        if args.file_extension == "sigmf":
            anno = "synthetic signal"
            sigmf_meta_dict = make_sigmf_meta_dict(args,anno,sdr="synthetic_sdr")
            fullpath = save_to_sigmf(signal,args.center_freq,sigmf_meta_dict)
        else:
            fullpath = save_to_npy(samples, args.num_samples, args.center_freq, args.sample_rate, args.metadata, sdr="synthetic_sdr")
        global_vars.buffer = samples
        return fullpath, samples

def stream_synth(args):

    n_tapes = args.stream_time * args.sample_rate / args.num_samples

    print(n_tapes)

    # infinite_stream = args.stream_time == float('inf')
    print("Starting stream")
    start_time = time.time()
    while True:
        tch = time.time()
        fullpath, samples = synth_logiq(args,nsigs=1,stream=True)
        global_vars.buffer =samples
        elapsed_time = time.time() - tch
        remaining_sleep_time = max(args.num_samples/args.sample_rate - elapsed_time, 0)
        time.sleep(remaining_sleep_time)

        if args.stream_time != float('inf') and time.time() >= (start_time + args.stream_time):
            break
    return None


if __name__ == "__main__":
    # add argparse
    #parse arguments if theyre provided
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_samples", "-n",  type=int,   default=2000000, help="Number of samples to capture. Default = 10,000")
    parser.add_argument("--center_freq", "-f",  type=float, default=2440e6, help="Center frequency in Hz. Default 2400e6")
    parser.add_argument("--sample_rate", "-r",  type=float, default=20e6, help="sample rate in Hz, default is 20e6")
    parser.add_argument("--gain",        "-g",  type=int,   default=32, help="Set gain in dB, if unspecified, usrp will use 32")
    parser.add_argument("--channel",     "-c",  type=int,   default=0, help="specify the channel of the usrp, default = 0")
    parser.add_argument("--ip_addr",     "-i",  type=str,   default='192.168.40.2', help="specify the ip address of the usrp, default = 192.168.40.2")
    parser.add_argument("--metadata",    "-m",  type=str,   default="logiq_meta.yaml", help = "Full path to metadata to add to the numpy file. Default is logiq_meta.yaml in modules folder")
    parser.add_argument("--stream_time", "-t",  type=int,   help="Stream time for stream_usrp")
    parser.add_argument("--file_extension", "-x",  type=str, default="npy",   help="file extenstion. Default = 'npy'. Also supports 'sigmf', but only in block capture mode.")
    args = parser.parse_args()


    #usrp_logiq(args)

    if args.stream_time:
        stream_synth(args)
    else:
        synth_logiq(args)



# TODO : change the method for distributing transmitted signal blocks
# TODO : clip or rero pad
# TODO : stream mode