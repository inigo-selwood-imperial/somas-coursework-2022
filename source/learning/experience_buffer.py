import numpy as np
import tensorflow as tf


class ExperienceBuffer:

    def __init__(self,
            action_count: int,
            state_count: int,
            capacity: int = int(5e5)):
        
        self.capacity = capacity

        self.pointer = 0

        self.state_memory = np.zeros((capacity, state_count))
        self.action_memory = np.zeros((capacity, action_count))
        self.reward_memory = np.zeros((capacity, 1))
        self.new_state_memory = np.zeros((capacity, state_count))
    
    def record(self,
            state: np.ndarray,
            action: np.ndarray,
            reward: int,
            new_state: np.ndarray):
        
        index = self.pointer % self.capacity

        assert not np.isnan(state).any()
        assert not np.isnan(action).any()
        assert not np.isnan(new_state).any()

        self.state_memory[index] = state
        self.action_memory[index] = action
        self.reward_memory[index] = reward
        self.new_state_memory[index] = new_state

        self.pointer += 1
    
    def sample(self, batch_size: int) -> tuple:
        range = min(self.pointer, self.capacity)
        indices = np.random.choice(range, batch_size)

        states = tf.convert_to_tensor(self.state_memory[indices])
        actions = tf.convert_to_tensor(self.action_memory[indices])
        new_states = tf.convert_to_tensor(self.new_state_memory[indices])

        rewards = tf.convert_to_tensor(self.reward_memory[indices])
        rewards = tf.cast(rewards, dtype=tf.float32)

        return states, actions, rewards, new_states