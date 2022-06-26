import polars as pl
import seaborn as sns

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation, util
from vi.config import Window, Config, dataclass, deserialize
from numpy.random import choice

import random


@deserialize
@dataclass
class CompetitionConfig(Config):
    # Add all parameters here
    rabbit_reproduction_prob: float = 0.01

    fox_reproduction_prob: float = 0.5
    energy_decrease_rate: float = 0.002

    # aging_rate: float = 0.02
    hunger_threshold: float = 0.8
    fox_reproduction_threshold: float = 0.5

    # fox_fertility_age: int = 10
    # rabbit_fertility_age: int = 10

    def weights(self) -> tuple[float]:
        return (self)

    ...


class Fox(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        # All agents start with the same energy level
        self.energy = 0.5 - 0.01
        # All animals have age, and they can only live for a specific time

        self.death_cause = "alive"
        self.change_image(1)

    def update(self):
        # Save the type of the animal
        self.save_data("kind", "fox")
        self.save_data("death_cause", self.death_cause)
        # Increase the age of the animal
        # self.age += self.config.aging_rate
        # Decrease the energy of the fox
        self.energy -= self.config.energy_decrease_rate
        self.asexualReproduction()
        # *(self.age/100))
        # If the fox has no energy, it dies
        if self.energy <= 0:
            self.death_cause = "starvation"
            self.kill()
        # Check if there are rabbits near
        rabbit = (self.in_proximity_accuracy()
                  .without_distance()
                  .filter_kind(Rabbit)
                  .first()
                  )
        # If there is a rabbit, eat it and energy increases
        if rabbit is not None and self.energy < self.config.hunger_threshold:
            rabbit.death_cause = "eaten"
            rabbit.kill()
            self.energy = 1

    def asexualReproduction(self):
        partner = (self.in_proximity_accuracy()
                       .without_distance()
                       .filter_kind(Fox)
                       .first()
                  )
        if partner is not None and util.probability(self.config.rabbit_reproduction_prob) \
                and self.energy >= self.config.fox_reproduction_threshold:
                self.reproduce()
                # Reproduction takes energy, so decrease energy
                self.energy /= 2



class Rabbit(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        self.death_cause = "alive"
        self.change_image(0)

    def update(self):
        # Save the type of the animal
        self.save_data("kind", "rabbit")
        self.save_data("death_cause", self.death_cause)
        # Increase the age of the animal
        # self.age += self.config.aging_rate
        self.asexualReproduction()
        # print(self.energy)
        # *(self.age/100))

    def asexualReproduction(self):
        partner = (self.in_proximity_accuracy()
                       .without_distance()
                       .filter_kind(Rabbit)
                       #.filter(lambda agent: agent.age > self.config.rabbit_fertility_age)
                       .first()
                  )
        if partner is not None and util.probability(self.config.rabbit_reproduction_prob):
                self.reproduce()


class Grass(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        self.change_image(2)
        # The grass grows in random places & it does not move
        # Initialize a counter to keep track of time
        self.counter = 0
        self.death_cause = "alive"
        # The grass does not move
        self.freeze_movement()
        # Where is the grass?
        # Is it in multiple places?

    def update(self):
        # Save the type of the organism
        self.save_data("kind", "grass")
        self.save_data("death_cause", self.death_cause)
        # The grass grows back if it dies
        if self.is_dead():
            self.reproduce()


config = Config()
n_fox = 50
n_rabbit = 50
n_grass = n_rabbit *4
n = n_fox + n_rabbit
config.window.height = n * 10
config.window.width = n * 10
x, y = config.window.as_tuple()

df = (
    Simulation(
        CompetitionConfig(
            image_rotation=True,
            movement_speed=1,
            radius=15,
            seed=1,
            window=Window(width=n * 6, height=n * 6),
            duration=120 * 60,
            fps_limit=60,
        )
    )
        .batch_spawn_agents(n_fox, Fox, images=["images/white.png", "images/red.png", "images/green.png"])
        .batch_spawn_agents(n_rabbit, Rabbit, images=["images/white.png", "images/red.png", "images/green.png"])
        .batch_spawn_agents(n_grass, Grass, images=["images/white.png", "images/red.png", "images/grass.png"])
        .run()
        .snapshots
        # Get the number of animals per death cause per timeframe
        .groupby(["frame", "kind", "death_cause"])
        # Get the number of rabbits and foxes per timeframe
        .agg(pl.count('id').alias("number of agents"))
        .sort(["frame", "kind", "death_cause"])
)

print(df)
for n in range(0, len(df['frame'])):
    if df['frame'][n] == (20 * 60):
        print(df.row(n))
    if df['frame'][n] == (60 * 60):
        print(df.row(n))

# n_new = df.get_column("number of agents")[-3] + df.get_column("number of agents")[-1]
# print('Proportion of foxes of all agents: {}'.format(df.get_column("number of agents")[-3] / n_new))
# print('Proportion of rabbits of all agents: {}'.format(df.get_column("number of agents")[-1] / n_new))

# Plot the number of animals per frame
# plot1 = sns.relplot(x=df["frame"], y=df["number of agents"], hue= df["kind"], kind="line")
# plot1.savefig("number_agents.png", dpi=300)