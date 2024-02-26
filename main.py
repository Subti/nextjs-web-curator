# from flask import Flask, render_template, request, render_template_string, jsonify, Response, redirect, url_for, send_from_directory
import os
import sys
import subprocess
import threading
from airium import Airium
import yaml
from argparse import Namespace
import shutil
import pathlib
import pandas as pd
import numpy as np
from queue import Queue

from fastapi import FastAPI, Request, Form, Response, HTTPException, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import List, Optional, Union
from starlette.status import HTTP_302_FOUND
from ast import literal_eval


from inspection_utils.view_rec import view_rec
from recording_curation.npy_slicer import npy_slicer
from recording_curation.signal_inspector import signal_folder_inspector_npy2, load_numpy2
from recording_curation.get_html import get_index_html, get_curate, generate_draft_html
from inspection_utils.dataset_review import dataset_review
from recording_curation.gui_curator_reset import clear_directories
import sdr as sdr
from sdr.sdr_capture import sdr_module, get_attached_radios
print("running from sdr repo as submodule")

os.makedirs("static/", exist_ok=True)

app = FastAPI()

origins = [
    "http://localhost:3000",  # React app address
    # add more origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates") # HTML TEMPLATES HERE
app.mount("/static", StaticFiles(directory="static"), name="static")

# get radios installed on this system
passes=get_attached_radios()
use_sdr=passes[0]

default_values = {
    'ip_address': '192.168.40.2',
    'num_samples': 10000000,
    'center_frequency': 2440000000,
    'gain': 32,
    'channel': 0,
    'sample_rate': 40000000,
    'protocol': "Wifi-BGN",
    'use_case': "ambient",
    'testbed': "Portable-Blade",
    'transmitters': "Ambient",
    'project_name': "Collision2023",
    'sdr': f"{use_sdr}",
    'passes':f"{passes}"
}

class RecArgs(BaseModel):
    ip_addr: str
    num_samples: int
    center_freq: float
    sample_rate: int
    gain: float
    channel: int
    metadata: str
    file_extension: str
    sdr: str
    stream_time: int
    zmq: int

@app.get("/")
def read_root():
    return RedirectResponse(url='http://localhost:3000/')

@app.post("/")
async def create_home(request: Request,
    protocol: str = Form(...),
    use_case: str = Form(...),
    testbed: str = Form(...),
    transmitters: str = Form(...),
    project_name: str = Form(...),
    sdr: str = Form(...),
    ip_address: str = Form(...),
    num_samples: str = Form(...),
    center_frequency: str = Form(...),
    sample_rate: str = Form(...),
    gain: str = Form(...),
    channel: str = Form(...)
    ):
    # Convert string fields to the correct type
    num_samples = int(num_samples)
    center_frequency = float(center_frequency)
    gain = float(gain)
    sample_rate = int(sample_rate)
    channel = int(channel)
    """
    Process a form submission to create a new home configuration and save metadata.

    :param request: The request object for HTTP details.
    :param protocol: Communication protocol.
    :param use_case: Intended use case.
    :param testbed: Testbed description.
    :param transmitters: Transmitter details.
    :param project_name: Name of the project.
    :param sdr: Software-defined radio identifier.
    :param ip_address: IP address for SDR.
    :param num_samples: Number of samples to capture.
    :param center_frequency: Center frequency for capture.
    :param sample_rate: Sample rate for capture.
    :param gain: Gain setting for the receiver.
    :param channel: Channel number for capture.
    :type request: Request
    :type protocol: str
    :type use_case: str
    :type testbed: str
    :type transmitters: str
    :type project_name: str
    :type sdr: str
    :type ip_address: str
    :type num_samples: int
    :type center_frequency: float
    :type sample_rate: int
    :type gain: float
    :type channel: int
    :return: A template response rendering the result with the capture metadata and image.
    :rtype: templates.TemplateResponse
    """
    
    metadata = {
        'metadata': {
            'protocol': protocol,
            'use_case': use_case,
            'testbed': testbed,
            'transmitters': transmitters,
            'project_name': project_name,
            'sdr': sdr
        }
    }

    use_sdr=sdr

    metafile = "logiq_meta.yaml"
    metapath = pathlib.Path("sdr/"+metafile)
    metapath2 = pathlib.Path("sdr/modules/"+metafile)

    # Writing data to YAML file
    with open(metapath, 'w') as file:
        yaml.dump(metadata, file,  sort_keys=False, default_flow_style=False)
    shutil.copy(metapath, metapath2)

    #copy so sdr repo knows... #TODO: correct this - it is not appropriately callign the yaml template in sdr/modules

    # Construct args object
    rec_args = RecArgs(
        ip_addr=ip_address,
        num_samples=num_samples,
        center_freq=center_frequency,
        sample_rate=sample_rate,
        gain=gain,
        channel=channel,
        file_extension="npy",
        sdr=use_sdr,
        stream_time=0,
        zmq=5555,
        metadata=metafile
    )

    # capture from SDR
    os.makedirs("slice_review", exist_ok=True)
    os.makedirs("example_review", exist_ok=True)

    fullpath,_ = sdr_module(rec_args)
    print(f"capture {use_sdr}  and saved to {fullpath}")

    view_args = Namespace(
        plottime="full",
        saveplot=True,
        filename=fullpath
    )

    print(view_args.filename)
    image_filename = view_rec(view_args)
    image_url = request.url_for('static', path=image_filename)
    print("hello")
    print(image_url)

    return {"image_url": image_url, "filename": fullpath}
    # image_filename = view_rec(view_args)
    # rec_dict = rec_args.dict()
    # view_dict = view_args
    # return templates.TemplateResponse('result.html', {"request": request, 'image_filename': image_filename, 'view_args': view_dict, 'rec_args': rec_dict, 'metadata': metadata["metadata"]})


def namespace_to_dict(namespace):
    """
    Convert a namespace object to a dictionary.

    :param namespace: The namespace object to convert.
    :type namespace: Namespace
    :return: A dictionary representation of the namespace.
    :rtype: dict
    """
    return vars(namespace)


@app.post("/result")
async def result(request: Request, action: str = Form(...), cuts: str = Form(None), protocol: str = Form(None),
                filename: str = Form(None), num_samples: float = Form(None), 
                sample_rate: float = Form(None)):
    """
    Process the action ('discard' or 'save') on the form submission and perform corresponding operations.

    :param request: The request object for HTTP details.
    :param action: The action to perform ('discard' or 'save').
    :param cuts: Comma-separated string of cut points for slicing the signal.
    :param protocol: Protocol name used for organizing saved slices.
    :param filename: The filename of the signal file to process.
    :param num_samples: Total number of samples in the signal file.
    :param sample_rate: Sample rate of the signal recording.
    :type request: Request
    :type action: str
    :type cuts: str, optional
    :type protocol: str, optional
    :type filename: str, optional
    :type num_samples: float, optional
    :type sample_rate: float, optional
    :return: A response that could be a redirection to the home page, a template response with the processing result, or an error message.
    :rtype: Response or dict
    """

    if action == 'discard':
        # Delete files and redirect to index.html
        print("skipping discarding image, will overwrite.")
        if os.path.isfile(filename):
            os.remove(filename)
        # Redirect to index.html
        return Response(content=get_index_html(**default_values), media_type="text/html")

    elif action == 'save':
        if cuts and protocol and filename and num_samples and sample_rate:
                cuts_clean = str(cuts.replace(',', ' ').replace('\n', ' ').replace('\r', ' '))
                cuts_list = cuts_clean.split()
                cuts_list.sort()
                duration_ms = (num_samples/sample_rate)*1000
                cuts_list = [int(num_samples*int(i)/duration_ms) for i in cuts_list if i.isdigit()]

                cuts_args = Namespace(
                    source_signal_file=filename,
                    target_folder=f"./slice_review/{protocol}/",
                    cuts=cuts_list
                )

                npy_slicer(cuts_args)

                backup_folder = "../rec_backups/"
                os.makedirs(backup_folder, exist_ok=True)
                shutil.copy(filename, backup_folder)

                try:
                    os.remove("./static/signal.svg")
                except Exception as e:
                    print("An error occurred:", e)

                html_filename = signal_folder_inspector_npy2(f"./slice_review/","collect")
                all_files = [str(pathlib.Path(dp) / f) for dp, dn, filenames in os.walk(pathlib.Path('slice_review')) for f in filenames if pathlib.Path(f).suffix in ['.png', '.svg']]
                print(f"All files:{all_files}")
                return templates.TemplateResponse(html_filename, {"request": request, "recordings": all_files})

        else:
            return {"error": "Required form data missing"}

    return "Invalid request"

class Files(BaseModel):
    selectedFiles: List[str]

@app.post("/collect")
async def collect(files: Files):
    """
    Handle file selection for processing, moving selected files based on the application's current state.

    This function processes selected files for review or inclusion, based on the global state variable. It moves files between directories for review or inclusion, and cleans up directories as needed.

    :param files: The selected files for processing, encapsulated in a `Files` object.
    :type files: Files
    :return: A message indicating the successful addition of files and their corresponding numpy files.
    :rtype: dict
    :raises HTTPException: If an error occurs during file processing, detailing the specific file and error encountered.
    """
    selectedFiles = files.selectedFiles
    global state

    if 'state' not in globals():
        state = "collect"

    print(f"Selected files: {selectedFiles}")  # print selected files to console


    if state == "review":
        for file in selectedFiles: 
            original_files_folder = './example_review/'+file.split('/')[0]  # Update this to the path to the original .npy files
            destination = "./included/"
            pathlib.Path(destination).mkdir(parents=True, exist_ok=True)
            npyfile = file.split("/")[-1].split(".")[-2]+".npy"
            try:
                shutil.copy(f"{original_files_folder}/{npyfile}", destination)

            except Exception as e:
                print(f"Error: {e}")  
                raise HTTPException(status_code=400, detail={'error': f'An error occurred while processing file: {file}.', 'details': str(e)})

        shutil.rmtree(original_files_folder.split("/")[1])
        shutil.rmtree(f"./static/")


    else:
        original_files_folder = './slice_review/'+selectedFiles[0].split('/')[0]  # Update this to the path to the original .npy files
        destination = "./example_review/"+selectedFiles[0].split('/')[0]
        pathlib.Path(destination).mkdir(exist_ok=True)

        for file in selectedFiles: 
            npyfile = file.split("/")[-1].split(".")[-2]+".npy"
            try:
                shutil.copy(f"{original_files_folder}/{npyfile}", destination)

            except Exception as e:
                print(f"Error: {e}")  
                raise HTTPException(status_code=400, detail={'error': f'An error occurred while processing file: {file}.', 'details': str(e)})

        shutil.rmtree(original_files_folder)
        shutil.rmtree(f"./static/{selectedFiles[0].split('/')[0]}")
    pathlib.Path("./static").mkdir(parents=True, exist_ok=True)
    state = None
    return {'message': 'Files and corresponding numpy files added successfully!'}

@app.get("/review")
@app.post("/review")
async def review(request: Request):
    """
    Prepare and display files for review.

    This function marks the application's state as 'review', calls a function to inspect signal files in a specific directory, and collects all image files in that directory to be displayed in a template.

    :param request: The request object for HTTP details.
    :type request: Request
    :return: A template response that renders 'inspect_final.html', passing the list of image files for display.
    :rtype: templates.TemplateResponse
    """
    print("include then review")

    # Assume signal_folder_inspector_npy2 is defined elsewhere or imported
    signal_folder_inspector_npy2(f"./example_review/", "review") 

    all_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk('example_review') 
                 for f in filenames if os.path.splitext(f)[1] in ['.png', '.svg']]
    global state
    state = "review" 

    return templates.TemplateResponse('inspect_final.html', {"request": request, "recordings": all_files})

