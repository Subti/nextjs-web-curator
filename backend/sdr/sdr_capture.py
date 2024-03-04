try:

    passes = []
    fails = []
    block_functions = {}
    stream_functions = {}

    sdrstr = "usrp"
    try:
        import usrp_logiq
        stream_functions[sdrstr] = usrp_logiq.stream_usrp
        block_functions[sdrstr] = usrp_logiq.usrp_logiq
        passes.append(sdrstr)
    except:
        fails.append(sdrstr)
    sdrstr = "blade"
    try:
        import blade_logiq, run_blade
        stream_functions[sdrstr] = run_blade.stream_blade
        block_functions[sdrstr] = blade_logiq.blade_to_npy
        passes.append(sdrstr)
    except:
        fails.append(sdrstr)
    sdrstr = "pluto"
    try:
        import pluto_logiq
        stream_functions[sdrstr] = pluto_logiq.stream_pluto
        block_functions[sdrstr] = pluto_logiq.run_pluto_rx
        passes.append(sdrstr)
    except:
        fails.append(sdrstr)

    sdrstr = "rtl"
    try:
        import rtlsdr_logiq
        stream_functions[sdrstr] = rtlsdr_logiq.stream_rtlsdr
        block_functions[sdrstr] = rtlsdr_logiq.rtlsdr_logiq
        passes.append(sdrstr)
    except Exception as e:
        fails.append(sdrstr)

    sdrstr = "hackrf"
    try:
        import hackrf_logiq
        stream_functions[sdrstr] = hackrf_logiq.stream_hackrf
        block_functions[sdrstr] = hackrf_logiq.hackrf_block
        passes.append(sdrstr)
    except Exception as e:
        fails.append(sdrstr)

    import zmq
    import threading
    import modules.global_vars as global_vars
    import synth_logiq
    from modules.support_functions import cli_parser, find_uhd_device_ip, find_adalm_pluto_ip, argscleanup, radio_zmq_publisher

    print("RUNNING FROM ROOT")


except:
    from sdr.modules import global_vars
    from sdr.modules.support_functions import cli_parser, argscleanup, find_adalm_pluto_ip, find_uhd_device_ip, radio_zmq_publisher
    import zmq
    import threading
    print("RUNNING FROM PARENT")

    passes = []
    fails = []
    block_functions = {}
    stream_functions = {}

    sdrstr = "usrp"
    try:
        from sdr import usrp_logiq
        stream_functions[sdrstr] = usrp_logiq.stream_usrp
        block_functions[sdrstr] = usrp_logiq.usrp_logiq
        passes.append(sdrstr)
    except Exception as e:
        fails.append(sdrstr)
        print(f"{sdrstr} failed {e}")

    sdrstr = "blade"
    try:
        from sdr import blade_logiq, run_blade
        stream_functions[sdrstr] = run_blade.stream_blade
        block_functions[sdrstr] = blade_logiq.blade_to_npy
        passes.append(sdrstr)
    except:
        fails.append(sdrstr)

    sdrstr = "pluto"
    try:
        from sdr import pluto_logiq
        stream_functions[sdrstr] = pluto_logiq.stream_pluto
        block_functions[sdrstr] = pluto_logiq.run_pluto_rx
        passes.append(sdrstr)
    except:
        fails.append(sdrstr)

    sdrstr = "rtl"
    try:
        from sdr import rtlsdr_logiq
        stream_functions[sdrstr] = rtlsdr_logiq.stream_rtlsdr
        block_functions[sdrstr] = rtlsdr_logiq.rtlsdr_logiq
        passes.append(sdrstr)
    except:
        fails.append(sdrstr)

    sdrstr = "synth"
    try:
        from sdr import synth_logiq
        stream_functions[sdrstr] = synth_logiq.stream_synth
        block_functions[sdrstr] = synth_logiq.synth_logiq
        passes.append(sdrstr)
    except Exception as e:
        fails.append(sdrstr)
        print(f"{sdrstr} failed {e}")


    
    sdrstr = "hackrf"
    try:
        from sdr import hackrf_logiq
        stream_functions[sdrstr] = hackrf_logiq.stream_hackrf
        block_functions[sdrstr] = hackrf_logiq.hackrf_block
        passes.append(sdrstr)
    except Exception as e:
        fails.append(sdrstr)
        print(f"{sdrstr} failed {e}")


