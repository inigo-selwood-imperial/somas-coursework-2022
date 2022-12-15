import tensorflow as tf
import numpy as np

from tensorflow import keras

from game.action import Action
from game.state import State

from game.actors.peasant import Peasant

from learning.actor import Actor
from learning.critic import Critic
from learning.ornstein_uhlenbeck_noise import OrnsteinUhlenbeckNoise
from learning.experience_buffer import ExperienceBuffer


class DDPGPeasant(Peasant):

    def __init__(self, 
            level: float,
            batch_size: int = 32,
            memory_capacity: int = int(5e5),
            actor_alpha: float = 0.002,
            critic_alpha: float = 0.001,
            rebalance_tau: float = 0.005,
            discount_gamma: float = 0.99,
            noise_deviation: float = 0.2):
        
        stamina = level * np.random.uniform(0.25, 0.75)
        health = level - stamina

        attack = level * np.random.uniform(0.25, 0.75)
        defence = level - attack
    
        super().__init__(stamina, health, attack, defence)
        
        # DDPG stuff
        state_count = 9
        action_count = 2

        self.actor = Actor(state_count, action_count)
        self.critic = Critic(state_count, action_count)

        self.target_actor = Actor(state_count, action_count)
        self.target_critic = Critic(state_count, action_count)

        self.target_actor.model.set_weights(self.actor.model.get_weights())
        self.target_critic.model.set_weights(self.critic.model.get_weights())

        self.actor_optimizer = \
                keras.optimizers.Adam(learning_rate=actor_alpha)
        self.critic_optimizer = \
                keras.optimizers.Adam(learning_rate=critic_alpha)
        
        self.buffer = ExperienceBuffer(action_count, state_count)
        self.batch_size = batch_size
        
        self.noise_generator = \
                OrnsteinUhlenbeckNoise(deviation=noise_deviation)

        self.tau = rebalance_tau
        self.gamma = discount_gamma

        self.previous_state = None
        self.previous_action = None

        self.previous_stamina = stamina
        self.previous_health = health
        self.previous_round = 0

        self.reward_total = 0
    
    def create_state_tensor(self, state: State) -> tf.Tensor:
        """ Transforms a state object into a trainable tensor """

        combatant_count = len(state.combatants)
        abstainer_count = len(state.abstainers)
        peasant_count = len(state.cohort.peasants)

        result = [
            state.action.attack / state.monster.health,
            state.action.defence / state.monster.attack,

            combatant_count / peasant_count,
            abstainer_count / peasant_count,
            (combatant_count + abstainer_count) / peasant_count,

            self.stamina,
            self.health,
            self.attack,
            self.defence,
        ]
        
        result = tf.expand_dims(tf.convert_to_tensor(result), 0)
        return result
    
    def create_action_object(self, tensor: np.ndarray) -> Action:
        return Action(0, 0)
    
    @tf.function
    def update(self,
            states: tf.Tensor,
            actions: tf.Tensor,
            rewards: tf.Tensor,
            new_states: tf.Tensor):
        
        """ TensorFlow wrapped gradient update function """

        # Train critic
        with tf.GradientTape() as tape:
            target_actions = self.target_actor.model(new_states, 
                    training=True)

            target_critic_inputs = [new_states, target_actions]
            target_critic_values = (rewards + self.gamma 
                    * self.target_critic.model(target_critic_inputs, 
                        training=True))
                
            critic_inputs = [states, actions]
            critic_values = self.critic.model(critic_inputs, training=True)
            
            values_mean = tf.math.square(target_critic_values - critic_values)
            critic_loss = tf.math.reduce_mean(values_mean)

        # Apply critic gradients
        critic_gradients = tape.gradient(critic_loss, 
                self.critic.model.trainable_variables)
        critic_gradients = zip(critic_gradients, 
                self.critic.model.trainable_variables)
        self.critic_optimizer.apply_gradients(critic_gradients)

        # Train actor
        with tf.GradientTape() as tape:
            actions = self.actor.model(states, training=True)
            critic_inputs = [states, actions]
            critic_value = self.critic.model(critic_inputs, training=True)
            actor_loss = -tf.math.reduce_mean(critic_value)

        # Apply actor gradients
        actor_gradients = tape.gradient(actor_loss,
                self.actor.model.trainable_variables)
        actor_gradients = zip(actor_gradients, 
                self.actor.model.trainable_variables)
        self.actor_optimizer.apply_gradients(actor_gradients)


    def update_target(self, 
            target: keras.Model, 
            source: keras.Model):
        
        """ Rebalances the target actor/critic models by a factor tau """
        
        target_weights = target.model.variables
        source_weights = source.model.variables
        iteratable = zip(target_weights, source_weights)
        
        for (target_weights, source_weights) in iteratable:
            target_weights.assign(source_weights * self.tau 
                    + target_weights * (1 - self.tau))

    def action(self, state: State) -> Action:
        state_tensor = self.create_state_tensor(state)

        # Sample action, with noise
        samples = tf.squeeze(self.actor.model(state_tensor)).numpy() 
        samples += self.noise_generator()

        # Create new action object from model
        action_tensor = np.asarray([np.squeeze(np.clip(samples, 0.0, 1.0))])
        action = self.create_action_object(action_tensor)

        # Calculate reward
        reward = ((self.stamina - self.previous_stamina)
                + (self.health - self.previous_health)
                + int(state.round != self.previous_round) * 2)
        self.reward_total += reward

        # Store experience
        self.buffer.record(self.previous_state,
                self.previous_action,
                reward,
                state_tensor.numpy())

        # Train
        if self.previous_state is not None and self.buffer.pointer >= self.batch_size:

            # Learn
            states, actions, rewards, new_states = \
                    self.buffer.sample(self.batch_size)
            self.update(states, actions, rewards, new_states)
            self.update_target(self.target_actor, self.actor)
            self.update_target(self.target_critic, self.critic)

        # Track state for updating reward
        self.previous_action = action_tensor
        self.previous_state = state_tensor.numpy()

        self.previous_stamina = self.stamina
        self.previous_health = self.health
        self.previous_round = state.round

        # Return result
        return action