@app.get("/curate")
async def curate(request: Request):
    """
    Load a summary of recordings for curation and return an HTML view.

    This function reads a summary of numpy file recordings from a specified directory and generates an HTML view for curation purposes, using the summary data.

    :param request: The request object for HTTP details.
    :type request: Request
    :return: An HTML response that renders the curated view of recordings.
    :rtype: Response
    """
    print("curate")

    npy_files_folder = "./included/"
    recordingsummary = load_recordingsummary(npy_files_folder)

    return Response(content=get_curate(recordingsummary), media_type="text/html")

def load_recordingsummary(folderpath: str):
    """
    Load metadata from `.npy` files in a directory into a DataFrame.

    Iterates over `.npy` files in the given folder, loading metadata into a DataFrame. The metadata is then organized into specified columns for easy access and manipulation.

    :param folderpath: The path to the folder containing `.npy` files.
    :type folderpath: str
    :return: A DataFrame containing metadata from the `.npy` files.
    :rtype: pd.DataFrame
    """ 
    recordingsummary = pd.DataFrame()

    # Loop over all files in the directory
    for filename in os.listdir(folderpath):
        if filename.endswith(".npy"): 
            filepath = os.path.join(folderpath, filename)
            
            # Load data from the file
            _, extended_metaf = load_numpy2(filepath)        
            new_row = pd.DataFrame(extended_metaf, index=[0])
            # Add filename in the DataFrame
            new_row['filename'] = filename
            # Append the new row to the summary DataFrame
            recordingsummary = pd.concat([recordingsummary, new_row], ignore_index=True)

    try:
        recordingsummary = recordingsummary.loc[:,["center_freq","sample_rate","date_recorded","time_recorded","protocol","use_case","testbed","project_name","filename","sdr"]]
    except:
        print("not reducing pd size")

    return recordingsummary

