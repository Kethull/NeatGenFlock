# predator.py
import pygame
from entity import Entity
import numpy as np
from pheromone import Pheromone
import neat_config as neat

class Predator(Entity):
    def __init__(self, position, width, height, speed=None):
        if speed is None:
            speed = [0, 0]
        super().__init__(position)
        self.color = (255, 0, 0) # define a default color for the predator
        self.radius = 5 # Set the radius here
        self.max_speed = speed
        self.chase_speed = speed
        self.avoidance_distance = 110
        self.communication_distance = 150
        self.communication_strength = 0.5
        self.pheromone_strength = 0.1
        self.survival_time = 0
        self.width = width
        self.height = height
        self.speed = speed
        self.turn_rate = 0.1  # Smaller values make turning smoother
        self.energy = 100
        self.regenerating = False
        self.separation_distance = 110
        self.score = 0

    def target_closest_prey(self, prey_list):
        if len(prey_list) > 0:
            closest_prey = min(prey_list, key=lambda prey: np.linalg.norm(prey.position - self.position))
            self.velocity += (closest_prey.position - self.position) * self.chase_speed

            # Limit the predator's speed
            speed = np.linalg.norm(self.velocity)
            if speed > self.max_speed:
                self.velocity = (self.velocity / speed) * self.max_speed
            

    def apply_boids_rules(self, predators, prey_list):
        # Filter out the current predator from the list
        other_predators = [predator for predator in predators if predator != self]

        cohesion = self._rule_cohesion(other_predators)
        separation = self._rule_separation(other_predators, self.separation_distance)
        alignment = self._rule_alignment(other_predators)

        # Apply the avoidance rule for the edges of the screen
        edge_avoidance = self._rule_avoid_edges(self.width, self.height, distance=50)

        # Adjust weights for each rule (1.0, 1.0, 1.0)
        self.velocity += cohesion * 1.0 + separation * 1.0 + alignment * 1.0 + edge_avoidance * 1.0

        # Limit the predator's speed
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity = (self.velocity / speed) * self.max_speed

    def update(self, predators, prey_list):
        old_position = self.position.copy()

        if self.energy <= 1:
            self.regenerating = True
        else:
            if not self.regenerating:
                self.apply_boids_rules(predators, prey_list)
                self.target_closest_prey(prey_list)
                self.catch_prey(prey_list)

                # LERP: linear interpolation between current velocity and desired velocity
                desired_velocity = self.velocity.copy()
                self.velocity = self.velocity * (1 - self.turn_rate) + desired_velocity * self.turn_rate

                self.update_position()

        new_position = self.position

        if not np.all(new_position == old_position):
            self.energy -= 1  # Reduce energy for moving

        if self.energy <= 0:
            predators.remove(self)  # Remove predator if energy reaches zero

        if self.energy > 30:
            self.regenerating = False

                

    def catch_prey(self, prey_list, catch_distance=5):
        caught_prey = []
        for prey in prey_list:
            distance = np.linalg.norm(prey.position - self.position)

            if distance < catch_distance:
                    caught_prey.append(prey)
                    self.score += 1  # Add a point for catching prey
                    self.energy -= 1
            for prey in caught_prey:
                prey_list.remove(prey)
                prey.score = 0  # Reset the score of the caught prey
                self.create_new_predator()

    def create_new_predator(self):
        # Implement your genetic algorithm for creating a new predator here
        pass

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


    def emit_pheromone(self, pheromones):
        # Emit a pheromone at the predator's current position
        pheromones.append(Pheromone(self.position, intensity=10))
