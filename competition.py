import polars as pl
import seaborn as sns

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation, util
from vi.config import Window, Config, dataclass, deserialize

import random

@deserialize
@dataclass
class CompetitionConfig(Config):
    # Add all parameters here
    rabbit_reproducton_prob: float = 0.01
    fox_reproduction_prob: float = 0.1
    energy_decrease_rate: float = 0.99
    energy_decrease_rate_rabbit: float = 0.99
    energy_decrease_rate_fox: float = 0.5
    grass_grow_rate: int = 200
    aging_rate: float = 0.001

    def weights(self) -> tuple[float]:
        return (self)
    ...


class Fox(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        # All agents start with the same energy level
        self.energy = 1
        # All animals have age, and they can only live for a specific time
        self.age = 0
        self.death_cause = "alive"
        self.gender = random.choices(["male", "female", "other"],
                      weights= (40, 40, 20))
        self.change_image(1)

    def update(self):
        # Save the type of the animal
        self.save_data("kind", "fox")
        self.save_data("death_cause", self.death_cause)
        # Increase the age of the animal
        self.age += self.config.aging_rate
        # Decrease the energy of the fox
        self.energy *= self.config.energy_decrease_rate_fox
        # If the fox has no energy, it dies
        if self.energy == 0:
            self.death_cause = "starvation"
            self.kill()
        # Check if there are rabbits near
        rabbit = (self.in_proximity_accuracy()
                      .without_distance()
                      .filter_kind(Rabbit)
                      .first()
                 )
        # If there is a rabbit, eat it and energy increases
        if rabbit is not None:
            rabbit.death_cause = "eaten"
            rabbit.kill()
            self.energy = 1
            self.sexual_reproduction()
            # Asexual reproduction:
            #if util.probability(self.config.fox_reproduction_prob):
            #    self.reproduce()
                # Reproduction takes energy, so the energy level of the animal decreasdes
            #    self.energy /= 2
    
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


class Rabbit(Agent):
    config: CompetitionConfig
        
    def on_spawn(self):
        # All agents start with the same energy level
        self.energy = 1
        # All animals have age, and they can only live for a specific time
        self.age = 0
        self.death_cause = "alive"
        self.gender = random.choices(["male", "female", "other"],
                      weights= (50, 50, 0))
        self.change_image(0)

    def update(self):
        # Save the type of the animal
        self.save_data("kind", "rabbit")
        self.save_data("death_cause", self.death_cause)
        # Increase the age of the animal
        self.age += self.config.aging_rate
        # Decrease the energy of the rabbit
        self.energy *= self.config.energy_decrease_rate_rabbit
        # If the rabbit has no energy, it dies
        if self.energy == 0:
            self.death_cause = "starvation"
            self.kill() 
        # Check if there is grass near
        grass = (self.in_proximity_accuracy()
                     .without_distance()
                     .filter_kind(Grass)
                     .first()
                )
        # If there is a grass, eat it and energy increases
        if grass is not None:
            grass.death_cause = "eaten"
            grass.kill()
            self.energy = 1
        # Sexual reproduction:
        self.sexual_reproduction()
        # Asexual reproduction:
        # Reproduce with given probability
        #if util.probability(self.config.rabbit_reproducton_prob):
         #   self.reproduce()
            # Reproduction takes energy, so the energy level of the animal decreasdes
          #  self.energy /= 2
        
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
        if partner is not None and util.probability(self.config.fox_reproduction_prob) and self.energy >= 0.5:
            # A female can only be cloned and it must meet a male to do it
            if self.gender == "female" and partner.gender == 'male':
                # Currently only gets 3 offspring, should it be more?
                babies_count = 3
                for n in range(0, babies_count):
                    self.reproduce()
                # Reproduction takes energy, so decrease energy
                self.energy /= 2

            
            
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
        self.counter += 1

        # The grass grows every grass_grow_rate timesteps
        if self.counter % self.config.grass_grow_rate == 0:
            self.reproduce()
            
            
config = Config()
n_fox = 40
n_rabbit = 40
n_grass = 50
n = n_fox + n_rabbit
config.window.height = n*10
config.window.width = n*10
x, y = config.window.as_tuple()

df = (
    Simulation(
        CompetitionConfig(
            image_rotation=True,
            movement_speed=1,
            radius=15,
            seed=1,
            window=Window(width=n*10, height=n*10),
            duration=60*60,
            #fps_limit=0,
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
n_new = df.get_column("number of agents")[-3] + df.get_column("number of agents")[-1]
print('Proportion of foxes of all agents: {}'.format(df.get_column("number of agents")[-3] / n_new))
print('Proportion of rabbits of all agents: {}'.format(df.get_column("number of agents")[-1] / n_new))

# Plot the number of animals per frame
plot1 = sns.relplot(x=df["frame"], y=df["number of agents"], hue= df["kind"], kind="line")
plot1.savefig("number_agents.png", dpi=300)



"""Age 
-    rabbits (live expectancy 8-12 years)
-    foxes (live expectancy 1-9 years)"""
# Should we have a unique time to die or would it be better if we have that
# the energy is decreased more at every frame the older the agent is?
# Should the grass be in specific places?
# Is it in multiple places?
# Should the animals have more than one offspring each reproduction time?


