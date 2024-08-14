from model import get_model
from dataset_generation.generate_dataset import generate_dataset
from dataset_generation.generate_menu_dataset import generate_menu_dataset
from keras.api.callbacks import Callback
import logging
import numpy as np
class ResetStatesCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        self.model.reset_states()


print("get model")
model = get_model()

x_train, y_train, x_val, y_val = generate_dataset("Game_20210715T231546")
x_train_menu, y_train_menu = generate_menu_dataset("MELEE_MENU")
x_train = np.concatenate(x_train_menu, x_train) # add menu training data to start of each training set 
y_train = np.concatenate(y_train_menu, y_train) # add menu training data to start of each training set 
print("gathered training data, beginning training")
# Add the callback when training
model.fit(
    x_train,
    y_train,
    epochs=11,
    batch_size=1,
    validation_data=(x_val, y_val),
    shuffle=False,
    callbacks=[ResetStatesCallback()]
)
print("finished training, saving model")
# Save the entire model to a file
model.save('zain.h5')