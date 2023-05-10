# entity.py
import pygame
import numpy as np

class Entity:
    def __init__(self, position, speed=1):
        if np.isnan(position).any():
            raise ValueError("Invalid position argument: {}".format(position))
        self.position = position.astype(float)
        self.velocity = np.random.randn(2) * speed
        self.acceleration = np.zeros(2)
        self.cohesion_speed = 0.9
        self.separation_speed = 0.9
        self.alignment_speed = 0.9
        self.max_speed = 5

    def update(self, other_entities):
        if np.isnan(self.position).any():
            raise ValueError("Invalid position value: {}".format(self.position))
        self.acceleration *= 0
        self.acceleration += self._rule_cohesion(other_entities)
        self.acceleration += self._rule_separation(other_entities)
        self.acceleration += self._rule_alignment(other_entities)
        self.velocity += self.acceleration
        self.velocity = np.clip(self.velocity, -self.max_speed, self.max_speed)
        self.update_position()

    def update_position(self):
        if np.isnan(self.position).any():
            raise ValueError("Invalid position value: {}".format(self.position))
        self.position += self.velocity

    def render(self, screen):
        pass  # To be implemented in subclasses

    def _rule_cohesion(self, other_entities):
        center_of_mass = np.mean([entity.position for entity in other_entities], axis=0)
        return (center_of_mass - self.position) * self.cohesion_speed

    def _rule_separation(self, other_entities, separation_distance=50):
        separation_force = np.zeros(2)
        for entity in other_entities:
            distance = np.linalg.norm(entity.position - self.position)
            if distance < separation_distance:
                separation_force -= (entity.position - self.position) / distance
        return separation_force * self.separation_speed

    # def _rule_separation(self, other_entities, separation_distance=50, min_separation_distance=50):
    #     separation_force = np.zeros(2)
    #     for entity in other_entities:
    #         distance = np.linalg.norm(entity.position - self.position)
    #         if distance < separation_distance and distance > min_separation_distance:
    #             separation_force -= (entity.position - self.position) / distance
    #     return separation_force * self.separation_speed

    def _rule_alignment(self, other_entities):
        average_velocity = np.mean([entity.velocity for entity in other_entities], axis=0)
        return (average_velocity - self.velocity) * self.alignment_speed
    
    def _rule_avoid_edges(self, screen_width, screen_height, distance):
        avoidance_force = np.zeros(2)
        if self.position[0] < distance:
            avoidance_force[0] += distance - self.position[0]
        elif self.position[0] > screen_width - distance:
            avoidance_force[0] -= self.position[0] - (screen_width - distance)
        if self.position[1] < distance:
            avoidance_force[1] += distance - self.position[1]
        elif self.position[1] > screen_height - distance:
            avoidance_force[1] -= self.position[1] - (screen_height - distance)
        return avoidance_force

