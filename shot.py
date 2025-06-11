from circleshape import CircleShape
import pygame
from constants import *


class Shot(CircleShape):
    def __init__(self, x, y,radius,color):
        super().__init__(x, y, radius)
        self.color=color
    
    def draw(self, screen):
        pygame.draw.circle(screen,self.color,self.position,self.radius,2)

    def update(self, dt):
        self.position = self.position + (self.velocity * dt)