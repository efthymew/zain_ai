"""input data is 3 x 29 3 frames of data structured like this:

    [
        int(gamestate.stage.value,
        int(port),
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
        player.hitlag_left,
        int(port),
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

    output is three layers
    3 x 12 for buttons
    [
        is_flag_set(physical_buttons, Buttons.Physical.A),
        is_flag_set(physical_buttons, Buttons.Physical.B),
        is_flag_set(physical_buttons, Buttons.Physical.X),
        is_flag_set(physical_buttons, Buttons.Physical.Y),
        is_flag_set(physical_buttons, Buttons.Physical.Z),
        is_flag_set(physical_buttons, Buttons.Physical.L),
        is_flag_set(physical_buttons, Buttons.Physical.R),
        is_flag_set(physical_buttons, Buttons.Physical.START),
        is_flag_set(physical_buttons, Buttons.Physical.DPAD_UP),
        is_flag_set(physical_buttons, Buttons.Physical.DPAD_DOWN),
        is_flag_set(physical_buttons, Buttons.Physical.DPAD_LEFT),
        is_flag_set(physical_buttons, Buttons.Physical.DPAD_RIGHT)
    ]
    3 x 4 for sticks
    [
        controller_data.joystick.x,
        controller_data.joystick.y,
        ontroller_data.cstick.x,
        controller_data.cstick.y
    ]
    3 x 2 for triggers
    [
        controller_data.triggers.physical.l,
        controller_data.triggers.physical.r
    ]
""" 

from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, LSTM, Dense, TimeDistributed, Flatten
from tensorflow.keras.optimizers import Adam


def get_model(timesteps=3, dimensions=820):
    # Define the input layer
    inputs = Input(batch_shape=(1, timesteps, dimensions))

    optimizer = Adam(learning_rate=0.00001)

    # dense up initial processing
    x = Dense(units=256, activation='relu')(inputs)
    x = Dense(units=256, activation='relu')(x)
    x = Dense(units=128, activation='relu')(x)

    # Shared layers
    x = LSTM(64, stateful=True, return_sequences=True)(x)

    # Third output (e.g., button presses)
    button_output = Dense(12, activation='sigmoid', name='buttons')(x)

    # First output (e.g., joystick values)
    joystick_output = Dense(4, activation='linear', name='sticks')(x)

    # Second output (e.g., trigger values)
    trigger_output = Dense(2, activation='linear', name='triggers')(x)

    
    model = Model(inputs=inputs, outputs=[button_output, joystick_output, trigger_output])

    # Compile the model
    model.compile(
        optimizer=optimizer,
        loss={
            'sticks': 'mean_squared_error',
            'triggers': 'mean_squared_error',
            'buttons': 'binary_crossentropy'
        },
        metrics={
            'sticks': 'mse',
            'triggers': 'mse',
            'buttons': 'accuracy'
        }
    )
    return model

def get_model_from_file(filepath):
    return load_model(filepath)