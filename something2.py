import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
from enum import Enum, auto, unique
from vi import Agent, Simulation
from vi.config import Window, Config, dataclass, deserialize
import pygame as pg
import random
from pygame.math import Vector2
import numpy as np
import math

#Plot constants
RESOLUTION = 200
Y_AXIS_MAX = 250

CHANCE_GENERATOR_MAX = 999

# rabbit Constants
RABBIT_COUNT = 5
REPRODUCTION_THRESHOLD_RABBIT = 995
RABBIT_CAPACITY = 250
RABBIT_GROWTH_RATE = 0.5
RABBIT_GROWTH_TIME = 50

#Fox constants
FOX_COUNT = 3
REPRODUCTION_THRESHOLD_FOX = 998
FOX_ENERGY = 80 #between 0 and 100. Fox dies when 0 is reached.
ENERGY_GAIN_FOX = 50
ENERGY_LOSS_FOX = 0.4
ENERGY_MAX_FOX = 100
FOX_CAPACITY = 250
FOX_GROWTH_RATE = 0.5
FOX_GROWTH_TIME = 80

# Global vars
rabbit_count = RABBIT_COUNT
reproduction_timer_rabbit = 0
reproduction_amount_rabbit = 0
reproduction_amount_rabbit_max = 0
fox_count = FOX_COUNT
reproduction_timer_fox = 0
reproduction_amount_fox = 0
reproduction_amount_fox_max = 0

rabbit_numbered = 1

site_zero_birds = 0  # how many birds settled on the west ice
site_one_birds = 0   # how many birds settled on the east ice
experiment = 1

@deserialize
@dataclass
class AggregationConfig(Config):
    # Add all parameters here
    agents: int = 0
    reproduce: bool = True
    rabbit_reproduction_prob: float = 0.05
    fox_reproduction_prob: float = 0.1
    grass_grow_prob: float = 0.5
    energy_decrease_rate: float = 0.02
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.5
    separation_weight: float = 0.5

    movement_speed: float = 1
    delta_time: float = 3

    mass: int = 20
    maxVelocity: int = 1
    mode: str = "outside obstacle"
    start = True

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)

@unique
class States(Enum):
    STILL = auto()
    WANDERING = auto()

class Fox(Agent):
    config: AggregationConfig

    def on_spawn(self):
       self._state = States.WANDERING
       self.energy = FOX_ENERGY
       self.hunger = 100 - FOX_ENERGY
       self.change_image(0)
       self.died = False

    def update(self):
        rabbits = self.in_proximity_accuracy().without_distance().filter_kind(Rabbit)

        if rabbits is not None and self.hunger > 20:
            for obj_rabbit in rabbits:
                if not obj_rabbit.died:
                    obj_rabbit.die()
                    self.eat()
                    break

        global reproduction_timer_fox
        global reproduction_amount_fox
        global reproduction_amount_fox_max

        reproduction_timer_fox += 1
        if reproduction_timer_fox >= fox_count * FOX_GROWTH_TIME:
            reproduction_timer_fox = 0
            reproduction_amount_fox = max(int(FOX_GROWTH_RATE * fox_count * ((FOX_CAPACITY - fox_count) / FOX_CAPACITY) + 0.5), 1)
            reproduction_amount_fox_max = reproduction_amount_fox
            print(f"foxes: {fox_count} produce: {reproduction_amount_fox}")

        if reproduction_amount_fox > 0:
            reproduction_progress = 1 - reproduction_amount_fox / reproduction_amount_fox_max
            time_progress = reproduction_timer_fox / (fox_count * FOX_GROWTH_TIME)
            if reproduction_progress < time_progress:
                self.reproduction()
                reproduction_amount_fox -= 1
                print(f"f produce: {reproduction_amount_fox}")

        self.lose_energy()

        if self.energy <= 0 and not self.died:
            self.die()

        self.save_data("kind", 0)

        #for flocking
        neighbours = list(self.in_proximity_accuracy().filter_kind(Fox))
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
            super(Fox, self).change_position()
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
            if d != 0:
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
        

    def set_state(self, state):
        self._state = state

    def get_state(self):
        return self._state
    
    def die(self):
        self.died = True
        self.kill()
        global fox_count
        fox_count -= 1
        #print(f"Foxes: {fox_count}, rabbits: {rabbit_count}")

    def eat(self):
        # Replenish energy
        # Assumes only one can be eaten even if more rabbits are in proximity
        self.energy = min(self.energy + ENERGY_GAIN_FOX, ENERGY_MAX_FOX)
        self.hunger = 100 - self.energy


    def lose_energy(self):
        # Decrease energy over time
        self.energy = max(self.energy - ENERGY_LOSS_FOX, 0)
        self.hunger = 100 - self.energy

    def reproduction(self):
        global fox_count
        self.reproduce()
        fox_count += 1

