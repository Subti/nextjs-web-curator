import gc
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
import psutil

# import matplotlib.style as mplstyle
# mplstyle.use("fast")

from airium import Airium


def load_numpy(filepath: str):
    # load from numpy
    with open(filepath, 'rb' ) as f:
        iqdata = np.load(f) 
        meta = np.load(f) 
        extended_metaf = np.load(f, allow_pickle=True)[0] #note its saved as an np array
    return iqdata, extended_metaf


def write_html(data: dict):
    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang='en'):
        with a.head():
            a.title(_t="Numpy Signal Inspector")
            a.link(rel="icon", type="image/png", href="https://www.qoherent.ai/wp-content/uploads/2021/10/part-logo-colour-e1633139269793.png")
            a('''<style>
            table, th, td {
            border-bottom: 1px solid gray;
            border-collapse: collapse;
            }
            </style>''')
        
        with a.body():
            a.h1(_t="Numpy Signal Inspector", style="text-align:center; font-family:verdana")
            with a.table(style="width:100%; text-align:center; font-family:verdana"):
                with a.thead():
                    with a.tr(style="font-size: 125%"):
                        a.th(_t="IQ Plot and Spectrogram", rowspan="2", style="width:55%")
                        a.th(_t="Metadata", colspan="6", style="padding-bottom: 10px; padding-top: 10px")
                    with a.tr():
                        a.th(_t="File", style="padding-bottom: 3px; padding-top: 3px")
                        a.th(_t="Project Name", style="padding-bottom: 3px; padding-top: 3px")
                        a.th(_t="Center Frequency (MHz)", style="padding-bottom: 3px; padding-top: 3px")
                        a.th(_t="Sample Rate (MHz)", style="padding-bottom: 3px; padding-top: 3px")
                        a.th(_t="Protocol", style="padding-bottom: 3px; padding-top: 3px")
                        a.th(_t="Usage", style="padding-bottom: 3px; padding-top: 3px")
                with a.tbody():
                    for key in data:
                        with a.tr():
                            a.td().img(src=data[key]['plot'], alt="IQ Plot and Spectrogram for " + str(key))
                            a.td(_t=str(key))
                            a.td(_t=data[key]['metadata']['project'])
                            a.td(_t=data[key]['metadata']['freq'])
                            a.td(_t=data[key]['metadata']['rate'])
                            a.td(_t=data[key]['metadata']['protocol'])
                            a.td(_t=data[key]['metadata']['usage'])                        
    return a


def signal_folder_inspector_npy(folderpath: str, subfolders: bool):
    folderpath =  pathlib.Path(str(folderpath))
    plotpath = str(folderpath) + '\\Plots\\'    # create Plots subfolder in folderpath
    if not os.path.exists(plotpath):
        os.mkdir(plotpath)

    # create a list of files from the folder
    if subfolders == True:
        paths = list(folderpath.glob('**/*.npy'))
        print("Examining only subfoldersfolder.")
    else:
        paths = list(folderpath.rglob('*.npy'))
        print("Examining only target folder.")
    print(len(paths), "numpy files found in folder")

    process = psutil.Process(os.getpid())
    print('BeforeFigures: ', process.memory_info().rss)  # in byte

    metadata = {}
    for i in range(len(paths)):
        filepath = paths[i]                     # full path of file
        filename = os.path.basename(filepath)   # file name only
        print(f"Loading {filename}")

        # load iqdata and metadata
        iqdata, extended_metaf = load_numpy(filepath)

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
        fig, (ax1, ax3) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]})
        fig.subplots_adjust(hspace=0)
        fig.set_figwidth(8)
        pltlen = len(iqdata[0,:])
        t = np.arange(0, pltlen, 1)

        # plotting timeseries
        ax1.plot(t,iqdata[0,:], t, iqdata[1,:])
        ax1.set_xlim(0, pltlen)
        ax1.set_xticks([])
        ax1.set_ylabel("Amplitude \n(Normalized)")
        ax1.set_ylim(-1, 1.05)
        ax1.set_yticks([])
        ax1.grid(True)

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

        # Manual garbage collection
        iqdata = None
        iqcombined = None
        f = None
        t = None

        # saves plots as svg in Plots folder

        plot_name = os.path.join(plotpath, str(filename)[:-4] + '.svg')
        plt.savefig(plot_name, bbox_inches="tight")
        plt.close("all")
        plt.cla()
        plt.clf() 


        
        # add select metadata to full metadata dict under the file name
        relative_plot_path = str(filename)[:-4] + '.svg'
        metadata[filename[:-4]] = {'metadata': select_meta, 'plot': relative_plot_path}


        print('After Figures:\t', process.memory_info().rss)  # in bytes
        # clear plots from memory
        all_fignums = plt.get_fignums()
        for j in all_fignums:
            _fig = plt.figure(j)
            _fig.clear()
            plt.close()
        gc.collect()

        print('After Deletion:\t', process.memory_info().rss)  # in bytes


    
    html = write_html(metadata)
    htmlpath = os.path.join(plotpath, "folder_inspector.html")
    with open(htmlpath, 'wb') as f:
        f.write(bytes(html))
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", type=str, help="Source folder that has recordings.")
    args = parser.parse_args()

    start_time = time.time()
    signal_folder_inspector_npy(args.s, False)
    print("--- %s seconds ---" % (time.time() - start_time))