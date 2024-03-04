import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec

import numpy as np
import pickle
import pathlib
import pandas as pd
import math
import random
import argparse

try:
    from inspection_utils.dataset_review import dataset_review
except Exception:
    from dataset_review import dataset_review

def sample_array(arr):
    index = np.random.randint(0, arr.shape[0]) # Select a random index from 0 to m
    return arr[index, :, :]


def inspector(df,save):
    print(df.head())
    print("###############################")
    # random_example_df = df.groupby(['Label1', 'Label2'])

    # print(random_example_df.head())

    cmap = plt.get_cmap('twilight')

    example_table = df.set_index(['Label1', 'Label2'])['Data']
    try:
        sampled_table = example_table.apply(sample_array)
        print(sampled_table)
            # Get unique Label1 and Label2 values
        unique_label1 = sampled_table.index.get_level_values('Label1').unique()
        unique_label2 = sampled_table.index.get_level_values('Label2').unique()
    except:
        return None







    ncols = len(unique_label1)
    nrows = len(unique_label2) * 3 # Adjusted for 2:1 ratio

    # Define the GridSpec
    gs = GridSpec(nrows, ncols)

    # Create the figure
    fig = plt.figure(figsize=(10, 10))

    for i, label1 in enumerate(unique_label1):
        for k, label2 in enumerate(unique_label2):
            if (label1, label2) in sampled_table.index:
                # Extract the corresponding data
                data = sampled_table.loc[label1, label2]
                complex_data = data[0,:]+1j*data[1,:]
                complex_data = complex_data.astype("complex64")

                vector_length = data[0,:].shape[0]

                t = np.arange(0,vector_length,1)

                ax1 = fig.add_subplot(gs[k*3, i])
                ax1.plot(t,data[0,:],t,data[1,:])
                ax1.set_ylim([-1, 1.2])
                ax1.text(0.1, 0.8, f'{label1} - {label2}', fontsize=8, weight='bold', transform=ax1.transAxes)
                ax1.axis("off")

                FFT_size = 2**round(np.log2(vector_length/32))

                # Calculate and plot the spectrogram
                ax2 = fig.add_subplot(gs[k*3+1:k*3+3, i])
                Pxx, freqs, bins, im = ax2.specgram(complex_data, NFFT=64, Fs=FFT_size, noverlap=int(FFT_size/8),cmap=cmap)
                ax2.axis("off")

                # Add border around each pair
                rect1 = patches.Rectangle((0,0),1,1, transform=ax1.transAxes, clip_on=False, fill=False, linewidth=1)
                ax1.add_patch(rect1)
                rect2 = patches.Rectangle((0,0),1,1, transform=ax2.transAxes, clip_on=False, fill=False, linewidth=1)
                ax2.add_patch(rect2)
            else:
                # Leave the plot blank
                ax1 = fig.add_subplot(gs[k*3, i])
                ax1.axis('off')
                ax2 = fig.add_subplot(gs[k*3+1:k*3+3, i])
                ax2.axis('off')






    plt.tight_layout()


    plt.subplots_adjust(left=.03, right=.97, bottom=.07, top=0.97, wspace=0, hspace=0)
      

    if save==True:
        matplotlib.use('cairo')
        pathlib.Path("static").mkdir(exist_ok=True)
        img = "ds.svg"
        plt.savefig(f"./static/{img}")
        return img
    else:
        plt.show()
        return None







if __name__ == "__main__":
    #parse arguments if theyre provided
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_dataset_file", "-d", help="Source dataset (can be a path)")
    parser.add_argument("--saveplot", "-s", type=bool, default=False, help="Save plot instead of generating on screen.", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    if args.saveplot:
        save=True
    else:
        save=False

    df, _, _, _,  _ = dataset_review(args)

    inspector(df,save)