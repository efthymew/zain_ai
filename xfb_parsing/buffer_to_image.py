from pymem import Pymem
from pymem.ptypes import RemotePointer
import numpy as np
import cv2
import dolphin_memory_engine
import time
import difflib

addr = 0x003fc860
target_fps = 60
frame_duration = 1.0 / target_fps

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
    data = dolphin_memory_engine.read_bytes(addr, 640 * 480 * 3)
    # Convert byte array to numpy array and reshape
    image_np = np.frombuffer(data, dtype=np.uint8)
    if image_np[0] == 0:
        continue
    image_np = image_np.reshape((480, 640, 3))
    # Convert RGBA to RGB
    image_rgb = cv2.cvtColor(image_np, cv2.COLOR_YUV2BGR)
    cv2.imshow("Input", image_rgb)
    cv2.waitKey(0)
    print('hi')
