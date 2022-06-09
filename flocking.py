from enum import Enum, auto
from matplotlib import image

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation, obstacle
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 4.5
    cohesion_weight: float = 5
    separation_weight: float = 6
    delta_time: float = 3
    mass: int = 30
    maxVelocity: int = 5

    def weights(self) -> tuple[float , float , float]:
        return (self.alignment_weight , self.cohesion_weight , self.separation_weight)
    ...


class Bird(Agent):
    config: FlockingConfig

    def update(self):
        pass

        
    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        #YOUR CODE HERE -----------
        # Get the neighbours of the boid
        neighbours = self.in_proximity_accuracy().collect_set()
        # If the set in empty, wandering behaviour
        if len(neighbours) == 0:
            super(Bird, self).change_position()
        # Else, calculate new direction
        else:
            # Calculate alignment
            alignment = self.alignment(neighbours)
            # Calculate separation
            separation = self.separation(neighbours)
            # Calculate cohesion
            cohesion = self.cohesion(neighbours)
            # Calculate new force to update velocity
            f_total = (self.config.alignment_weight*alignment + self.config.separation_weight*separation + self.config.cohesion_weight*cohesion) / self.config.mass
            self.move = self.move + f_total
            # Normalize velocity
            if self.move[1] < self.config.maxVelocity:
                self.move.normalize() * self.config.maxVelocity
            # Change position
            self.pos = self.pos + (self.move * self.config.delta_time)
        #END CODE -----------------

    def alignment(self, neighbours):
        average = [0, 0]
        for i in neighbours:
            average += i[0].move
        
        return (average / len(neighbours)) - self.move
    
    def separation(self, neighbours):
        distances = [0, 0]
        for i in neighbours:
            distances += (self.pos - i[0].pos)
        return distances*(1/len(neighbours))
    
    def cohesion(self, neighbours):
        positions = [0, 0]
        for i in neighbours:
            positions += i[0].pos
        fc = (positions / len(neighbours)) - self.pos
        return fc - self.move
        

class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")

config = Config()
x, y = config.window.as_tuple()
(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=70,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Bird, images=["images/bird.png"])
    .spawn_obstacle("images/bubble-full.png", x // 4, y //4)
    .run()
)



