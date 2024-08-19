""" for each file in slippi files, run it and output an avi file
        for each avi file convert to rgb numpy array of frames and match each frame with frame of slippi file inputs for each
        skip every 12 frames to keep it relatively realistic in reacting
"""
import os
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
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

# encoders for enums
action_encoder = OneHotEncoder(categories=[[str(e.value) for e in melee.Action]], sparse_output=False)
action_encoder.fit(np.array([str(e.value) for e in melee.Action]).reshape(-1, 1))

stage_encoder = OneHotEncoder(categories=[[str(e.value) for e in melee.Stage]], sparse_output=False)
stage_encoder.fit(np.array([str(e.value) for e in melee.Stage]).reshape(-1, 1))

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
    button_inputs = []
    stick_inputs = []
    trigger_inputs = []

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

        button_inputs.append(buttons[:12])
        stick_inputs.append(buttons[12:16])
        trigger_inputs.append(buttons[16:])

    return button_inputs, stick_inputs, trigger_inputs


def normalize_game_data(data):

    # ranges of values needed for normalization
    number_of_stocks = 4
    number_of_ports = 4
    max_shield_strength = 60
    max_percent = 1000
    min_x_stage = -255.0
    max_x_stage = 255.0
    min_y_stage = -140.0
    max_y_stage = 250.0

    # encode stage
    encoded_stage = stage_encoder.transform(np.array([str(int(data[0]))]).reshape(-1, 1))[0].tolist()
    # encode actions
    encoded_marth_action = action_encoder.transform(np.array([str(int(data[11]))]).reshape(-1, 1))[0].tolist()
    encoded_opp_action = action_encoder.transform(np.array([str(int(data[22]))]).reshape(-1, 1))[0].tolist()

    # ports
    data[1] = (data[1] - 1) / 3
    data[12] = (data[12] - 1) / 3
    # stocks
    data[10] = (data[10] - 1) / 3
    data[21] = (data[21] - 1) / 3
    # shield
    data[6] = (data[6]) / 60
    data[17] = (data[17]) / 60

    # percent
    data[9] = (data[9]) / 1000
    data[20] = (data[20]) / 1000

    # position
    data[7] = (data[7] - min_x_stage) / (max_x_stage - min_x_stage)
    data[8] = (data[8] - min_y_stage) / (max_y_stage - min_y_stage)
    data[18] = (data[18] - min_x_stage) / (max_x_stage - min_x_stage)
    data[19] = (data[19] - min_y_stage) / (max_y_stage - min_y_stage)

    # add stage
    data = encoded_stage + data[1:]

    # add marth action
    data = data[:18] + encoded_marth_action + data[19:]

    # add opp action
    data = data[:-1] + encoded_opp_action

    data = np.array(data, dtype=np.float32)
    data = data.flatten()
    return data



def generate_player_data(port, player: melee.PlayerState):
    data = []
    data.append(port)
    # action, action frame, character, 
    # invulnerability, jumps left, off_stage, on_ground, x, y, percent, shield_strength, stock, action, action_frame
    # hitstun + hitlag
    jumps = 1 if player.jumps_left >= 1 else 0

    data.extend(
        [
            int(player.invulnerable),
            jumps,
            int(player.off_stage),
            int(player.on_ground),
            player.shield_strength,
            player.position.x,
            player.position.y,
            player.percent,
            player.stock,
            int(player.action.value)
        ]
    )
    return data

def gamestate_to_model_input(gamestate: melee.GameState, zain_port):
    
    zain_port += 1 ## zero indexedw when passed
    data = []

    data.append(int(gamestate.stage.value))
    # values to gather from gamestate itself
    # get player data, marth first other player second
    # player 1 then 2 irrespective of port, include port no. in data, it matters for combos
    zain_state = None
    other_player_state = None

    for port, player in gamestate.players.items():
        if port == zain_port:
            zain_state = generate_player_data(port, player)
        else:
            other_player_state = generate_player_data(port, player)
    if not zain_state or not other_player_state:
        raise Exception("Failure parsing gamestates")
    data.extend(zain_state)
    data.extend(other_player_state)
    return normalize_game_data(data)

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

def get_frame_data(console: melee.Console, zain_port, length, frame_skip=10):
    console.connect()
    count = 0
    data = []
    curr_stream = []
    while True:
        gamestate = console.step()
        # step() returns None when the file ends
        if gamestate is None:
            break
        curr_stream.append(gamestate_to_model_input(gamestate, zain_port))
        count += 1
        if count >= length - frame_skip + 1:
            break
        if not count % frame_skip:
            data.append(curr_stream)
            # flush stream
            curr_stream = []

    return np.array(data, dtype=np.float32)
    
def get_input_data(game: slippi.Game, zain_port, frame_skip=10):
    buttons, sticks, triggers = get_slippi_inputs(game.frames, zain_port)

    np_buttons = filter_inputs_to_frame_windows(buttons, frame_skip)
    np_sticks = filter_inputs_to_frame_windows(sticks, frame_skip)
    np_triggers = filter_inputs_to_frame_windows(triggers, frame_skip)

    return np_buttons, np_sticks, np_triggers

def generate_dataset_for_file(slippi_file_name, frame_skip=10):
    # convert to game obj
    game = slippi.Game(slippi_file_name)
    console = melee.Console(path=slippi_file_name, system="file", allow_old_version=True)
    length = len(game.frames)

    zain_port = get_zain_port(game)
    
    x_data = get_frame_data(console, zain_port, length, frame_skip)
    y_data_button, y_data_sticks, y_data_triggers = get_input_data(game, zain_port, frame_skip)

    return x_data, y_data_button, y_data_sticks, y_data_triggers

def generate_full_dataset(filepath_root=r"F:\Documents\python_projects\zain_ai\dataset_generation", frame_skip=10):
    count = 0
    for subdir, dirs, files in os.walk(filepath_root + "\\zain_games"):
        for file in files[:-4]:
            x_train, y_train_button, y_train_sticks, y_train_triggers = generate_dataset_for_file(os.path.join(subdir, file), frame_skip)
            np.savez(f"{filepath_root}\\training_data\\game{count}_training_data", x=x_train, y_button=y_train_button, y_sticks=y_train_sticks, y_triggers=y_train_triggers)
            print(f"saved: game{count}")
            count += 1
        for file in files[-4:-1]:
            x_val, y_val_button, y_val_sticks, y_val_triggers = generate_dataset_for_file(os.path.join(subdir, file), frame_skip)
            np.savez(f"{filepath_root}\\val_data\\game{count}_training_data", x=x_val, y_button=y_val_button, y_sticks=y_val_sticks, y_triggers=y_val_triggers)
            print(f"saved: game{count} validation")
            count += 1
        
        test = files[-1]
        x_test, y_test_button, y_test_sticks, y_test_triggers = generate_dataset_for_file(os.path.join(subdir, test), frame_skip)
        np.savez(f"{filepath_root}\\test_data\\game{count}_training_data", x=x_test, y_button=y_test_button, y_sticks=y_test_sticks, y_triggers=y_test_triggers)
        print(f"saved: game{count} test")


if __name__ == "__main__":
    generate_full_dataset(frame_skip=3)