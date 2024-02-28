import sys
import matplotlib.pyplot as plt
import numpy as np
import pickle
import pathlib
import argparse


def load_file(filename):
    with open(filename, 'rb') as f:
        iqdata = np.load(f)
        metaf = np.load(f)
        try:
            extended_metaf = np.load(f, allow_pickle=True)[0] #note its saved as an np array
        except Exception:
            print("no extended metadata")
            extended_metaf = {}
    return (iqdata, metaf, extended_metaf)


def npy_slicer(args):
    ##open the files
    iqdata, metaf, extended_metaf = load_file(args.source_signal_file)

    ### slice decision handling
    cuts = list(map(int, args.cuts))
    cuts.sort()
    n_cuts = len(cuts)
    print(f"Will perform {n_cuts} cuts on {args.source_signal_file}")

    ###folder / file handling for output file
    target_folder_name = str(args.target_folder)
    pathlib.Path(target_folder_name).mkdir(exist_ok=True) #check if folder exists then make it
    target_folder = pathlib.Path(target_folder_name)

    for index, cut in enumerate(cuts):
        slicestart = 0 if index == 0 else cuts[index-1]
        slicestop = cut

        # Ensure slicestop is within the bounds of the iqdata array
        slicestop = min(slicestop, iqdata.shape[1])

        # Ensure slicelen matches the actual slice length
        slicelen = slicestop - slicestart

        if slicelen < 0:
            print(f"Skipping cut number {index}: slicestart ({slicestart}) is greater than slicestop ({slicestop})")
            continue

        slice_data = np.zeros([2, slicelen])

        print(f"cut number {index}: from {slicestart} to {slicestop}, length {len(slice_data[0,:])}")
        slice_data[0,:] = iqdata[0,slicestart:slicestop]
        slice_data[1,:] = iqdata[1,slicestart:slicestop]

        # file handling
        signalfilename = pathlib.Path(args.source_signal_file)
        outputsignalfilename = f"{str(index)}_{signalfilename.name}"
        pathlib.Path(target_folder).mkdir(exist_ok=True)
        fullpath = target_folder / outputsignalfilename

        extended_meta = np.array([extended_metaf])
        print(f"saving to {fullpath}")
        # open and save a new file
        with open(fullpath, 'wb' ) as f:
            np.save(f,slice_data) ############# change iqdata to the new sliced string
            np.save(f,metaf)
            if extended_metaf:
                np.save(f,extended_meta) 

    print("slicing completed")

if __name__ == '__main__':
    #parse arguments if theyre provided
    parser = argparse.ArgumentParser(description='NPY_SLICER - splits up a file into user defined slices and saves to a destination folder.')
    parser.add_argument("--source_signal_file", "-s", help="Source signal (can be a path)")
    parser.add_argument("--target_folder", "-t", help="Target signal (can be a path)")
    parser.add_argument("--cuts", "-c", nargs="+", type=int, help="Locations to perform cuts.")
    args = parser.parse_args()

    npy_slicer(args)