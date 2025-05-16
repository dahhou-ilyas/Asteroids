import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
import sys

def main():
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
	clock = pygame.time.Clock()
  
	updatable = pygame.sprite.Group()
	drawable = pygame.sprite.Group()
	asteroids = pygame.sprite.Group()
	shots = pygame.sprite.Group()

	Player.containers = (updatable, drawable)
	Asteroid.containers = (asteroids, updatable, drawable)
	AsteroidField.containers = (updatable)
	Shot.containers = (shots,updatable, drawable)

	player = Player(SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
	asteroidField = AsteroidField()

	dt = 0
	while True :
		for event in pygame.event.get():
    			if event.type == pygame.QUIT:
        			return
				
		updatable.update(dt)

		for asteroid in asteroids:
			if asteroid.collides_with(player):
				print("Game over!")
				sys.exit()
			for shot in shots:
				if shot.collides_with(asteroid):
					asteroid.kill()
					shot.kill()

		screen.fill("black")

		for obj in drawable: 
			obj.draw(screen)
		
		pygame.display.flip()
		
		# limit the framerate to 60 FPS
		dt = clock.tick(60) / 1000
		print(dt)

if __name__ == "__main__":
	main()

# speed : vitesse en pixels par seconde (ex. : 200 px/s)
# dt : delta time, durée écoulée entre deux images (en secondes)

# ➤ speed * dt représente la distance à parcourir pendant le temps écoulé entre deux images.
# Cela permet un déplacement fluide, peu importe le nombre de FPS (images par seconde).

# ➤ En simplifié : c’est le nombre de pixels à bouger pendant cette frame
# pour respecter une vitesse constante dans le temps réel.

# Exemple :
# Si speed = 200 (pixels/seconde) et dt = 0.016 (≈ 60 FPS),
# alors le déplacement sera 200 * 0.016 = 3.2 pixels sur cette frame.

# comment on peut crée un mode multiplayer qui permet de deux player de player dans un single gameplay donc comment faire (je besoin de travaillé avec socket with go et socket en create my own protocol)
