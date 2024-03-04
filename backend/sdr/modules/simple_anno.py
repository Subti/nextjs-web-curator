# python simple_anno.py -f /home/qrf/workarea/ash/sdr/recordings/iq2620MHz040053.npy

import sys
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('cairo')
import numpy as np
# from scipy import fft, signal
import random
import matplotlib.ticker as ticker
import argparse
import pathlib
import os
# import scipy.ndimage as ndimage
import cv2

from modules.numpy_modules import convert_2xn_to_complex
from matplotlib.patches import Rectangle
from scipy.ndimage import binary_opening, find_objects, binary_closing, label, sum, binary_dilation, binary_erosion
from scipy.signal import convolve2d

def erode_clean(specmask,keepsize):
    print("**Using Connected Component Analysis and Erosion to Remove Isolated Pixels**")
    # Define horizontal and vertical structures
    horizontal_structure = np.array([[0, 1, 0],
                                    [0, 1, 0],
                                    [0, 1, 0]])
    vertical_structure = np.array([[0, 0, 0],
                                [1, 1, 1],
                                [0, 0, 0]])

    # Perform horizontal and vertical erosions
    horizontal_eroded = binary_erosion(specmask, structure=horizontal_structure)
    vertical_eroded = binary_erosion(specmask, structure=vertical_structure)

    failed_both_tests = np.logical_and(np.logical_not(horizontal_eroded), np.logical_not(vertical_eroded))
    final_mask = np.where(failed_both_tests, 0, specmask)


    # labeled_mask, num_features = ndimage.label(eroded_mask)
    labeled_mask, num_features = label(final_mask)
    sizes = sum(final_mask, labeled_mask, range(num_features + 1))

    min_size_to_keep = keepsize  ##Define the minimum size (number of contiguous elements) to keep Adjust as needed

    specmask = np.where(sizes[labeled_mask] >= min_size_to_keep, 1, 0) #Filter out small clusters and set them to 0
    return specmask


def sweep_clean(specmask,signal,sliced_signal):
    magnitude = np.abs(signal)
    sigmax = np.max(magnitude)
    sigmin = np.min(magnitude)

    diff_magnitude = np.diff(magnitude, prepend=magnitude[0])
    valleys = np.where((diff_magnitude[:-1] < 0) & (diff_magnitude[1:] > 0))[0]
    valley_depths = magnitude[valleys]
    avg_valley = np.mean(valley_depths)
    time_thres = 1.5*avg_valley
    # print("Average Valley Depth:", avg_valley)
    # plt.plot(magnitude)
    # plt.plot(valleys, magnitude[valleys], 'ro')
    # plt.show()

    # # Create Histogram
    # hist, bins = np.histogram(magnitude, bins=256)
    # # Find the most frequent lower magnitude (assuming it corresponds to valleys)
    # lower_half_hist = hist[:len(hist)//2]  # Consider only the lower half of magnitudes
    # peak_index = np.argmax(lower_half_hist)
    # peak_valley_depth = (bins[peak_index] + bins[peak_index + 1]) / 2
    # print("Depth from Histogram:", peak_valley_depth)
    # # plt.bar(bins[:-1], hist, width=np.diff(bins))
    # # plt.axvline(peak_valley_depth, color='red', linestyle='dashed', linewidth=1)
    # # plt.show()

    for n, snip in enumerate(sliced_signal):
        slicemag = np.abs(snip)
        slicemax = np.max(slicemag)
        slicemin = np.min(slicemag)
        if slicemax < time_thres:
            specmask[n] = np.zeros(len(sliced_signal[0]))
    return specmask

def scipy_bbox(specmask):
    ##################### SCIPY METHOD
    # Apply binary opening with a vertical structure to refine along frequency axis
    vertical_structure = np.ones((3,1))
    refined_mask = binary_opening(specmask, structure=vertical_structure)
    specmask = refined_mask

    # Apply binary dilation to slightly expand the regions
    refined_mask = binary_opening(specmask, structure=np.ones((3,3)))
    specmask = refined_mask

    labeled_spectrum, num_features = label(specmask)
    bounding_boxes = find_objects(labeled_spectrum)
    # region_sizes = sum(refined_mask, labeled_spectrum, range(num_features + 1))

    filtered_boxes = []
    # ## DENSITY THRESHOLD
    # density_threshold = .01  # for example, at least 40% of the pixels in the box should be active
    # for box in bounding_boxes:
    #     # Calculate the number of active pixels in the bounding box
    #     active_pixels = sum(specmask[box])
    #     # Calculate the total pixels in the bounding box
    #     total_pixels = (box[1].stop - box[1].start) * (box[0].stop - box[0].start)
    #     # Calculate density
    #     density = active_pixels / total_pixels
    #     if density >= density_threshold:
    #         filtered_boxes.append(box)
    ## AREA THRESHOLD
    area_threshold = 4  # for example, at least 6 pixels of area
    for box in bounding_boxes:
        # Calculate the area of the bounding box
        area = (box[1].stop - box[1].start) * (box[0].stop - box[0].start)
        # Check if the area meets the threshold
        if area >= area_threshold:
            filtered_boxes.append(box)
    bounding_boxes=filtered_boxes

    for box in bounding_boxes:
        time_slice, freq_slice = box
        time_range = (time_slice.start, time_slice.stop)
        freq_bin_range = (freq_slice.start, freq_slice.stop)
        print(f"Signal detected from time {time_range[0]} to {time_range[1]} and frequency bins {freq_bin_range[0]} to {freq_bin_range[1]}")

    return filtered_boxes

