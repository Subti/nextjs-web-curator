import sys
import matplotlib.pyplot as plt
import numpy as np
import pickle
import pathlib
import random
import argparse

def drop_classes(args, dataset):
    remove_list = [tuple(element.split('_')) for element in args.remove_list] 

    print(f"Keys in dataset: {dataset.keys()}")

    if args.remove_list:
        new_dataset = {}
        print(f"Keys for removal in new dataset: {remove_list}")

        for key in dataset:
            if key in remove_list:
                print(f"removing {key} key")
            else:
                new_dataset[key] = dataset[key]

        dataset = new_dataset

    return dataset
