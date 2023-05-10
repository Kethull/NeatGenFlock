import pygame
from entity import Entity
import numpy as np
from pheromone import Pheromone
import neat
import time


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

    def create_new_prey(self):
        # Create a new prey entity with the same position and speed
        new_prey = Prey(self.position, self.width, self.height, self.speed)
        new_prey.color = self.color
        new_prey.radius = self.radius
        new_prey.max_speed = self.max_speed
        new_prey.avoidance_distance = self.avoidance_distance
        new_prey.cohesion_distance = self.cohesion_distance
        new_prey.alignment_distance = self.alignment_distance
        new_prey.communication_distance = self.communication_distance
        new_prey.communication_strength = self.communication_strength
        new_prey.pheromone_strength = self.pheromone_strength
        new_prey.survival_time = self.survival_time
        new_prey.score = self.score
        new_prey.time_since_last_score = self.time_since_last_score
        new_prey.energy = self.energy
        new_prey.energy_regeneration_rate = self.energy_regeneration_rate
        new_prey.original_energy_regeneration_rate = self.original_energy_regeneration_rate
        new_prey.energy_regeneration_range = self.energy_regeneration_range
        return new_prey
