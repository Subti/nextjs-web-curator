
import datetime
import numpy as np
import numpy.typing as npt
import os
import pathlib
import sigmf
import yaml
import argparse

from pathlib import Path
from sigmf   import SigMFFile
from sigmf.utils import get_data_type_str


# =============================================================================
# Convert complex ndarray to 2xn ndarray with real and imaginary parts
# =============================================================================
def convert_to_2xn(samples):
    # Separate the real and imaginary parts
    real_part = np.real(samples)
    imag_part = np.imag(samples)
    return np.vstack((real_part, imag_part))

# =============================================================================
# Convert bytes to ndarray
# ============================================================================='

def convert_bytes_to_samples(data: bytes) -> npt.NDArray[np.complex64]:
    """
    Convert bytes to samples in IQ complex format.
    :param data: Array of bytes
    :return: IQ samples as numpy complex type
    """
    samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
    samples /= 2048
    samples = samples[::2] + 1j * samples[1::2]
    # samples = samples.view(np.complex64)
    return samples


# =============================================================================
# Save data to numpy
# =============================================================================
def save_to_npy(samples, num_samps, center_freq, sample_rate, metadata, iteration=None, sdr="unknown", inputmetadict=None):
    pathlib.Path("recordings").mkdir(exist_ok=True) #make recordings folder if it doesnt exist
    
    # folder/file handling
    now = datetime.datetime.now()
    month = now.strftime("%m")
    day = now.strftime("%d")
    time = now.strftime("%H%M%S")
    try:
        savelen = samples.shape[1]
    except:
        savelen = len(samples[0])
    
    folder = pathlib.Path("recordings")
    if iteration is not None:
        filename = f"iq{int(center_freq / 1000000.0)}MHz{time}_{iteration}.npy"
    else:
        filename = f"iq{int(center_freq / 1000000.0)}MHz{time}.npy"
    
    current_path = Path(__file__).resolve().parent
    meta_path = Path.joinpath(current_path, metadata)

    # load metadata from yaml file 
    with open(meta_path, "r") as stream:
        try:
            meta_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    if sdr == "synth":
        sig_type = "Synthetic-IQ"
        filename = "synth"+filename
    else:
        sig_type = "Recorded Baseband-IQ"

    interim_dict = {
            'center_freq': center_freq,
            'rec_length': savelen,
            'decimation': 1, #needs to be removed in future
            'sdr': sdr,
            'hw_sample_rate': sample_rate,
            'effective_sample_rate': sample_rate,
            'signal_type': sig_type,
            'date_recorded': f"{month}-{day}",
            'time_recorded': time
            }

    meta = np.array([center_freq, savelen, num_samps//1000, sample_rate]) #save simple metadata

    ## defaults to a provided metadata dict of the code calls for it otherwise it will use the loaded template for labels.
    if inputmetadict is not None:
        if 'metadata' in inputmetadict:
            x_dict = inputmetadict['metadata']
        else:
            x_dict = inputmetadict
    else:    
        if 'metadata' in meta_config:
            x_dict = meta_config['metadata']
        else:
            x_dict = meta_config
    meta_dict = {**x_dict, **interim_dict}

    extended_meta = np.array([meta_dict])

    print(meta_dict)


    fullpath = folder / filename
    if iteration is None: print(f"Saving {savelen} samples as: {filename}")
    with open(fullpath, 'wb' ) as f:
        np.save(f,samples) 
        np.save(f,meta)
        np.save(f,extended_meta)
    
    return fullpath


# =============================================================================
# Save data to sigmf
# =============================================================================
def make_sigmf_meta_dict(args: argparse.Namespace, anno:str="",sdr:str="unknown", anno_list=None):
    # metadata dictionary for adding to sigmf file - will need a better way to handle actual annotations

    # load metadata from yaml file 
    with open(args.metadata, "r") as stream:
        try:
            meta_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    description = f"{sdr} SDR captured IQ signal at sample rate {args.sample_rate} via {meta_config['metadata']['testbed']} testbed for {meta_config['metadata']['project_name']} project."

    sigmf_meta_dict = {
        'author': meta_config['metadata']['author'],
        'center_freq': args.center_freq,
        'description': description, 
        'rec_length': args.num_samples,
        'sdr': sdr,
        'sample_rate': int(args.sample_rate)
    }

    if anno_list is not None:


        sigmf_meta_dict["anno_list"]=anno_list

        # 'comment': anno, #
        # 'flo': int(args.center_freq - args.sample_rate/2),
        # 'fhi': int(args.center_freq + args.sample_rate/2),
    return sigmf_meta_dict

# def save_to_sigmf(samples, filename: str, frequency: float, sample_rate: float, description: str = '', meta_file: str = 'logiq_meta.yaml'):
def save_to_sigmf(samples, frequency: float, sigmf_meta_dict:dict={}):

    #cast to cx64
    samples = samples.astype('complex64')

    ###folder / file handling
    now = datetime.datetime.now()
    time = now.strftime("%H%M%S")
    Path("recordings").mkdir(exist_ok=True)
    folder = Path("recordings")
    filename = f"iq{int(int(frequency) / 1000000)}MHz{time}"
    fullpath = folder / filename

    # Save data file
    samples.tofile(f'{fullpath}.sigmf-data')

    # create the metadata
    meta = SigMFFile(
        data_file=f'{fullpath}.sigmf-data',  
        global_info={
            SigMFFile.DATATYPE_KEY: 'cf32_le',  # get_data_type_str(samples),
            SigMFFile.SAMPLE_RATE_KEY: int(sigmf_meta_dict["sample_rate"]),
            SigMFFile.AUTHOR_KEY: sigmf_meta_dict["author"],
            SigMFFile.DESCRIPTION_KEY: sigmf_meta_dict["description"],
            SigMFFile.VERSION_KEY: sigmf.__version__,
            SigMFFile.HW_KEY: sigmf_meta_dict["sdr"],
        }
    )

    # create a capture key at time index 0
    meta.add_capture(0, metadata={
        SigMFFile.FREQUENCY_KEY: frequency,
        SigMFFile.DATETIME_KEY: datetime.datetime.utcnow().isoformat() + 'Z',
        SigMFFile.GLOBAL_INDEX_KEY: 0
    })

    if "anno_list" in sigmf_meta_dict:
        anno_list = sigmf_meta_dict["anno_list"]

        for i,anno in enumerate(anno_list):
            # TODO: pls fix
            anno["start_sample"]
            meta.add_annotation(anno["start_sample"], anno["sample_count"], metadata = {
                SigMFFile.FLO_KEY: anno["flo"],
                SigMFFile.FHI_KEY: anno["fhi"],
                SigMFFile.LABEL_KEY: anno["annotation"],
                SigMFFile.COMMENT_KEY: anno["comment"], 
            })


        #example annotation
            #     {
            #     "core:sample_start": 919552,
            #     "core:sample_count": 40960,
            #     "core:generator": null,
            #     "core:label": null,
            #     "core:comment": null,
            #     "core:freq_lower_edge": 8486146718.75,
            #     "core:freq_upper_edge": 8486225937.5,
            #     "core:uuid": null,
            #     "core:description": "Unknown"
            # }


        # meta.add_annotation(0, 1, metadata=yaml_dict["metadata"])
        print(f"Added {len(anno_list)} to the metadata.")
    else:
        print("No annotations to be saved in this sigmf-meta file")

    print(f"Metadata: {sigmf_meta_dict}")

    meta.tofile(f'{fullpath}.sigmf-meta')
    return f"{filename}.sigmf-data" 



def convert_2xn_to_complex(arr):

    if arr.shape[0] != 2:
        raise ValueError("Input array must have two rows")
    
    real_part = arr[0, :]
    imaginary_part = arr[1, :]
    
    # iqsslicecomplex = sliced_iqarray[iqarray_i,0,:]+1j*sliced_iqarray[iqarray_i,1,:]
    # iqsslicecomplex = iqsslicecomplex.astype("complex64")

    return real_part + 1j * imaginary_part

def bytes_to_complex_array(interleaved_bytes):
    # Convert interleaved bytes to NumPy array of complex64
    real_bytes = interleaved_bytes[::2]  # Get every other byte for the real part
    imag_bytes = interleaved_bytes[1::2]  # Get every other byte for the imaginary part

    real_array = np.frombuffer(real_bytes, dtype=np.int8)
    imag_array = np.frombuffer(imag_bytes, dtype=np.int8)

    # Create a complex array from the real and imaginary parts
    complex_array = real_array.astype(np.float32) + 1j * imag_array.astype(np.float32)
    
    return complex_array
