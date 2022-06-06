from vi import Agent, Simulation

(
    Simulation()
    .batch_spawn_agents(500, Agent, images=["images/white.png"])
    .run()
)