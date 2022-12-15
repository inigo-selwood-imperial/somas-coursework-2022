import tensorflow as tf

from tensorflow import keras


class Critic:

    def __init__(self, state_count: int, action_count: int):
        state_input = keras.layers.Input(shape=(state_count, ))
        layer = keras.layers.Dense(16, activation="relu")(state_input)
        state_output = keras.layers.Dense(32, activation="relu")(layer)

        action_input = keras.layers.Input(shape=(action_count, ))
        action_output = keras.layers.Dense(32, activation="relu")(action_input)

        merge = keras.layers.Concatenate()([state_output, action_output])
        layer = keras.layers.Dense(16, activation="relu")(merge)
        layer = keras.layers.Dense(16, activation="relu")(layer)
        outputs = keras.layers.Dense(1)(layer)

        self.model = keras.Model([state_input, action_input], outputs)