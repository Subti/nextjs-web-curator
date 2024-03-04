## More automated version of folder2dataset, without plotting, and less user prompting
#
## This script opens a .npy iq recordings that are found in a target folder, as produced by a  {}_logiq.py, 
# asks for a label, reads in the iq data, asks if you want to add it to the dataset, 
# then adds the signal as a sample in the specified dataset
## To run this:
##     <OS python command> add2dataset.py <path to folder with recordings> <(pathtodataset)datasetfilename>.dat new 
# example >folder2dataset.py sourcefolder targetdataset.dat new
#####################################ONLY FOR USE AFTER THE folder-slicer.py HAS BEEN USED FIRST


## ASSUMES FILES IN THE FOLDER ALL HAVE THE SAME METADATA

import numpy as np
import pathlib
import random
from sigmf import SigMFFile, sigmffile


def quantize_tape(tape: np.ndarray, num_bins: int = 64, rounding_type: str = "floor"):
    # quantize the whole tape

    # print(f"tape.min(){tape.min()}, tape.max(){tape.max()}, num_bins {num_bins}")

    # set up certain number of bins equally spaced across the tape
    # every data point will be placed into the bin it is closest to, either rounding down to the floor or up to the ceiling
    bins = np.linspace(tape.min(), tape.max(), num_bins) 
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

    # print(f"num_bins {num_bins}")
    # print(f"tape {tape}")
    # print(f"quantized_tape {quantized_tape}")
    # print(f"quantized_tape shape {quantized_tape.shape}")
    # print(f"quantized_tape type {type(quantized_tape[0][0])}")
    # max_amplitude_tape = np.max(np.abs(tape))
    # print(f"max_amplitude_tape {max_amplitude_tape}")

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

    if max_amplitude > 0.12: #2500 usually measured for bigger signals, 
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

    # print(min_norm_rms_list + 0.4 * std_norm_rms_list)
    # print(min_norm_rms_list + 0.8 * std_norm_rms_list)
    # print(min_norm_rms_list + 1.6 * std_norm_rms_list)
    # print(mean_norm_rms_list + 1.8 * std_norm_rms_list)


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
    
    print(f"Qualify and slice stats:")
    print(f"Signal max amplitude: {max_amplitude}. min normalized rms_list: {min_norm_rms_list}. mean of normalized rms_list {mean_norm_rms_list}, std of normalized rms_list {std_norm_rms_list}  ")
    print(f"Test threshold: {T_RMS}. Slices above: {slice_counter}. Skips: {not_counter}. Pass ratio: {slice_counter/(slice_counter+not_counter)}  ")
    # print(f"total slices above threshold: {slice_counter}")
    # print(f"total nots (skipped): {not_counter}")
    # print(f"threshold ratio: {slice_counter/(slice_counter+not_counter)}")

    #drop failed slices and capture some of the noise slices too
    noise_slice_list = np.zeros([n_slices,2,slice_length])  #define an empty slice array number of slices
    noise_slice_list = sliced_tape_list[pass_list==0]
    noise_slice_list = noise_slice_list[0:slice_counter]

    sliced_tape_list =np.zeros([n_slices,2,slice_length])
    for i in range(0,n_slices):
        sliced_tape_list[i,0,:] = tape[0,i:i+slice_length]
        sliced_tape_list[i,1,:] = tape[1,i:i+slice_length]
    sliced_tape_list = sliced_tape_list[pass_list.nonzero()]

    return sliced_tape_list, noise_slice_list


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
    for i in range(0, n_slices):
        sliced_tape_list[i,0,:] = tape[0,i:i+slice_length]
        sliced_tape_list[i,1,:] = tape[1,i:i+slice_length]
    ###************************************************************

    ## run a qualification test
    if test == 'RMS':
        max_amplitude = np.max(np.abs(tape))
        print(f"max amplitude: {max_amplitude}")

        if max_amplitude > 0.18: #2500 usually measured for bigger signals, 
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

        if max_amplitude > .25:
            T_RMS = min_norm_rms_list + 0.3 * std_norm_rms_list
        elif max_amplitude > 0.1:
            T_RMS = min_norm_rms_list + 0.7 * std_norm_rms_list
        elif max_amplitude > .05:
            T_RMS = min_norm_rms_list + 1.5 * std_norm_rms_list
        else:
            T_RMS = mean_norm_rms_list + 1.8 * std_norm_rms_list
        
        print(f"Threshold for snippet is {T_RMS}")
        print(f"snippet rms: mean {mean_norm_rms_list}, min {min_norm_rms_list}, std {std_norm_rms_list}")

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

        # maxmin = np.amax(rms_list, axis=None)/np.amin(rms_list, axis=None)
        print(f"total iterations:\t{slice_counter+not_counter}")
        print(f"total slices above threshold:\t{slice_counter}")
        print(f"total nots (skipped):\t{not_counter}")
        # print(f"total slices above threshold: {m}")
        # print(f"max/minratio: {maxmin}")
        print(f"threshold ratio:\t{slice_counter/(slice_counter+not_counter)}")

        #drop failed slices and capture some of the noise slices too
        noise_slice_list =np.zeros([n_slices,2,slice_length])  #define an empty slice array number of slices
        noise_slice_list = sliced_tape_list[pass_list==0]
        noise_slice_list = noise_slice_list[0:slice_counter]
        sliced_tape_list = sliced_tape_list[pass_list.nonzero()]
    else: #no qualification case
        print("no qualification test applied")
 
    return sliced_tape_list, noise_slice_list


