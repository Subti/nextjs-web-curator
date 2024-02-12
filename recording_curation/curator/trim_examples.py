##used to make examples shorter

## usage > python3 trim_examples.py -d <source dataset> -t <target dataset> -l <optional: e.g. 256> -k <region>



#takes a dataset, an example length, and a keep argument, then trims the dataset examples according to these parameters
def trim_examples(dataset, example_length, keep):
    # Check the size of the first axis in each array
    vector_lengths = [arr.shape[2] for arr in dataset.values()]

    print(f"Vector lengths (per key): {vector_lengths}")

    if example_length:
        target_size = int(example_length)
        print(f"{target_size} will be made new vector length.")
    else:
        # Get the minimum size and use that as the target size
        target_size = int(min(vector_lengths))
        print(f"Desired length unspecified, {target_size} will be made new vector length.")

    # Iterate over dictionary items and modify arrays
    for key in dataset:
        if keep == "end":
            dataset[key] = dataset[key][:, :, -target_size:]
        elif keep == "middle":
            _, _, exlen = dataset[key].shape
            start = int((exlen - target_size) / 2)
            end = int(start + target_size)
            dataset[key] = dataset[key][:, :, start:end]
        else:
            # start case
            dataset[key] = dataset[key][:, :, :target_size]
    
    return dataset
