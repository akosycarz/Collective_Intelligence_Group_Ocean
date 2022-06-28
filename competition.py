import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

from vi import Agent, HeadlessSimulation, util
from vi.config import Window, Config, dataclass, deserialize

import random

@deserialize
@dataclass
class CompetitionConfig(Config):
    # Add all parameters here
    agents: int = 0
    reproduce: bool = True
    rabbit_reproduction_prob: float = 0.05
    fox_reproduction_prob: float = 0.1
    grass_grow_prob: float = 0.5
    energy_decrease_rate: float = 0.02
    # aging_rate: float = 0.02
    rabbit_offspring_number: int = 3
    fox_offspring_number: int = 3
    hunger_threshold: float = 0.8
    fox_reproduction_threshold: float = 0.5
    rabbit_reproduction_threshold: float = 0.3
    caring_capacity: int = 1000
    # fox_fertility_age: int = 10
    # rabbit_fertility_age: int = 10

    def weights(self) -> tuple[float]:
        return (self)
    ...


class Fox(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        # All agents start with the same energy level
        self.energy =  1
        # All animals have age, and they can only live for a specific time
        # self.age = 0
        self.death_cause = "alive"
        genders_list = ["male", "female", "other"]
        self.gender = random.choices(genders_list, k=1, weights=[0.5, 0.5, 0.0])[0]
        self.change_image(1)

    def update(self):
        self.save_data("gender", self.gender)
        # Save the type of the animal
        self.save_data("kind", "fox")
        self.save_data("death_cause", self.death_cause)
        # Increase the age of the animal
        #self.age += self.config.aging_rate
        # Decrease the energy of the fox
        self.energy -= self.config.energy_decrease_rate
        #*(self.age/100))
        # If the fox has no energy, it dies
        if self.energy <= 0:
            self.death_cause = "starvation"
            self.kill()
            self.config.agents -= 1
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
            self.config.agents -= 1
        # Reproduce if caring capacity is not exceeded
        if self.config.agents >= self.config.caring_capacity:
            self.config.reproduce = False
        else: self.config.reproduce = True
        if self.config.reproduce:
            self.sexual_reproduction()
    
    def sexual_reproduction(self):
        # If there is another fox near, and both this fox and the possible 
        # partner are old enough, reproduce with given probability
        #if self.age < self.config.fox_fertility_age:
        #    return 
        
        partner = (self.in_proximity_accuracy()
                       .without_distance()
                       .filter_kind(Fox)
                       #.filter(lambda agent: agent.age > self.config.fox_fertility_age)
                       .first()
                  )
        if partner is not None and util.probability(self.config.fox_reproduction_prob) \
                and self.energy >= self.config.fox_reproduction_threshold:
            if self.gender == "female" and partner.gender == "male":
                for n in range(0, self.config.fox_offspring_number):
                    self.reproduce()
                    self.config.agents += 1
            # Reproduction takes energy, so decrease energy
            self.energy /= 2


class Rabbit(Agent):
    config: CompetitionConfig
        
    def on_spawn(self):
        # All agents start with the same energy level
        self.energy = 1
        # All animals have age, and they can only live for a specific time
        # self.age = 0
        self.death_cause = "alive"
        genders_list = ["male", "female", "other"]
        self.gender = random.choices(genders_list, k=1, weights=[0.5, 0.5, 0])[0]
        self.change_image(0)

    def update(self):
        self.save_data("gender", str(self.gender))
        # Save the type of the animal
        self.save_data("kind", "rabbit")
        self.save_data("death_cause", self.death_cause)
        # Increase the age of the animal
        #self.age += self.config.aging_rate
        # Decrease the energy of the rabbit
        self.energy -= self.config.energy_decrease_rate
        #print(self.energy)
        #*(self.age/100))
        # If the rabbit has no energy, it dies
        if self.energy <= 0:
            self.death_cause = "starvation"
            self.kill() 
            self.config.agents -= 1
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
            self.energy += 1
        # Sexual reproduction:
        # Reproduce if caring capacity is not exceeded
        if self.config.agents >= self.config.caring_capacity:
            self.config.reproduce = False
        else: self.config.reproduce = True
        if self.config.reproduce:
            self.sexual_reproduction()
        
    def sexual_reproduction(self):
        # If there is another rabbit near, and both this rabbit and the 
        # possible partner are old enough, reproduce with given probability
        #if self.age < self.config.rabbit_fertility_age:
        #    return

        partner = (self.in_proximity_accuracy()
                       .without_distance()
                       .filter_kind(Rabbit)
                       #.filter(lambda agent: agent.age > self.config.rabbit_fertility_age)
                       .first()
                  )
        if partner is not None and util.probability(self.config.rabbit_reproduction_prob) and self.energy >= self.config.rabbit_reproduction_threshold:
            # A female can only be cloned and it must meet a male to do it

            if self.gender == "female" and partner.gender == 'male':
                # Currently only gets 3 offspring, should it be more?
                for n in range(0, self.config.rabbit_offspring_number):
                    self.reproduce()
                    self.config.agents += 1
                # Reproduction takes energy, so decrease energy
                self.energy /= 2


class Grass(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        self.change_image(2)
        # The grass grows in random places & it does not move
        # Initialize a counter to keep track of time
        self.death_cause = "alive"
        # The grass does not move
        self.freeze_movement()
        # Where is the grass?
        # Is it in multiple places?

    def update(self):
        self.save_data("gender", "---")
        # Save the type of the organism
        self.save_data("kind", "grass")
        self.save_data("death_cause", self.death_cause)
        # The grass grows back if it dies with given probability
        if util.probability(self.config.grass_grow_prob) and self.is_dead():
            self.reproduce()



config = Config()
n_fox = 50
n_rabbit = 50
n_grass = 1000
n = n_fox + n_rabbit
experiments = 30

for i in range(experiments):
    filename = "competition_{}.csv".format(i)
    df = (
        HeadlessSimulation(
            CompetitionConfig(
                image_rotation=True,
                movement_speed=1,
                radius=15,
                seed=i,
                window=Window(width=n*10, height=n*10),
                duration=300*60,
                agents=n,
                fps_limit=0,
            )
        )
        .batch_spawn_agents(n_fox, Fox, images=["images/white.png", "images/red.png", "images/green.png"])
        .batch_spawn_agents(n_rabbit, Rabbit, images=["images/white.png", "images/red.png", "images/green.png"])
        .batch_spawn_agents(n_grass, Grass, images=["images/white.png", "images/red.png", "images/grass.png"])
        .run()
        .snapshots
        # Get the number of animals per death cause per timeframe 
        .groupby(["frame", "kind", "death_cause", "gender"])
        # Get the number of rabbits and foxes per timeframe
        .agg(pl.count('id').alias("number of agents"))
        .sort(["frame", "kind", "death_cause", "gender"])
        .write_csv(filename)
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

