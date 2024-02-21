import sys
import numpy as np
import random
import argparse
import pathlib
import json
from scipy import signal

def view_rec(args):
    #input handling
    filename = args.filename

    try:
        plottime = float(args.plottime)
    except:
        plottime = str(args.plottime)

    ##open the files
    with open(filename, 'rb' ) as f:
        iqdata = np.load(f) 
        meta = np.load(f) 
        extended_metaf = np.load(f, allow_pickle=True)[0] #note its saved as an np array

    iqdata = iqdata.astype("float16")

    # get details on sampling from metadata
    try:
        sample_rate = int(extended_metaf["effective_sample_rate"])
    except Exception:
        sample_rate = int(extended_metaf["sample_rate"])

    rec_length = len(iqdata[0,:])
    duration = rec_length/sample_rate

    if plottime == "full":
        plotsamples = rec_length
    else:
        plotsamples = int(plottime*.001*sample_rate)

    time_rec = extended_metaf['time_recorded']
    center_freq = int(extended_metaf["center_freq"])

    if center_freq > pow(10,6): # double check that all frequencies are in MHz
        center_freq /= pow(10,6)
    if sample_rate > pow(10,6):
        sample_rate = sample_rate/pow(10,6)

    #construct array of slices
    slices = int(rec_length/plotsamples)
    sliced_iqarray = np.empty([slices,2,plotsamples],dtype='float16')

    for slicenum in range(slices):           
        slicestart = slicenum*plotsamples
        slicestop = plotsamples*(slicenum+1)
        sliced_iqarray[slicenum,0,:] = iqdata[0,slicestart:slicestop]
        sliced_iqarray[slicenum,1,:] = iqdata[1,slicestart:slicestop]

    #manual garbage collection
    iqdata = None 

    #find index
    iqarray_i = int(random.uniform(0,slices))

    #Joined Complex slice vector
    iqsslicecomplex = sliced_iqarray[iqarray_i,0,:]+1j*sliced_iqarray[iqarray_i,1,:]
    iqsslicecomplex = iqsslicecomplex.astype("complex64")

    ##### first subplot  (time series)
    t = np.arange(0,plotsamples,1)

    #more manual garbage collection
    t = None
    sliced_iqarray = None

    ##FFT Handling
    if rec_length < 2000:
        fft_size = int(64)
    elif rec_length < 10000:
        fft_size = int(256)
    elif rec_length < 1000000:
        fft_size = int(1024)
    else:     
        fft_size = int(2048)

    # Sxx, f, t, im = ax3.specgram(iqsslicecomplex, Fs=sample_rate, Fc=center_freq, NFFT=fft_size, noverlap=fft_size/8,cmap=cmap)
    f, t, Sxx = signal.spectrogram(iqsslicecomplex, Fs=sample_rate, NFFT=fft_size, noverlap=int(fft_size/8))

    # Prepare the data for the plots
    plot_data = {
        'time_series': {
            't': t.tolist(),
            'i': sliced_iqarray[iqarray_i,0,:].tolist(),
            'q': sliced_iqarray[iqarray_i,1,:].tolist(),
        },
        'spectrogram': {
            't': t.tolist(),
            'f': f.tolist(),
            'Sxx': Sxx.tolist(),
        },
    }

    # Convert the data to a JSON string
    plot_data_json = json.dumps(plot_data)

    # Return the JSON data directly
    return plot_data_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plottime", "-t", default="full", help="Time (in ms) to plot graphs. type 'full' for full tape")
    parser.add_argument("--filename", "-f",  type=str, default='test.npy', help="File to load. Default - test.npy")

    args = parser.parse_args()

    view_rec(args)