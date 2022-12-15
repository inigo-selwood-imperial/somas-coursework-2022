import numpy as np


class OrnsteinUhlenbeckNoise:
    """ To implement exploration of the actor network, we use noise
    perturbations; this process samples noise from a correlated normal
    distribution """

    def __init__(self,
            mean: int = 0,
            deviation: int = 0.2,
            shape: tuple = (1),
            theta: float = 0.15,
            time_step: float = 1e-2,
            initial_value: float = None):
        
        self.mean = np.ones(shape) * mean
        self.deviation = np.ones(shape) * deviation

        self.theta = theta
        self.time_step = time_step
        self.initial_value = initial_value

        self.previous_value = None
        self.reset()

    def __call__(self):
        value = (self.previous_value
            + self.theta * (self.mean - self.previous_value) * self.time_step
            + self.deviation 
                * np.sqrt(self.time_step) 
                * np.random.normal(size=self.mean.shape))
        
        self.previous_value = value
        return value
    
    def reset(self):
        if self.initial_value is not None:
            self.previous_value = self.initial_value
        else:
            self.previous_value = np.zeros_like(self.mean)