import sys
import pickle

from dolphin import event

frame_buffer = []
count = 0

def write_to_file(width: int, height: int, data: bytes):
    # print(f"attempting write dimensions: {width} x {height}")
    # with open("F:/Documents/python_projects/zain_ai/frame_parsing/output/melee.raw", "wb") as f:
    #     f.write(data)
    # print("successful write")
    # add frame buffer
    # increment count
    # on count 10 create input buffer of size 10 and send of

    # 0 1 2 3 
    print(sys.version)

event.on_framedrawn(write_to_file)