from enum import Enum, auto
from turtle import window_height
from matplotlib import image

import pygame as pg
from pygame.math import Vector2
from sklearn import metrics, neighbors
from vi import Agent, Simulation, util
from vi.config import Config, dataclass, deserialize

@deserialize
@dataclass
class AggregationConfig(Config):
    # Add all parameters here
    random_walk_time: int = 20
    constant_a: float = None
    constant_b: float = None
    state: str = 'wandering'

    def weights(self) -> tuple[float]:
        return (self.random_walk_time)
    ...


class Cockroach(Agent):
    config: AggregationConfig

    def on_spawn(self):
        # Used if we want to override some init parameters
        # We choose a random starting position that is not inside the site
        prng = self.shared.prng_move
        # Change the values
        x = prng.uniform(286, 750)
        y = prng.uniform(286, 750)
        self.pos = Vector2((x, y))

    def update(self):
        neighbours = self.in_proximity_performance()
        if self.on_site():
            self.freeze_movement()
            
        
    """def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()"""
    
    def join(self, neighbours):
        # Calculate the joining probability using the number of neighbours
        probability = None
        # WHAT FUNCTION HERE
        # Return True if join the aggregate, else return False
        if self.on_site() & util.probability(probability):
            return True
        else:
            return False

    def leave(self, neighbours):
        # Calculate the leaving probability
        # If there are many neighbours, leave less likely
        probability = None
        # WHAT FUNCTION HERE
        # Return True if leave the aggregate, else return False
        if util.probability(probability):
            return True
        else:
            return False

config = Config()
n = 50
config.window.height = n*(4**2)
config.window.width = n*(4**2)
x, y = config.window.as_tuple()

(
    Simulation(
        AggregationConfig(
            image_rotation=True,
            movement_speed=1,
            radius=100,
            seed=1,
        )
    )
    .batch_spawn_agents(n, Cockroach, images=["images/white.png"])
    .spawn_site("images/bubble-full.png", x//2, y//2)
    .run()
)



