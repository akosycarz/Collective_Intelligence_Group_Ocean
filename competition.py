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
    energy_decrease_rate: float = 0.99
    grass_grow_rate: int = 60

    def weights(self) -> tuple[float]:
        return (self.grass_grow_rate)
    ...


class Fox(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        # All agents start with the same energy level
        self.energy = 1
        self.change_image(1)

    def update(self):
        # Decrease the energy of the fox
        self.energy *= self.config.energy_decrease_rate
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
    
    # If we have (an) obstacle(s), we need to use this function to make sure
    # no agents spawn there
    def choose_start_pos(self):
        # Choose a random start position that is not on an obstacle
        prng = self.shared.prng_move
        xw, yw = self.config.window.as_tuple()
        x = prng.uniform(0, xw)
        y = prng.uniform(0, yw)
        return Vector2((x, y))


class Rabbit(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        # All agents start with the same energy level
        self.energy = 1
        self.change_image(0)
    
    def update(self):
        # Decrease the energy of the rabbit
        self.energy *= self.config.energy_decrease_rate
        # If the rabbit has no energy, it dies
        if self.energy == 0:
            self.kill()
        # Reproduce with given probability
        if util.probability(self.config.rabbit_reproducton_prob):
            self.reproduce()

    # If we have (an) obstacle(s), we need to use this function to make sure
    # no agents spawn there
    def choose_start_pos(self):
        # Choose a random start position that is not on an obstacle
        prng = self.shared.prng_move
        xw, yw = self.config.window.as_tuple()
        x = prng.uniform(0, xw)
        y = prng.uniform(0, yw)
        return Vector2((x, y))

class Grass(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        # The grass grows only in specific places & it does not move
        #self.pos = 0
        # Initialize a counter to keep track of time
        self.counter = 0
        # The grass does not move
        self.freeze_movement()
        # Where is the grass?
        # How much grass?
        # Is it in multiple places?
    
    def update(self):
        self.counter += 1

        # The grass grows every grass_grow_rate timesteps
        if self.counter % self.config.grass_grow_rate == 0:
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
#print('Proportion of foxes of all agents: {}'.format(df.get_column("2nd aggregate size")[-1] / n))
#print('Proportion of agents in left aggregate: {}'.format(df.get_column("1st aggregate size")[-1] / n))

# Plot the number of stopped agents per frame
plot1 = sns.relplot(x=df["frame"], y=df["number of agents"], hue= df["image_index"], kind="line")
plot1.savefig("number_agents.png", dpi=300)
# Change the plots so that image index 0 is rabbits and image index 1 is foxes

# Does the fox get energy from killling a rabbit if they also reproduce?
# How about sexual reproduction and some characteristics that make rabbits
# less likely to be eaten by foxes?
