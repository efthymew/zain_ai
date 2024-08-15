"""
    generate training data on menus and outside the game and map them always to 0 inputs
"""
import cv2
import numpy as np

def merge_and_format_data_sliding_window(pixel_data, length, frame_skip=10):
    # gather every 10 frames of pixel data
    # map pixel data of past 10 frames to next 10 frames of actions
    x_data = []
    y_data = []
    for index in range(frame_skip, length - frame_skip + 1, frame_skip):
        pixels = np.array(pixel_data[index - frame_skip:index])
        x_data.append(pixels)
        # dependent variable add
        # next 10 frames of action
        next_inputs = np.array([[0.0 for i in range(18)] for j in range(10)], dtype=np.float32)
        y_data.append(next_inputs)

    return np.array(x_data), np.array(y_data)

def generate_menu_dataset(file_name):
    path = f"F:\\Documents\\python_projects\\zain_ai\\dataset_generation\\{file_name}"
    avi_file = path + ".avi"

    # avi video capture using cv2
    vcap = cv2.VideoCapture(avi_file)
    if not vcap.isOpened():
        return
    rgba_frames = []
    # Used as counter variable

    # checks whether frames were extracted
    success = 1
    count = 0

    while success:
        # vidObj object calls read
        # function extract frames
        success, image = vcap.read()

        if not success:
            break

       
        # resize to dimensions of internal framebuffer
        image = cv2.resize(image, (318, 262))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgba_frames.append(image)
        count += 1

    return merge_and_format_data_sliding_window(rgba_frames, count)

    

# generate_menu_dataset("MELEE_MENU")