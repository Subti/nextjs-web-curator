import pickle
import numpy as np
import argparse

def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data

def save_pickle(data, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)

def merge_dictionaries(dict1, dict2):
    merged_dict = dict1.copy()
    
    for key, value in dict2.items():
        if key in merged_dict:
            m1, _, n1 = merged_dict[key].shape
            m2, _, n2 = value.shape
            
            if n1 != n2:
                print(f"Warning: Mismatch in n dimensions for key {key}. Skipping this key.")
                continue
            
            merged_dict[key] = np.vstack((merged_dict[key], value))
        else:
            merged_dict[key] = value
    
    return merged_dict

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Dataset combiner - takes two ds1 files (assuming same tuple key structure) and combines them into one')
    parser.add_argument("--ds1", type=str, help="Path to the first dataset.") 
    parser.add_argument("--ds2", type=str, help="Path to the first dataset.") 
    parser.add_argument("--target_file", "-f", type=str, default="merged_dataset.dat", help="Path for saving the new file.") 
    args = parser.parse_args()

    dict1 = load_pickle(args.ds1)
    dict2 = load_pickle(args.ds2)
    
    merged_dict = merge_dictionaries(dict1, dict2)
    
    save_pickle(merged_dict, args.target_file)
    
    print(f"Merging complete! Merged dictionary saved to {args.target_file}")
