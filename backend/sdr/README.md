# sdr
- Repo for multi-sdr calls.
- Currently only does one batch of IQ at a time, and saves to recording.
- Example code shown in logiq_loop.py
- Designed to be called from other repos.

``` python logiq_loop.py -h ```

or

``` python -m sdr.blade_logiq -h ```

- Generally preferable to be called as module from wherever the the file is needed, if not calling it as a module, remove anywhere that says `from sdr`, and replace this line `metapath = pathlib.Path("sdr/"+args.metadata)` with `metapath = pathlib.Path(args.metadata)`.

## recording executive

utility for adding a bit of diversity in recordings, capturing a few centre frequencies near the desired one, sample rates, and even antennad

currently a lot is hardcoded, but eventually we can make this be more configrued (e.g. number of channels/antennas, number of sample rates to try, or specific ones to try etc)

``` python3 recording_executive.py --center=2500e6 -time=0.5```
----> to do - new import statment on import error (if calling directly from the folder)

or when as submodule (which will be the main behaviour in QDM)

``` python3 -m sdr.recording_executive -h```
```python -m sdr.recording_executive -t .01 -o 3```


## other example operations commands:

```python3 usrp_logiq.py -i name=MyB210```
```python3 usrp_logiq.py -i 192.168.64.1```

use log_view (saves in /static/)
```python3 log_view.py -s usrp -i name=MyB210```

stream capture for infinity
```python3 -m sdr.sdr_capture -s pluto -t inf```

stream capture with zmq streaming
```python3 -m sdr.sdr_capture -s pluto -t inf -z 5556```


### help


SDR capture module, cross platform library provides a common interface for common testbed receiving functions.

options:
  -h, --help            show this help message and exit
  -i IP_ADDR, --ip_addr IP_ADDR
                        Specify the IP address of the SDR. Default = 'find', which searches for an IP address.
                        If the search fails, defaults of 192.168.40.2 are used for USRP and 192.168.3.1 for the
                        pluto.
  -n NUM_SAMPLES, --num_samples NUM_SAMPLES
                        Number of samples to capture. Default = 128,000
  -f CENTER_FREQ, --center_freq CENTER_FREQ
                        Center frequency in Hz. Default 2440e6 except for RTL: 1700e6 (1.7GHz)
  -r SAMPLE_RATE, --sample_rate SAMPLE_RATE
                        sample rate in Hz. Default is 50000000 (50MHz)
  -g GAIN, --gain GAIN  Set gain in dB. Default is 32
  -m METADATA, --metadata METADATA
                        Metadata to add to the numpy file. Default is ./logiq_meta.yaml
  -c CHANNEL, --channel CHANNEL
                        The channel for the usrp or blade. Default is 0
  -s SDR, --sdr SDR     Choice of which sdr to receive signals from. If none is chosen, program will try usrp,
                        then blade, then pluto, then rtl.
  -x FILE_EXTENSION, --file_extension FILE_EXTENSION
                        File extension to save - default npy, also supports sigmf (block capture only).
  -t STREAM_TIME, --stream_time STREAM_TIME
                        Length of time to stream continuously. If 'inf' is given, program will stream
                        indefinitely and not save any recordings. If none is given, program will not stream
                        continuously and will receive signal from chosen sdr once.
  -z ZMQ, --zmq ZMQ     Specify a port for publising on zmq (instead of stream buffer) Suggested port 5556.
                        Default = None i.e use stream buffer
  --equalize EQUALIZE, -e EQUALIZE
                        --equalize for equalization or no argument for none.


## pluto install instructions

> from pysdr.org: https://pysdr.org/content/pluto.html


``` 
sudo apt-get install build-essential git libxml2-dev bison flex libcdk5-dev cmake python3-pip libusb-1.0-0-dev libavahi-client-dev libavahi-common-dev libaio-dev
cd ~
git clone --branch v0.23 https://github.com/analogdevicesinc/libiio.git
cd libiio
mkdir build
cd build
cmake -DPYTHON_BINDINGS=ON ..
make -j$(nproc)
sudo make install
sudo ldconfig

cd ~
git clone https://github.com/analogdevicesinc/libad9361-iio.git
cd libad9361-iio
mkdir build
cd build
cmake ..
make -j$(nproc)
sudo make install 


pip install pyadi-iio
```

