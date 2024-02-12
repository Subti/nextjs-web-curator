## prototype augmentation script for opening a npy recording applying a user defined augmentation to the whole tape, then saving as a new npy recording as _<augmentation>.npy
#(maybe eventually modified for sigmf)


## This script opens a .npy iq recording as produced by a {}_logiq.py, reads in the iq data, plots it, plots a spectrogram, prints details about the original signal
##Credut to torchsig and Peraton Labs for enabling and publishing about this: Ref: <> and <https://torchsig.com/>


## To run this:
##      example> python slice_augmenter.py <><><>


import argparse
import matplotlib.pyplot as plt
import numpy as np
import random








def noise_generator(a, axis=0, ddof=0, factor=1, size=1):
    a = np.asanyarray(a)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)
    SNR = np.where(sd == 0, 0, m/sd)*factor
    sig_avgpower_watt = np.mean((a/4)**2)*2
    noise_pow = sig_avgpower_watt / (10**(SNR/10))
    noise = np.sqrt(noise_pow) * np.random.randn(1, size)
    return noise

def time_reversal(iqdata: np.ndarray, max_drop: int, starting_bounds: tuple, max_magnitude: int, bin_number: int, rounding_type = "floor"):
    #reverse time  order of IQ samples
    idata = iqdata[0]
    qdata = iqdata[1]
    modified_iqdata = [np.flip(idata), np.flip(qdata)]
    return modified_iqdata # printing looks good

def spectral_inversion(iqdata: np.ndarray, max_drop: int, starting_bounds: tuple, max_magnitude: int, bin_number: int, rounding_type = "floor"):
    #negate the imaginary components
    idata = iqdata[0]
    qdata = iqdata[1]
    modified_iqdata = [idata, np.negative(qdata)]
    return modified_iqdata # printing looks good

def channel_swap(iqdata: np.ndarray, max_drop: int, starting_bounds: tuple, max_magnitude: int, bin_number: int, rounding_type = "floor"):
    #switch I and Q
    idata = iqdata[0]
    qdata = iqdata[1]
    modified_iqdata = [qdata, idata]
    return modified_iqdata # printing looks good

def amplitude_reversal(iqdata: np.ndarray, max_drop: int, starting_bounds: tuple, max_magnitude: int, bin_number: int, rounding_type = "floor"):
    #swap amplitudes of both I and Q
    idata = iqdata[0]
    qdata = iqdata[1]
    modified_iqdata = [np.negative(idata), np.negative(qdata)]
    return modified_iqdata # printing looks good

def drop_samples(iqdata: np.ndarray, max_drop: int, starting_bounds: tuple, max_magnitude: int, bin_number: int, rounding_type = "floor"):
    #see doc - random dropping of samples
    fill_type = random.randint(0,3)
    print("fill type:\t", fill_type)
    idata = iqdata[0]
    qdata = iqdata[1]
    sample_size = idata.size
    print("sample size:\t", sample_size)
    i = 0
    while i < sample_size:
        # move forward a random amount to a new index
        i = i + random.randint(1, sample_size)
        # create drop size of 1 to max inputted size
        drop_size = random.randint(1, max_drop)
        j = i + drop_size
        if j > sample_size: # check that the full drop is within the dataset
            break
        print("current index:\t", i)
        print("drop size:\t", drop_size)
        # create separate lists for dropped areas - may remove and replace use with indexed lists
        drop_sample_i = idata[i:j]
        drop_sample_q = qdata[i:j]
        if fill_type == 0: # fills drop with last valid value
            drop_fill_i = [idata[min(i - 1, sample_size - 1)] for k in range(drop_size)]
            drop_fill_q = [qdata[min(i - 1, sample_size - 1)] for k in range(drop_size)]
            # drop_fill_i = [idata[i-1] for k in range(drop_size)]
            # drop_fill_q = [qdata[i-1] for k in range(drop_size)]
        elif fill_type == 1: # fills drop with next valid value
            drop_fill_i = [idata[min(j, sample_size - 1)] for k in range(drop_size)]
            drop_fill_q = [qdata[min(j, sample_size - 1)] for k in range(drop_size)]
            # drop_fill_i = [idata[j] for k in range(drop_size)]
            # drop_fill_q = [qdata[j] for k in range(drop_size)]
        elif fill_type == 2: # fills drop with mean of drop
            mean_i = sum(drop_sample_i)/len(drop_sample_i)
            mean_q = sum(drop_sample_q)/len(drop_sample_q)
            drop_fill_i = [mean_i for k in range(drop_size)]
            drop_fill_q = [mean_q for k in range(drop_size)]
        elif fill_type == 3: # fills drop with 0s
            drop_fill_i = [0 for k in range(drop_size)]
            drop_fill_q = [0 for k in range(drop_size)]
        
        # replaces dropped samples with fill values
        idata[i:j] = drop_fill_i
        qdata[i:j] = drop_fill_q
    modified_iqdata = [idata, qdata]
    return modified_iqdata # printing looks good

