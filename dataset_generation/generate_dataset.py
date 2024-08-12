""" for each file in slippi files, run it and output an avi file
        for each avi file convert to rgb numpy array of frames and match each frame with frame of slippi file inputs for each
        skip every 12 frames to keep it relatively realistic in reacting
"""

from PIL import Image
import io
import numpy as np
import cv2

import slippi
from slippi.id import CSSCharacter
from slippi.event import Buttons

"""
class GCInputs(TypedDict, total=False):
    A: bool
    B: bool
    X: bool
    Y: bool
    Z: bool
    Start: bool
    Up: bool
    Down: bool
    Left: bool
    Right: bool
    L: bool
    R: bool
    StickX: float
    StickY: float
    CStickX: float
    CStickY: float
    TriggerLeft: float
    TriggerRight: float
"""

def merge_and_format_data(input_data, pixel_data, length, frame_skip=10):
    # gather every 10 frames of pixel data
    # map pixel input to next 10 frames of output
    x_data = []
    y_data = []
    for index in range(0, length, frame_skip):
        # independent variable add
        x_data.append(pixel_data[index])

        # dependent variable add
        # next 10 frames of action
        next_inputs = np.array(input_data[index:index + frame_skip], dtype=np.float32)
        if len(next_inputs) < 10:
            next_inputs = np.resize(next_inputs, (10, 18))
        y_data.append(next_inputs)

    return np.array(x_data), np.array(y_data)


def get_zain_port(game):
    # check to see players to find red marth
    for i, p in enumerate(game.start.players):
        if not p:
            continue
        if p.character == CSSCharacter.MARTH and p.costume == 1 and p.type == 0:
            return i

def is_flag_set(value, flag):
    return float((value & flag) == flag)

def get_slippi_inputs(slippi_frames, zain_port):
    inputs = []
    for f in slippi_frames:
        buttons = [0.0 for i in range(18)]
        controller_data = f.ports[zain_port].leader.pre
        physical_buttons = controller_data.buttons.physical
        buttons[0] = is_flag_set(physical_buttons, Buttons.Physical.A)
        buttons[1] = is_flag_set(physical_buttons, Buttons.Physical.B)
        buttons[2] = is_flag_set(physical_buttons, Buttons.Physical.X)
        buttons[3] = is_flag_set(physical_buttons, Buttons.Physical.Y)
        buttons[4] = is_flag_set(physical_buttons, Buttons.Physical.Z)
        buttons[5] = is_flag_set(physical_buttons, Buttons.Physical.START)
        buttons[6] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_UP)
        buttons[7] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_DOWN)
        buttons[8] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_LEFT)
        buttons[9] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_RIGHT)
        buttons[10] = is_flag_set(physical_buttons, Buttons.Physical.L)
        buttons[11] = is_flag_set(physical_buttons, Buttons.Physical.R)
        buttons[12] = controller_data.joystick.x
        buttons[13] = controller_data.joystick.y
        buttons[14] = controller_data.cstick.x
        buttons[15] = controller_data.cstick.y
        buttons[16] = controller_data.triggers.physical.l
        buttons[17] = controller_data.triggers.physical.r
        inputs.append(buttons)

    return inputs


def generate_dataset(slippi_file_name):
    path = f"F:\\Documents\\python_projects\\zain_ai\\dataset_generation\\{slippi_file_name}"
    slippi_file = path + ".slp"
    avi_file = path + ".avi"

    # convert to game obj
    game = slippi.Game(slippi_file)

    # avi video capture using cv2
    vcap = cv2.VideoCapture(avi_file)
    if not vcap.isOpened():
        return

    zain_port = get_zain_port(game)
    input_frames = get_slippi_inputs(game.frames, zain_port)
    rgba_frames = []

    maximum = len(input_frames)
    # Used as counter variable
    count = 0

    # checks whether frames were extracted
    success = 1

    while success and count < maximum:
        # vidObj object calls read
        # function extract frames
        success, image = vcap.read()

       
        # resize to dimensions of internal framebuffer
        image = cv2.resize(image, (636, 524))
        # swap to rgb
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Saves the frames
        rgba_frames.append(image)
        count += 1
    
    x_data, y_data = merge_and_format_data(input_frames, rgba_frames, maximum)
    # Split the dataset into training and validation sets
    split = int(0.8 * len(x_data))
    x_train, x_val = x_data[:split], x_data[split:]
    y_train, y_val = y_data[:split], y_data[split:]
    return x_train, y_train, x_val, y_val

generate_dataset("Game_20210715T231546")