Pluto SDR doesn't automatically connect to the Ubuntu server as it is a USB device that emulates an ethernet conenction, and the Ubuntu server does not let USB devices install themselves automatically.  
To set it up, first verify the pluto is connected via lsusb:  
```
lsusb
```  
With the pluto plugged in run:  
```
ip link show
```  
Take note of what is shown, then unplug the pluto and run it again. Note what link is missing.  
```
ip link show
```
Plug the pluto in again then run it one more time to see the new connection.  
```
ip link show
```
Note the name of the interface of the pluto.  

Manually set ifconfig for {interface name}.  
```
sudo ifconfig {interface name} 192.168.3.2 netmask 255.255.255.0 up
```
Make special note to use the same IP subnet of your pluto (this one is set to the default of 192.168.3.1, so any IP on 192.168.3.x will do).

Run ifconfig to see that the new interface exists.  
```
ifconfig
```
Test with a ping  
```
ping 192.168.3.1
```
if it returns a result, you are good to go!
NOTE, this will NOT persist across reboots.

Alternatively, create a netplan to connect to the Pluto.  
```
sudo nano /etc/netplan/02-usb-device.yaml
```
Add the following lines to the contents:  
```
network:
  version: 2
  renderer: networkd
  ethernets:
    enx00e022f21353:  # Replace this with the correct interface name
      dhcp4: no
      addresses: [192.168.3.2/24]
```

Then run this line and test by pinging:
```
sudo netplan apply
ping 192.168.3.1
```

For Apple Silicon, follow [these instructions](https://github.com/qoherent/apple-silicon-SDR/blob/main/README.md)

## blade install instructions


> from: https://github.com/Nuand/bladeRF/wiki/Getting-Started%3A-Linux#user-content-Easy_installation_for_Ubuntu_The_bladeRF_PPA

```

sudo add-apt-repository ppa:nuandllc/bladerf
sudo apt-get update
sudo apt-get install bladerf

sudo apt-get install libbladerf-dev

sudo apt-get install bladerf-fpga-hostedxa4   # nessecary for installation of bladeRF 2.0 Micro A4

```
For macOS, run `brew install libbladerf`

## usrp/uhd instructions

> From pysdr.org:

```
sudo apt-get install git cmake libboost-all-dev libusb-1.0-0-dev python3-docutils python3-mako python3-numpy python3-requests python3-ruamel.yaml python3-setuptools build-essential
cd ~
git clone https://github.com/EttusResearch/uhd.git
cd uhd/host
mkdir build
cd build
cmake -DENABLE_TESTS=OFF -DENABLE_C_API=OFF -DENABLE_MANUAL=OFF ..
make -j8
sudo make install
sudo ldconfig
```


* it may need the following to be added to .bashrc:

``` export PYTHONPATH="/usr/local/lib/python3.10/site-packages/" ```
For a full tutorial including how to load the FPGA image, read [this](https://docs.google.com/document/d/1G_WzvqHkh9w2hbVooOZWlwEaFUcyV9fr-YjQWS4yS5c/edit)

For macOS, run `breq install uhd`

## rtlsdr instructions
`sudo apt-get install librtlsdr-dev`
`pip install pyrtlsdr`

For macOS, run `brew install librtlsdr`

NOTE: For sdr capture.py must do -s rtl not -s rtlsdr

# to do 
run imports from here
have the selector be here so that code elsewhere is far simpler
set up stream mode for everything


# for accessing in WSL from windows

make usb available in WSL:

https://learn.microsoft.com/en-us/windows/wsl/connect-usb

Flllow the most recent instructions for the usbipd project - start by installing it via the most recent msi file

https://github.com/dorssel/usbipd-win/releases

Then install ubuntu side things

```
sudo apt install linux-tools-generic hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20
```

find the SDR using (you may need to open a new powershell instance as administrator) - if the device is missing firmware it wont show up as a USRP

`usbipd list`

get the bus id (in this case 1-2)

then bind

```usbipd bind --busid <id>```

then attach (a system restart might be needed, and you must have a WSL window open)

```usbipd attach --wsl --busid 1-2 -a```