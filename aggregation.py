from enum import Enum, auto
import matplotlib.pyplot as plt
import numpy as np
import math
import polars as pl
import seaborn as sns
import random

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation, util
from vi.config import Window, Config, dataclass, deserialize

@deserialize
@dataclass
class AggregationConfig(Config):
    # Add all parameters here
    D: int = 20
    factor_a: float = 2.6
    factor_b: float = 2.2
    t_join: int = 50
    t_leave: int = 50
    small_circle_radius: int = 128/2
    big_circle_radius: int = 200/2
    number_popular_agents: int = 0
    max_popular_agents: int = 6

    def weights(self) -> tuple[float, float]:
        return (self.factor_a, self.factor_b)
    ...


class Cockroach(Agent):
    config: AggregationConfig

    def on_spawn(self):
        # All agents start at the wandering state and with counter 0
        self.state = 'wandering'
        self.counter = 0
        if self.config.number_popular_agents <= self.config.max_popular_agents:
            self.config.number_popular_agents += 1
            self.popularity = 3
            self.change_image(1)
        else:
            self.popularity = random.randint(1, 2)
            self.change_image(0)
        # Create the time constraints
        # Sample some Gaussian noise
        noise = np.random.normal()
        self.max_join_time = self.config.t_join + noise
        self.max_leave_time = self.config.t_leave
        # Make sure no agents start at the aggregation site
        self.pos = self.choose_start_pos()
        

    def update(self):
        # Save the current state of the agent
        self.save_data("state", self.state)
        # The number of immediate neighbours
        neighbours = list(self.in_proximity_performance())
        if self.state == 'wandering': 
            # If detect an aggregation site, join the aggregation with given 
            # probability
            if self.join(neighbours):
                self.state = 'joining'
        elif self.state == 'joining':
            self.counter += 1
            # When the agent has joined the aggregation, change the state to still
            if self.counter > self.max_join_time: 
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
            if self.counter > self.max_leave_time: 
                self.state = 'wandering'
                self.counter = 0

            
    def join(self, neighbours):
        # The average popularity of the neighbours
        avg_pop = self.neighbour_popularity(neighbours)
        # Calculate the joining probability using the number of neighbours
        # The probability to stop is 0.03 if no neighbours and at most 0.51
        probability = 0.03 + 0.48*(1 - math.e**(-self.config.factor_a * len(neighbours)))
        # Return True if join the aggregate, else return False
        if self.popularity == 3:
            if self.on_site_id() == 0:
                return True
        else:
            if self.on_site_id() is not None and util.probability(probability):
                return True
        return False


    def leave(self, neighbours):
        # The average popularity of the neighbours
        avg_pop = self.neighbour_popularity(neighbours)
        # Calculate the leaving probability
        # If there are many neighbours, leaving is less likely
        # If there are no neighbours, it is nearly certain that the agents
        # leave, probability is 1
        probability = math.e**(-self.config.factor_b * len(neighbours))
        print(f'Leave popularity: {probability}')
        # Return True if leave the aggregate, else return False
        if util.probability(probability):
            return True
        else:
            return False
    
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
        if (((xw//4-r1) < x < (xw//4+r1)) or (((xw//4)*3-r1) < x < ((xw//4)*3+r1))) and ((yw//2-r1) < y < (yw//2+r1)):
        # Two different size circles:
        #if (((xw//4-r2) < x < (xw//4+r2)) and ((yw//2+r2) < y < (yw//2+r2))) or ((((xw//4)*3-r1) < x < ((xw//4)*3+r1)) and ((yw//2-r1) < y < (yw//2+r1))):
            new_pos = self.choose_start_pos()
            return new_pos
        # Else, return the position
        else:
            return Vector2((x, y))
    
    def neighbour_popularity(self, neighbours):
        avg_popularity = 0
        if len(neighbours) != 0:
            for i in neighbours:
                avg_popularity += i.popularity
            if avg_popularity / len(neighbours) > 3:
                return 3
            elif avg_popularity / len(neighbours) < 1:
                return 1
            else:
                return avg_popularity / len(neighbours)
        else:
            return 1


config = Config()
n = 50
config.window.height = n*(4**2)
config.window.width = n*(4**2)
x, y = config.window.as_tuple()

df = (
    Simulation(
        AggregationConfig(
            image_rotation=True,
            movement_speed=1,
            radius=100,
            seed=1,
            window=Window(width=n*(4**2), height=n*(4**2)),
            duration=30*60,
            fps_limit=0,
        )
    )
    .batch_spawn_agents(n, Cockroach, images=["images/white.png", "images/red.png"])
    # One circle: .spawn_site("images/circle.png", x//2, y//2)
    # Two same size circles: 
    .spawn_site("images/circle.png", x//4, y//2)
    .spawn_site("images/circle.png", (x//4)*3, y//2)
    # Two different sizde circles:
    #.spawn_site("images/bigger_circle.png", x//4, y//2)
    #.spawn_site("images/circle.png", (x//4)*3, y//2)
    .run()
    .snapshots
    # Get the number of stopped agents per timeframe and also per aggregation
    # site
    .filter(pl.col("state") == 'still')
    .with_columns([
        ((((x//4)*3+64) > pl.col("x")) & (pl.col("x") > ((x//4)*3-64)) & ((y//2+64) > pl.col("y")) & (pl.col("y") > (y//2-64))).alias("small aggregate"),
        (((x//4+100) > pl.col("x")) & (pl.col("x") > (x//4-100)) & ((y//2+100) > pl.col("y")) & (pl.col("y") > (y//2-100))).alias("big aggregate")
    ])
    .groupby(["frame"])
    .agg([
        pl.count('id').alias("number of stopped agents"),
        pl.col("small aggregate").cumsum().alias("small aggregate size").last(),
        pl.col("big aggregate").cumsum().alias("big aggregate size").last()
    ])
    .sort(["frame", "number of stopped agents"])
)

print(df)
print('Proportion of agents in small aggregate: {}'.format(df.get_column("small aggregate size")[-1] / n))
print('Proportion of agents in big aggregate: {}'.format(df.get_column("big aggregate size")[-1] / n))

# Plot the number of stopped agents per frame
plot1 = sns.relplot(x=df["frame"], y=df["number of stopped agents"], kind="line")
plot1.savefig("stopped.png", dpi=300)
plot2 = sns.relplot(x=df["frame"], y=df["small aggregate size"], kind="line")
plot2.savefig("small_aggregate.png", dpi=300)
plot3 = sns.relplot(x=df["frame"], y=df["big aggregate size"], kind="line")
plot3.savefig("big_aggregate.png", dpi=300)