def load_numpy(filepath: str):
    # load from numpy
    with open(filepath, 'rb' ) as f:
        iqdata = np.load(f) 
        meta = np.load(f) 
        extended_metaf = np.load(f, allow_pickle=True)[0] #note its saved as an np array
    return iqdata, meta, extended_metaf

def load_sigmf(filepath: str):
    # iqdata from data file, meta data from meta file
    full_meta = sigmffile.fromfile(filepath)
    timeseries = full_meta.read_samples().view(np.complex64).flatten()      # returns all timeseries data
    iqdata = timeseries.view(np.float32).reshape(timeseries.shape + (2,)).T # splitting the data into 2 iq arrays

    # extended_metaf: all
    extended_metaf = full_meta.get_global_info()
    for capture in full_meta.get_captures():
        for key in capture:
            if key in extended_metaf:
                if type(extended_metaf[key]) == list:
                    extended_metaf[key].append(capture[key])
                else:
                    extended_metaf[key] = [extended_metaf[key], capture[key]]
            else:
                extended_metaf[key] = capture[key]
    for annotation in full_meta.get_annotations():
        for key in annotation:
            if key in extended_metaf:
                if type(extended_metaf[key]) == list:
                    extended_metaf[key].append(annotation[key])
                else:
                    extended_metaf[key] = [extended_metaf[key], annotation[key]]
            else:
                extended_metaf[key] = annotation[key]
    ''' for removing "core:" from extended_metaf keys
    for key in meta:
        if "core:" in key:
            extended_metaf[key.split('core:')[1]] = extended_metaf.pop(key)
    '''
    # pulling meta data from full metadata
    # meta: [center_freq (in MHz), rec_length, PPB, decimation]
    meta = []
    try:
        freq_center = extended_metaf[SigMFFile.FREQUENCY_KEY]
        length = len(iqdata[0])
        meta = [freq_center, length]
    except:
        print('Could not find select metadata')

    return iqdata, meta, extended_metaf

