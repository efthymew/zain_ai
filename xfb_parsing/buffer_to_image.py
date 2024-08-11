from PIL import Image
import numpy as np
import dolphin_memory_engine
import time
import difflib

addr = 0x80000000
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
    start_time = time.perf_counter()
    
    # Read memory
    data = dolphin_memory_engine.read_bytes(addr, 640 * 480 * 4)
    if data != last:
        print('here')
        d = list(differ.compare(data, last))
    last = data
    print('hi')
    
    # Calculate elapsed time
    elapsed_time = time.perf_counter() - start_time
    
    # Sleep for the remaining time to maintain the target frame rate
    sleep_time = max(0, frame_duration - elapsed_time)
    time.sleep(sleep_time)
