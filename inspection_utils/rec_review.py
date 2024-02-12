## This script opens a .npy iq recording as produced by a {}_logiq.py, reads in the iq data, plots it, plots a spectrogram, prints details about the signal
## To run this:
##     <your OS python command> view_rec.py -f <(pathtofile)filename>.npy -t <milliseconds to show> <-s if wanting to plot>

##      example> python .\view_rec.py -f D:\QProjects\development\r22_prototyping\iq2440MHz051219.npy  -t full -s
##      example> python view_rec.py -f D:\QProjects\development\r22_prototyping\iq2440MHz051219.npy  -t full



import sys
import numpy as np
# from scipy import fft, signal
import random
import argparse
import pathlib



def rec_review(args):


    #input handling
    filename = args.filename



    ##open the files
    with open(filename, 'rb' ) as f:
        try:
            iqdata = np.load(f,allow_pickle=True) 
        except Exception:
            iqdata = np.load(f) 
        try:
            meta = np.load(f) 
            extended_metaf = np.load(f, allow_pickle=True)[0] #note its saved as an np array
        except Exception as e:
            print(f"no metadata: {e}")

    print(iqdata)
    print(iqdata.shape)

    iqdata = iqdata.astype("float16")




    # get details on sampling from metadata
    try:
        sample_rate = int(extended_metaf["effective_sample_rate"])
    except Exception:
        sample_rate = int(extended_metaf["sample_rate"])

    rec_length = len(iqdata[0,:])
    duration = rec_length/sample_rate

    plotsamples = rec_length


    time_rec = extended_metaf['time_recorded']
    center_freq = int(extended_metaf["center_freq"])

    if center_freq > pow(10,6): # double check that all frequencies are in MHz
        center_freq /= pow(10,6)
    if sample_rate > pow(10,6):
        sample_rate = sample_rate/pow(10,6)


    ##print signal details based on metadata
    print("iq data:",iqdata)
    print("sample rate:", sample_rate)
    print("tape length (samples):",rec_length)
    print("tape duration (seconds):", duration)
    print("samples needed for desired slice", plotsamples)
    print("metadata contents:",extended_metaf)

    



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("--plottime", "-t", default="full", help="Time (in ms) to plot graphs. type 'full' for full tape")
    parser.add_argument("--filename", "-f",  type=str, default='test.npy', help="File to load. Default - test.npy")
    args = parser.parse_args()


    rec_review(args)




