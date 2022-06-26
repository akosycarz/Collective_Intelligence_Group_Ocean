import polars as pl
import seaborn as sns

from vi import Agent, Simulation, util
from vi.config import Window, Config, dataclass, deserialize


@deserialize
@dataclass
class CompetitionConfig(Config):
    # Add all parameters here
    rabbit_reproduction_prob: float = 0.01
    fox_reproduction_prob: float = 0.5
    energy_decrease_rate: float = 0.002
    hunger_threshold: float = 0.8
    fox_reproduction_threshold: float = 0.5

    def weights(self) -> tuple[float]:
        return (self)

    ...


class Fox(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        # All agents start with the same energy level
        self.energy = 0.5 - 0.01
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
        # Reproduce
        self.asexualReproduction()

    def asexualReproduction(self):
        if util.probability(self.config.rabbit_reproduction_prob):
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
        # Reproduce
        self.asexualReproduction()

    def asexualReproduction(self):
        if util.probability(self.config.rabbit_reproduction_prob):
            self.reproduce()


config = Config()
n_fox = 50
n_rabbit = 50
n = n_fox + n_rabbit

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
        .batch_spawn_agents(n_fox, Fox, images=["images/white.png", "images/red.png"])
        .batch_spawn_agents(n_rabbit, Rabbit, images=["images/white.png", "images/red.png"])
        .run()
        .snapshots
        # Get the number of animals per death cause per timeframe
        .groupby(["frame", "kind", "death_cause"])
        # Get the number of rabbits and foxes per timeframe
        .agg(pl.count('id').alias("number of agents"))
        .sort(["frame", "kind", "death_cause"])
)

print(df)

n_new = df.get_column("number of agents")[-2] + df.get_column("number of agents")[-1]
print('Proportion of foxes of all agents: {}'.format(df.get_column("number of agents")[-2] / n_new))
print('Proportion of rabbits of all agents: {}'.format(df.get_column("number of agents")[-1] / n_new))
