import polars as pl
import seaborn as sns

from vi import Agent, Simulation, util
from vi.config import Window, Config, dataclass, deserialize
from numpy.random import choice

import random

@deserialize
@dataclass
class CompetitionConfig(Config):
    # Add all parameters here
    rabbit_reproduction_prob: float = 0.01
    fox_reproduction_prob: float = 0.07
    energy_decrease_rate: float = 0.001
    rabbit_offspring_number: int = 3
    fox_offspring_number: int = 3
    hunger_threshold: float = 0.8
    fox_reproduction_threshold: float = 0.5

    def weights(self) -> tuple[float]:
        return (self)
    ...


class Fox(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        # All agents start with the same energy level
        self.energy = 1
        self.death_cause = "alive"
        genders_list = ["male", "female", "other"]
        self.gender = random.choices(genders_list, k=1, weights=[0.5, 0.5, 0.0])[0]
        self.change_image(1)

    def update(self):
        self.save_data("gender", self.gender)
        # Save the type of the animal
        self.save_data("kind", "fox")
        self.save_data("death_cause", self.death_cause)
        # Decrease the energy of the fox
        self.energy -= self.config.energy_decrease_rate
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
        self.sexual_reproduction()
    
    def sexual_reproduction(self):
        # If there is another fox near, reproduce with given probability  
        partner = (self.in_proximity_accuracy()
                       .without_distance()
                       .filter_kind(Fox)
                       .first()
                  )
        if partner is not None and util.probability(self.config.fox_reproduction_prob) and self.energy >= self.config.fox_reproduction_threshold:
            if self.gender == "female" and partner.gender == "male":
                for n in range(0, self.config.fox_offspring_number):
                    self.reproduce()
            # Reproduction takes energy, so decrease energy
            self.energy /= 2


class Rabbit(Agent):
    config: CompetitionConfig
        
    def on_spawn(self):
        self.death_cause = "alive"
        genders_list = ["male", "female", "other"]
        self.gender = random.choices(genders_list, k=1, weights=[0.5, 0.5, 0])[0]
        self.change_image(0)

    def update(self):
        self.save_data("gender", str(self.gender))
        # Save the type of the animal
        self.save_data("kind", "rabbit")
        self.save_data("death_cause", self.death_cause)
        # Sexual reproduction:
        self.sexual_reproduction()
        
    def sexual_reproduction(self):
        # If there is another rabbit near, reproduce with given probability

        partner = (self.in_proximity_accuracy()
                       .without_distance()
                       .filter_kind(Rabbit)
                       .first()
                  )
        if partner is not None and util.probability(self.config.rabbit_reproduction_prob):
            # A female can only be cloned and it must meet a male to do it
            if self.gender == "female" and partner.gender == 'male':
                # Currently only gets 3 offspring, should it be more?
                for n in range(0, self.config.rabbit_offspring_number):
                    self.reproduce()



config = Config()
n_fox = 50
n_rabbit = 50
n_grass = 1000
n = n_fox + n_rabbit

df = (
    Simulation(
        CompetitionConfig(
            image_rotation=True,
            movement_speed=1,
            radius=15,
            seed=1,
            window=Window(width=n*10, height=n*10),
            duration=20*60,
            # 20*60, 60*60, 
            #fps_limit=0,
        )
    )
    .batch_spawn_agents(n_fox, Fox, images=["images/white.png", "images/red.png"])
    .batch_spawn_agents(n_rabbit, Rabbit, images=["images/white.png", "images/red.png"])
    .run()
    .snapshots
    # Get the number of animals per death cause per timeframe 
    .groupby(["frame", "kind", "death_cause", "gender"])
    # Get the number of rabbits and foxes per timeframe
    .agg(pl.count('id').alias("number of agents"))
    .sort(["frame", "kind", "death_cause", "gender"])
)

print(df)

#n_new = df.get_column("number of agents")[-3] + df.get_column("number of agents")[-1]
#print('Proportion of foxes of all agents: {}'.format(df.get_column("number of agents")[-3] / n_new))
#print('Proportion of rabbits of all agents: {}'.format(df.get_column("number of agents")[-1] / n_new))

# Plot the number of animals per frame
#plot1 = sns.relplot(x=df["frame"], y=df["number of agents"], kind="line")
#hue=df["kind"], kind="line")
#plt.legend(labels=["rabbits","grass", "foxes"])
#plot1.savefig("number_agents.png", dpi=300)
