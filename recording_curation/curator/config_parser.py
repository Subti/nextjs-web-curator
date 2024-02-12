import argparse
import yaml

#configparser for folder2dataset-auto

def cli_parser():

    parser = argparse.ArgumentParser(description='folder2dataset - produces a 1.0 or 2.0-dataset from all files within a numpy or sigmf folder, edits existing datasets, or adds examples to existing datasets from a folder.')

    parser.add_argument('-sdf', '--source_dataset_file', 
                        help='Path to the source dataset file')
    
    parser.add_argument("-r", "--recordings_folder", metavar='RECORDINGS_FOLDER',
                        type=str, 
                        default=None , 
                        help="Path to the folder with npy recordings. Examples './recs/'. Default None")

    parser.add_argument("-j", "--keys", metavar='KEYS',
                        type=str,
                        nargs="+",
                        help="Keys for the dataset's classes")

    parser.add_argument("-f", "--filename", metavar='FILENAME',
                        type=str, 
                        default='example_dataset.dat' , 
                        help="Filename for the dataset to be produced. Default example 'example_dataset.dat'")
    
    parser.add_argument("-e", "--example_length", # Makes sense 
                    type=int,
                    default=512,
                    help="Option for choosing example size when making a new dataset or adding to an existing one. Default is 512.")

    parser.add_argument("-m", "--num_classes", 
                    type=int,
                    default=2,
                    help="Select the number of labels each example will have.")

    parser.add_argument("-s","--subfolders", 
                        type=bool, 
                        default=False,
                        help="Flag for including all subfolders within the search. Default False")

    parser.add_argument("-p","--percent_files", 
                        type=float, 
                        default=100,
                        help="Option for only capturing a subset of the files in the source folder (e.g. 70pct of all recordings). Default example: 100")

    parser.add_argument("-i","--homogenize", 
                        type=int, 
                        default=None,
                        help="Homogenizes the size of each class within the dataset to the value provided i.e makes all classes the same length. Default None, which results in using minimum size within dataset")
    
    parser.add_argument("-a", "--augment_and_fill", 
                        type=int, 
                        default=None, 
                        help='Number of examples to homogenize each class to. If no number is provided, the average number of examples is calculated and used.')
    
    parser.add_argument("-c","--percent_slices_to_keep",
                        type=float, 
                        default=100,
                        help="Option for only capturing a subset of the SLICES from the files in the source folder (e.g. 70pct of all slices).  Note, this happens AFTER homogenize. Default example: 100")
    
    parser.add_argument("-l", "--remove_list", # Makes sense
                        type=str,
                        nargs="+",
                        help="List of keys to remove from dataset. Keys should be the unique label combination, separated with an underscore '_' example: bpsk_20 or 5GNR_ambient_synthetic")

    parser.add_argument("-x", "--trim_length", # Makes sense 
                        type=int,
                        default=None,
                        help="Option for trimming samples to a chosen length, generally from an existing dataset. Default is None, which results in vectors being trimmed to the length of the shortest vector.")


    parser.add_argument("-k", "--keep", # Makes sense 
                        type=str,
                        default="middle",
                        help="Section of data to keep when trimming samples. Options are start, middle, and end. Default is 'middle'")
    
    parser.add_argument("-n","--new_file", #USE IN CURATOR, NOT F2D
                        type=bool, 
                        default=True,
                        help="Flag for saving file as a new dataset. Default true")
    
    parser.add_argument("-t", "--target_dataset_file", # Makes sense 
                        type=str,
                        default="",
                        help="Target path where the dataset will be saved. If unspecified, dataset will not be saved.")
    
    parser.add_argument("-d", "--dataset_format", # Makes sense 
                        type=str,
                        default="pickle",
                        help="Option to choose dataset formatting between pickle and h5py. Default is pickle")


    # parser.add_argument("-c", "--config_file", metavar='CONFIG_FILE',
    #                     type=str, 
    #                     default="./gen-config.yaml" , 
    #                     help="Path to the yaml configuration file from PWD. Default is ./gen-config.yaml")

    #parse arguments
    args = parser.parse_args()

    #arg parser errors


    return args

# def yaml_parser(configfile_from_arg):
#     yamlconfig = yaml.load(open(configfile_from_arg), Loader=yaml.FullLoader)
#     return yamlconfig