def detect_time_discontinuities(slices_array, threshold=0.05):
    average_magnitudes = np.mean(np.abs(slices_array), axis=1)
    # Compute the differences between successive average magnitudes
    magnitude_differences = np.diff(average_magnitudes)

    threshold = 2*np.std(magnitude_differences)
    # Find where the magnitude difference exceeds the threshold
    discontinuity_indices = np.where(np.abs(magnitude_differences) > threshold)[0]
    print(discontinuity_indices)
    # Start and end of discontinuities
    start_points = np.roll(discontinuity_indices, 1)
    end_points = discontinuity_indices
    # Adjust for boundary conditions
    if len(discontinuity_indices) > 0:
        start_points[0] = 0
        end_points = np.append(end_points, len(average_magnitudes))
    # Since we want to cover the full frequency range, the freq_box remains constant
    freq_box = slice(0, slices_array.shape[1])
    # Construct bounding boxes in one go
    bounding_boxes = [(slice(start, end), freq_box) for start, end in zip(start_points, end_points)]

    return bounding_boxes

def detect_frequency_discontinuities(spectrum, time_bounding_boxes):
    all_bounding_boxes = []

    energy_spectrum = np.abs(spectrum)**2
    noise_floor = np.median(energy_spectrum)
    kernel = np.ones((3, 3)) / 9
    energy_spectrum = convolve2d(energy_spectrum, kernel, mode='same')
    threshold_freq = 2*np.std(energy_spectrum) 

    for time_box in time_bounding_boxes:
        time_range, freq_range = time_box
        sub_spectrum = energy_spectrum[time_range, freq_range]

        is_above_floor = sub_spectrum > noise_floor + threshold_freq
        percentage_threshold = 0.1  # threshold for acceptance
        is_above_floor = np.sum(is_above_floor, axis=0) / is_above_floor.shape[0] > percentage_threshold

        diffs = np.diff(is_above_floor.astype(int))
        f_starts = np.where(diffs == -1)[0] # Transition from True to False
        f_stops = np.where(diffs == 1)[0] # Transition from False to True

        # Create tagged points
        starts_tagged = list(zip(f_starts, ["start"]*len(f_starts)))
        stops_tagged = list(zip(f_stops, ["stop"]*len(f_stops)))

        # Merge and sort
        all_points = starts_tagged + stops_tagged
        all_points.sort(key=lambda x: x[0])

        # Construct the desired pairs
        pairs = []
        i = 0
        while i < len(all_points) - 1:
            if all_points[i][1] == "start":
                # Check if next is a transition
                if all_points[i+1][1] == "trans":
                    pairs.append((all_points[i][0], all_points[i+1][0]))
                    i += 1  # Move to transition, as it will be used as start in next iteration
                else:
                    pairs.append((all_points[i][0], all_points[i+1][0]))
                    i += 1  # Skip the next, because it's a stop and we've just paired it
            i += 1  # Regular increment for the loop

        print(pairs)

        global_start_freq = 0
        for start, end in pairs:
            all_bounding_boxes.append((time_range, slice(start, end)))
            
    print(noise_floor)
    print(threshold_freq)
    print(np.max(energy_spectrum))

        
    return all_bounding_boxes






