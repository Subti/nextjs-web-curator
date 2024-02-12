##a version of view_sgram for applying qualify_and_slice and viewing which slices would qualify for inclusion into a dataset.


import matplotlib
matplotlib.use('cairo')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import random
import sys
import argparse
import pathlib


## USAGE - vieW_slices.py <pathto-npy-file> <slicelengths> <length in ms snippet to capture from>

def quantize_tape(tape: np.ndarray, num_bins: int = 64, rounding_type: str = "floor"):
    # quantize the whole tape

    # set up certain number of bins equally spaced across the tape
    # every data point will be placed into the bin it is closest to, either rounding down to the floor or up to the ceiling
    bins = np.linspace(tape.min(), tape.max(), num_bins) # don't need (and may not want) rounding, but I thought it looked cleaner
    indexes = np.digitize(tape, bins, right=True) # use np.digitize to get the indexes of each data point within the bins array
    
    # map the data points to the correct bins
    if rounding_type == "ceiling":
        # because we are rounding to the ceiling, we use index (so each value is rounded up)
        modified_tape = bins[indexes]
    else:
        if rounding_type != "floor":
            print('rounding_type must be either "floor" or "ceiling", floor has been chosen as default')
        # because we are rounding to the floor, we use index-1 (so each value is rounded down)
        modified_tape = bins[indexes-1]
    return modified_tape

def quantize_slice_and_test(test, tape, slice_length, num_bins, rounding_type):
    # quantize tape
    quantized_tape = quantize_tape(tape, num_bins, rounding_type)

    # slice quantized tape
    tape_len = len(tape[0,:])
    n_slices =int(tape_len/slice_length)
    rms_list = np.zeros([n_slices,2],dtype='float16')
    pass_list = np.empty(n_slices,dtype='int8')
    slice_counter = 0
    not_counter = 0

    sliced_tape_list =np.zeros([n_slices,2,slice_length])
    for i in range(0,n_slices):
        sliced_tape_list[i,0,:] = quantized_tape[0,i:i+slice_length]
        sliced_tape_list[i,1,:] = quantized_tape[1,i:i+slice_length]

    # run RMS test on slices
    max_amplitude = np.max(np.abs(quantized_tape))

    if max_amplitude > .12: #2500 usually measured for bigger signals, 
        normalized_tape = quantized_tape / max_amplitude
    else: 
        normalized_tape = quantized_tape / 1000

    rms_counter = 0
    for i in range(0, tape.shape[1], slice_length):
        #normalize full tape
        rmssamples = normalized_tape[:, i:i+slice_length]
        # Calculate the RMS values for each row
        rms_values = np.sqrt(np.mean(rmssamples**2, axis=1))
        rms_list[rms_counter] = rms_values
        rms_counter += 1

        if rms_counter == n_slices:
            break

    rms_max = np.max(np.abs(rms_list))
    norm_rms_list = rms_list / rms_max

    #come up with a threshold
    min_norm_rms_list = np.amin(norm_rms_list, axis=None)
    mean_norm_rms_list = np.mean(norm_rms_list)
    std_norm_rms_list = np.std(norm_rms_list)

    if max_amplitude > .25:
        T_RMS = min_norm_rms_list + 0.5 * std_norm_rms_list
    elif max_amplitude > 0.12:
        T_RMS = min_norm_rms_list + 1 * std_norm_rms_list
    elif max_amplitude > .06:
        T_RMS = min_norm_rms_list + 2 * std_norm_rms_list
    else:
        T_RMS = mean_norm_rms_list + 2.9 * std_norm_rms_list
    
    print(f"Threshold for snippet is {T_RMS}")

    # apply the test
    for i in range(norm_rms_list.shape[0]):
        # Check if either row is above the threshold T_RMS
        if np.any(norm_rms_list[i] > T_RMS):
            pass_list[i] = 1
            slice_counter += 1
        else:
            pass_list[i] = 0
            not_counter += 1
            # If not, discard and move to the next slice_length samples
            continue

    print(f"total slices above threshold: {slice_counter}")
    print(f"total nots (skipped): {not_counter}")
    print(f"threshold ratio: {slice_counter/(slice_counter+not_counter)}")

    #drop failed slices and capture some of the noise slices too
    noise_slice_list = np.zeros([n_slices,2,slice_length])  #define an empty slice array number of slices
    noise_slice_list = sliced_tape_list[pass_list==0]
    noise_slice_list = noise_slice_list[0:slice_counter]

    sliced_tape_list =np.zeros([n_slices,2,slice_length])
    for i in range(0,n_slices):
        sliced_tape_list[i,0,:] = tape[0,i:i+slice_length]
        sliced_tape_list[i,1,:] = tape[1,i:i+slice_length]
    sliced_tape_list = sliced_tape_list[pass_list.nonzero()]

    return sliced_tape_list, norm_rms_list, pass_list, T_RMS, noise_slice_list


