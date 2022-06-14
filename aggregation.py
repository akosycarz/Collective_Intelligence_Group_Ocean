from enum import Enum, auto
from matplotlib import image
import numpy as np

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation, util
from vi.config import Window, Config, dataclass, deserialize

@deserialize
@dataclass
class AggregationConfig(Config):
    # Add all parameters here
    D: int = 20
    joining_prob: float = 0.7
    leaving_prob: float = 0.01
    t: int = 10

    def weights(self) -> tuple[float]:
        return (self)
    ...


class Cockroach(Agent):
    config: AggregationConfig

    def on_spawn(self):
        # All agents start at the wandering state and with counter 0
        self.state = 'wandering'
        self.counter = 0
        # Create the time constraints max_time =t_join = t_leave
        # Sample some Gaussian noise
        noise = np.random.normal()
        self.max_time = self.config.t + noise
        # Make sure no agents start at the aggregation site
        self.pos = self.choose_start_pos()
        

    def update(self):
        # The number of immediate neighbours
        neighbours = self.in_proximity_performance().count()
        if self.state == 'wandering': 
            # If detect an aggregation site, join the aggregation with given 
            # probability
            if self.join(neighbours):
                self.state = 'joining'
        elif self.state == 'joining':
            self.counter += 1
            # When the agent has joined the aggregation, change the state to still
            if self.counter > self.max_time: 
                self.freeze_movement()
                self.state = 'still'
                self.counter = 0
        elif self.state == 'still': 
            self.counter += 1
            # Leave the aggregate with given probability, but only check 
            # this every D timesteps
            if self.counter % self.config.D == 0 and self.leave(neighbours):
                self.continue_movement()
                self.counter = 0
                self.state = 'leaving'
        elif self.state == 'leaving':
            self.counter += 1
            # When the agent has left the aggregation site, change the state to wandering
            if self.counter > self.max_time: 
                self.state = 'wandering'
                self.counter = 0
            
    
    def join(self, neighbours):
        # Calculate the joining probability using the number of neighbours
        probability = self.config.joining_prob * neighbours
        # The probability function is currently random, not based on anything
        # Return True if join the aggregate, else return False
        if self.on_site() & util.probability(probability):
            return True
        else:
            return False

    def leave(self, neighbours):
        # Calculate the leaving probability
        # If there are many neighbours, leaving is less likely
        probability = self.config.leaving_prob * 0.1*neighbours
        # The probability function is currently random, not based on anything
        # Return True if leave the aggregate, else return False
        if util.probability(probability):
            return True
        else:
            return False
    
    def choose_start_pos(self):
        # Choose a random start position
        prng = self.shared.prng_move
        xw, yw = self.config.window.as_tuple()
        x = prng.uniform(0, xw)
        y = prng.uniform(0, yw)
        # If it is inside an aggregation site, repeat the choice
        if ((xw//2-110) < x < (xw//2+110)) & ((yw//2-110) < y < (yw//2+110)):
            new_pos = self.choose_start_pos()
            return new_pos
        # Else, return the position
        else:
            return Vector2((x, y))

config = Config()
n = 50
x, y = config.window.as_tuple()

(
    Simulation(
        AggregationConfig(
            image_rotation=True,
            movement_speed=1,
            radius=100,
            seed=1,
            window=Window(width=n*(4**2), height=n*(4**2)),
        )
    )
    .batch_spawn_agents(n, Cockroach, images=["images/white.png"])
    .spawn_site("images/circle.png", x//2, y//2)
    .run()
)