def quantize_tape(iqdata: np.ndarray, max_drop: int, starting_bounds: tuple, max_magnitude: int, bin_number: int, rounding_type = "floor"):
    #quantize the whole tape by a few bits (random 1-4)
    # print(type(iqdata))
    iqdata = np.array(iqdata)
    maximum = iqdata.max()
    minimum = iqdata.min()
    bins = np.linspace(minimum, maximum, bin_number) # don't need (and may not want) rounding, but I thought it looked cleaner
    # use np.digitize to get the indexes of each data point within the bins array
    indexes = np.digitize(iqdata, bins, right=True)
    print("bins:\t\t", bins)
    print("indexes:\t", indexes, "\n")
    if rounding_type == "ceiling":
        # map the data points to the correct bins
        # because we are rounding to the floor, we use index-1
        modified_iqdata = bins[indexes]
        print("modified iqdata:\t", modified_iqdata)
    else:
        if rounding_type != "floor":
            print('rounding_type must be either "floor" or "ceiling", floor has been chosen as default')
        # map the data points to the correct bins
        # because we are rounding to the ceiling, we use index
        modified_iqdata = bins[indexes-1]
        print("modified iqdata:\t", modified_iqdata)
    return modified_iqdata #printing looks good

def quantize_parts(iqdata: np.ndarray, max_drop: int, starting_bounds: tuple, max_magnitude: int, bin_number: int, rounding_type = "floor"):
    #quantize random parts of the tape by a a few bits (random 1-4)
    # print(type(iqdata))
    iqdata = np.array(iqdata)
    idata = iqdata[0]
    qdata = iqdata[1]
    maximum = iqdata.max()
    minimum = iqdata.min()
    bins = np.linspace(minimum, maximum, bin_number)
    indexes = np.digitize(iqdata, bins, right=True)

    sample_size = iqdata[0].size
    i = 0
    while i < sample_size:
        # move forward a random amount to a new index
        i = i + random.randint(1, sample_size)
        # create quantize size of 1 to max inputted size
        quantize_size = random.randint(1, max_drop)
        print("current index:\t", i)
        print("quantize size:\t", quantize_size)
        j = i + quantize_size
        if j > sample_size: # check that the full drop is within the dataset
            break
        if rounding_type == "ceiling":
            # map the data points to the correct bins
            # because we are rounding to the ceiling, we use index
            ipart = bins[indexes[0][i:j]]
            qpart = bins[indexes[1][i:j]]
            idata[i:j] = ipart
            qdata[i:j] = qpart
        else:
            if rounding_type != "floor":
                print('rounding_type must be either "floor" or "ceiling", floor has been chosen as default')
            # map the data points to the correct bins
            # because we are rounding to the floor, we use index-1
            ipart = bins[indexes[0][i:j]-1]
            qpart = bins[indexes[1][i:j]-1]
            idata[i:j] = ipart
            qdata[i:j] = qpart
    modified_iqdata = [idata, qdata]
    return modified_iqdata #printing looks good

def magnitude_rescale(iqdata: np.ndarray, max_drop: int, starting_bounds: tuple, max_magnitude: int, bin_number: int, rounding_type = "floor"):
    #multiply data by a random constant after a random starting point
    #starting_bounds is a tuple with the bounds of the starting point, in the form of decimals from 0 to 1 (eg. [0.25, 0.75])
    #max_magnitude is the maximum value of the constant used to rescale data
    idata = iqdata[0]
    qdata = iqdata[1]
    sample_size = idata.size
    starting_point = random.randint(int(starting_bounds[0]*sample_size), int(starting_bounds[1]*sample_size))
    magnitude = random.random()*max_magnitude
    print("sample size:\t", sample_size)
    print("starting point:\t", starting_point)
    print("magnitude:\t", magnitude, "\n")

    # should see if I can do this without separating i and q
    rescaled_idata = magnitude*idata[starting_point:]
    rescaled_qdata = magnitude*qdata[starting_point:]
    modified_idata = np.concatenate((idata[:starting_point], rescaled_idata), axis=None)
    modified_qdata = np.concatenate((qdata[:starting_point], rescaled_qdata), axis=None)
    modified_iqdata = [modified_idata, modified_qdata]
    return modified_iqdata # printing looks good