class Rabbit(Agent):
    config: AggregationConfig
    

    def on_spawn(self):
        #this part is for the dying of rabbits
        self._state = States.WANDERING #this is also for aggregation
        self.change_image(0)
        self.died = False
        #for aggregation
        self.time= 10

    def choose_start_pos(self):
        # Choose a random start position
        prng = self.shared.prng_move
        xw, yw = self.config.window.as_tuple()
        r1 = self.config.small_circle_radius
        r2 = self.config.big_circle_radius
        x = prng.uniform(0, xw)
        y = prng.uniform(0, yw)
        # If it is inside an aggregation site, repeat the choice
        # One circle: if ((xw//2-r1) < x < (xw//2+r1)) and ((yw//2-r1) < y < (yw//2+r1)):
        # Two same size circles: 
        if (((xw//4-r2) < x < (xw//4+r2)) or (((xw//4)*3-r2) < x < ((xw//4)*3+r2))) and ((yw//2-r2) < y < (yw//2+r2)):
        # Two different size circles:
        #if (((xw//4-r2) < x < (xw//4+r2)) and ((yw//2+r2) < y < (yw//2+r2))) or ((((xw//4)*3-r1) < x < ((xw//4)*3+r1)) and ((yw//2-r1) < y < (yw//2+r1))):
            new_pos = self.choose_start_pos()
            return new_pos
        # Else, return the position
        else:
            return Vector2((x, y))
        
    def update(self):
        #the update of the rabbit for the interacttion iwth the fox
        global reproduction_timer_rabbit
        global reproduction_amount_rabbit
        global reproduction_amount_rabbit_max

        reproduction_timer_rabbit += 1
        if reproduction_timer_rabbit >= rabbit_count * RABBIT_GROWTH_TIME:
            reproduction_timer_rabbit = 0
            reproduction_amount_rabbit = max(int(RABBIT_GROWTH_RATE * rabbit_count * ((RABBIT_CAPACITY - rabbit_count) / RABBIT_CAPACITY) + 0.5), 1)
            reproduction_amount_rabbit_max = reproduction_amount_rabbit
            print(f"rabbits: {rabbit_count} produce: {reproduction_amount_rabbit}")

        if reproduction_amount_rabbit > 0:
            reproduction_progress = 1 - reproduction_amount_rabbit / reproduction_amount_rabbit_max
            time_progress = reproduction_timer_rabbit / (rabbit_count * RABBIT_GROWTH_TIME)
            if reproduction_progress < time_progress:
                self.reproduction()
                reproduction_amount_rabbit -= 1
                print(f"produce: {reproduction_amount_rabbit}")

        self.save_data("kind", 1)

        #the updates so hat the rabbit aggregate
        self.time -= 1
        if self.time == 0:
            if self.get_state() == States.STILL:
                self.time = 100  # every x updates check to leave, i put on 100 to make them leave less quickly
            if self.get_state() == States.WANDERING:
                self.time = 10
            print(f"Westbois: {site_zero_birds}, Eastsiders: {site_one_birds}")
            if self.on_site():
                if self.get_state() == States.WANDERING:
                    self.join_site()
                elif self.get_state() == States.STILL:
                    self.leave_site()

    def join_site(self):
        neighbours = 0
        for agent, distance in self.in_proximity_accuracy():
            if agent.get_state() == States.STILL:
                neighbours += 1
        #print(f"neighbours: {neighbours}")
        join_chance = (0.001 * (neighbours ** 4) + (0.5 * neighbours) + 0.01) # exponential growth + tiny bit so it already takes a +1 effect at 2 neighbours
        if join_chance > 90:
            join_chance = 90
        join_chance *= 10
        join_luck = random.randint(0, 999)
        print(f"join chance: {join_chance}, join luck: {join_luck}")
        min_distance = 100                          # making sure they dont jump on top of each other/only settle on the borders
        for penguin, distance in self.in_proximity_accuracy():
            if penguin.get_state() == States.STILL and distance < min_distance:
                min_distance = distance
        if join_chance > join_luck and min_distance > 10:
            #print(f"i joined with min distance: {min_distance}")
            #print(f"neighbours: {neighbours}")
            #print(f"join chance: {join_chance}, join luck: {join_luck}")
            self.set_state(States.STILL)
            self.freeze_movement()
            self.time += 100 * neighbours # extra time to block it from leaving right after joining
            if self.on_site_id() == 0:
                global site_zero_birds
                site_zero_birds += 1
                self.change_image(0)
            elif self.on_site_id() == 1:
                global site_one_birds
                site_one_birds += 1
                self.change_image(1)

    def leave_site(self):
        neighbours = 0
        for agent, distance in self.in_proximity_accuracy():
            if agent.get_state() == States.STILL:
                neighbours += 1
        #print(f"neighbours: {neighbours}")
        #leave_chance = 3 - ((neighbours ** 2) * 0.1)       # more neighbours is less chance to leave
        join_chance = (0.001 * (neighbours ** 4)) + ((0.85 ** neighbours) * neighbours)
        if join_chance > 100:
            join_chance = 100
        leave_chance = (40 - join_chance / 3) / max(1, neighbours)
        leave_chance *= 10
        if leave_chance < 0:
            leave_chance = 0
        leave_chance += 0.1                    # always a tiny chance to leave
        leave_luck = random.randint(0, 999)
        print(f"leave chance: {leave_chance}, leave luck: {leave_luck}")
        if leave_chance > leave_luck:
            if self.on_site_id() == 0:
                global site_zero_birds
                site_zero_birds -= 1
            elif self.on_site_id() == 1:
                global site_one_birds
                site_one_birds -= 1
            self.set_state(States.WANDERING)
            self.continue_movement()
            self.change_image(2)
            self.time += 1000     # extra time to block it from rejoining after leaving
    
    def set_state(self, state):
        self._state = state

    def get_state(self):
        return self._state
    
    def reproduction(self):
        global rabbit_count
        self.reproduce()
        rabbit_count += 1

    def die(self):
        global rabbit_count
        rabbit_count -= 1
        self.died = True
        self.kill()
        #print(f"Foxes: {fox_count}, rabbits: {rabbit_count}")

class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()

class AggregationLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: AggregationConfig

   

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
        #print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")

df =(
    AggregationLive(
        AggregationConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
            duration = 600*60
        )
    )

    # optional obstacle border or loose ojects to avoid
    .batch_spawn_agents(FOX_COUNT, Fox, images=["/Users/ania/Desktop/Collective_Intelligence_Group_Ocean/images/red.png"])
    .batch_spawn_agents(RABBIT_COUNT, Rabbit, images=["/Users/ania/Desktop/Collective_Intelligence_Group_Ocean/images/green.png"])
  
    .spawn_site("/Users/ania/Desktop/Collective_Intelligence_Group_Ocean/images/bigger_big_circle.png", 563, 375)
    .run()


    #collect data
    .snapshots.rechunk()
    .groupby(["frame", "kind"])
    .agg(pl.count("id").alias("agent number"))
    .sort(["frame", "kind"])
)
print(df)

# graph data
sns.set(style="whitegrid")
plot = sns.relplot(x = df["frame"]/60,
    y = df["agent number"],
    hue = df["kind"],
    kind = "line",
    palette = "dark").set(title = "Population sizes over time")
plot.set_axis_labels("Seconds" , "Number of live agents")
plot.set(ylim = (0, Y_AXIS_MAX))
plot._legend.set_title("Populations")
legend_labels = ["Foxes", "Rabbits"]

for i, j in zip(plot._legend.texts, legend_labels):
    i.set_text(j)

plot.savefig("pip.png", dpi=RESOLUTION)