def annotate_npy(args, saveplot=True):

    filename = args.filename
    with open(filename, 'rb' ) as f:
        iqdata = np.load(f) 
        meta = np.load(f) 
        extended_metaf = np.load(f, allow_pickle=True)[0] #note its saved as an np array

    signal = convert_2xn_to_complex(iqdata)
    base_filename = os.path.splitext(os.path.basename(filename))[0]
    del iqdata

    # get details on sampling from metadata
    try:
        sample_rate = int(extended_metaf["effective_sample_rate"])
    except Exception:
        sample_rate = int(extended_metaf["sample_rate"])
    print(signal.shape)
    rec_length = len(signal)
    duration = rec_length/sample_rate
    nfft = args.nfft
    time_rec = extended_metaf['time_recorded']
    center_freq = int(extended_metaf["center_freq"])

    if center_freq > pow(10,6): # double check that all frequencies are in MHz
        center_freq /= pow(10,6)
    if sample_rate > pow(10,6):
        sample_rate = sample_rate/pow(10,6)

    ##print signal details based on metadata
    print("iq data:",signal)
    print("sample rate:", sample_rate)
    print("tape length (samples):",rec_length)
    print("tape duration (seconds):", duration)
    print("fft bins:", nfft)
    print("metadata contents:",extended_metaf)

    #construct array of slices
    slices = int(rec_length/nfft)
    sliced_signal = np.empty([slices,nfft],dtype='complex64')
    print ("this recording contains", slices,"slices of length", nfft) 
    sliced_signal = signal[:slices * nfft].reshape(slices, nfft)

    print("slices",slices)
    print ("sliced iq data shape", sliced_signal.shape)

    # EQUALIZER CODE
    if args.equalize:
        print("**EQUALIZING SIGNAL SLICES**")
        magnitude = np.abs(sliced_signal)
        # Step 2: Apply histogram equalization to the magnitude
        equalized_magnitude = cv2.equalizeHist((magnitude * 255).astype(np.uint8)) / 255.0
        # Step 3: Reconstruct the complex values with equalized magnitudes and original phases
        equalized_signal = equalized_magnitude * np.exp(1j * np.angle(sliced_signal))
        windowed_signal = equalized_signal * np.hanning(equalized_signal.shape[1])
    else:
        windowed_signal = sliced_signal * np.hanning(sliced_signal.shape[1])

    spectrum = np.fft.fftshift(np.fft.fft(windowed_signal, axis=1), axes=1)

    print(spectrum.shape)

    magnitude_spectrum = np.abs(spectrum)   
    min_amplitude = np.min(magnitude_spectrum)
    max_amplitude = np.max(magnitude_spectrum)
    normalized_mag_spectrum = np.abs((magnitude_spectrum - min_amplitude) / (max_amplitude - min_amplitude))

    # TODO: Test these values
    if args.bbox and duration > 0.01:
        method = "1"
        args.clean = True
        args.sweep_clean = True
        keepsize = 6
    elif args.bbox: 
        method = "1"
        args.clean = True
        args.sweep_clean = True
        keepsize = 3
    else: 
        method = "3" 


    if method == "1": #method 1 - energy global threshold based
        print("using global energy threshold")
        energy_spectrum = magnitude_spectrum**2
        threshold = np.percentile(energy_spectrum, 80)
        specmask = energy_spectrum > threshold
    elif method == "2":#method 2 - energy local threshold based - for longer recordings.
        print("using local energy threshold")
        from skimage.filters import threshold_local
        energy_spectrum = magnitude_spectrum**2
        block_size = 33  # Size of the neighborhood. Adjust based on data characteristics.
        adaptive_thresh = threshold_local(energy_spectrum, block_size, offset=-4)
        specmask = energy_spectrum > adaptive_thresh

    else: # method 3 - magnitude threshold based - when not doing bounding boxes.
        print("using global magnitude threshold")
        spec_mean = np.mean(normalized_mag_spectrum)
        primethres = np.std(normalized_mag_spectrum) * 1.5 + spec_mean
        specmask = np.where(normalized_mag_spectrum < primethres, 0, 1)



    #### TODO: mask cleanup - needs work
    if args.clean:
        specmask = erode_clean(specmask,keepsize)


    if args.sweep_clean:
        specmask = sweep_clean(specmask,signal,sliced_signal)

    if args.bbox:
        ######################################### SCIPY METHOD
        bounding_boxes = scipy_bbox(specmask)
        
        ######################################################

        # #HOMEBREW METHOD
        # Generate bounding boxes
        # Generate bounding boxes for the time domain
        print("HOMEBREW")
        bounding_boxes = detect_time_discontinuities(sliced_signal)

        print(len(bounding_boxes))
        bounding_boxes = detect_frequency_discontinuities(spectrum,bounding_boxes)
        print(len(bounding_boxes))


        # for box in bounding_boxes:
        #     time_slice, freq_slice = box
        #     time_range = (time_slice.start, time_slice.stop)
        #     freq_bin_range = (freq_slice.start, freq_slice.stop)
        #     print(f"Signal detected from time {time_range[0]} to {time_range[1]} and frequency bins {freq_bin_range[0]} to {freq_bin_range[1]}")
        # print(len(bounding_boxes))
        figs = 3
    else:  
        figs = 2

    if saveplot == True:
        # Create a figure with two subplots (1 row, 2 columns)
        fig, axes = plt.subplots(1, figs, figsize=(figs*6, 30))  # Adjust the figure size as needed

        # Plot normalized_mag_spectrum on the left subplot
        axes[0].imshow(normalized_mag_spectrum, aspect='auto', cmap='viridis', origin='lower', vmin=0, vmax=0.3)
        axes[0].set_title('FFT Spectrum')
        axes[0].set_xlabel(f'Frequency bin range from LF {center_freq-sample_rate/2} to CF {center_freq} to HF {center_freq+sample_rate/2}')
        axes[0].set_ylabel(f'Slice Index. Total duration: {round(duration,6)} s')
        # axes[0].set_colorbar(label='Magnitude')

        # Plot specmask on the right subplot
        axes[1].imshow(specmask, aspect='auto', cmap='viridis', origin='lower', vmin=0, vmax=1)  # Adjust the colormap and range as needed
        axes[1].set_title('Spec Mask')
        axes[1].set_xlabel(f'Frequency bin. range from LF {center_freq-sample_rate/2} to CF {center_freq} to HF {center_freq+sample_rate/2}')
        # axes[1].set_xlim(center_freq-sample_rate/2, center_freq+sample_rate/2)
        axes[1].set_ylabel(f'Slice Index. Total duration: {round(duration,6)} s')
        # axes[1].set_colorbar(label='Mask')

        if args.bbox:
            # Bounding boxes plotting on the third subplot
            axes[2].imshow(normalized_mag_spectrum, aspect='auto', cmap='viridis', origin='lower', vmin=0, vmax=0.3)
            axes[2].set_title('Bounding Boxes on FFT Spectrum')
            axes[2].set_xlabel(f'Frequency bin range from LF {center_freq-sample_rate/2} to CF {center_freq} to HF {center_freq+sample_rate/2}')
            axes[2].set_ylabel(f'Slice Index. Total duration: {round(duration,6)} s')

            # Draw bounding boxes on the third subplot
            for box in bounding_boxes:
                time_slice, freq_slice = box
                # Calculate width and height for each box
                width = freq_slice.stop - freq_slice.start
                height = time_slice.stop - time_slice.start
                # Draw the bounding box
                rect = Rectangle((freq_slice.start, time_slice.start), width, height, edgecolor='red', facecolor='none')
                axes[2].add_patch(rect)



        # Adjust the layout to prevent overlap
        plt.tight_layout()

        # Save the plot as a PNG file
        pathlib.Path("annotations").mkdir(exist_ok=True) #check if folder exists then make it
        plt.savefig(f'annotations/{base_filename}_anno_{nfft}.png', bbox_inches='tight')

    extended_meta = np.array([extended_metaf])

    with open(f'annotations/{base_filename}_anno_{nfft}.xnp', 'wb') as file:
        np.save(file,sliced_signal)
        np.save(file,spectrum)
        np.save(file,specmask)
        np.save(file,extended_meta)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--nfft", "-n",  type=int, default=2048, help="NFFT's to calculate from. Default - 2048")
    parser.add_argument("--filename", "-f",  type=str, default='test.npy', help="File to load. Default - test.npy")
    parser.add_argument("--anno_type", "-x",  type=str, default='pixels', help="Annotation type - pixels and bounding_box (not implemented)")
    parser.add_argument("--annotation", "-a",  type=str, default='unknown', help="Default annotation to add to ALL components")
    parser.add_argument("--clean", "-w",  type=bool, action=argparse.BooleanOptionalAction, help="--clean or -w to clean with erosion")
    parser.add_argument("--equalize", "-e",  type=bool, action=argparse.BooleanOptionalAction, help="--equalize for equalization or no argument for none.")
    parser.add_argument("--sweep_clean", "-s",  type=bool, action=argparse.BooleanOptionalAction, help="--sweep_clean for zeroing specmask based on time series response.")
    parser.add_argument("--bbox", "-b",  type=bool, action=argparse.BooleanOptionalAction, help="--bbox for bounding box based.")
    parser.add_argument("--threshold", "-t",  type=float, default=1.0, help="Threshold in Standard Deviations from the mean for mask creation")

    args = parser.parse_args()
    annotate_npy(args)

