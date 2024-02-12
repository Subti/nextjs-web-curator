import matplotlib

try:
    matplotlib.use('cairo')
except:
    matplotlib.use('Agg')
    

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import pathlib
import time
import argparse

from airium import Airium

def load_numpy2(filepath: str):
    # load from numpy
    with open(filepath, 'rb' ) as f:
        iqdata = np.load(f) 
        meta = np.load(f) 
        extended_metaf = np.load(f, allow_pickle=True)[0] #note its saved as an np array
    return iqdata, extended_metaf


def write_html2(data: dict, case: str): #writes inspect.html
    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang='en'):
        with a.head():
            a.title(_t="Select signals to include in training dataset:")
            a.link(rel="icon", type="image/png", href="https://www.qoherent.ai/wp-content/uploads/2021/10/part-logo-colour-e1633139269793.png")
            # a.link(rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css')

        with a.style():
            a('''
            body {
                font-family: Arial, sans-serif;
                color: #444;
                background-color: #ffffff;
                margin: 20px;    
            }

            h1, h2 {
                background-color: #2298dc;
                color: #ffffff;
                padding: 10px;
                border-radius: 12px;
                text-align: center;
            }

            table {
                width: 100%;
                margin-bottom: 20px;
                border-collapse: collapse;
            }

            table, th, td {
                border-bottom: 1px solid gray;
                padding: 10px;
                text-align: center;
            }

            input[type="checkbox"] {
                height: 20px;
                width: 20px;
                cursor: pointer;
            }

            button {
                    background: linear-gradient(to right, #2298dc, #7a64a7);
                    border: none;
                    border-radius: 25px;
                    color: #fff;
                    padding: 15px 30px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 20px;
                    margin: 4px 2px;
                    cursor: pointer;
                    transition: 0.3s;
            }

            button:hover {
                box-shadow: 0 12px 16px 0 rgba(0,0,0,0.24), 0 17px 50px 0 rgba(0,0,0,0.19);
            }


            ''')

            


        print("Writing HTML.")
        print("Data items:", data.items())
        with a.body():
            with a.script():
                a('''
                    async function collectSelected(action) { 
                        var checkboxes = document.querySelectorAll('input[type=checkbox]:checked')
                        var selectedFiles = []
                        for (var i = 0; i < checkboxes.length; i++) {
                            selectedFiles.push(checkboxes[i].value)
                        }
                        var data = {selectedFiles: selectedFiles};
                        console.log(data);
                        fetch("/collect", {
                            method: "POST",
                            body: JSON.stringify(data),
                            headers: {
                                "Content-Type": "application/json"
                            }
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            console.log(data.message);  // "Files added successfully!"
                            if (action === "collect") {
                                window.location.href = "/";
                            } else if (action === "review") {
                                window.location.href = "/review";
                            } else if (action === "curate") {
                                window.location.href = "/curate";
                            }
                        })
                        .catch((error) => {
                            console.error('Error:', error);
                        });
                    }
                ''')
            
            
            a.h1(_t="Select Signals to Include in Training Dataset:", style="text-align:center; font-family:verdana")
            for class_name, class_data in data.items():
                print("Class name:", class_name)
                print("Class data:", class_data)
                a.h2("Class: ", _t=class_name)
                with a.table(klass="striped centered highlight"): 
                    with a.thead():
                        with a.tr():
                            a.th(_t="Select") 
                            a.th(_t="IQ Plot and Spectrogram")
                            a.th(_t="File")
                            a.th(_t="Project Name")
                            a.th(_t="Center Frequency (MHz)")
                            a.th(_t="Sample Rate (MHz)")
                            a.th(_t="Protocol")
                            a.th(_t="Usage")
                    with a.tbody():
                        for key in class_data:
                            with a.tr():
                                with a.td(): 
                                    checkbox_value = f"{class_name}/{key}.svg"
                                    a.input(type="checkbox", value=checkbox_value, klass="custom-checkbox")

                                a.td().img(src=class_data[key]['plot'], alt="IQ Plot and Spectrogram for " + str(key),style="width: 75%; object-fit: cover;")
                                a.td(_t=str(key))
                                a.td(_t=class_data[key]['metadata']['project'])
                                a.td(_t=class_data[key]['metadata']['freq'])
                                a.td(_t=class_data[key]['metadata']['rate'])
                                a.td(_t=class_data[key]['metadata']['protocol'])
                                a.td(_t=class_data[key]['metadata']['usage'])

            with a.div(style="text-align:center; padding-top: 20px;"):
                if case == "collect":
                    with a.button(class_='btn waves-effect waves-light', onclick="collectSelected('collect')"):
                        a("Save and Capture More")
                    with a.button(class_='btn waves-effect waves-light', onclick="collectSelected('review')"):
                        a("Include Selected and Review")
                elif case == "review":
                    with a.button(class_='btn waves-effect waves-light', onclick="collectSelected('curate')"):
                        a("Include and curate")

            with a.form(method='POST', action='/reset'):
                a.button(klass='btn waves-effect waves-light', _t='Clear all and reset', type="submit")

    return a


