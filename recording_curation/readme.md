# Qoherent Dataset Curator

## Usage

curator.py [-h] [-sdf SOURCE_DATASET_FILE] [-r RECORDINGS_FOLDER] [-f FILENAME] [-e EXAMPLE_LENGTH] [-m NUM_CLASSES] [-s SUBFOLDERS] [-p PERCENT_FILES] [-i HOMOGENIZE] [-a AUGMENT_AND_FILL]
                  [-c PERCENT_SLICES_TO_KEEP] [-l REMOVE_LIST] [-x TRIM_LENGTH] [-k KEEP] [-n NEW_FILE] [-t TARGET_DATASET_FILE] [-d DATASET_FORMAT]

folder2dataset-auto - produces a 1.0-dataset from all files within a numpy folder.

### Optional Arguments:  
  -h, --help      &emsp;&emsp;      show this help message and exit  
  -sdf SOURCE_DATASET_FILE, --source_dataset_file SOURCE_DATASET_FILE  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Path to the source dataset file  
  -r RECORDINGS_FOLDER, --recordings_folder RECORDINGS_FOLDER  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Path to the folder with npy recordings. Examples './recs/'. Default None  
  -j KEYS, --keys KEYS  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Keys for the dataset's classes
  -f FILENAME, --filename FILENAME  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Filename for the dataset to be produced. Default example 'example_dataset.dat'  
  -e EXAMPLE_LENGTH, --example_length EXAMPLE_LENGTH  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Option for choosing example size when making a new dataset or adding to an existing one. Default is 512.  
  -m NUM_CLASSES, --num_classes NUM_CLASSES  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Select the number of labels each example will have.  
  -s SUBFOLDERS, --subfolders SUBFOLDERS  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Flag for including all subfolders within the search. Default False  
  -p PERCENT_FILES, --percent_files PERCENT_FILES  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Option for only capturing a subset of the files in the source folder (e.g. 70pct of all recordings). Default example: 100  
  -i HOMOGENIZE, --homogenize HOMOGENIZE  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Homogenizes the size of each class within the dataset to the value provided i.e makes all classes the same length. Default None,
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     which results in using minimum size within dataset  
  -a AUGMENT_AND_FILL, --augment_and_fill AUGMENT_AND_FILL  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Number of examples to homogenize each class to. If no number is provided, the average number of examples is used.  
  -c PERCENT_SLICES_TO_KEEP, --percent_slices_to_keep PERCENT_SLICES_TO_KEEP  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Option for only capturing a subset of the SLICES from the files in the source folder (e.g. 70pct of all slices). Note, this happens
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     AFTER homogenize. Default example: 100  
  -l REMOVE_LIST, --remove_list REMOVE_LIST  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     List of keys to remove from dataset. Default: []  
  -x TRIM_LENGTH, --trim_length TRIM_LENGTH  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Option for trimming samples to a chosen length, generally from an existing dataset. Default is None, which results in vectors
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     being trimmed to the length of the shortest vector.  
  -k KEEP, --keep KEEP  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Section of data to keep when trimming samples. Options are start, middle, and end. Default is 'middle'  
  -n NEW_FILE, --new_file NEW_FILE  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Flag for saving file as a new dataset. Default true  
  -t TARGET_DATASET_FILE, --target_dataset_file TARGET_DATASET_FILE  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Target path where dataset will be saved.  
  -d DATASET_FORMAT, --dataset_format DATASET_FORMAT  
  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;     Option to choose dataset formatting between pickle and h5py. Default is pickle  
 
### Functions  
**Folder to Dataset**  
Takes a folder of numpy or sigmf files and compiles them all into a dataset of type dict(tuple, ndarray).  
Note: if a folder containing both numpy and sigmf files is given, only numpy files will be compiled.  

Input: args - arguments from cli parser (recordings_folder, subfolders, percent_files, num_classes, keys, example_length), dataset (optional) - existing dataset to append data to    
Output: dataset - recording data, type dict(tuple, ndarray)  

**Drop Classes**  
Removes given classes (keys) from the dataset  
Input: args - arguments from cli parser (remove_list), dataset - dataset to remove classes from  
Output: dataset - dataset with given classes removed

