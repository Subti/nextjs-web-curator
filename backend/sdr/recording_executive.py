import subprocess
import itertools
import argparse
import numpy as np


def rec_executive(args):

    # Constants
    ch_values = [0,1]
    # ch_values = [0]
    #create arg for number of sample rates
    rate_values = [10e6,20e6,40e6,60e6]
    rate_values = [ int(x) for x in rate_values]

    print(type(rate_values[0]))

    use_sdr = args.sdr

    # Get all combinations of ch and rate
    combinations = list(itertools.product(ch_values, rate_values))

    cfg = 0
    len_comb = len(combinations)*args.offsets

    # For each combination
    for ch, rate in combinations:
        # calculate cf, freq, and num
        cf = int(args.center)
        num = int(rate * args.time)

        # Generate a specific number of frequency values based on offsets argument
        freq_values = np.linspace(cf - rate/2, cf + rate/2, args.offsets + 2,dtype=np.int64)[1:-1]

        # For each freq
        for freq in freq_values:
            print(f"Recording config {cfg} of {len_comb}")
            print(f"Capturing f={freq} r={rate} cf={cf} n={num} ch={ch}")
            # Call blade_logiq.py with subprocess.run
            # subprocess.run(["python", f"{use_sdr}_logiq.py", f"-f={freq}", f"-r={rate}", f"-c={cf}", f"-n={num}", f"-ch={ch}"], check=True)
            # Call blade_logiq.py with subprocess.run

            # completed_process = subprocess.run(["python","-m", f"sdr.{use_sdr}_logiq", f"-f={freq}", f"-r={rate}", f"-n={num}", f"-c={ch}"], check=True, capture_output=True, text=True)

            if args.ip_addr:
                completed_process = subprocess.run(["python", f"{use_sdr}_logiq.py", f"-i={args.ip_addr}", f"-f={freq}", f"-r={rate}", f"-n={num}"], check=True, capture_output=True, text=True)
            else:
                completed_process = subprocess.run(["python","-m", f"sdr.{use_sdr}_logiq", f"-f={freq}", f"-r={rate}", f"-n={num}", f"-c={ch}"], check=True, capture_output=True, text=True)

            # Split the output into lines
            lines = completed_process.stdout.splitlines()

            # Get the last 10 lines and join them into a single string
            last_n_lines = '\n'.join(lines[-2:])

            # Print the string
            print(last_n_lines)
            cfg+=1
if __name__ == '__main__':

    # Parse the arguments for recording_executive.py
    parser = argparse.ArgumentParser(description="Run {sdr}_logiq.py with various argument configurations.")
    parser.add_argument('--center','-c', type=int, default=2440e6, help='Center frequency')
    parser.add_argument('--ip_addr','-i', type=str, help='IP Address - no default')
    parser.add_argument('--channel_list',nargs="+", default=[0,1], help='Channels to use.')
    parser.add_argument('--time','-t', type=float, default=0.1, help='Time, usually less than 1')
    parser.add_argument('-o', '--offsets', type=int, default=5, help='Number of frequency offsets')
    parser.add_argument("--sdr", "-s",  type=str, default="blade", help="Pick an SDR urrent support for 'usrp', 'blade', 'pluto'. default is blade ThinkRF tbd.")

    args = parser.parse_args()


    rec_executive(args)