#to load from xnp file
# with open(filename, 'rb' ) as f:
#     sliced_signal = np.load(f) 
#     spectrum = np.load(f) 
#     specmask = np.load(f) 
#     extended_metaf = np.load(f, allow_pickle=True)[0] #note its saved as an np array

# TODO:
# explore which methods of cleaning are more appropriae for shorter signals, and which method of thresholding are better for hsort vs long signals
# improve bounding box script for shorter signals
    













### OLDER SIMPLE_ANNO PROTOTYPE WITH THE INTERESTING DISCONTINUITIES CONCEPT


# # python simple_anno.py -f /home/qrf/workarea/ash/sdr/recordings/iq2620MHz040053.npy

# import sys
# import matplotlib
# import matplotlib.pyplot as plt
# matplotlib.use('cairo')
# import numpy as np
# # from scipy import fft, signal
# import random
# import matplotlib.ticker as ticker
# import argparse
# import pathlib
# import os
# # import scipy.ndimage as ndimage
# import cv2

# from numpy_modules import convert_2xn_to_complex
# from matplotlib.patches import Rectangle
# from scipy.ndimage import binary_opening, find_objects, binary_closing, label, sum, binary_dilation, binary_erosion


# def detect_time_discontinuities(slices_array, threshold=0.5):
#     average_magnitudes = np.mean(np.abs(slices_array), axis=1)
#     discontinuities = [0]  # Start with the first slice

