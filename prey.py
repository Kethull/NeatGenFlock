import pygame
from entity import Entity
import numpy as np
from pheromone import Pheromone
import neat
import time
import random


class Prey(Entity):
    def __init__(self, position, width, height, speed=None):
        if speed is None:
            speed = [0, 0]
        super().__init__(position, speed)
        self.color = (0, 255, 0)  # define a default color for the prey
        self.radius = 5  # Set the radius here
        self.max_speed = speed
        self.avoidance_distance = 110
        self.cohesion_distance = 110
        self.alignment_distance = 110
        self.communication_distance = 150
        self.communication_strength = 0.5
        self.pheromone_strength = 0.1
        self.survival_time = 0
        self.score = 0
        self.time_since_last_score = 0
        self.color = (0, 255, 0)
        self.speed = speed
        self.turn_rate = 0.1  # Smaller values make turning smoother
        self.width = width
        self.height = height
        self.separation_distance = 110

        self.energy = 100  # Initial energy level
        self.energy_regeneration_rate = 0.2  # Initial energy regeneration rate
        self.original_energy_regeneration_rate = self.energy_regeneration_rate
        self.energy_regeneration_range = 100

    def apply_boids_rules(self, prey_list):
        # Filter out the current prey from the list
        other_prey = [prey for prey in prey_list if prey != self]

        if other_prey:
            cohesion = self._rule_cohesion(other_prey)
            separation = self._rule_separation(other_prey, self.separation_distance)
            alignment = self._rule_alignment(other_prey)

            # Apply the avoidance rule for the edges of the screen
            avoidance = self._rule_avoid_edges(self.width, self.height, distance=50)

            # Adjust weights for each rule (1.0, 1.0, 1.0)
            self.velocity += cohesion * 1.0 + separation * 1.0 + alignment * 1.0 + avoidance * 0.5

            # Limit the prey's speed
            speed = np.linalg.norm(self.velocity)
            if speed > self.max_speed:
                self.velocity = (self.velocity / speed) * self.max_speed

        # Calculate energy regeneration factor based on proximity to other prey
        total_increase = 0  # Variable to store the total increase in energy_regeneration_rate

        for other_prey in prey_list:
            if other_prey != self:
                distance = np.linalg.norm(other_prey.position - self.position)
                if distance < self.energy_regeneration_range:
                    increase = (1 - distance / self.energy_regeneration_range) * self.energy_regeneration_rate
                    total_increase += increase

        # Limit the total increase to 20% of the original energy_regeneration_rate
        max_increase = 0.2 * self.original_energy_regeneration_rate
        total_increase = min(total_increase, max_increase)

        # Apply the total increase to the energy_regeneration_rate
        self.energy_regeneration_rate += total_increase

    def avoid_predators(self, predators, avoidance_distance=50):
        avoidance_force = np.zeros(2)
        for predator in predators:
            distance = np.linalg.norm(predator.position - self.position)
            if distance < avoidance_distance:
                avoidance_force += (self.position - predator.position) / distance
        self.velocity += avoidance_force * self.speed

        # Limit the prey's speed
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity = (self.velocity / speed) * self.max_speed

    def update(self, predators, prey_list):
        old_position = self.position.copy()
        self.apply_boids_rules(prey_list)
        self.avoid_predators(predators)
        
        # LERP: linear interpolation between current velocity and desired velocity
        desired_velocity = self.velocity.copy()
        self.velocity = self.velocity * (1 - self.turn_rate) + desired_velocity * self.turn_rate

        self.update_position()
        new_position = self.position

        if np.linalg.norm(new_position - old_position) < 1e-6:  # Check if the prey is stationary
            if time.time() - self.last_moved_time >= 4:  # Check if the prey has been stationary for 4 seconds
                self.create_new_prey()
                self.score = 0  # Reset score after creating a new prey
                if self.energy <= 100:
                    self.energy += 1
        else:
            self.last_moved_time = time.time()
            self.score += 1  # Add a point for staying alive

        # Decrease energy by 1 for movement
        self.energy -= 1

        # Regenerate energy if it falls below the maximum value
        if self.energy < 100 and np.linalg.norm(self.velocity) < 1e-6:
            self.energy += self.energy_regeneration_rate

        # Cap the energy at the maximum value
        self.energy = min(self.energy, 100)


    def emit_pheromone(self, pheromones):
        # Emit a pheromone at the prey's current position
        pheromones.append(Pheromone(self.position, intensity=5))

    def render(self, screen):
        if not np.isnan(self.position[0]) and not np.isnan(self.position[1]):
            pygame.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), self.radius)

            # Draw the eyes to indicate direction
            direction = self.velocity / np.linalg.norm(self.velocity)
            eye_offset = np.array([direction[1], -direction[0]]) * self.radius * 0.3
            eye_distance = direction * self.radius * 0.6
            eye_radius = 2

            left_eye_position = self.position + eye_distance - eye_offset
            right_eye_position = self.position + eye_distance + eye_offset

            pygame.draw.circle(screen, (0, 0, 0), left_eye_position.astype(int), eye_radius)
            pygame.draw.circle(screen, (0, 0, 0), right_eye_position.astype(int), eye_radius)


    def create_new_prey(self, prey_list):
        # 1. Select two parent prey randomly from the existing prey population
        parent1, parent2 = random.sample(prey_list, 2)

        # 2. Perform crossover by averaging the attributes of the two parent prey
        max_speed = (parent1.max_speed + parent2.max_speed) / 2
        avoidance_distance = (parent1.avoidance_distance + parent2.avoidance_distance) / 2
        cohesion_distance = (parent1.cohesion_distance + parent2.cohesion_distance) / 2
        alignment_distance = (parent1.alignment_distance + parent2.alignment_distance) / 2
        communication_distance = (parent1.communication_distance + parent2.communication_distance) / 2
        communication_strength = (parent1.communication_strength + parent2.communication_strength) / 2
        pheromone_strength = (parent1.pheromone_strength + parent2.pheromone_strength) / 2
        separation_distance = (parent1.separation_distance + parent2.separation_distance) / 2

        # 3. Apply mutation to the offspring's attributes by introducing small random changes
        mutation_rate = 0.1  # Adjust this value to control the rate of mutation
        max_speed *= 1 + (random.random() * 2 - 1) * mutation_rate
        avoidance_distance *= 1 + (random.random() * 2 - 1) * mutation_rate
        cohesion_distance *= 1 + (random.random() * 2 - 1) * mutation_rate
        alignment_distance *= 1 + (random.random() * 2 - 1) * mutation_rate
        communication_distance *= 1 + (random.random() * 2 - 1) * mutation_rate
        communication_strength *= 1 + (random.random() * 2 - 1) * mutation_rate
        pheromone_strength *= 1 + (random.random() * 2 - 1) * mutation_rate
        separation_distance *= 1 + (random.random() * 2 - 1) * mutation_rate

        # 4. Create a new prey with the modified attributes
        offspring_position = (parent1.position + parent2.position) / 2
        offspring = Prey(offspring_position, self.width, self.height, speed=[max_speed, max_speed])
        offspring.avoidance_distance = avoidance_distance
        offspring.cohesion_distance = cohesion_distance
        offspring.alignment_distance = alignment_distance
        offspring.communication_distance = communication_distance
        offspring.communication_strength = communication_strength
        offspring.pheromone_strength = pheromone_strength
        offspring.separation_distance = separation_distance

        prey_list.append(offspring)  # Add the new prey to the population

