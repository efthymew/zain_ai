from model import get_model, get_model_from_file
import os
import tensorflow as tf
from keras.api.callbacks import Callback
from tensorflow.keras.layers import LSTM
import logging
import numpy as np
class ResetStatesCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        self.model.layers[self.lstm_index].reset_states()


def generate_validation_data(filepath_to_dataset=r"F:\Documents\python_projects\zain_ai\dataset_generation\val_data"):
    validation_set = []

    for subdir, dirs, files in os.walk(filepath_to_dataset):
        for file in files:
            val_data = np.load(os.path.join(subdir, file))
            x_val = val_data["x"]
            y_button_val = val_data["y_button"]
            y_stick_val = val_data["y_sticks"]
            y_trigger_val = val_data["y_triggers"]
            validation_set.append((x_val, y_button_val, y_stick_val, y_trigger_val))

    return validation_set


def generate_test_data(filepath_to_testgame=r"F:\Documents\python_projects\zain_ai\dataset_generation\test_data\game44_training_data.npz"):

    test_data = np.load(filepath_to_testgame)
    x_test = test_data["x"]
    y_button_test = test_data["y_button"]
    y_stick_test = test_data["y_sticks"]
    y_trigger_test = test_data["y_triggers"]

    return x_test, y_button_test, y_stick_test, y_trigger_test

def train_model(model, filepath_to_dataset=r"F:\Documents\python_projects\zain_ai\dataset_generation\training_data"):

    # find lstm layer for state resetting
    for i, layer in enumerate(model.layers):
        if isinstance(layer, LSTM):
            lstm_index = i
    
    callback = ResetStatesCallback()
    callback.lstm_index = lstm_index


    validation_set = generate_validation_data()

    count = 0
    for subdir, dirs, files in os.walk(filepath_to_dataset):
        for file in files:
            training_data = np.load(os.path.join(subdir, file))
            # train on this file, then reset states
            x_train = training_data['x']
            y_button_train = training_data["y_button"]
            y_stick_train = training_data["y_sticks"]
            y_trigger_train = training_data["y_triggers"]

            x_val, y_button_val, y_stick_val, y_trigger_val = validation_set[count]

            # train 5 epochs per game validated on a test game
            # resetting state after each run

            model.fit(
                x=x_train,
                y={
                    "buttons": y_button_train,
                    "sticks": y_stick_train,
                    "triggers":  y_trigger_train
                    
                },
                epochs=5,
                batch_size=1,
                validation_data=(x_val, {
                    "buttons": y_button_val,
                    "sticks": y_stick_val,
                    "triggers":  y_trigger_val
                    
                })
            )
            count = (count + 1) % len(validation_set)

    # x_test, y_button_test, y_stick_test, y_trigger_test = generate_test_data()
    # # Evaluate the model
    # loss, acc = model.evaluate(x_test, {
    #     "buttons": y_button_test,
    #     "sticks": y_stick_test,
    #     "triggers":  y_trigger_test
    # }, verbose=2)
    # print("Restored model, accuracy: {:5.2f}%".format(100 * acc))
    model.layers[lstm_index].reset_states()
    model.save('zain.keras')

if __name__ == "__main__":
    print("get model")
    # Create a MirroredStrategy.
    strategy = tf.distribute.MirroredStrategy()
    print('Number of devices: {}'.format(strategy.num_replicas_in_sync))
    # Open a strategy scope.
    with strategy.scope():
        model = get_model(10, 28)
    model.summary()

    train_model(model)