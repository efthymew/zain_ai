from pymem import Pymem
from pymem.ptypes import RemotePointer
import numpy as np
import cv2
import dolphin_memory_engine
import time
import difflib

root_addr = 0x80000000
xfb = 0x003FC860
width = 640
height = 480
offset_top_fb = width * 2
addr = root_addr + xfb
target_fps = 60
frame_duration = 1.0 / target_fps
stride_maybe = 1280

import numpy as np

import numpy as np


def process_xfb_buffer(raw_bytes, fb_width, fb_height, fb_stride, interlaced=True):
    if interlaced:
        fb_height //= 2
        fb_stride *= 2
    
    # Calculate the output frame height considering interlacing
    output_height = fb_height * 2 if interlaced else fb_height
    
    # Create an array to store the final YUV image
    frame = np.zeros((output_height, fb_width, 3), dtype=np.uint8)
    
    # Extract and process the top (odd) field
    for i in range(fb_height):
        start = i * fb_stride
        # Read the raw data as 4 bytes per pixel, ignoring the 4th byte (alpha)
        yuv_data = np.frombuffer(raw_bytes[start:start + fb_width * 4], dtype=np.uint8).reshape((fb_width, 4))[:, :3]
        if interlaced:
            frame[2 * i] = yuv_data  # Top field (odd)
        else:
            frame[i] = yuv_data  # Progressive scan

    if interlaced:
        # Extract and process the bottom (even) field
        for i in range(fb_height):
            start = (i + fb_height) * fb_stride
            yuv_data = np.frombuffer(raw_bytes[start:start + fb_width * 4], dtype=np.uint8).reshape((fb_width, 4))[:, :3]
            frame[2 * i + 1] = yuv_data  # Bottom field (even)

    return frame


# Example usage
# Assuming raw_bytes is the byte array containing the XFB buffer
# width = 640, height = 480, and stride = 640 for instance


last = b""
differ = difflib.Differ()
while True:
    if not dolphin_memory_engine.is_hooked():
        dolphin_memory_engine.hook()
        if dolphin_memory_engine.is_hooked():
            print("Hooked to Dolphin")
            break
while True:
    # Read memory
    stride = 0x4D << 5

    data = dolphin_memory_engine.read_bytes(addr, stride_maybe * height * 4)
    xfb_image = process_xfb_buffer(data, 640, 480, 640, True)
    # Convert RGBA to RGB
    xfb_image = cv2.cvtColor(xfb_image, cv2.COLOR_YUV2BGR)
    # # Read memory
    # data = dolphin_memory_engine.read_bytes(addr + offset_top_fb, width // 2 * 480 * 4)
    # # Convert byte array to numpy array and reshape
    # image_np = np.frombuffer(data, dtype=np.uint8)
    # if image_np[0] == 0:
    #     continue
    # image_rgb = image_np.reshape((width // 2, 480, 4))
    # image_rgb = image_np.reshape((width // 2, 480, 4))
    # top_image = np.delete(image_rgb, (3), axis=2)
    # # Convert RGBA to RGB
    # top_image = cv2.cvtColor(top_image, cv2.COLOR_YUV2BGR)

    cv2.imshow("Input", xfb_image)
    cv2.waitKey(0)
    # print('hiafterbottom')
    # cv2.imshow("Input", top_image)
    # cv2.waitKey(0)
    # print('hiaftertop')
