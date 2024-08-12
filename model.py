import numpy as np
import tensorflow as tf
from keras import Sequential

def create_model(input_shape, num_classes):
    model = tf.keras.Sequential()
    
    model.add(tf.keras.layers.ConvLSTM2D(filters=32, kernel_size=(3, 3), padding='same', 
                                         input_shape=input_shape, return_sequences=True))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation('relu'))
    
    model.add(tf.keras.layers.ConvLSTM2D(filters=64, kernel_size=(3, 3), padding='same', 
                                         return_sequences=True))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation('relu'))
    
    model.add(tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), padding='same'))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation('relu'))
    
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(128, activation='relu'))
    model.add(tf.keras.layers.Dense(num_classes, activation='softmax'))
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    return model


create_model((10, 10), 4)