#     for i in range(1, len(average_magnitudes)):
#         if abs(average_magnitudes[i] - average_magnitudes[i-1]) > threshold:
#             discontinuities.append(i)

#     discontinuities.append(len(average_magnitudes))  # End with the last slice
#     return discontinuities

# def detect_freq_discontinuities(slice_spectrum, threshold=0.5):
#     freq_changes = [0]  # Start with the first frequency bin

#     for i in range(1, slice_spectrum.shape[0]):
#         if abs(slice_spectrum[i] - slice_spectrum[i-1]) > threshold:
#             freq_changes.append(i)

#     freq_changes.append(slice_spectrum.shape[0])  # End with the last frequency bin
#     return freq_changes


# def merge_time_boxes(time_discontinuities, magnitude_spectrum, merge_threshold=0.2):
#     merged_boxes = []
#     prev_box = time_discontinuities[0]

#     for i in range(1, len(time_discontinuities)):
#         # Compare frequency profile of the current box with the previous
#         current_profile = np.mean(magnitude_spectrum[time_discontinuities[i-1]:time_discontinuities[i]], axis=0)
#         prev_profile = np.mean(magnitude_spectrum[prev_box:time_discontinuities[i-1]], axis=0)

#         profile_diff = np.abs(current_profile - prev_profile)

#         if np.mean(profile_diff) < merge_threshold:
#             # If the profiles are similar, continue without starting a new box
#             continue
#         else:
#             merged_boxes.append((prev_box, time_discontinuities[i-1]))
#             prev_box = time_discontinuities[i]

#     merged_boxes.append((prev_box, time_discontinuities[-1]))
#     return merged_boxes


# def filter_small_boxes(boxes, min_area=6):
#     return [box for box in boxes if (box[1]-box[0]) >= min_area]

# def merge_freq_boxes(freq_discontinuities, slice_spectrum, merge_threshold=0.2):
#     merged_boxes = []
#     prev_box = freq_discontinuities[0]

#     for i in range(1, len(freq_discontinuities)):
#         # Compare magnitude profile of the current box with the previous
#         current_profile = np.mean(slice_spectrum[freq_discontinuities[i-1]:freq_discontinuities[i]])
#         prev_profile = np.mean(slice_spectrum[prev_box:freq_discontinuities[i-1]])

#         profile_diff = abs(current_profile - prev_profile)

#         if profile_diff < merge_threshold:
#             # If the profiles are similar, continue without starting a new box
#             continue
#         else:
#             merged_boxes.append((prev_box, freq_discontinuities[i-1]))
#             prev_box = freq_discontinuities[i]

#     merged_boxes.append((prev_box, freq_discontinuities[-1]))
#     return merged_boxes




# def annotate_npy(args, saveplot=True):


#     #input handling
#     filename = args.filename


#     ##open the files
#     with open(filename, 'rb' ) as f:
#         iqdata = np.load(f) 
#         meta = np.load(f) 
#         extended_metaf = np.load(f, allow_pickle=True)[0] #note its saved as an np array

#     signal = convert_2xn_to_complex(iqdata)

#     base_filename = os.path.splitext(os.path.basename(filename))[0]

#     del iqdata

#     # get details on sampling from metadata
#     try:
#         sample_rate = int(extended_metaf["effective_sample_rate"])
#     except Exception:
#         sample_rate = int(extended_metaf["sample_rate"])

#     print(signal.shape)

#     rec_length = len(signal)
#     duration = rec_length/sample_rate

#     nfft = args.nfft

#     time_rec = extended_metaf['time_recorded']
#     center_freq = int(extended_metaf["center_freq"])

#     if center_freq > pow(10,6): # double check that all frequencies are in MHz
#         center_freq /= pow(10,6)
#     if sample_rate > pow(10,6):
#         sample_rate = sample_rate/pow(10,6)


#     ##print signal details based on metadata
#     print("iq data:",signal)
#     print("sample rate:", sample_rate)
#     print("tape length (samples):",rec_length)
#     print("tape duration (seconds):", duration)
#     print("fft bins:", nfft)
#     print("metadata contents:",extended_metaf)


#     #construct array of slices
#     slices = int(rec_length/nfft)
#     sliced_signal = np.empty([slices,nfft],dtype='complex64')
#     print ("this recording contains", slices,"slices of length", nfft) 

