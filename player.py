from circleshape import CircleShape
from constants import *
import pygame
from shot import Shot
import json
class Player(CircleShape):
    def __init__(self, x, y,player_id):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.space_pressed = False
        self.player_id=player_id
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
    
    def update(self, dt,sock):
        self.shoot_timer -= dt
        
        keys = pygame.key.get_pressed()

        inputs = {
            "left": keys[pygame.K_LEFT],
            "right": keys[pygame.K_RIGHT],
            "forward": keys[pygame.K_UP],
            "backward": keys[pygame.K_DOWN],
            "shoot": keys[pygame.K_SPACE],
        }
        
        # if keys[pygame.K_LEFT]:
        #     self.rotate(dt)
        # if keys[pygame.K_RIGHT]:
        #     self.rotate(-dt)
        # if keys[pygame.K_DOWN]:
        #     self.move(-dt)
        # if keys[pygame.K_UP]:
        #     self.move(dt)
        # if keys[pygame.K_SPACE]:
        #     self.shoot()

        message = {
            "type": "input",
            "data": {
                "player_id": self.player_id,
                "inputs": inputs
            }
        }
        
        try:
            sock.sendall((json.dumps(message) + "\n").encode())
        except Exception as e:
            print(f"⚠️ Erreur envoi au serveur : {e}")
        
            

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

        