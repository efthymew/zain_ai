from model import get_model
import os
import tensorflow as tf
from keras.api.callbacks import Callback
import logging
import numpy as np
class ResetStatesCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        self.model.layers[1].reset_states()


def generate_validation_data(filepath_to_dataset=r"F:\Documents\python_projects\zain_ai\dataset_generation\val_data"):
    validation_set = []

    for subdir, dirs, files in os.walk(filepath_to_dataset):
        for file in files:
            val_data = np.load(os.path.join(subdir, file))
            x_val = val_data["x"]
            y_val = val_data["y"]
            validation_set.append((x_val, y_val))

    return validation_set


def generate_test_data(filepath_to_testgame=r"F:\Documents\python_projects\zain_ai\dataset_generation\test_data\game44_training_data.npz"):

    test_data = np.load(filepath_to_testgame)
    x_test = test_data["x"]
    y_test = test_data["y"]

    return x_test, y_test

def train_model(model, filepath_to_dataset=r"F:\Documents\python_projects\zain_ai\dataset_generation\training_data"):

    validation_set = generate_validation_data()

    count = 0
    for subdir, dirs, files in os.walk(filepath_to_dataset):
        for file in files:
            training_data = np.load(os.path.join(subdir, file))
            # train on this file, then reset states
            x_train = training_data['x']
            y_train = training_data['y']
            x_val, y_val = validation_set[count]

            # train 5 epochs per game validated on a test game
            # resetting state after each run

            model.fit(
                x_train,
                y_train,
                epochs=5,
                batch_size=1,
                validation_data=(x_val, y_val),
                shuffle=False,
                callbacks=[ResetStatesCallback()]
            )
            count = (count + 1) % len(validation_set)

    x_test, y_test = generate_test_data()
    # Evaluate the model
    loss, acc = model.evaluate(x_test, y_test, verbose=2)
    print("Restored model, accuracy: {:5.2f}%".format(100 * acc))
    model.layer[1].reset_states()
    model.save('zain.keras')

if __name__ == "__main__":
    print("get model")
    # Create a MirroredStrategy.
    strategy = tf.distribute.MirroredStrategy()
    print('Number of devices: {}'.format(strategy.num_replicas_in_sync))
    # Open a strategy scope.
    with strategy.scope():
        model = get_model()
    model.summary()

    train_model(model)