def cut_out(iqdata: np.ndarray, max_drop: int, starting_bounds: tuple, max_magnitude: int, bin_number: int, rounding_type = "floor"):
    #cuts out random regions and replaces with either 0s, 1s, or low, average, or high SNR noise
    fill_type = random.randint(0,4)
    print("fill type:\t", fill_type)
    idata = iqdata[0]
    qdata = iqdata[1]
    sample_size = idata.size
    i = 0
    while i < sample_size:
        # move forward a random amount to a new index
        i = i + random.randint(1, sample_size/2)
        # create drop size of 1 to max inputted size
        cut_size = random.randint(1, max_drop)
        j = i + cut_size
        cut_sample_i = idata[i:j]
        cut_sample_q = qdata[i:j]
        if j > sample_size: # check that the full drop is within the dataset
            break
        print("current index:\t", i)
        print("drop size:\t", cut_size)
        # generate fill based on randomly selected fill type
        if fill_type == 0:
            fill_i = [0 for i in range(cut_size)]
            fill_q = [0 for i in range(cut_size)]
        elif fill_type == 1:
            fill_i = [1 for i in range(cut_size)]
            fill_q = [1 for i in range(cut_size)]
        elif fill_type == 2:
            # factor of 0.5 for low SNR
            fill_i = noise_generator(cut_sample_i, 0, 0, 0.5, cut_size)
            fill_q = noise_generator(cut_sample_q, 0, 0, 0.5, cut_size)
        elif fill_type == 3:
            # factor of 1 for avg SNR
            fill_i = noise_generator(cut_sample_i, 0, 0, 1, cut_size)
            fill_q = noise_generator(cut_sample_q, 0, 0, 1, cut_size)
        elif fill_type == 4:
            # factor of 2 for avg SNR
            fill_i = noise_generator(cut_sample_i, 0, 0, 2, cut_size)
            fill_q = noise_generator(cut_sample_q, 0, 0, 2, cut_size)
        idata[i:j] = fill_i
        qdata[i:j] = fill_q
    modified_iqdata = [idata, qdata]
    return modified_iqdata

def patch_shuffle(iqdata: np.ndarray, max_drop: int, starting_bounds: tuple, max_magnitude: int, bin_number: int, rounding_type = "floor"):
    #see doc - move entire sections around ---> do later?
    idata = iqdata[0]
    qdata = iqdata[1]
    sample_size = idata.size
    print("sample size:\t", sample_size)
    i = 0
    while i < sample_size:
        # move forward a random amount to a new index
        i = i + random.randint(1, sample_size)
        # create drop size of 1 to max inputted size
        drop_size = random.randint(1, max_drop)
        print("current index:\t", i)
        print("patch size:\t", drop_size)
        j = i + drop_size
        if j > sample_size: # check that the full drop is within the dataset
            break
        print("idata before:\t", idata[i-3:j+3])
        isample = idata[i:j]
        qsample = qdata[i:j]
        random.shuffle(isample)
        random.shuffle(qsample)
        idata[i:j] = isample
        qdata[i:j] = qsample
        print("idata after:\t", idata[i-3:j+3])
    modified_iqdata = [idata, qdata]
    return modified_iqdata


def convert_to_2xn(samples):
    # Separate the real and imaginary parts
    real_part = np.real(samples)
    imag_part = np.imag(samples)

    # Stack the real and imaginary parts vertically
    reshaped_array = np.vstack((real_part, imag_part))

    return reshaped_array




