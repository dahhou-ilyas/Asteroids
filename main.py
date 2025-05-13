import pygame
from constants import *
from player import Player
def main():
	print("Starting Asteroids!")
	print(f"Screen width: {SCREEN_WIDTH}")
	print(f"Screen height: {SCREEN_HEIGHT}")
	
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
	clock = pygame.time.Clock()
	dt = 0
	player = Player(SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
	while True :
		for event in pygame.event.get():
    			if event.type == pygame.QUIT:
        			return
		screen.fill("black")
		player.draw(screen)
		player.update(dt)
		pygame.display.flip()
		dt = clock.tick(60) / 1000

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