def qualify_and_slice(test,tape,slice_length):

    tape_len = len(tape[0,:])
    n_slices =int(tape_len/slice_length) #calculate number of slices
    rms_list = np.zeros([n_slices,2],dtype='float16')
    pass_list = np.empty(n_slices,dtype='int8')
    slice_counter = 0
    not_counter = 0

    ###*************SEPARATE TAPE INTO AN ARRAY OF SLICES*************
    sliced_tape_list =np.zeros([n_slices,2,slice_length])  #define an empty slice array number of slices
    #populate the slice array
    for i in range(0,n_slices):
        sliced_tape_list[i,0,:] = tape[0,i:i+slice_length]
        sliced_tape_list[i,1,:] = tape[1,i:i+slice_length]
    ###************************************************************

    ## run a qualification test
    if test == 'RMS':
        max_amplitude = np.max(np.abs(tape))
        print(f"max amplitude: {max_amplitude}")

        if max_amplitude > 20: #2500 usually measured for bigger signals, 
            normalized_tape = tape / max_amplitude
        else: 
            normalized_tape = tape / 1000

        rms_counter = 0
        for i in range(0, tape.shape[1], slice_length):
            
            #normalize full tape
            rmssamples = normalized_tape[:, i:i+slice_length]
            # Calculate the RMS values for each row
            rms_values = np.sqrt(np.mean(rmssamples**2, axis=1))
            rms_list[rms_counter] = rms_values
            rms_counter+=1

            if rms_counter == n_slices:
                break

        rms_max = np.max(np.abs(rms_list))
        norm_rms_list = rms_list / rms_max

        #come up with a threshold
        min_norm_rms_list = np.amin(norm_rms_list, axis=None)
        mean_norm_rms_list = np.mean(norm_rms_list)
        std_norm_rms_list = np.std(norm_rms_list)

        #if rms > 2 * mean - min pass - std/2
        # T_RMS = 2*mean_norm_rms_list - min_norm_rms_list - std_norm_rms_list/3

        if max_amplitude > 1000:
            T_RMS = min_norm_rms_list + 0.3*std_norm_rms_list
        elif max_amplitude > 100:
            T_RMS = min_norm_rms_list + 0.7*std_norm_rms_list
        elif max_amplitude >20:
            T_RMS = min_norm_rms_list + 1.5*std_norm_rms_list
        else:
            T_RMS = mean_norm_rms_list + 1.8*std_norm_rms_list
        

        print(f"Threshold for snippet is {T_RMS}")
        print(f"snippet rms mean {mean_norm_rms_list} and min {min_norm_rms_list} and std {std_norm_rms_list}")

        #apply the test
        print(norm_rms_list.shape[0])

        for i in range(norm_rms_list.shape[0]):
            # Check if either row is above the threshold T_RMS
            if np.any(norm_rms_list[i] > T_RMS):
                pass_list[i] = 1
                # print("adding to stack")
                slice_counter+=1

            else:
                # print("not adding to stack")
                pass_list[i] = 0
                not_counter+=1
                # If not, discard and move to the next slice_length samples
                continue

        # print(rms_list)
        # maxmin = np.amax(rms_list, axis=None)/np.amin(rms_list, axis=None)
        print(f"total iterations: {slice_counter+not_counter}")
        print(f"total slices above threshold: {slice_counter}")
        print(f"total nots (skipped): {not_counter}")
        # print(f"total slices above threshold: {m}")
        # print(f"max/minratio: {maxmin}")
        print(f"threshold ratio: {slice_counter/(slice_counter+not_counter)}")

        #drop failed slices and
        #capture some of the noise slices too
        noise_slice_list =np.zeros([n_slices,2,slice_length])  #define an empty slice array number of slices
        noise_slice_list = sliced_tape_list[pass_list==0]
        noise_slice_list = noise_slice_list[0:slice_counter]
        sliced_tape_list = sliced_tape_list[pass_list.nonzero()]

    else: #no qualification case
        print("no qualification test applied")
 
    return sliced_tape_list, norm_rms_list, pass_list, T_RMS, noise_slice_list


