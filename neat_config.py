#neat_config.py
import neat

# Define the fitness function for the predators
def predator_fitness(predator):
    return sum(p.score for p in predator.caught_prey)

# Define the fitness function for the prey
def prey_fitness(prey):
    return 1 / (1 + prey.survival_time)

# Set up the NEAT configuration
config_file = "neat_config.txt"
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_file)

# Set up the population
population = neat.Population(config)

# Add reporters to output statistics during evolution
stats = neat.StatisticsReporter()
population.add_reporter(stats)
population.add_reporter(neat.StdOutReporter(True))

# Set up the simulation
num_predators = 10
num_prey = 50
predator_speed = 0.7
prey_speed = 0.8

def eval_genomes(genomes, config):
    # Create the predator and prey classes from the genomes
    predators = []
    prey_list = []
    for genome_id, genome in genomes:
        if genome_id < num_predators:
            predators.append(Predator(position=np.random.rand(2) * np.array([width, height]),
                                      width=width, height=height, speed=predator_speed))
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            predators[-1].set_brain(net)
            genome.fitness = 0.0
        else:
            prey_list.append(Prey(position=np.random.rand(2) * np.array([width, height]),
                                  width=width, height=height, speed=prey_speed))
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            prey_list[-1].set_brain(net)
            genome.fitness = 0.0

    # Run the simulation
    frame_count = 0
    while frame_count < 3000:
        # Update predators
        for predator in predators:
            predator.update(predators, prey_list)

        # Update prey
        for prey in prey_list:
            prey.update(predators, prey_list)

        # Emit pheromones periodically
        if frame_count % 5 == 0:
            for predator in predators:
                predator.emit_pheromone(pheromones)
            for prey in prey_list:
                prey.emit_pheromone(pheromones)

        # Update pheromones and remove those with zero intensity
        delta_time = clock.tick(60) / 1000.0
        pheromones = [pheromone for pheromone in pheromones if pheromone.intensity > 0]
        for pheromone in pheromones:
            pheromone.update
