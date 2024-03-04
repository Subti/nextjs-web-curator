# global variables used within multiple files
import numpy as np

# TODO: Rename this to sdr_stream_buffer where referenced.
def init():
    global buffer
    # buffer = []
    global buffer_count
    buffer = np.array([])
    buffer_count = 0



# class RIE_IQ_Buffer:
#     def __init__(self, size):
#         # self.buffer = []
#         self.buffer = np.array([])
#         self.size = size

#     def current_size(self):
#         return len(self.buffer)
    
#     def put(self, item):
#         if len(self.buffer) >= self.size:
#             self.buffer.pop(0)
#         self.buffer.append(item)

#     def get(self):
#         return self.buffer.pop(0)

#     def empty(self):
#         return len(self.buffer) == 0
    
#     def check_shape(self, item):
#         x_test_full, iqdata = item
#         print(f"Shape of x_test_full: {x_test_full.shape}")
#         print(f"Shape of iqdata: {iqdata.shape}")



    ### RIE BIFFER REF CODE
            # def sdr_preprocessing(self, callback, get_rec_args):
    #     global rec_args, use_sdr
    #     t_end = time.time() + self.args.max_time
    #     while True:  
    #         if get_rec_args is not None:
    #             rec_args = get_rec_args()

    #         # SDR capture
    #         try:
    #             #try stream first
    #             sdr_module(rec_args)         
    #         except:
    #             fullpath, samples = sdr_module(rec_args)

    #             print(Color.RED + f"Capture {use_sdr} and saved to {fullpath}" + Color.RESET)
                    
    #             print(Color.RED + "Data captured and trying to load..." + Color.RESET)

    #             iqdata, extended_meta = load_numpy2(fullpath)
    #             # x_test_full = simple_slice(iqdata, 1024)
    #             x_test_full = qualify_and_slice('RMS', iqdata, 1024)
    #             print(Color.RED + f"Data sliced. x_test_full shape: {x_test_full[0].shape}"+ Color.RESET)


    #             self.send_data((x_test_full, iqdata)) 
    #             self.buffer.put((x_test_full, iqdata))
    #             #self.buffer.check_shape((x_test_full, iqdata))  
    #             print(Color.RED + f"Data has been added to the buffer, current buffer size is {self.buffer.current_size()}" + Color.RESET)
    #             del iqdata
    #             del x_test_full
    #             gc.collect()