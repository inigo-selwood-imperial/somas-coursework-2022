import tensorflow as tf

from tensorflow import keras


class Actor:

    def __init__(self, state_count: int, action_count: int):
        inputs = keras.layers.Input(shape=(state_count, ))

        layer = keras.layers.Dense(48, activation="relu")(inputs)
        layer = keras.layers.Dense(24, activation="relu")(layer)
        
        initial_weights = tf.random_uniform_initializer(minval=-0.003, maxval=0.003)
        outputs = keras.layers.Dense(action_count, 
                activation="tanh", 
                kernel_initializer=initial_weights)(layer)
        
        self.model = keras.Model(inputs, outputs)