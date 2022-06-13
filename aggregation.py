from enum import Enum, auto
from matplotlib import image

import pygame as pg
from pygame.math import Vector2
from sklearn import neighbors
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize

@deserialize
@dataclass
class AggregationConfig(Config):
    # Add all parameters here
    random_walk_time: int = 20

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
        # If we detect an aggregation site, we join the aggregation
        if self.on_site():
            self.freeze_movement()
            
        
    """def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()"""

config = Config()
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
    .batch_spawn_agents(50, Cockroach, images=["images/white.png"])
    .spawn_site("images/bubble-full.png", x//2, y//2)
    .run()
)



