import sys
import os


# from recording_curation.augment_and_fill import augment_and_fill
from augment_and_fill import augment_and_fill

from drop_classes import drop_classes
from homogenize_dataset import homogenize_dataset
from subsample_dataset import subsample_dataset
from trim_examples import trim_examples
from folder2dataset import folder2dataset
from config_parser import cli_parser
# from slice_augmenter import noise_generator, time_reversal, spectral_inversion, channel_swap, amplitude_reversal, drop_samples, quantize_tape, quantize_parts, magnitude_rescale, patch_shuffle, convert_to_2xn, slice_augmenter


current_script_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(os.path.dirname(current_script_directory))
# print(parent_directory)
sys.path.append(parent_directory)
import dataset_formats.ds1 as ds1
import dataset_formats.ds2 as ds2

def main():
    args = cli_parser()

    dataset = None

    # if args.recordings_folder and args.filename:
    #     dataset = folder2dataset(args)
    # elif args.source_dataset_file:
    #     try:
    #         dataset = ds2.load_ds2(args.source_dataset_file)
    #     except:
    #         dataset = ds1.load_ds1(args.source_dataset_file)

    # if dataset is None:
    #     print("error: no valid dataset source")
    #     return

    if args.recordings_folder and args.source_dataset_file:
        print("Both recordings folder and source dataset file identified")
        try:
            dataset = ds2.load_ds2(args.source_dataset_file)
            print("ds2 loaded")
        except:
            dataset = ds1.load_ds1(args.source_dataset_file)
            print("ds1 loaded")
    
        dataset = folder2dataset(args,dataset=dataset)

    elif args.source_dataset_file:
        try:
            dataset = ds2.load_ds2(args.source_dataset_file)
        except:
            dataset = ds1.load_ds1(args.source_dataset_file)

    elif args.recordings_folder:
        dataset = folder2dataset(args)

    else:
        print("error: no valid dataset or recording source selected")
        return
    


    # drop_classes
    if args.remove_list: 
        dataset = drop_classes(args, dataset)

    # homogenize_dataset
    if args.homogenize: 
        dataset = homogenize_dataset(dataset, args.homogenize)
    
    # subsample_dataset
    if args.percent_slices_to_keep:
        dataset = subsample_dataset(dataset, args.percent_slices_to_keep)

    # fill_and_augment
    if args.augment_and_fill is not None:
        print(f"adding augmentations to {args.augment_and_fill} total samples")
        dataset = augment_and_fill(dataset, user_specified_value=args.augment_and_fill)
    
    # trim_examples.py
    if args.trim_length and args.keep:
        dataset = trim_examples(dataset, args.trim_length, args.keep)

    # Save the final dataset
    if args.target_dataset_file:
        if args.dataset_format == "h5py":
            if args.new_file == False:
                ds2.append_ds2(args.target_dataset_file, dataset)
            else:
                ds2.save_ds2(args.target_dataset_file, dataset)
        else:
            if args.new_file == False:
                ds1.append_ds1(ds1.load_ds1(args.target_dataset_file), dataset)
                ds1.save_ds1(args.target_dataset_file, dataset)
            else:
                ds1.save_ds1(args.target_dataset_file, dataset)

if __name__ == '__main__':
    main()