def folder2dataset(args, dataset={}):
    #set threshold test
    test = "RMS"
    #get foldername from cli parser
    signalfolder = pathlib.Path(str(args.recordings_folder))
    print(signalfolder)

    #create a list of files from the folder
    try:
        if args.subfolders == True:
            paths = list(signalfolder.glob('**/*.npy'))
            print("Examining only subfolders.")
        else:
            paths = list(signalfolder.rglob('*.npy'))
            print("Examining only target folder.")
        if len(paths) == 0:
            raise Exception
        filetype = "numpy"
    except:
        try:
            if args.subfolders == True:
                paths = list(signalfolder.glob('**/*.sigmf-data'))
            else:
                paths = list(signalfolder.rglob('*.sigmf-data'))
            if len(paths) == 0:
                raise Exception
            filetype = "sigmf"
        except:
            print("Files are not the correct format. Please use try again with .npy or .sigmf_data files.")

    n_paths = len(paths)
    print(n_paths, filetype, "files found in folder")

    if args.percent_files <100:
        num_paths_to_keep = int(n_paths * args.percent_files/100)
        paths_to_keep = random.sample(paths, num_paths_to_keep)
        paths=[path for path in paths if path in paths_to_keep]
        print(n_paths, "files left after reduction")

    #check if appending to existing dataset or new dataset
    if dataset == {}:
        append=False
    else:
        append=True

    print(f"append = {append}")

    ### BUILDING THE KEY
    ##get metadata example
    if filetype == "numpy":
        iqdata, meta, extended_metaf = load_numpy(paths[0])
    elif filetype == "sigmf":
        iqdata, meta, extended_metaf = load_sigmf(str(paths[0]))
    else:
        print("Files cannot load.")
    print("The metadata for this file has the following keys:")
    print(extended_metaf.keys())

    #manual assignment of labels

    labels = []

    if args.num_classes:

        if args.keys:
            labels.extend(args.keys[i] for i in range(len(args.keys)))
        else:
            for i in range(args.num_classes):
                labels.append(input(f"\nPlease select the metadata key that corresponds to label {i} and hit <enter>: "))
    
    else:

        if args.keys:
            labels.extend(args.keys[i] for i in range(len(args.keys)))
        else:
            labels.append(input("\nPlease select the metadata key that corresponds to the primary label and hit <enter>: "))
            labels.append(input("\nPlease select the metadata key that corresponds to the secondary label and hit <enter>: "))
            #sets second key to zero if user does not want it
            if labels[1] == "":
                extended_metaf[""]=0

    print("The recordings in this dataset are "+ str(len(iqdata[0,:])) +" samples long.")
    slicelen = args.example_length
    print(f"Signal recordings will be sliced into examples of size {slicelen}.")

    ### FOR LOOP TO ITERATE EACH FILE
    for k in range(len(paths)):
        signalfilename = paths[k]
        print(f"\nadding {signalfilename} to dataset")

        ##open the files
        if filetype == "numpy":
            iqdata, meta, extended_metaf = load_numpy(signalfilename)
        elif filetype == "sigmf":
            iqdata, meta, extended_metaf = load_sigmf(str(signalfilename))
        else:
            print("Files cannot load.")
        #sets second key to zero if user does not want it
        if labels[1] == "":
            extended_metaf[""]=0
        
        for label in labels:
            if label not in extended_metaf:
                print(f"Error: Invalid label: {label}")
                return   # or handle the error in another way that makes sense for your application


        recordingkey = tuple(extended_metaf[label] for label in labels)
        # recordingkey = (extended_metaf[labels[0]], extended_metaf[labels[1]])
        pltlen = len(iqdata[0,:])
        # slices_array, noise_slices = qualify_and_slice(test, iqdata[:,:], slicelen)

        #######################################
        ## LABEL EDITING BLOCK - should be a function
        #normalize thinkrf data
        if extended_metaf["sdr"] =='ThinkRF R5550-427':
            max_amplitude = np.max(np.abs(iqdata))
            iqdata = iqdata / max_amplitude
        if extended_metaf["use_case"] =='4K-Video':
            extended_metaf["use_case"] = "streaming" # updated name for this class

        slices_array, noise_slices = quantize_slice_and_test(test, iqdata[:,:], slicelen,32,'floor')
        
        if append:
            #in the case of an existing dataset
            #check for key existing in dataset
            if recordingkey in dataset:
                dataset[recordingkey] = np.append(dataset[recordingkey], slices_array, axis=0)
            else:
                dataset[recordingkey] = slices_array
        else:
            #in the case of a NEW dataset
            dataset = {recordingkey:slices_array}
            append = True
            print("Dataset has been created. Will now append all other signals to this dataset")

    
    first_axis_sizes = [arr.shape[0] for arr in dataset.values()]
    print(first_axis_sizes)

    return dataset