def enqueue_output(out, queue):
    """
    Read lines from a subprocess output stream and enqueue them.

    Continuously reads lines from the given output stream until it encounters an empty byte string (indicating EOF), placing each line into the specified queue for asynchronous processing.

    :param out: The output stream to read from, typically stdout or stderr of a subprocess.
    :type out: _io.TextIOWrapper
    :param queue: The queue to which read lines are added.
    :type queue: Queue
    """
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

def run_curate(curate_args,action):
    """
    Execute the curation process with specified arguments and action.

    Dynamically constructs and runs a command to curate recordings, either by performing final adjustments or initial processing, depending on the specified action. Handles additional options like homogenization, augmentation, and class dropping based on attributes of `curate_args`.

    :param curate_args: Arguments object containing options for the curation process.
    :type curate_args: Namespace or similar
    :param action: Specifies the curation action to perform ('final' for final adjustments, or other values for initial processing).
    :type action: str
    :return: The last 100 lines of output from the curation command.
    :rtype: list[str]
    """
    if action == "final":
        command = ['python3', './recording_curation/curator/curator.py', "-sdf", curate_args.target_dataset_file, "-t", curate_args.target_dataset_file] 

        try:
            command.extend(["-i",str(curate_args.homogenize)])
        except Exception:
            print("no subsampling needed.")

        try:
            command.extend(["-a",str(curate_args.augment_and_fill)])
        except Exception:
            print("no augmentation to be added.")

        if hasattr(curate_args, 'drop_classes') and curate_args.drop_classes is not None:
            if len(curate_args.drop_classes):
                command.append("-l")
                command.extend(curate_args.drop_classes)
        else:
            print("no classes to be dropped.")


    else:
        command = ['python3', './recording_curation/curator/curator.py', "-r", "./included/", "-t", curate_args.target_dataset_file, "-e", curate_args.example_length, "-j", curate_args.keys[0], curate_args.keys[1]]  
    if sys.platform.startswith('win'): # handling in case running on windows
        command[0] = 'python'

    print(command)

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output_lines = []  # Variable to store the output lines
    while True:
        line = process.stdout.readline()
        if not line:
            break
        formatted_line = line.rstrip()
        output_lines.append(formatted_line)  # Append the output line to the list
        print(formatted_line)  # Print the output line to the terminal
    process.wait()  # Wait for the script to complete before closing the SSE connection
    return output_lines[-100:]

