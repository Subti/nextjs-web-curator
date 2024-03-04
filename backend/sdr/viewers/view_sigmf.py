import numpy as np
import matplotlib.pyplot as plt
from sigmf import SigMFFile, sigmffile
import argparse
from pathlib import Path
import os
import json

def load_sigmf(data_file_path):
    data_file_path = os.path.abspath(data_file_path)
    print("Loading SigMF file...")
    # meta_file_path = data_file_path.replace('.sigmf-data', '.sigmf-meta') #not sure if this is even doing anything
    # print(f"Data file path {data_file_path} Metadata file path {meta_file_path}")
    sigmf_file = sigmffile.fromfile(data_file_path)
    data = sigmf_file.read_samples()
    # meta_file= sigmffile.fromfile(meta_file_path)
    # annotations = meta_file.get_annotations()
    # captures = meta_file.get_captures()
    # global_metadata = meta_file.get_global_info()
    annotations = sigmf_file.get_annotations()
    captures = sigmf_file.get_captures()
    global_metadata = sigmf_file.get_global_info()
    print(global_metadata)
    print(captures)
    sigmf_meta = [global_metadata, captures, annotations]
    # print(annotations)
    return data, sigmf_meta


def create_plots(data, sigmf_meta, boxes=True, save=False, format='svg'):
    global_metadata = sigmf_meta[0]
    captures = sigmf_meta[1]
    if len(captures)==1:
        captures = captures[0]
    else:
        captures = captures[0]   # TODO : add handlign for the case where we do more than one "capture" per file

    annotations = sigmf_meta[2]
    sample_rate = global_metadata['core:sample_rate']
    centre_frequency = int(captures['core:frequency'])

    fig, axs = plt.subplots(2, 1, figsize=(12, 10))
    # Time Series Plot
    axs[0].plot(data.real, label='Real part')
    axs[0].plot(data.imag, label='Imaginary part')
    axs[0].set_title('Time Series')
    axs[0].set_xlabel('Samples')
    axs[0].set_ylabel('Amplitude')
    axs[0].set_xlim(0, len(data))

    # Spectrogram Plot
    Pxx, freqs, bins, im = axs[1].specgram(data, NFFT=1024,Fc=centre_frequency, Fs=sample_rate, cmap='twilight')
    axs[1].set_title('Spectrogram')
    axs[1].set_xlabel('Time (s)')
    axs[1].set_ylabel('Frequency (Hz)')
    axs[1].set_ylim(centre_frequency-sample_rate/2, centre_frequency+sample_rate/2)

    # Annotations
    if boxes == True:
        print("Plotting annotations.")
        for annotation in annotations:
            print(f"Detected annotation: {annotation}")
            start_idx = annotation['core:sample_start']
            length = annotation['core:sample_count']
            end_idx = start_idx + length

            # Convert sample indices to time in seconds
            start_time = start_idx / sample_rate
            end_time = end_idx / sample_rate

            # Assuming the 'core:frequency_lower_edge' and 'core:frequency_upper_edge'
            # keys define the frequency range for the annotation
            freq_lower_edge = annotation.get('core:freq_lower_edge', 0)
            freq_upper_edge = annotation.get('core:freq_upper_edge', sample_rate / 2)  # Default to Nyquist

            comment = json.loads(annotation.get('core:comment', ''))
            if comment.get('type') == 'intersection':
                colour = 'green'
            else:
                colour = 'red'



            # Draw a rectangle on the spectrogram
            rect = plt.Rectangle((start_time, freq_lower_edge), end_time - start_time, freq_upper_edge - freq_lower_edge,
                                color=colour, alpha=0.3)
            axs[1].add_patch(rect)
            # Add a label at the top left corner of the rectangle
            label = annotation.get('core:label', 'Unlabeled')  # Default label if none is provided
            axs[1].text(start_time, freq_upper_edge, label, color='white', fontsize='small', 
                        ha='left', va='top', bbox=dict(boxstyle="round,pad=0.1", fc=colour, alpha=0.5))
    else:
        print("Not plotting annotations.")

        # print("Plotting annotations...")
        # for annotation in annotations:
        #     print(f"Detected annotation: {annotation}")
        #     start_idx = annotation['core:sample_start']
        #     length = annotation['core:sample_count']
        #     end_idx = start_idx + length
        #     # Convert sample indices to time in seconds
        #     start_time = start_idx / sample_rate
        #     end_time = end_idx / sample_rate
        #     axs[1].axvspan(start_time, end_time, color='red', alpha=0.3)

    # Saving or Showing the Plot
    if save:
        print(f"Saving plot as './static/combined_plot.{format}'")
        plt.savefig(f"./static/combined_plot.{format}")
    else:
        print("Displaying plot...")
        plt.show()


def view_sigmf(args):
    data, sigmf_meta = load_sigmf(args.file_path)
    if args.saveplot:
        Path("static").mkdir(exist_ok=True)
        img_format = 'png' if args.png else 'svg'
        create_plots(data, sigmf_meta, boxes=args.no_boxes, save=True, format=img_format)
    else:
        create_plots(data, sigmf_meta, boxes=args.no_boxes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load and visualize a SigMF file")
    parser.add_argument("--file_path",'-f', help="Path to the SigMF file")
    parser.add_argument("--saveplot", action="store_true", help="Save plots instead of showing them")
    parser.add_argument("--png", action="store_true", help="Save plots as PNG (default is SVG)")
    parser.add_argument("--no_boxes", action="store_false", default=True, help="Flag to skip drawing boxes.")
    args = parser.parse_args()
    view_sigmf(args)

