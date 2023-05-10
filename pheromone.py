#pheromone.py
import pygame
import numpy as np

class Pheromone:
    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity
        self.color = (255, 255, 255)
        self.radius = 3

    def update(self, delta_time):
        self.intensity -= delta_time

    def is_expired(self):
        return self.intensity <= 0

    def render(self, screen):
        pygame.draw.circle(screen, self.color, self.position.astype(int), self.radius)
