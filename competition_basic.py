import polars as pl
import seaborn as sns

from vi import Agent, HeadlessSimulation, util
from vi.config import Window, Config, dataclass, deserialize


@deserialize
@dataclass
class CompetitionConfig(Config):
    # Add all parameters here
    agents: int = 0
    reproduce: bool = True
    rabbit_reproduction_prob: float = 0.05
    fox_reproduction_prob: float = 0.1
    energy_decrease_rate: float = 0.02
    hunger_threshold: float = 0.8
    fox_reproduction_threshold: float = 0.5
    caring_capacity: int = 1000

    def weights(self) -> tuple[float]:
        return (self)

    ...


class Fox(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        # All agents start with the same energy level
        self.energy = 1
        self.death_cause = "alive"
        self.change_image(1)

    def update(self):
        # Save the type of the animal
        self.save_data("kind", "fox")
        self.save_data("death_cause", self.death_cause)
        # Decrease the energy of the fox
        self.energy -= self.config.energy_decrease_rate
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
            self.config.agents -= 1
            self.energy = 1
        # Reproduce if caring capacity is not exceeded
        if self.config.agents >= self.config.caring_capacity:
            self.config.reproduce = False
        else: self.config.reproduce = True
        if self.config.reproduce:
            self.asexualReproduction()

    def asexualReproduction(self):
        if util.probability(self.config.rabbit_reproduction_prob):
            self.reproduce()
            self.config.agents += 1
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
        # Reproduce if caring capacity is not exceeded
        if self.config.agents >= self.config.caring_capacity:
            self.config.reproduce = False
        else: self.config.reproduce = True
        if self.config.reproduce:
            self.asexualReproduction()

    def asexualReproduction(self):
        if util.probability(self.config.rabbit_reproduction_prob):
            self.reproduce()
            self.config.agents += 1



config = Config()
n_fox = 50
n_rabbit = 50
n = n_fox + n_rabbit
experiments = 30

for i in range(experiments):
    filename = "competition_basic_{}.csv".format(i)
    df = (
        HeadlessSimulation(
            CompetitionConfig(
                image_rotation=True,
                movement_speed=1,
                radius=15,
                seed=i,
                window=Window(width=n * 10, height=n * 10),
                agents=n,
                duration=300 * 60,
                fps_limit=0,
            )
        )
            .batch_spawn_agents(n_fox, Fox, images=["/Users/ania/Desktop/Collective_Intelligence_Group_Ocean/images/white.png", "/Users/ania/Desktop/Collective_Intelligence_Group_Ocean/images/popular_cockroaches.png"])
            .batch_spawn_agents(n_rabbit, Rabbit, images=["/Users/ania/Desktop/Collective_Intelligence_Group_Ocean/images/white.png", "/Users/ania/Desktop/Collective_Intelligence_Group_Ocean/images/popular_cockroaches.png"])
            .run()
            .snapshots
            # Get the number of animals per death cause per timeframe
            .groupby(["frame", "kind", "death_cause"])
            # Get the number of rabbits and foxes per timeframe
            .agg(pl.count('id').alias("number of agents"))
            .sort(["frame", "kind", "death_cause"])
            .write_csv(filename)
    )

    #print(df)

    #n_new = df.get_column("number of agents")[-2] + df.get_column("number of agents")[-1]
    #print('Proportion of foxes of all agents: {}'.format(df.get_column("number of agents")[-2] / n_new))
    #print('Proportion of rabbits of all agents: {}'.format(df.get_column("number of agents")[-1] / n_new))
