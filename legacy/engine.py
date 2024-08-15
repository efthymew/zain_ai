""" this file will be the script that runs embedded in dolphin it should:
    tally frames each frame drawn and store in a buffer until on the 11th frame then send
    the past 10 frames through a model and gather the next 10 frames of actions and store them in a buffer
    that the engine pulls from and sends to dolphin over the course of the next 10 frames, then repeat

    clamp frame bytes to 318 by 262 and convert to numpy
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
"""
import sys
# add local python 3.8 installation to path, where Pillow is installed
sys.path.append("F:/Documents/python_projects/zain_ai/.venv/Lib/site-packages")
sys.path.append("F:/Documents/python_projects/zain_ai")

from dolphin import event, controller
import cv2
import numpy as np

from model import get_model_from_file

model = get_model_from_file()
print("model acquired")

frame_buffer = []
count = 0

input_buffer = None

def float_to_bool(number, prob_threshold=0.6):
    if number >= prob_threshold:
        return True
    return False

def apply_deadzone(value, threshold=0.2):
    if abs(value) < threshold:
        return 0.0
    return value

def array_to_gc_input(array):
    gc_input: controller.GCInputs = {
        "A": float_to_bool(array[0]),
        "B": float_to_bool(array[1]),
        "X": float_to_bool(array[2]),
        "Y": float_to_bool(array[3]),
        "Z": float_to_bool(array[4]),
        "Start": float_to_bool(array[5]),
        "Up": float_to_bool(array[6]),
        "Down": float_to_bool(array[7]),
        "Left": float_to_bool(array[8]),
        "Right": float_to_bool(array[9]),
        "L": float_to_bool(array[10]),
        "R": float_to_bool(array[11]),
        "StickX": apply_deadzone(array[12]),
        "StickY": apply_deadzone(array[13]),
        "CStickX": apply_deadzone(array[14]),
        "CStickY": apply_deadzone([15]),
        "TriggerLeft": apply_deadzone(array[16]),
        "TriggerRight": apply_deadzone(array[17])
    }
    return gc_input

def add_frame_to_buffer(frame):
    global frame_buffer

    # Convert byte array to numpy array and reshape
    print("running np buffer")
    image_np = np.frombuffer(frame, dtype=np.uint8)
    image_np = image_np.reshape((524, 636, 4))  # 4 channels for RGBA

    print("running cv2 conversion")
    # Convert RGBA to RGB
    image  = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
    image = cv2.resize(image, (318, 262))
    print("running append")
    frame_buffer.append(image)



def get_frame(width: int, height: int, data: bytes):
    global count, input_buffer, frame_buffer

    if count == 10:
        print("10 frames collected, filling input buffer")
        # clean frame buffer
        # model predict
        # Convert byte array to numpy array and reshape
        input_frames = np.array(frame_buffer)
        # predict and set input buffer
        input_buffer = model.predict(input_frames)
        # flush frames
        frame_buffer = []
        count = 0

    # format data for processing
    print("adding frame")
    add_frame_to_buffer(data)
    count += 1
    if input_buffer:
        print("Sending input from buffer")
        controller.set_gc_buttons(3, input_buffer[0])
        input_buffer = np.delete(input_buffer, (0), axis=0)

event.on_framedrawn(get_frame)