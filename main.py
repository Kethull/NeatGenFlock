import pygame
import numpy as np
from predator import Predator
from prey import Prey
#from pheromone import Pheromone
import os
import neat as neat_package


# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("NEAT Evolution Simulation")

# Set up the clock
clock = pygame.time.Clock()

# Set up font
font = pygame.font.SysFont('Arial', 30)

def run_simulation(genomes, config):
    num_predators = 10
    num_prey = 50
    predator_speed = 0.7
    prey_speed = 0.9

    for genome_id, genome in genomes:
        # Initialize predators and prey using the genomes
        predators = [Predator(np.random.rand(2) * np.array([width, height]), width, height, predator_speed) for _ in range(num_predators)]
        prey_list = [Prey(np.random.rand(2) * np.array([width, height]), width, height, prey_speed) for _ in range(num_prey)]
        #pheromones = []

        # Main simulation loop
        running = True
        frame_count = 0
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Clear the screen
            screen.fill((255, 255, 255))

            # Update predators
            for predator in predators:
                predator.update(predators, prey_list)
                if not np.isnan(predator.position).any():
                    predator.render(screen)

            # Update prey
            for prey in prey_list:
                prey.update(predators, prey_list)
                if not np.isnan(prey.position).any():
                    prey.render(screen)

            # # Emit pheromones periodically
            # if frame_count % 5 == 0:
            #     for predator in predators:
            #         predator.emit_pheromone(pheromones)
            #     for prey in prey_list:
            #         prey.emit_pheromone(pheromones)

            # # Update pheromones and remove those with zero intensity
            # delta_time = clock.tick(60) / 1000.0
            # pheromones = [pheromone for pheromone in pheromones if pheromone.intensity > 0]
            # for pheromone in pheromones:
            #     pheromone.update(delta_time)
            #     pheromone.render(screen)

            # Display the new frame
            pygame.display.flip()

            # Increment frame count
            frame_count += 1

        # Calculate the fitness for each genome using the scoring systems
        predator_fitness = sum([predator.score for predator in predators])
        prey_fitness = sum([prey.score for prey in prey_list])
        genome.fitness = predator_fitness - prey_fitness

def run_neat():
    # Load the configuration file
    config_path = os.path.join(os.path.dirname(__file__), "neat_config.txt")
    config = neat_package.Config(neat_package.DefaultGenome, neat_package.DefaultReproduction,
                                  neat_package.DefaultSpeciesSet, neat_package.DefaultStagnation,
                                  config_path)

    # Create a new population
    pop = neat_package.Population(config)

    # Add a stdout reporter to show progress in the terminal
    pop.add_reporter(neat_package.StdOutReporter(True))
    stats = neat_package.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat_package.Checkpointer(5))

    # Run the NEAT algorithm for up to 50 generations
    winner = pop.run(run_simulation, 50)

    # Display the winning genome
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    run_neat()
    pygame.quit()

