import polars as pl
import seaborn as sns

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation, util
from vi.config import Window, Config, dataclass, deserialize

@deserialize
@dataclass
class CompetitionConfig(Config):
    # Add all parameters here
    rabbit_reproducton_prob: float = 0.01
    fox_reproduction_prob: float = 0.1

    def weights(self) -> tuple[float]:
        return (self)
    ...


class Fox(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        # All agents start with the same energy level
        self.energy = 1
        self.change_image(1)

    def update(self):
        # Decrease the energy of the fox
        self.energy *= 0.9999
        # If the fox has no energy, it dies
        if self.energy == 0:
            self.kill()
        # Check if there are rabbits near
        rabbit = (self.in_proximity_accuracy()
                      .without_distance()
                      .filter_kind(Rabbit)
                      .first()
                 )
        # If there is a rabbit, eat it and energy increases
        if rabbit is not None:
            rabbit.kill()
            self.energy = 1
            if util.probability(self.config.fox_reproduction_prob):
                self.reproduce()


class Rabbit(Agent):
    config: CompetitionConfig
        
    def on_spawn(self):
        self.change_image(0)

    def update(self):
        # Reproduce with given probability
        if util.probability(self.config.rabbit_reproducton_prob):
            self.reproduce()


config = Config()
n_fox = 10
n_rabbit = 10
n = n_fox + n_rabbit
config.window.height = n*10
config.window.width = n*10
x, y = config.window.as_tuple()

df = (
    Simulation(
        CompetitionConfig(
            image_rotation=True,
            movement_speed=1,
            radius=125,
            seed=1,
            #window=Window(width=n*10, height=n*10),
            duration=5*60,
            #fps_limit=0,
        )
    )
    .batch_spawn_agents(n_fox, Fox, images=["images/white.png", "images/red.png"])
    .batch_spawn_agents(n_rabbit, Rabbit, images=["images/white.png", "images/red.png"])
    .run()
    .snapshots
    # Get the number of stopped rabbits and foxes per timeframe 
    .groupby(["frame", "image_index"])
    .agg(pl.count('id').alias("number of agents"))
    .sort(["frame", "image_index"])
)

print(df)
# Plot the number of stopped agents per frame
plot1 = sns.relplot(x=df["frame"], y=df["number of stopped agents"], hue= df["image_index"], kind="line")
plot1.savefig("number_agents.png", dpi=300)
