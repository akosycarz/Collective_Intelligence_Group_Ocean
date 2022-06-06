from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    ...


class Bird(Agent):
    ...


(
    # Step 1: Create a new simulation.
    Simulation(FlockingConfig(image_rotation=True, movement_speed=1, radius=50))
    # Step 2: Add 50 birds to the simulation.
    .batch_spawn_agents(50, Bird, images=["images/triangle.png"])
    # Step 3: Profit! 🎉
    .run()
)