print(f"Loaded SDR drivers: {passes}")
print(f"Failed SDR driver loads: {fails}")
sdr_order=passes

def get_attached_radios():
    # implement a new function in each logiq to find the attached radio to a system
    return passes


def sdr_module(args):

    """
    Manages the capture process for Software Defined Radio (SDR) based on specified arguments.

    This function initializes global variables and determines the capture mode (streaming or single block) 
    based on the `stream_time` parameter in `args`. It supports both a specified SDR device or prioritizes 
    available devices. In streaming mode, it can optionally publish data using ZeroMQ.

    Parameters:
    args (Namespace): A namespace object containing various parameters, including:
                      - stream_time (int): Determines the capture mode. Positive value for streaming, zero for single block.
                      - sdr (str, optional): The identifier for a specific SDR device. If None, devices are tried based on priority.
                      - zmq (str, optional): Endpoint for ZeroMQ publisher, used in streaming mode.
                      Other parameters required by the capture functions and ZeroMQ publisher are also included.

    Returns:
    tuple or None: In single block mode, returns a tuple (fullpath, samples) where `fullpath` is the path to the captured data 
                   and `samples` is the data itself. In streaming mode, returns None.

    Raises:
    Exception: If an error occurs during the capture process.

    Notes:
    - The function uses a global `global_vars` module for initialization.
    - The capture functions are selected from either `stream_functions` or `block_functions` based on the mode.
    - In streaming mode, a new thread is spawned for the ZeroMQ publisher if `zmq` is specified.
    - The function handles exceptions during capture, attempting fallbacks or reporting errors as appropriate.
    """

    global_vars.init()
    if args.stream_time > 0 :
        sdr_capture_functions = stream_functions
        mode = "Stream"
    else:
        sdr_capture_functions = block_functions
        mode = "Single block"
    

    if args.sdr is not None:
        args = argscleanup(args)
        try:
            print("***********************")
            print(f"{mode} capture with {args.sdr}")
            print("***********************")
            if mode == "Stream" :
                if args.zmq is not None:
                    publisher_thread = threading.Thread(target=radio_zmq_publisher, args=(args.zmq,))
                    publisher_thread.start()
                sdr_capture_functions[args.sdr](args)
            else:
                print("##########################")
                fullpath, samples = sdr_capture_functions[args.sdr](args)

        except Exception as e:
            print(f"Error attempting capture with {args.sdr}: {e}")
    else:
        print("CAPTURE BASED ON PRIORITY")
        for radio in sdr_order:
            try:
                print("_____________________")
                print(f"Attempting {mode} Capture with {radio}")
                args.sdr = radio
                args = argscleanup(args)
                if mode == "Stream":
                    if args.zmq is not None:
                        publisher_thread = threading.Thread(target=radio_zmq_publisher, args=(args.zmq,))
                        publisher_thread.start()
                    sdr_capture_functions[radio](args)
                else:
                    fullpath, samples = sdr_capture_functions[radio](args)
                break
            except Exception as e:
                print(f"Failed capture from {radio} due to: {e}")
                continue

    # return samples

    if mode == "Stream":
        # publisher_thread.join()
        return None # maybe replace with buffer later
    else:
        return fullpath, samples

    # return None


if __name__ == "__main__":

    args = cli_parser()

    # _, samples = sdr_module(args)

    sdr_module(args)


    print(args)
    # TODO: clean up repo 
    # TODO: fix rtl write error and buffer size problems
    # TODO: simplify this file (less nested if/elses)
    # TODO: make output of various scripts less verbous and consistent
    # TODO: blade breaks priority because of a shutdow nfunction. change it
    # TODO: better import handling so that not all sdr familes need ot be set up
    # TODO: file handling and saving within streaming modes.