from circleshape import CircleShape
import pygame
class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(screen,"white",self.position,self.radius,2)