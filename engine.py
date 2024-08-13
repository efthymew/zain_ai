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

from dolphin import event, controller

frame_buffer = []
count = 0

input_buffer = []

dummy_action = [0.0 for i in range(18)]
dummy_action[5] = 1.0

def array_to_gc_input(array):
    gc_input: controller.GCInputs = {
        "A": bool(array[0]),
        "B": bool(array[1]),
        "X": bool(array[2]),
        "Y": bool(array[3]),
        "Z": bool(array[4]),
        "Start": bool(array[5]),
        "Up": bool(array[6]),
        "Down": bool(array[7]),
        "Left": bool(array[8]),
        "Right": bool(array[9]),
        "L": bool(array[10]),
        "R": bool(array[11]),
        "StickX": array[12],
        "StickY": array[13],
        "CStickX": array[14],
        "CStickY": array[15],
        "TriggerLeft": array[16],
        "TriggerRight": array[17]
    }
    return gc_input

def get_frame(width: int, height: int, data: bytes):
    global count, input_buffer, frame_buffer

    if count == 10:
        print("10 frames collected, filling input buffer")
        # model predict
        input_buffer = [array_to_gc_input(dummy_action) for i in range(10)]
        # flush frames
        frame_buffer = []
        count = 0

    # format data for processing
    frame_buffer.append(data)
    count += 1
    if input_buffer:
        print("Sending input from buffer")
        controller.set_gc_buttons(3, input_buffer[0])
        input_buffer.pop(0)

event.on_framedrawn(get_frame)