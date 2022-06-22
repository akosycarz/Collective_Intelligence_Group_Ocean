from enum import Enum, auto
from matplotlib import image

import pygame as pg
from pygame.math import Vector2
from sklearn import neighbors
from vi import Agent, Simulation, obstacle
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 5
    cohesion_weight: float = 6
    separation_weight: float = 6
    delta_time: float = 3
    mass: int = 30
    maxVelocity: int = 2
    mode: str = "outside obstacle"
    start = True

    def weights(self) -> tuple[float , float , float]:
        return (self.alignment_weight , self.cohesion_weight , self.separation_weight)
    ...


class Bird(Agent):
    config: FlockingConfig

    def on_spawn(self):
        # We choose a random starting position that is or is not inside the 
        # obstacle depending on mode
        prng = self.shared.prng_move
        if self.config.mode == "outside obstacle":
            x = prng.uniform(286, 750)
            y = prng.uniform(286, 750)
            self.pos = Vector2((x, y))
        elif self.config.mode == "inside obstacle":
            x = prng.uniform(87, 286)
            y = prng.uniform(87, 286)
            self.pos = Vector2((x, y))
        

    def update(self):
        neighbours = list(self.in_proximity_accuracy())
        #intersections = self.obstacle_intersections(scale=2)
        # For an intersection, check which side it is and then make sure the boids go the opposite way
        # Obstacle Avoidance
        """obstacle_hit = pg.sprite.spritecollideany(self, self._obstacles, pg.sprite.collide_mask)  # type: ignore
        collision = bool(obstacle_hit)

        # Reverse direction when colliding with an obstacle.
        if collision & self._still_stuck:
            self.move.rotate_ip(180)
            self._still_stuck = True

        if not collision:
            self._still_stuck = True

        # Actually update the position at last.
        self.pos += self.move"""

        """for i in intersections:
            print(self.id)
            print(i)
        if self.:
            self.move.rotate_ip(180)
            self.pos += self.move"""
        self.collide = True
        # Try if intersects with obstacle, turn around & the same for neighbours
        if self.obstacle_intersections(scale=1):
            if (self.pos.x > 85) & (self.pos.x < 295) & (self.pos.y > 85) & (self.pos.y < 295) & self.collide:
                self.move.rotate_ip(180)
                self.pos += self.move
                self.collide = True
                for i, _ in neighbours:
                    i.move = self.move
        else:
            self.collide = False
            
        
    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        #YOUR CODE HERE -----------
        # Get the neighbours of the boid
        neighbours = list(self.in_proximity_accuracy())
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
            f_total = (self.config.alignment_weight*alignment + self.config.separation_weight*separation + self.config.cohesion_weight*cohesion)/self.config.mass
            self.move = self.move + f_total
            # Normalize velocity
            if Vector2.length(self.move) > self.config.maxVelocity:
                self.move = self.move.normalize() * self.config.maxVelocity
            # Change position
            self.pos = self.pos + (self.move * self.config.delta_time)
        #END CODE -----------------

    def alignment(self, neighbours):
        average = [0, 0]
        for i, d in neighbours:
            average += i.move
        average /= len(neighbours)
        alignment = (average.normalize() * self.config.maxVelocity) - self.move
        return alignment
    
    def separation(self, neighbours):
        distances = [0, 0]
        for i, d in neighbours:
            distances += (self.pos - i.pos)/d
        separation = distances / len(neighbours)
        return separation.normalize() * self.config.maxVelocity
    
    def cohesion(self, neighbours):
        positions = [0, 0]
        for i, d in neighbours:
            positions += i.pos
        fc = (positions / len(neighbours)) - self.pos
        cohesion = fc.normalize() * self.config.maxVelocity
        return cohesion - self.move
        

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
            radius=100,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Bird, images=["images/bird.png"])
    .spawn_obstacle("images/bubble-full.png", x // 4, y //4)
    .run()
)



