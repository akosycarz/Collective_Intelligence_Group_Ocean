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
    rabbit_reproducton_prob: float = 0.8
    fox_reproduction_prob: float = 0.3
    energy_decrease_rate: float = 0.99
    grass_grow_rate: int = 90
    aging_rate: float = 0.01

    def weights(self) -> tuple[float]:
        return (self.grass_grow_rate)
    ...


class Fox(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        # All agents start with the same energy level
        self.energy = 1
        # All animals have age, and they can only live for a specific time
        self.age = 0
        self.change_image(1)

    def update(self):
        # Save the type of the animal
        self.save_data("kind", "fox")
        # Increase the age of the animal
        self.age += self.config.aging_rate
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
            self.sexual_reproduction()
            #if util.probability(self.config.fox_reproduction_prob):
            #    self.reproduce()
    
    def sexual_reproduction(self):
        # If there is another fox near, and both this fox and the possible 
        # partner are old enough, reproduce with given probability
        if self.age < 0.5:
            return 
        
        partner = (self.in_proximity_accuracy()
                       .without_distance()
                       .filter_kind(Fox)
                       .filter(lambda agent: agent.age > 0.5)
                       .first()
                  )
        if partner is not None and util.probability(self.config.fox_reproduction_prob):
            # Currently only gets one offspring, should it be more?
            self.reproduce()
            # Reproduction takes energy, so decrease energy
            self.energy /= 2
    
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
        # All animals have age, and they can only live for a specific time
        self.age = 0
        self.change_image(0)
    
    def update(self):
        # Save the type of the animal
        self.save_data("kind", "rabbit")
        # Increase the age of the animal
        self.age += self.config.aging_rate
        # Decrease the energy of the rabbit
        self.energy *= self.config.energy_decrease_rate
        # If the rabbit has no energy, it dies
        if self.energy == 0:
            self.kill()
        # Check if there is grass near
        grass = (self.in_proximity_accuracy()
                     .without_distance()
                     .filter_kind(Grass)
                     .first()
                )
        # If there is a grass, eat it and energy increases
        if grass is not None:
            grass.kill()
            self.energy = 1
        self.sexual_reproduction()
        # Reproduce with given probability
        #if util.probability(self.config.rabbit_reproducton_prob):
         #   self.reproduce()
    
    def sexual_reproduction(self):
        # If there is another rabbit near, and both this rabbit and the 
        # possible partner are old enough, reproduce with given probability
        if self.age < 0.3:
            return
        
        partner = (self.in_proximity_accuracy()
                       .without_distance()
                       .filter_kind(Rabbit)
                       .filter(lambda agent: agent.age > 0.3)
                       .first()
                  )
        if partner is not None and util.probability(self.config.fox_reproduction_prob):
            # Currently only gets one offspring, should it be more?
            self.reproduce()
            # Reproduction takes energy, so decrease energy
            self.energy /= 2

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
        self.change_image(2)
        # The grass grows only in specific places & it does not move
        #self.pos = 0
        # Initialize a counter to keep track of time
        self.counter = 0
        # The grass does not move
        self.freeze_movement()
        # Where is the grass?
        # Is it in multiple places?
    
    def update(self):
        # Save the type of the organism
        self.save_data("kind", "grass")
        self.counter += 1

        # The grass grows every grass_grow_rate timesteps
        if self.counter % self.config.grass_grow_rate == 0:
            self.reproduce()


config = Config()
n_fox = 20
n_rabbit = 20
n_grass = 30
n = n_fox + n_rabbit
config.window.height = n*10
config.window.width = n*10
x, y = config.window.as_tuple()

df = (
    Simulation(
        CompetitionConfig(
            image_rotation=True,
            movement_speed=1,
            radius=25,
            seed=1,
            window=Window(width=n*10, height=n*10),
            duration=5*60,
            #fps_limit=0,
        )
    )
    .batch_spawn_agents(n_fox, Fox, images=["images/white.png", "images/red.png", "images/green.png"])
    .batch_spawn_agents(n_rabbit, Rabbit, images=["images/white.png", "images/red.png", "images/green.png"])
    .batch_spawn_agents(n_grass, Grass, images=["images/white.png", "images/red.png", "images/grass.png"])
    .run()
    .snapshots
    # Get the number of stopped rabbits and foxes per timeframe 
    .groupby(["frame", "kind"])
    .agg(pl.count('id').alias("number of agents"))
    .sort(["frame", "kind"])
)

print(df)
n_new = df.get_column("number of agents")[-3] + df.get_column("number of agents")[-1]
print('Proportion of foxes of all agents: {}'.format(df.get_column("number of agents")[-3] / n_new))
print('Proportion of rabbits of all agents: {}'.format(df.get_column("number of agents")[-1] / n_new))

# Plot the number of stopped agents per frame
plot1 = sns.relplot(x=df["frame"], y=df["number of agents"], hue= df["kind"], kind="line")
plot1.savefig("number_agents.png", dpi=300)
# Change the plots so that image index 0 is rabbits and image index 1 is foxes

# Does the fox get energy from killling a rabbit if they also reproduce?
# How about sexual reproduction and some characteristics that make rabbits
# less likely to be eaten by foxes?



"""Age 
-    rabbits (live expectancy 8-12 years)
-    foxes (live expectancy 1-9 years)"""
# Should we have a unique time to die or would it be better if we have that
# the energy is decreased more at every frame the older the agent is?
# Should the grass be in specific places?
# Should the animals have more than one offspring each reproduction time?
