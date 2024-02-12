## This script opens a .npy iq recording as produced by a {}_logiq.py, reads in the iq data, plots it, plots a spectrogram, prints details about the signal
## To run this:
##     <your OS python command> view_rec.py -f <(pathtofile)filename>.npy -t <milliseconds to show> <-s if wanting to plot>

##      example> python .\view_rec.py -f D:\QProjects\development\r22_prototyping\iq2440MHz051219.npy  -t full -s
##      example> python view_rec.py -f D:\QProjects\development\r22_prototyping\iq2440MHz051219.npy  -t full



import sys
import matplotlib
matplotlib.use('cairo')
import matplotlib.pyplot as plt
import numpy as np
# from scipy import fft, signal
import random
import matplotlib.ticker as ticker
import argparse
import pathlib



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
        # plottime = duration*0.001
        plotsamples = rec_length
    else:
        plotsamples = int(plottime*.001*sample_rate)


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

    ###Plot preparation
    fig, (ax1, ax3) = plt.subplots(2, 1)
    fig.subplots_adjust(hspace=0.5) # make a little extra space between the subplots
    fig.set_figwidth(12)

    #construct array of slices
    slices = int(rec_length/plotsamples)
    sliced_iqarray = np.empty([slices,2,plotsamples],dtype='float16')
    print ("this recording contains", slices,"slices of length", plotsamples) 

    for slicenum in range(slices):           
        slicestart = slicenum*plotsamples
        slicestop = plotsamples*(slicenum+1)
        sliced_iqarray[slicenum,0,:] = iqdata[0,slicestart:slicestop]
        sliced_iqarray[slicenum,1,:] = iqdata[1,slicestart:slicestop]

    #manual garbage collection
    iqdata = None 

    print("slices",slices)
    print ("sliced iq data shape", sliced_iqarray.shape)


    #find index
    iqarray_i = int(random.uniform(0,slices))

    print("plotting slice:" ,iqarray_i)


    #Joined Complex slice vector
    iqsslicecomplex = sliced_iqarray[iqarray_i,0,:]+1j*sliced_iqarray[iqarray_i,1,:]
    iqsslicecomplex = iqsslicecomplex.astype("complex64")

    print("iq string shape",iqsslicecomplex.shape)


    ##### first subplot  (time series)
    print("time series subplot")

    t = np.arange(0,plotsamples,1)


    ax1.plot(t,sliced_iqarray[iqarray_i,0,:], t, sliced_iqarray[iqarray_i,1,:])
    ax1.set_xlim(0,plotsamples)
    ax1.set_xticks([])
    # ax1.set_xlabel("sample number")
    ax1.set_ylabel("iq")
    ax1.grid(True)

    #more manual garbage collection
    t = None
    sliced_iqarray = None

    cmap = plt.get_cmap('twilight')

    ##FFT Handling
    if rec_length < 2000:
        fft_size = int(64)
        # window = np.hanning(512).astype("float16")
    elif rec_length < 10000:
        fft_size = int(256)
    elif rec_length < 1000000:
        fft_size = int(1024)
    else:     
        fft_size = int(2048)

    print("computing spectrogram with fft size ", fft_size)


    # Sxx, f, t, im = ax3.specgram(iqsslicecomplex, Fs=sample_rate, Fc=center_freq, NFFT=fft_size, noverlap=fft_size/8,cmap=cmap)
    Sxx, f, t, im = ax3.specgram(iqsslicecomplex, Fs=sample_rate, Fc=center_freq, NFFT=fft_size, noverlap=int(fft_size/8),cmap=cmap)
    
    ax3.set_ylim(center_freq-sample_rate/2, center_freq+sample_rate/2)
    ticks_x = ticker.FuncFormatter(lambda t, pos: '{0:g}'.format(t/pow(10,3)))
    ax3.xaxis.set_major_formatter(ticks_x)
    ax3.set_ylabel('Frequency (Hz)')
    ax3.set_xlabel(f'Time (ms) Starting at {time_rec[0:2]}:{time_rec[2:4]}:{time_rec[4:6]}')
    ax3.xaxis.set_minor_locator(ticker.AutoMinorLocator())


    plt.subplots_adjust(bottom=.12, top=0.96, wspace=0, hspace=0)



    if args.saveplot:
        pathlib.Path("static").mkdir(exist_ok=True)
        img = "signal.svg"
        plt.savefig(f"./static/{img}")
        return img
    else:
        plt.show()
        return None



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plottime", "-t", default="full", help="Time (in ms) to plot graphs. type 'full' for full tape")
    parser.add_argument("--filename", "-f",  type=str, default='test.npy', help="File to load. Default - test.npy")
    parser.add_argument("--saveplot", "-s", type=bool, default=False, help="Save plot instead of generating on screen.", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()


    view_rec(args)