class CurateArgs:
    def __init__(self, example_length: str, keys: List[str], target_dataset_file: str, num_classes: int, homogenize: Optional[int] = 0, augment_and_fill: Optional[int] = 0, drop_classes: Optional[List[str]] = None):
        self.example_length = example_length
        self.keys = keys
        self.target_dataset_file = target_dataset_file
        self.num_classes = num_classes
        self.homogenize = homogenize
        self.augment_and_fill = augment_and_fill
        self.drop_classes = drop_classes

@app.post("/folder2dataset", response_class=HTMLResponse)
async def draft_dataset(request: Request,
                        action: str = Form(...),
                        example_length: str = Form(...),
                        class_1: str = Form(...),
                        class_2: str = Form(...),
                        dataset_name: str = Form(...),
                        num_classes: int = Form(2),
                        homogenize: Optional[str] = Form(None),
                        augment: Optional[str] = Form(None),
                        drop_classes: Union[List[str], str] = Form(None)):
    """
    Process form submission to draft or finalize a dataset based on input parameters.

    This endpoint handles the creation or finalization of a dataset, processing form data to apply specified curation actions like homogenization, augmentation, and class dropping. It dynamically constructs arguments for the curation process based on form inputs and executes the curation command.

    :param request: The request object containing the form data.
    :param action: The action to perform ('final' for final adjustments, others for initial drafting).
    :param example_length: Length of examples in the dataset.
    :param class_1: Name of the first class.
    :param class_2: Name of the second class.
    :param dataset_name: The name for the dataset.
    :param num_classes: The number of classes in the dataset.
    :param homogenize: Option to homogenize the dataset.
    :param augment: Option to augment the dataset.
    :param drop_classes: Classes to be dropped from the dataset, if any.
    :type request: Request
    :type action: str
    :type example_length: str
    :type class_1: str
    :type class_2: str
    :type dataset_name: str
    :type num_classes: int
    :type homogenize: Optional[str]
    :type augment: Optional[str]
    :type drop_classes: Union[List[str], str]
    :return: An HTML response displaying the output of the dataset curation process.
    :rtype: HTMLResponse
    """

    action = action

    form_data = await request.form()
    print(f"Form: {form_data}")

    curate_args = CurateArgs(example_length, [class_1, class_2], dataset_name, num_classes, homogenize, augment, drop_classes)
    review_args = Namespace(source_dataset_file=dataset_name)

    if action == "final":
        curate_args.homogenize = int(homogenize) if homogenize and homogenize.isdigit() else 0
        curate_args.augment_and_fill = int(augment) if augment and augment.isdigit() else 0
        curate_args.drop_classes = form_data.getlist('drop_classes')

        print(f"Homogenize to: {curate_args.homogenize}")
        print(f"Augment to: {curate_args.augment_and_fill}")
        print(f"Classes to drop: {curate_args.drop_classes}")

    output_lines = run_curate(curate_args, action)
    terminal_output = "\n".join(output_lines)

    html_string = generate_draft_html(review_args, curate_args, action, terminal_output)
    return HTMLResponse(content=html_string)

