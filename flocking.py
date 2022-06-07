from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 0.6
    cohesion_weight: float = 0.6
    separation_weight: float = 0.1
    delta_time: float = 2
    mass: int = 30
    maxVelocity: int = 5

    def weights(self) -> tuple[float , float , float]:
        return (self.alignment_weight , self.cohesion_weight , self.separation_weight)
    ...


class Bird(Agent):
    config: FlockingConfig

    def update(self):
        pass

    def change_position(self):
        # Get the neighbours of the boid
        neighbours = self.in_proximity_accuracy().collect_set()
        # If the set in empty, wandering behaviour
        if len(neighbours) == 0:
            super(Bird, self).change_position()
        # Else, calculate new direction
        else:
            # Calculate alignment
            alignment = self.alignment(neighbours)
            # Calculate separation
            separation = self.separation(neighbours)
            # Calculate cohesion
            cohesion = self.cohesion(neighbours)
            # Calculate new force to update velocity
            f_total = (self.config.alignment_weight*alignment + self.config.separation_weight*separation + self.config.cohesion_weight*cohesion) / self.config.mass
            self.move = self.move + f_total
            # Normalize velocity
            if self.move[1] > self.config.maxVelocity:
                self.move.normalize() * self.config.maxVelocity
            # Change position
            self.pos = self.pos * self.config.delta_time

    def alignment(self, neighbours):
        average = [0, 0]
        for i in neighbours:
            average += i[0].move
        
        return (average / len(neighbours)) - self.move
    
    def separation(self, neighbours):
        distances = [0, 0]
        for i in neighbours:
            distances += (self.pos - i[0].pos)
        return distances*(1/len(neighbours))
    
    def cohesion(self, neighbours):
        positions = [0, 0]
        for i in neighbours:
            positions += i[0].pos
        fc = (positions / len(neighbours)) - self.pos

        return fc - self.move


(
    # Step 1: Create a new simulation.
    Simulation(FlockingConfig(image_rotation=True, movement_speed=1, radius=50))
    # Step 2: Add 50 birds to the simulation.
    .batch_spawn_agents(50, Bird, images=["images/triangle.png"])
    # Step 3: Profit! 🎉
    .run()
)