def qualify_and_slice(test,tape,slice_length):

    tape_len = len(tape[0,:])
    n_slices =int(tape_len/slice_length) #calculate number of slices
    rms_list = np.zeros([n_slices,2],dtype='float16')
    pass_list = np.empty(n_slices,dtype='int8')
    slice_counter = 0
    not_counter = 0

    ###*************SEPARATE TAPE INTO AN ARRAY OF SLICES*************
    sliced_tape_list =np.zeros([n_slices,2,slice_length])  #define an empty slice array number of slices
    #populate the slice array
    for i in range(0,n_slices):
        sliced_tape_list[i,0,:] = tape[0,i:i+slice_length]
        sliced_tape_list[i,1,:] = tape[1,i:i+slice_length]
    ###************************************************************

    ## run a qualification test
    if test == 'RMS':
        max_amplitude = np.max(np.abs(tape))
        print(f"max amplitude: {max_amplitude}")

        if max_amplitude > 0.18:
            normalized_tape = tape / max_amplitude
        else: 
            normalized_tape = tape / 1000

        rms_counter = 0
        for i in range(0, tape.shape[1], slice_length):
            
            #normalize full tape
            rmssamples = normalized_tape[:, i:i+slice_length]
            # Calculate the RMS values for each row
            rms_values = np.sqrt(np.mean(rmssamples**2, axis=1))
            rms_list[rms_counter] = rms_values
            rms_counter+=1

            if rms_counter == n_slices:
                break

        rms_max = np.max(np.abs(rms_list))
        norm_rms_list = rms_list / rms_max

        #come up with a threshold
        min_norm_rms_list = np.amin(norm_rms_list, axis=None)
        mean_norm_rms_list = np.mean(norm_rms_list)
        std_norm_rms_list = np.std(norm_rms_list)

        if max_amplitude > .25:
            T_RMS = min_norm_rms_list + 0.3 * std_norm_rms_list
        elif max_amplitude > 0.1:
            T_RMS = min_norm_rms_list + 0.7 * std_norm_rms_list
        elif max_amplitude > .05:
            T_RMS = min_norm_rms_list + 1.5 * std_norm_rms_list
        else:
            T_RMS = mean_norm_rms_list + 1.8*std_norm_rms_list
        

        print(f"Threshold for snippet is {T_RMS}")
        print(f"snippet rms mean {mean_norm_rms_list} and min {min_norm_rms_list} and std {std_norm_rms_list}")

        #apply the test
        print(norm_rms_list.shape[0])

        for i in range(norm_rms_list.shape[0]):
            # Check if either row is above the threshold T_RMS
            if np.any(norm_rms_list[i] > T_RMS):
                pass_list[i] = 1
                # print("adding to stack")
                slice_counter+=1

            else:
                # print("not adding to stack")
                pass_list[i] = 0
                not_counter+=1
                # If not, discard and move to the next slice_length samples
                continue

        # print(rms_list)
        # maxmin = np.amax(rms_list, axis=None)/np.amin(rms_list, axis=None)
        print(f"total iterations: {slice_counter+not_counter}")
        print(f"total slices above threshold: {slice_counter}")
        print(f"total nots (skipped): {not_counter}")
        # print(f"total slices above threshold: {m}")
        # print(f"max/minratio: {maxmin}")
        print(f"threshold ratio: {slice_counter/(slice_counter+not_counter)}")

        #drop failed slices and
        #capture some of the noise slices too
        sliced_tape_list = sliced_tape_list[pass_list.nonzero()]

    else: #no qualification case
        print("no qualification test applied")
 
    return sliced_tape_list, norm_rms_list, pass_list, T_RMS


