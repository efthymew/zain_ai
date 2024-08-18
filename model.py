""" architecture for the neural network of the bot. input should be 10 x m x n where m and n are the dimensions of the image to use
    and the output is 10 x 18 where it is a sequence of the next 10 frames of actions formatted like this:
    output[0:9][0] = is_flag_set(physical_buttons, Buttons.Physical.A)
    output[0:9][1] = is_flag_set(physical_buttons, Buttons.Physical.B)
    output[0:9][2] = is_flag_set(physical_buttons, Buttons.Physical.X)
    output[0:9][3] = is_flag_set(physical_buttons, Buttons.Physical.Y)
    output[0:9][4] = is_flag_set(physical_buttons, Buttons.Physical.Z)
    output[0:9][5] = is_flag_set(physical_buttons, Buttons.Physical.START)
    output[0:9][6] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_UP)
    output[0:9][7] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_DOWN)
    output[0:9][8] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_LEFT)
    output[0:9][9] = is_flag_set(physical_buttons, Buttons.Physical.DPAD_RIGHT)
    output[0:9][10] = is_flag_set(physical_buttons, Buttons.Physical.L)
    output[0:9][11] = is_flag_set(physical_buttons, Buttons.Physical.R)
    output[0:9][12] = controller_data.joystick.x
    output[0:9][13] = controller_data.joystick.y
    output[0:9][14] = controller_data.cstick.x
    output[0:9][15] = controller_data.cstick.y
    output[0:9][16] = controller_data.triggers.physical.l
    output[0:9][17] = controller_data.triggers.physical.r
"""

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, LSTM, Dense, TimeDistributed, Flatten

from keras.src.legacy.saving import legacy_h5_format


def get_model():
    model = Sequential()
    
    # Input shape (1, 10, 262, 318, 3)
    model.add(Input(batch_shape=(1, 10, 30)))

    # early dense layer before lstm
    model.add(Dense(units=18))
    
    # LSTM layer
    model.add(LSTM(units=128, stateful=True, return_sequences=True))
    
    # Final Dense layer for output
    model.add(Dense(units=18))
    
    # Compile the model
    model.compile(optimizer='adam', loss='mse')

    return model

def get_model_from_file(filepath):
    return legacy_h5_format.load_model_from_hdf5(filepath, custom_objects={'mse': 'mse'})