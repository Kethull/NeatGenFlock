#prey.py
import pygame
from entity import Entity
import numpy as np
from pheromone import Pheromone
import neat_config as neat
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
        self.separation_distance = 110
        self.communication_distance = 150
        self.communication_strength = 0.5
        self.pheromone_strength = 0.1
        self.survival_time = 0
        self.score = 0
        self.time_since_last_score = 0
        self.color = (0, 255, 0)
        self.speed = speed
        self.energy = 100
        self.energy_regeneration_rate = 0.01
        self.regenerating = False
        self.width = width
        self.height = height
        self.score = 0
        self.last_moved_time = time.time()

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
            self.velocity += cohesion * 1.0 + separation * 1.0 + alignment * 1.0 + avoidance * 0.8

            # Limit the prey's speed
            speed = np.linalg.norm(self.velocity)
            if speed > self.max_speed:
                self.velocity = (self.velocity / speed) * self.max_speed

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

        if self.energy <= 1:
            self.energy += self.energy_regeneration_rate  # Regenerate energy
            self.regenerating = True
        else:
            if not self.regenerating:
                #self.apply_boids_rules(prey_list)
                #self.avoid_predators(predators)
                self.update_position()            

        new_position = self.position

        if np.all(new_position == old_position):  # Check if the prey is stationary
            if time.time() - self.last_moved_time >= 4:  # Check if the prey has been stationary for 4 seconds
                self.create_new_prey()
                self.score = 0  # Reset score after creating a new prey
            if self.energy < 100:
                self.energy += self.energy_regeneration_rate  # Regenerate energy
        else:
            self.last_moved_time = time.time()
            self.score += 1  # Add a point for staying alive
            self.energy -= 1  # Reduce energy for moving

        if self.energy > 30:
            self.regenerating = False


    def create_new_prey(self):
        # Implement your genetic algorithm for creating a new prey here
        pass

    def emit_pheromone(self, pheromones):
        # Emit a pheromone at the prey's current position
        pheromones.append(Pheromone(self.position, intensity=5))

    def render(self, screen):
        if not np.isnan(self.position[0]) and not np.isnan(self.position[1]):
            pygame.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), self.radius)

   