def signal_folder_inspector_npy2(folderpath: str,case: str):
    before = time.time()
    folderpath =  pathlib.Path(str(folderpath))
    print(folderpath)
    # plotpath = 'templates/'  # HTML will save under templates 
    plotpath = pathlib.Path('./templates')  # HTML will save under templates 
    static_dir = 'static'
    
    if not os.path.exists(plotpath):
        os.makedirs(plotpath)
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    # create a list of files from the folder
    subfolders = [x for x in folderpath.iterdir() if x.is_dir()]
    print("Examining subfolders.")
    print(len(subfolders), "subfolders found in folder")

    full_metadata = {}
    for subfolder in subfolders:
        paths = list(subfolder.glob('*.npy'))
        print("Examining subfolder:", subfolder)
        print(len(paths), "numpy files found in subfolder")

        # Initialise metadata dictionary here
        metadata = {} 

        for filepath in paths:
            filename = os.path.basename(filepath)   # file name only
            print(f"Loading {filename}")


            # load iqdata and metadata
            iqdata, extended_metaf = load_numpy2(filepath)

            # create dict of select metadata
            select_meta = {}
            for key in extended_metaf:
                if 'project' in key:
                    select_meta['project'] = extended_metaf[key]
                elif 'freq' in key:
                    select_meta['freq'] = extended_metaf[key]
                elif 'effective_sample_rate' in key:
                    if int(extended_metaf[key]) > pow(10, 5):
                        select_meta['rate'] = int(extended_metaf[key])/pow(10,6)
                    else:
                        select_meta['rate'] = int(extended_metaf[key])
                elif 'protocol' in key:
                    select_meta['protocol'] = extended_metaf[key]
                elif 'usage' in key or 'use_case' in key:
                    select_meta['usage'] = extended_metaf[key]

            time_rec = extended_metaf['time_recorded']
            sample_rate = select_meta['rate']
            iqcombined = iqdata[0,:] +1j*iqdata[1,:]

            center = int(float(select_meta['freq']))
            if center > pow(10,6): # double check that all frequencies are in MHz
                center = center/pow(10,6)
            if sample_rate > pow(10,6):
                sample_rate = sample_rate/pow(10,6)

            # plot preparation
            if case == "review":
                fig, (ax1,ax2, ax3) = plt.subplots(3, 1, gridspec_kw={'height_ratios': [1,1, 3]}, figsize=(6, 3))
            else:
                fig, (ax1, ax3) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(6, 3))

            fig.subplots_adjust(hspace=0)
            fig.set_figwidth(8)
            pltlen = len(iqdata[0,:])
            t = np.arange(0, pltlen, 1)

            # plotting timeseries
            ax1.plot(t,iqdata[0,:], t, iqdata[1,:])
            ax1.set_xlim(0, pltlen)
            ax1.set_xticks([])
            ax1.set_ylabel("Amplitude \n(Normalized)")
            ax1.set_ylim(-1.3, 1.3)
            ax1.set_yticks([])
            ax1.grid(True)

            if case == "review":
                _, rmsvals, passlist, _ = qualify_and_slice("RMS",iqdata,1024)

                ax2.set_xlim(xmin=0,xmax=len(rmsvals))
                ax2.set_ylim(0,1)
                # ax2.plot(rmsvals)
                x=range(len(passlist))
                ax2.bar(x,passlist, color='dodgerblue')
                # ax2.axhline(T_RMS)




            ##FFT Handling
            if pltlen < 2000:
                fft_size = int(64)
            elif pltlen < 10000:
                fft_size = int(256)
            elif pltlen < 1000000:
                fft_size = int(1024)
            else:     
                fft_size = int(2048)

            cmap = plt.get_cmap('twilight')
            Sxx, f, t, im = ax3.specgram(iqcombined, Fs=sample_rate, Fc=center, NFFT=fft_size, noverlap=int(fft_size/8),cmap=cmap)
            ax3.set_ylim(center-sample_rate/2, center+sample_rate/2)
            ticks_x = ticker.FuncFormatter(lambda t, pos: '{0:g}'.format(t/pow(10,3)))
            ax3.xaxis.set_major_formatter(ticks_x)
            ax3.set_ylabel('Frequency (MHz)')
            ax3.set_xlabel(f'Time (ms) Starting at {time_rec[0:2]}:{time_rec[2:4]}:{time_rec[4:6]}')
            ax3.xaxis.set_minor_locator(ticker.AutoMinorLocator())

            # Manual garbage collection
            iqdata = None
            iqcombined = None
            f = None
            t = None

            # saves plots as svg in static folder
            class_dir = os.path.join('static', subfolder.name)
            if not os.path.exists(class_dir):
                os.makedirs(class_dir)
            plot_name = os.path.join(class_dir, str(filename)[:-4] + '.svg')


            plt.savefig(plot_name, format='svg', dpi=80, bbox_inches="tight")
            plt.close()  


            
            # add select metadata to full metadata dict under the file name
            relative_plot_path = os.path.join('static', subfolder.name, str(filename)[:-4] + '.svg')
            metadata[filename[:-4]] = {'metadata': select_meta, 'plot': relative_plot_path}


        # add this class's metadata to the full metadata dict
        full_metadata[subfolder.name] = metadata

    html = write_html2(full_metadata,case)

    html_files = list(plotpath.glob('*.html'))
    max_index = -1

    for file in html_files:
        filename = file.stem  # Get the filename without extension

        if filename == 'inspect_final':
            continue
        if filename.startswith('inspect'):
            try:
                index = int(filename[7:])  # Ignore the first 7 characters ('inspect')
                if index > max_index:
                    max_index = index
            except ValueError:
                print(f"Warning: File '{file.name}' does not have a proper integer index.") # If there is no integer after 'inspect', print a warning and continue

    html_filename = f'inspect{max_index + 1}.html'


    if case == "review": 
        htmlpath = os.path.join(plotpath, "inspect_final.html")
    else:
        # htmlpath = os.path.join(plotpath, "inspect.html")
        htmlpath = os.path.join(plotpath, html_filename)


    with open(htmlpath, 'wb') as f:
        f.write(bytes(html))

    after = time.time()
    print(f"Case: {case}. Generated html file {htmlpath} for {folderpath}")
    print(f"before: {before}, after: {after}, diff: {after-before}")
    return html_filename

def get_num_classes_from_metadata(metadata):
    # get list of all classes from the metadata
    classes = list(metadata.keys())
    return len(classes), classes


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", type=str, help="Source folder that has recordings.")
    args = parser.parse_args()

    start_time = time.time()
    signal_folder_inspector_npy2(args.s)
    print("--- %s seconds ---" % (time.time() - start_time))