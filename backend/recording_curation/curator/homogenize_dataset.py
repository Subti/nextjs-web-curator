# from gettext import npgettext
import numpy as np

def homogenize_dataset(dataset, n_examples=None):
    new_dataset = {}

    # Check the size of the first axis in each array
    first_axis_sizes = [arr.shape[0] for arr in dataset.values()]

    if n_examples:
        target_size = n_examples
    else:
        # Get the minimum size and use that as the target size
        target_size = min(first_axis_sizes)

    # Iterate over dictionary items and modify arrays
    for key, value in dataset.items():
        num_rows = value.shape[0]
        max_mean = np.mean(np.max(np.max(np.abs(value), axis=2), axis=1)) # the mean of the max of each slice

        if num_rows > target_size:
            indices = np.random.choice(num_rows, size=target_size, replace=False)
            new_value = value[indices]

            # get array of max values (amplitudes) of each slice, and which ones don't meet the threshold
            # threshold is 10% of mean of amplitudes
            maxes = np.max(np.max(np.abs(new_value), axis=2), axis=1)
            m_indices = np.argwhere(maxes < max_mean/10).T[0]
            maxes_below_threshold = maxes[m_indices]
            print(len(maxes_below_threshold))

            # replace slices with low amplitudes with ones not previously selected until less than 10% have low amplitudes 
            # (or loop has iterated 5 times)
            i = 0
            while len(maxes_below_threshold) > target_size*0.1 and i < 5:
                # get indices of values not included in new values, and create a new list of indices for replacement from those
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
        else:
            new_dataset[key] = value

    return new_dataset