def view_slices(args):

    filename = str(args.filename)
    slc_len = int(args.slice_len)
    test = "RMS"
    
    try:
        plottime = float(args.plottime)
    except:
        plottime = str(args.plottime)
        

    ##open the files

    ##open the files
    with open(filename, 'rb' ) as f:
        iqdata = np.load(f) 
        meta = np.load(f)
        ###check if there is extended metadata
        try:
            extended_metaf = np.load(f, allow_pickle=True)[0]
            print("extended metadata")
            print("extended metadata contents:",extended_metaf)

        except:
            print('no extended metadata in this recording')
            ##code for including parsing of older recordings where decimation was not included in metadata
            if int(meta.shape[0]) < 4:
                decimation = 1  #############################change if decimation was actually 4
            else:
                decimation = float(meta[3])


    iqdata = iqdata.astype("float16")

    if extended_metaf:
        # get details on sampling from metadata
        sample_rate = extended_metaf["effective_sample_rate"]
        decimation = extended_metaf["decimation"]
        time_rec = extended_metaf['time_recorded']
        center_freq = extended_metaf["center_freq"]

    else:
        sample_rate = 125000000/decimation
        time_rec = "00000000"
        center_freq = float(meta[0]) * 1e6

    #FROM VIEW_SGRAM

    # get details on sampling from metadata
    rec_length = len(iqdata[0,:])
    duration = rec_length/sample_rate

    if plottime == "full":
        # plottime = duration*0.001
        plotsamples = rec_length
    else:
        plotsamples = int(plottime*.001*sample_rate)

    if center_freq > pow(10,6): # double check that all frequencies are in MHz
        center_freq /= pow(10,6)
    if sample_rate > pow(10,6):
        sample_rate = sample_rate/pow(10,6)


    print(plottime)
    print(sample_rate)

    ##print signal details based on metadata
    print("iq data:",iqdata)
    print("metadata contents:",meta)
    print("sample rate:", sample_rate)
    print("tape duration (seconds):", duration)
    print("samples needed for desired slice", plotsamples)



    ###Plot preparation
    fig, (ax1, ax5, ax3) = plt.subplots(3, 1)
    fig.subplots_adjust(hspace=0.5) # make a little extra space between the subplots

    #construct array of slices
    slices = int(rec_length/plotsamples)
    sliced_iqarray = np.empty([slices,2,plotsamples],dtype='float16')
    print ("this recording contains", slices,"slices of length", plotsamples) 

    for slicenum in range(slices):           
        slicestart = slicenum*plotsamples
        slicestop = plotsamples*(slicenum+1)
        sliced_iqarray[slicenum,0,:] = iqdata[0,slicestart:slicestop]
        sliced_iqarray[slicenum,1,:] = iqdata[1,slicestart:slicestop]

    # #manual garbage collection
    # iqdata = None 

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
    ax1.set_ylabel("iq")
    ax1.grid(True)

    #more manual garbage collection
    t = None
    # sliced_iqarray = None

    #https://matplotlib.org/stable/tutorials/colors/colormaps.html
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



    Sxx, f, t, im = ax3.specgram(iqsslicecomplex, Fs=sample_rate, Fc=center_freq, NFFT=fft_size, noverlap=fft_size/8,cmap=cmap)
    ax3.set_ylim(center_freq-sample_rate/2, center_freq+sample_rate/2)
    ticks_x = ticker.FuncFormatter(lambda t, pos: '{0:g}'.format(t/pow(10,3)))
    ax3.xaxis.set_major_formatter(ticks_x)
    ax3.set_ylabel('Frequency (Hz)')
    ax3.set_xlabel(f'Time (ms) Starting at {time_rec[0:2]}:{time_rec[2:4]}:{time_rec[4:6]}')
    ax3.xaxis.set_minor_locator(ticker.AutoMinorLocator())


    # sliced_class, rmsvals, passlist, T_RMS, noise_slices = qualify_and_slice(test,sliced_iqarray[iqarray_i,:,:],slc_len)
    sliced_class, rmsvals, passlist, T_RMS, noise_slices = quantize_slice_and_test(test,sliced_iqarray[iqarray_i,:,:],slc_len,64,"floor")




    print(sliced_class.shape)

    # plt.hist(rmsvals, bins=100)
    # plt.show()

    ax5.set_xlim(xmin=0,xmax=len(rmsvals))
    ax5.set_ylim(0,1)
    ax5.plot(rmsvals)

    x=range(len(passlist))
    ax5.bar(x,passlist, color='pink')
    ax5.axhline(T_RMS)

    # ttt = np.arange(0,noise_slices.shape[2],1)
    # rrr = random.randint(0, noise_slices.shape[0]-1)
    # ax7.plot(ttt,noise_slices[rrr,0,:], ttt, noise_slices[rrr,1,:])

    plt.subplots_adjust(bottom=.12, top=0.96, wspace=0, hspace=0)


    if args.saveplot:
        pathlib.Path("static").mkdir(exist_ok=True)
        img = "signal.jpg"
        plt.savefig(f"./static/{img}")
        return img
    else:
        plt.show()
        return None



if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument("--plottime", "-t", default="full", help="Time (in ms) to plot graphs. type 'full' for full tape")
    parser.add_argument("--slice_len", "-l", default=1024, help="Slice length in samples. Default = 1024")
    parser.add_argument("--filename", "-f",  type=str, default='test.npy', help="File to load. Default - test.npy")
    parser.add_argument("--saveplot", "-s", type=bool, default=False, help="Save plot instead of generating on screen.", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()


    view_slices(args)