#     sliced_signal = signal[:slices * nfft].reshape(slices, nfft)

#     print("slices",slices)
#     print ("sliced iq data shape", sliced_signal.shape)

#     # EQUALIZER CODE
#     if args.equalize:
#         print("**EQUALIZING SIGNAL SLICES**")
#         magnitude = np.abs(sliced_signal)
#         # Step 2: Apply histogram equalization to the magnitude
#         equalized_magnitude = cv2.equalizeHist((magnitude * 255).astype(np.uint8)) / 255.0
#         # Step 3: Reconstruct the complex values with equalized magnitudes and original phases
#         equalized_signal = equalized_magnitude * np.exp(1j * np.angle(sliced_signal))
#         windowed_signal = equalized_signal * np.hanning(equalized_signal.shape[1])
#     else:
#         windowed_signal = sliced_signal * np.hanning(sliced_signal.shape[1])

#     spectrum = np.fft.fftshift(np.fft.fft(windowed_signal, axis=1), axes=1)

#     print(spectrum.shape)

#     magnitude_spectrum = np.abs(spectrum)   
#     min_amplitude = np.min(magnitude_spectrum)
#     max_amplitude = np.max(magnitude_spectrum)
#     normalized_mag_spectrum = np.abs((magnitude_spectrum - min_amplitude) / (max_amplitude - min_amplitude))

#     if args.bbox and duration > 0.01:
#         method = "2"
#     elif args.bbox: 
#         method = "1"
#     else: 
#         method = "3" 


#     if method == "1": #method 1 - energy global threshold based
#         print("using global energy threshold")
#         energy_spectrum = magnitude_spectrum**2
#         threshold = np.percentile(energy_spectrum, 80)
#         specmask = energy_spectrum > threshold
#     elif method == "2":#method 2 - energy local threshold based - for longer recordings.
#         print("using local energy threshold")
#         from skimage.filters import threshold_local
#         energy_spectrum = magnitude_spectrum**2
#         block_size = 33  # Size of the neighborhood. Adjust based on data characteristics.
#         adaptive_thresh = threshold_local(energy_spectrum, block_size, offset=-3)
#         specmask = energy_spectrum > adaptive_thresh

#     else: # method 3 - magnitude threshold based - when not doing bounding boxes.
#         print("using global magnitude threshold")
#         spec_mean = np.mean(normalized_mag_spectrum)
#         primethres = np.std(normalized_mag_spectrum) * 1.5 + spec_mean
#         specmask = np.where(normalized_mag_spectrum < primethres, 0, 1)



#     #### TODO: mask cleanup - needs work
#     if args.clean:
#         print("**Using Connected Component Analysis and Erosion to Remove Isolated Pixels**")
#         # eroded_mask = ndimage.binary_erosion(specmask, structure=np.ones((1, 2)))

#         # Define horizontal and vertical structures
#         horizontal_structure = np.array([[0, 1, 0],
#                                         [0, 1, 0],
#                                         [0, 1, 0]])
#         vertical_structure = np.array([[0, 0, 0],
#                                     [1, 1, 1],
#                                     [0, 0, 0]])

#         # Perform horizontal and vertical erosions
#         horizontal_eroded = binary_erosion(specmask, structure=horizontal_structure)
#         vertical_eroded = binary_erosion(specmask, structure=vertical_structure)

#         failed_both_tests = np.logical_and(np.logical_not(horizontal_eroded), np.logical_not(vertical_eroded))
#         final_mask = np.where(failed_both_tests, 0, specmask)


#         # labeled_mask, num_features = ndimage.label(eroded_mask)
#         labeled_mask, num_features = label(final_mask)
#         sizes = sum(final_mask, labeled_mask, range(num_features + 1))

#         min_size_to_keep = 3  ##Define the minimum size (number of contiguous elements) to keep Adjust as needed

#         specmask = np.where(sizes[labeled_mask] >= min_size_to_keep, 1, 0) #Filter out small clusters and set them to 0


#     if args.sweep_clean:
#         magnitude = np.abs(signal)
#         sigmax = np.max(magnitude)
#         sigmin = np.min(magnitude)

#         diff_magnitude = np.diff(magnitude, prepend=magnitude[0])
#         valleys = np.where((diff_magnitude[:-1] < 0) & (diff_magnitude[1:] > 0))[0]
#         valley_depths = magnitude[valleys]
#         avg_valley = np.mean(valley_depths)
#         time_thres = 1.5*avg_valley
#         # print("Average Valley Depth:", avg_valley)
#         # plt.plot(magnitude)
#         # plt.plot(valleys, magnitude[valleys], 'ro')
#         # plt.show()

