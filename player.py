from circleshape import CircleShape
from constants import *
import pygame
from shot import Shot
class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.space_pressed = False

        self.shoot_timer = 0

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def draw(self, screen):
        pygame.draw.polygon(screen,"white",self.triangle(),2)
    
    def update(self, dt):
        self.shoot_timer -= dt
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotate(dt)
        if keys[pygame.K_d]:
            self.rotate(-dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_SPACE]:
            self.shoot()
        
        
            

    def rotate(self,dt):
        self.rotation = self.rotation + (PLAYER_TURN_SPEED * dt) 

    def move(self,dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation) * (PLAYER_SPEED_RUN * dt) 
        self.position = self.position + forward

    def shoot(self):
        if self.shoot_timer > 0:
            return
        self.shoot_timer = PLAYER_SHOOT_COOLDOWN
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        shot = Shot(self.position.x,self.position.y,SHOT_RADIUS)
        shot.velocity = PLAYER_SHOOT_SPEED * forward

        