**Homogenize Dataset**  
Homogenizes each class of data to have a uniform number of slices by randomly selecting the target number of slices from the class.  
If a target number is not given, the dataset is homogenized to the minimum number of slices in a class within the dataset.  
Function checks that less than 10% of slices have low amplitudes (defined as 10% of mean amplitude). If this condition is not met, it replaces low amplitude slices with previously unselected slices within the class until the condition is met, or the loop has iterated 5 times.  

Note: if a class has fewer slices than the target number, it will maintain the same number of slices, and will have fewer slices than the target number  

Input: dataset - recording data, n_examples (optional) - int, target number of rows/slices  
Output: dataset - homogenized dataset  

**Subsample Dataset**  
Subsamples each class of data to keep a certain percent of its slices by randomly selecting the target number of slices from the class.  
Function checks that less than 10% of slices have low amplitudes (defined as 10% of mean amplitude). If this condition is not met, it replaces low amplitude slices with previously unselected slices within the class until the condition is met, or the loop has iterated 5 times.  

Input: dataset - recording data, percent_kept - float, percent of slices each class will keep (given in percent, eg. 95 to keep 95% of slices)  
Output: dataset - subsampled dataset  

**Augment and Fill**  
Augments and fills classes of the dataset which have fewer slices than target number to have target number of slices. New slices are generated by randomly selecting slices and applying a sequence of randomly chosen transformations to each slice. If a target number is not specified by the user, it will be the average number of slices per class within the dataset.  

Input: dataset - recording data, user_specified_value (optional) - target number of slices for each class to have  
Output: dataset - filled dataset  

**Trim Examples**  
Trims slices from each class within the dataset. Either keeps the beginning, middle, or end protion of class.  
Input: dataset - recording data, example_length - number of slices to keep in each class, keep - which section of the slice will be kept (beginning, middle, or end)  
Output: dataset - trimmed dataset  

**Slice Augmenter**  
Performs augmentations on slices of data. Possible augmentations include:  

| Function | Description | Inputs |
| -------- | ----------- | ------ |
| noise_generator | generates noise | a (array), axis, ddof, factor, size |
| time_reversal   | reverses the time order of the IQ samples | iqdata |
| spectral_inversion | multiplies the imaginary components of the samples by -1 | iqdata |
| channel_swap | swaps I and Q portions of the sample | iqdata |
| amplitude_reversal | multiplies both I and Q components of the samples by -1 | iqdata |
| drop_samples | iterates through IQ data, moving forward to a random index before dropping a random number of samples, filling the drops with either the last value before the drop, the next value after the drop, the mean of the drop, or 0s (fill type is randomly selected) | iqdata, max_drop |
| quantize_tape | quantizes the entire tape. creates a specific number of bins, evenly spaced along the IQ data, and maps every data point to the closest bin. either maps points up to the nearest bin (ceiling), or down to the nearest bin (floor) | iqdata, bin_number, rounding_type |
| quantize_parts | quantizes random parts of the tape using the same method as in quantize_tape | iqdata, max_drop, bin_number, rounding_type |
| magnitude_rescale | multiplies all samples after a randomly selected point by a randomly selected magnitude | iqdata, starting_bounds, max_magnitude |
| cut_out | cuts out random regions and replaces with either 0s, 1s, or low, average, or high SNR noise (fill type is randomly selected) | iqdata, max_drop |
| patch_shuffle | iterates through IQ data, moving forward to a random index before shuffling a random number of samples | iqdata, max_drop |


### Example usage:

To load from a folder, homogenize to 1200 and to fill in any gaps:  
`python .\curator.py -r D:\QProjects\development\new-dataset-format\npyexamples -i 1200 -a 1200 -t test.dat`

To test the line above without making a dataset:  
`python .\curator.py -r D:\QProjects\development\new-dataset-format\npyexamples -i 1200 -a 1200`

To add to an existing dataset:  
`python .\curator.py -r D:\QProjects\development\new-dataset-format\npyexamples -i 4000 -a 5000 -t test7.dat -sdf test3.dat`  
*this example may take a few minutes.

To modify an existing dataset (e.g. homogenize, augment)  
`python .\curator.py -i 3900 -a 4100 -t test8.dat -sdf test7.dat `

### To Inspect:

`python ..\inspection-utils\ash-extras\dataset-review.py -d test.dat`


# todo

1. join two datasets
2. remove unused arguments (e.g. keep)
3. dict of augmentation configs
4. inspection and visualization tools
5. ds2 implementation
6. ds1.1 (more than two classes)
7. label definition in ds1
8. rules for augmentation limits
