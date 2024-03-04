import numpy as np

def subsample_dataset(dataset, percent_kept):
    percentage_to_keep = percent_kept/100
    new_dataset = {}

    # Check the size of the first axis in each array
    first_axis_sizes = [arr.shape[0] for arr in dataset.values()]

    print(f"First axis sizes before subsample: {first_axis_sizes}")

    for key, value in dataset.items():
        num_rows = value.shape[0]
        num_keep = int(num_rows * percentage_to_keep)
        if num_keep < 1:
            new_dataset[key] = np.empty((0, 2, value.shape[2]))
        else:
            indices = np.random.choice(num_rows, size=num_keep, replace=False)
            new_value = value[indices]
            max_mean = np.mean(np.max(np.max(np.abs(value), axis=2), axis=1)) # the mean of the max of each slice

            # get array of max values (amplitudes) of each slice, and which ones don't meet the threshold
            # threshold is 10% of mean of amplitudes
            maxes = np.max(np.max(np.abs(new_value), axis=2), axis=1)
            m_indices = np.argwhere(maxes < max_mean/10).T[0]
            maxes_below_threshold = maxes[m_indices]
            print(len(maxes_below_threshold))

            # replace slices with low amplitudes with ones not previously selected until less than 2% have low amplitudes 
            # (or loop has iterated 5 times)
            i = 0
            while len(maxes_below_threshold) > num_keep*0.1 and i < 5:
                # get indices of values not included in new values, and create a new list of indices for replacement from those
                # not_indices = np.setxor1d(np.indices(value.shape), indices)
                # not_indices = np.setxor1d(np.indices(value.shape), indices)
                # new_indices = np.random.choice(not_indices, len(maxes_below_threshold), replace=False)

                ## TODO - ensure this fits the goal it is trying to achieve
                total_indices = np.arange(num_rows)
                not_indices = np.setdiff1d(total_indices, indices)

                if len(maxes_below_threshold) > len(not_indices):
                    maxes_below_threshold = maxes_below_threshold[:len(not_indices)]

                new_indices = np.random.choice(not_indices, len(maxes_below_threshold), replace=False)


                # replace each slice whose amplitude does not meet the threshold with a new one
                # using new_indices to ensure the new values are not already in new value, and are random
                for j, index in enumerate(new_indices):
                    new_value[m_indices[j]] = value[index]

                # get the new amplitudes and which don't meet threshold
                maxes = np.max(np.max(np.abs(new_value), axis=2), axis=1)
                m_indices = np.argwhere(maxes < max_mean/10).T[0]
                maxes_below_threshold = maxes[m_indices]
                print(len(maxes_below_threshold))
                i += 1
            
            new_dataset[key] = new_value

    # Check the size of the first axis in each array
    first_axis_sizes = [arr.shape[0] for arr in new_dataset.values()]

    print(f"First axis sizes after subsample: {first_axis_sizes}")

    return new_dataset