def slice_augmenter(args):
    #input handling
    filename = str(args.source_signal_file)
    plottime = float(args.plottime)
    augmentation = int(args.augmentation)

    ##open the files
    with open(filename, 'rb' ) as f:
        iqdata = np.load(f) 
        meta = np.load(f)
        ###check if there is extended metadata
        try:
            extended_meta = np.load(f, allow_pickle=True)  
        except:
            print('No extended metadata')

    iqdata = iqdata.astype("float16")

    ##code for including parsing of older recordings where decimation was not included in metadata
    if int(meta.shape[0]) < 4:
        decimation = 1  #############################change if decimation was actually 4
    else:
        decimation = float(meta[3])


    # get details on sampling from metadata
    sample_rate = 125000000/decimation
    rec_length = len(iqdata[0,:])
    duration = rec_length/sample_rate
    plotsamples = int(plottime*.001*sample_rate)

    ##print signal details based on metadata
    print("iq data:",iqdata)
    print("metadata contents:",meta)
    print("sample rate:", sample_rate)
    print("tape duration (seconds):", duration)
    print("samples needed for desired slice", plotsamples, "\n")

    ###Augmentation
    augmentation_list = [time_reversal, spectral_inversion, channel_swap, amplitude_reversal, drop_samples, quantize_tape, quantize_parts, magnitude_rescale, cut_out, patch_shuffle]
    print("augmentation:\t", str(augmentation_list[augmentation]))
    augmented_data = augmentation_list[augmentation](iqdata, 1000, [0.25, 0.75], 5, 32, "floor")

    print("iq data 1: ", iqdata[0])
    print("iq data 2: ", iqdata[1])
    print("augmented iq data 1: ", augmented_data[0])
    print("augmented iq data 2: ", augmented_data[1], "\n")

    #checks if there is extended metadata
    try: 
        print("extended metadata contents:",extended_meta, "\n")
    except:
        print('no extended metadata in this recording')


    #construct array of slices
    slices = rec_length // plotsamples
    sliced_iqarray = np.empty([slices,2,plotsamples],dtype='float16')
    sliced_augmented_iqarray = np.empty([slices,2,plotsamples],dtype='float16')
    print ("this recording contains", slices,"slices of length", plotsamples) 

    for slicenum in range(slices):           
        slicestart = slicenum*plotsamples
        slicestop = plotsamples*(slicenum+1)
        sliced_iqarray[slicenum,0,:] = iqdata[0,slicestart:slicestop]
        sliced_iqarray[slicenum,1,:] = iqdata[1,slicestart:slicestop]
        sliced_augmented_iqarray[slicenum,0,:] = augmented_data[0][slicestart:slicestop]
        sliced_augmented_iqarray[slicenum,1,:] = augmented_data[1][slicestart:slicestop]

    #manual garbage collection
    iqdata = None
    augmented_data = None
    print("slices",slices)
    print ("sliced iq data shape", sliced_iqarray.shape)


    #find index
    iqarray_i = int(random.uniform(0,slices))
    print("plotting slice:" ,iqarray_i)


    #Joined Complex slice vector
    iqsslicecomplex = sliced_iqarray[iqarray_i,0,:]+1j*sliced_iqarray[iqarray_i,1,:]
    iqsslicecomplex = iqsslicecomplex.astype("complex64")
    augmented_slicecomplex = sliced_augmented_iqarray[iqarray_i,0,:]+1j*sliced_augmented_iqarray[iqarray_i,1,:]
    augmented_slicecomplex = augmented_slicecomplex.astype("complex64")

    print("iq string shape",iqsslicecomplex.shape)

    if args.plot:
        ###Plot preparation
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
        fig.subplots_adjust(hspace=1.0) # make a little extra space between the subplots

        ##### first subplot  (time series)
        print("time series subplot")
        t = np.arange(0,plotsamples,1)

        ax1.plot(t,sliced_iqarray[iqarray_i,0,:], t, sliced_iqarray[iqarray_i,1,:])
        ax1.set_xlim(0,plotsamples)
        ax1.set_xlabel("Sample Number")
        ax1.set_ylabel("IQ")
        ax1.grid(True)

        ax2.plot(t,sliced_augmented_iqarray[iqarray_i,0,:], t, sliced_augmented_iqarray[iqarray_i,1,:])
        ax2.set_xlim(0,plotsamples)
        ax2.set_xlabel("Sample Number")
        ax2.set_ylabel("Augmented IQ")
        ax2.grid(True)

        #more manual garbage collection
        t = None
        sliced_iqarray = None
        sliced_augmented_iqarray = None

        #https://matplotlib.org/stable/tutorials/colors/colormaps.html
        cmap = plt.get_cmap('twilight')

        ##FFT Handling
        if plottime < 1:
            fft_size = 64
        elif plottime < 100:
            fft_size = 512
        else:
            fft_size = 2048

        print("computing spectrogram with fft size ", fft_size)

        Sxx, f, t, im = ax3.specgram(iqsslicecomplex, Fs=sample_rate, NFFT=fft_size, noverlap=int(fft_size/8),cmap=cmap)
        ax3.set_ylabel('Frequency (normalized)')
        ax3.set_xlabel('Time (s)')
        Sxx, f, t, im = ax4.specgram(augmented_slicecomplex, Fs=sample_rate, NFFT=fft_size, noverlap=int(fft_size/8),cmap=cmap)
        ax4.set_ylabel('Frequency (normalized)')
        ax4.set_xlabel('Time (s)')
        plt.show()


    #http://www.sharetechnote.com/html/5G/5G_FrameStructure_old1.html
    return convert_to_2xn(augmented_slicecomplex)




if __name__ == '__main__':
    
    #parse arguments if theyre provided
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_signal_file", "-s", help="Source signal (can be a path)")
    parser.add_argument("--target_dataset_file", "-t", help="Target signal (can be a path)")
    parser.add_argument("--plottime", "-p", help="Time in ms to plot")
    parser.add_argument("--augmentation", "-a", type=int, help="Augmentation to apply, use integer as selector. Options are: {0: time_reversal, 1: spectral_inversion, 2: channel_swap, 3: amplitude_reversal, 4: drop_samples, 5: quantize_tape, 6: quantize_parts, 7: magnitude_rescale, 8: cut_out, 9: patch_shuffle> and 'random'.")
    parser.add_argument("--plot", "-d", default=False, help="Option to plot the data. Give --plot or -d to plot data and --no-plot (or no argument at all) not to plot data.", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    slice_augmenter(args)