@app.get("/download")
async def download(dataset_file: str):
    """
    Provide a file download given the dataset file path.

    Validates the existence and readability of the specified file and returns a response that prompts the client to download the file. If the file does not exist or cannot be read, it raises an HTTP 404 exception.

    :param dataset_file: The path to the dataset file intended for download.
    :type dataset_file: str
    :return: A file response that prompts the client to download the specified file.
    :rtype: FileResponse
    :raises HTTPException: If the file is not found or is not readable.
    """
    directory_path = os.path.dirname(dataset_file)
    filename = os.path.basename(dataset_file)
    file_path = os.path.join(directory_path, filename)
    if os.path.exists(file_path) and os.access(file_path, os.R_OK):
        return FileResponse(file_path, filename=filename, headers={"Content-Disposition": f"attachment; filename={filename}"})
    else:
        raise HTTPException(status_code=404, detail="File not found or no permission to read.")

@app.post("/reset")
async def reset():
    """
    Clear specified directories and redirect to the home page.

    This function deletes the contents of a predefined list of directories, effectively resetting the application's state. After clearing the directories, it redirects the user to the home page.

    :return: A redirect response to the home page.
    :rtype: RedirectResponse
    """
    directories = ['./static', './example_review', './included', './recordings', './slice_review']
    clear_directories(directories)
    print(f"Reset and cleared directories {directories}")
    return RedirectResponse(url='/', status_code=HTTP_302_FOUND)

if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)

### TODO's
## see if the rec_args (pydantic BaseModel) thing works with the sdr cals (likely wont)
## change index.html to template based
## num_classes should probably be num_labels
## update the SDR selection to test which sdr is attached.
## better defaults