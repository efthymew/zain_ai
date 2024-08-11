import sys
import pickle

from dolphin import event

def write_to_file(width: int, height: int, data: bytes):
    print(f"attempting write dimensions: {width} x {height}")
    with open("F:/Documents/python_projects/zain_ai/frame_parsing/output/melee.raw", "wb") as f:
        f.write(data)
    print("successful write")

event.on_framedrawn(write_to_file)