#         # # Create Histogram
#         # hist, bins = np.histogram(magnitude, bins=256)
#         # # Find the most frequent lower magnitude (assuming it corresponds to valleys)
#         # lower_half_hist = hist[:len(hist)//2]  # Consider only the lower half of magnitudes
#         # peak_index = np.argmax(lower_half_hist)
#         # peak_valley_depth = (bins[peak_index] + bins[peak_index + 1]) / 2
#         # print("Depth from Histogram:", peak_valley_depth)
#         # # plt.bar(bins[:-1], hist, width=np.diff(bins))
#         # # plt.axvline(peak_valley_depth, color='red', linestyle='dashed', linewidth=1)
#         # # plt.show()



#         for n, snip in enumerate(sliced_signal):
#             slicemag = np.abs(snip)
#             slicemax = np.max(slicemag)
#             slicemin = np.min(slicemag)
#             if slicemax < time_thres:
#                 specmask[n] = np.zeros(args.nfft)

#     if args.bbox:
#         # Apply binary opening with a vertical structure to refine along frequency axis
#         vertical_structure = np.ones((3,1))
#         refined_mask = binary_opening(specmask, structure=vertical_structure)

#         # Apply binary dilation to slightly expand the regions
#         refined_mask = binary_dilation(refined_mask, structure=np.ones((3,3)))
#         # refined_mask = binary_opening(specmask, structure=np.ones((3,3)))

#         labeled_spectrum, num_features = label(specmask)
#         bounding_boxes = find_objects(labeled_spectrum)
#         # labeled_spectrum, num_features = label(refined_mask)
#         # region_sizes = sum(refined_mask, labeled_spectrum, range(num_features + 1))

#         filtered_boxes = []
#         # ## DENSITY THRESHOLD
#         # density_threshold = .01  # for example, at least 40% of the pixels in the box should be active
#         # for box in bounding_boxes:
#         #     # Calculate the number of active pixels in the bounding box
#         #     active_pixels = sum(specmask[box])
#         #     # Calculate the total pixels in the bounding box
#         #     total_pixels = (box[1].stop - box[1].start) * (box[0].stop - box[0].start)
#         #     # Calculate density
#         #     density = active_pixels / total_pixels
#         #     if density >= density_threshold:
#         #         filtered_boxes.append(box)
#         ## AREA THRESHOLD
#         area_threshold = 4  # for example, at least 6 pixels of area
#         for box in bounding_boxes:
#             # Calculate the area of the bounding box
#             area = (box[1].stop - box[1].start) * (box[0].stop - box[0].start)
#             # Check if the area meets the threshold
#             if area >= area_threshold:
#                 filtered_boxes.append(box)
#         bounding_boxes=filtered_boxes

#         for box in bounding_boxes:
#             time_slice, freq_slice = box
#             time_range = (time_slice.start, time_slice.stop)
#             freq_bin_range = (freq_slice.start, freq_slice.stop)
#             print(f"Signal detected from time {time_range[0]} to {time_range[1]} and frequency bins {freq_bin_range[0]} to {freq_bin_range[1]}")

#         # #homebrew method
#         # Generate bounding boxes
#         # Generate bounding boxes for the time domain
#         # time_discontinuities = detect_time_discontinuities(sliced_signal)
#         # time_boxes = merge_time_boxes(time_discontinuities, magnitude_spectrum)
#         # time_boxes = filter_small_boxes(time_boxes)

#         # # Generate bounding boxes for the frequency domain within each time box
#         # freq_boxes_per_time_box = []
#         # for time_box in time_boxes:
#         #     slice_spectrum = magnitude_spectrum[time_box[0]:time_box[1]]
#         #     avg_slice_spectrum = np.mean(slice_spectrum, axis=0)
#         #     freq_discontinuities = detect_freq_discontinuities(avg_slice_spectrum)
#         #     freq_boxes = merge_freq_boxes(freq_discontinuities, avg_slice_spectrum)
#         #     freq_boxes = filter_small_boxes(freq_boxes)
#         #     freq_boxes_per_time_box.append(freq_boxes)

#         # # Output bounding box information
#         # bounding_boxes = []
#         # for time_idx, time_box in enumerate(time_boxes):
#         #     time_slice = slice(time_box[0], time_box[1])  # Convert the tuple to a slice object for time
#         #     for freq_box in freq_boxes_per_time_box[time_idx]:
#         #         freq_slice = slice(freq_box[0], freq_box[1])  # Convert the tuple to a slice object for frequency
#         #         bounding_boxes.append((time_slice, freq_slice))  # Store as a tuple of slices
#         #         print(f"Signal detected from time {time_box[0]} to {time_box[1]} and frequency bins {freq_box[0]} to {freq_box[1]}")




#         figs = 3
#     else:  
#         figs = 2

