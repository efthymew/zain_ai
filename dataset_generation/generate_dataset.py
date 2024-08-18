""" for each file in slippi files, run it and output an avi file
        for each avi file convert to rgb numpy array of frames and match each frame with frame of slippi file inputs for each
        skip every 12 frames to keep it relatively realistic in reacting
"""
import os
import numpy as np

import melee
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
        buttons[5] = is_flag_set(physical_buttons, Buttons.Physical.L)
        buttons[6] = is_flag_set(physical_buttons, Buttons.Physical.R)
        buttons[7] = is_flag_set(physical_buttons, Buttons.Physical.START)
        buttons[8] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_UP)
        buttons[9] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_DOWN)
        buttons[10] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_LEFT)
        buttons[11] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_RIGHT)
        buttons[12] = controller_data.joystick.x
        buttons[13] = controller_data.joystick.y
        buttons[14] = controller_data.cstick.x
        buttons[15] = controller_data.cstick.y
        buttons[16] = controller_data.triggers.physical.l
        buttons[17] = controller_data.triggers.physical.r
        inputs.append(buttons)

    return inputs

def generate_player_data(port, player: melee.PlayerState):
    data = []
    data.append(port)
    # action, action frame, character, 
    # invulnerability, jumps left, off_stage, on_ground, x, y, percent, shield_strength, stock, action, action_frame
    # hitstun + hitlag
    data.extend(
        [
            int(player.invulnerable),
            player.jumps_left,
            int(player.off_stage),
            int(player.on_ground),
            player.shield_strength,
            player.x,
            player.y,
            player.percent,
            player.stock,
            int(player.action.value),
            int(player.action_frame),
            player.hitstun_frames_left,
            player.hitlag_left
        ]
    )
    return data


def gamestate_to_model_input(gamestate: melee.GameState):
    
    data = []
    # values to gather from gamestate itself
    # frame and stage
    data.append(gamestate.frame)
    data.append(int(gamestate.stage.value))

    # get player data
    # player 1 then 2 irrespective of port, include port no. in data, it matters for combos
    for port, player in gamestate.players.items():
        data.extend(generate_player_data(port, player))
    return data

def filter_inputs_to_frame_windows(input_frames, frame_skip=10):
    # gather every 10 frames of pixel data
    # map pixel data of past 10 frames to next 10 frames of actions
    length = len(input_frames)
    y_data = []
    for index in range(frame_skip, length - frame_skip + 1, frame_skip):
        # dependent variable add
        # next 10 frames of action
        next_inputs = np.array(input_frames[index:index + frame_skip], dtype=np.float32)
        y_data.append(next_inputs)
    return np.array(y_data)

def get_frame_data(console: melee.Console, length, frame_skip=10):
    console.connect()
    count = 0
    data = []
    curr_stream = []
    while True:
        gamestate = console.step()
        # step() returns None when the file ends
        if gamestate is None:
            break
        curr_stream.append(gamestate_to_model_input(gamestate))
        count += 1
        if count >= length - frame_skip + 1:
            break
        if not count % 10:
            data.append(curr_stream)
            # flush stream
            curr_stream = []

    return np.array(data, dtype=np.float32)
    
def get_input_data(game: slippi.Game, frame_skip=10):
    zain_port = get_zain_port(game)
    inputs = get_slippi_inputs(game.frames, zain_port)

    return np.array(filter_inputs_to_frame_windows(inputs), dtype=np.float32)

def generate_dataset_for_file(slippi_file_name, frame_skip=10):
    # convert to game obj
    game = slippi.Game(slippi_file_name)
    console = melee.Console(path=slippi_file_name, system="file", allow_old_version=True)
    length = len(game.frames)

    
    x_data = get_frame_data(console, length, frame_skip)
    y_data = get_input_data(game, frame_skip)

    return x_data, y_data

def generate_full_dataset(filepath_root=r"F:\Documents\python_projects\zain_ai\dataset_generation", frame_skip=10):
    count = 0
    
    for subdir, dirs, files in os.walk(filepath_root + "\\zain_games"):
        for file in files:
            x_train, y_train = generate_dataset_for_file(os.path.join(subdir, file), frame_skip)
            np.savez(f"{filepath_root}\\training_data\\game{count}_training_data", x=x_train, y=y_train)
            print(f"saved: game{count}")
            count += 1