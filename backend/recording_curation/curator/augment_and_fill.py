from typing import Callable, Optional
import numpy as np
import random

#slice and augment functions:
# from recording_curation import slice_augmenter
from slice_augmenter import noise_generator, time_reversal, spectral_inversion, channel_swap, amplitude_reversal, drop_samples, quantize_tape, quantize_parts, magnitude_rescale, patch_shuffle, convert_to_2xn, slice_augmenter
augment_functions = [time_reversal, spectral_inversion, channel_swap, amplitude_reversal, drop_samples, quantize_tape, quantize_parts, magnitude_rescale, patch_shuffle]



def augment_and_fill(dataset: dict, user_specified_value: Optional[int]):
    #get number of examples in the class
    num_examples_dict = {label: data.shape[0] for label, data in dataset.items()}

    #figure out what number of examples we are homogenizing to, 
    # either user specified or by calculating the average number of examples between the classes
    if user_specified_value is None:
        total_examples = sum(num_examples_dict.values())
        num_classes = len(dataset)
        target_num_examples = total_examples // num_classes
    else:
        target_num_examples = user_specified_value

    print(type(num_examples_dict))
    print(num_examples_dict)


    for label, data in dataset.items():
        num_examples = num_examples_dict[label]
        num_to_add = target_num_examples - num_examples
    
    #choose random example from the class
    #apply random function(s) from slice_augmenter to that random example
    #add the new signal(s) to the class 
    
        if num_to_add > 0:
            #for each class, if the number of current examples is less than the target, it generates new examples by selecting random example 
            #from current set and applying a sequence of randomly chosen transformations to it 
            for _ in range(num_to_add):
                idx = np.random.randint(num_examples)
                example = data[idx]
                new_example = example

                # apply a random number of augmentations in random order
                num_augments = np.random.randint(1, len(augment_functions)+1)
                augment_order = random.sample(augment_functions, num_augments)

                #randomly chosen augmentation function(s) are applied to the selected example
                for augment_func in augment_order:
                    # new_example = augment_func(new_example, max_drop=1, starting_bounds=(0,1), max_magnitude=1, bin_number=2, rounding_type="floor")
                    new_example = augment_func(new_example, max_drop=1000, starting_bounds=[0.25, 0.75], max_magnitude=5, bin_number=32, rounding_type="floor")
                    # new_example = augment_func(new_example, 1000, [0.25, 0.75], 5, 32,"floor")
                #transformed example is added to the dataset
                new_example = np.array(new_example)
                dataset[label] = np.append(dataset[label], [new_example],axis=0)

                                # Check the size of the first axis in each array
    first_axis_sizes = [arr.shape[0] for arr in dataset.values()]
    print(f"First axis sizes after augmentations: {first_axis_sizes}")


    return dataset