#     if saveplot == True:
#         # Create a figure with two subplots (1 row, 2 columns)
#         fig, axes = plt.subplots(1, figs, figsize=(figs*6, 10))  # Adjust the figure size as needed

#         # Plot normalized_mag_spectrum on the left subplot
#         axes[0].imshow(normalized_mag_spectrum, aspect='auto', cmap='viridis', origin='lower', vmin=0, vmax=0.3)
#         axes[0].set_title('FFT Spectrum')
#         axes[0].set_xlabel(f'Frequency bin range from LF {center_freq-sample_rate/2} to CF {center_freq} to HF {center_freq+sample_rate/2}')
#         axes[0].set_ylabel(f'Slice Index. Total duration: {round(duration,6)} s')
#         # axes[0].set_colorbar(label='Magnitude')

#         # Plot specmask on the right subplot
#         axes[1].imshow(specmask, aspect='auto', cmap='viridis', origin='lower', vmin=0, vmax=1)  # Adjust the colormap and range as needed
#         axes[1].set_title('Spec Mask')
#         axes[1].set_xlabel(f'Frequency bin. range from LF {center_freq-sample_rate/2} to CF {center_freq} to HF {center_freq+sample_rate/2}')
#         # axes[1].set_xlim(center_freq-sample_rate/2, center_freq+sample_rate/2)
#         axes[1].set_ylabel(f'Slice Index. Total duration: {round(duration,6)} s')
#         # axes[1].set_colorbar(label='Mask')

#         if args.bbox:
#             # Bounding boxes plotting on the third subplot
#             axes[2].imshow(normalized_mag_spectrum, aspect='auto', cmap='viridis', origin='lower', vmin=0, vmax=0.3)
#             axes[2].set_title('Bounding Boxes on FFT Spectrum')
#             axes[2].set_xlabel(f'Frequency bin range from LF {center_freq-sample_rate/2} to CF {center_freq} to HF {center_freq+sample_rate/2}')
#             axes[2].set_ylabel(f'Slice Index. Total duration: {round(duration,6)} s')

#             # Draw bounding boxes on the third subplot
#             for box in bounding_boxes:
#                 time_slice, freq_slice = box
#                 # Calculate width and height for each box
#                 width = freq_slice.stop - freq_slice.start
#                 height = time_slice.stop - time_slice.start
#                 # Draw the bounding box
#                 rect = Rectangle((freq_slice.start, time_slice.start), width, height, edgecolor='red', facecolor='none')
#                 axes[2].add_patch(rect)



#         # Adjust the layout to prevent overlap
#         plt.tight_layout()

#         # Save the plot as a PNG file
#         pathlib.Path("annotations").mkdir(exist_ok=True) #check if folder exists then make it
#         plt.savefig(f'annotations/{base_filename}_anno_{nfft}.png', bbox_inches='tight')

#     extended_meta = np.array([extended_metaf])

#     with open(f'annotations/{base_filename}_anno_{nfft}.xnp', 'wb') as file:
#         np.save(file,sliced_signal)
#         np.save(file,spectrum)
#         np.save(file,specmask)
#         np.save(file,extended_meta)


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--nfft", "-n",  type=int, default=2048, help="NFFT's to calculate from. Default - 2048")
#     parser.add_argument("--filename", "-f",  type=str, default='test.npy', help="File to load. Default - test.npy")
#     parser.add_argument("--anno_type", "-x",  type=str, default='pixels', help="Annotation type - pixels and bounding_box (not implemented)")
#     parser.add_argument("--annotation", "-a",  type=str, default='unknown', help="Default annotation to add to ALL components")
#     parser.add_argument("--clean", "-w",  type=bool, action=argparse.BooleanOptionalAction, help="--clean or -w to clean with erosion")
#     parser.add_argument("--equalize", "-e",  type=bool, action=argparse.BooleanOptionalAction, help="--equalize for equalization or no argument for none.")
#     parser.add_argument("--sweep_clean", "-s",  type=bool, action=argparse.BooleanOptionalAction, help="--sweep_clean for zeroing specmask based on time series response.")
#     parser.add_argument("--bbox", "-b",  type=bool, action=argparse.BooleanOptionalAction, help="--bbox for bounding box based.")
#     parser.add_argument("--threshold", "-t",  type=float, default=1.0, help="Threshold in Standard Deviations from the mean for mask creation")

#     args = parser.parse_args()
#     annotate_npy(args)

# #to load from xnp file
# # with open(filename, 'rb' ) as f:
# #     sliced_signal = np.load(f) 
# #     spectrum = np.load(f) 
# #     specmask = np.load(f) 
# #     extended_metaf = np.load(f, allow_pickle=True)[0] #note its saved as an np array

# # TODO:
# # explore which methods of cleaning are more appropriae for shorter signals, and which method of thresholding are better for hsort vs long signals
# # improve bounding box script for shorter signals    