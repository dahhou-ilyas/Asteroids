import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
import sys
from socketserverconfig import connect_to_server,listen_to_server
import threading


def main():
	#connect to server
	sock, player_id = connect_to_server()
	#state game
	game_state = {} 
	players_by_id = {}

	def update_game_state(state):
		global game_state
		game_state = state

	threading.Thread(
	    target=listen_to_server,
	    args=(sock, update_game_state),
	    daemon=True
	).start()

	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
	clock = pygame.time.Clock()
  
	updatable = pygame.sprite.Group()
	drawable = pygame.sprite.Group()
	#asteroids = pygame.sprite.Group()
	#shots = pygame.sprite.Group()

	Player.containers = (updatable, drawable)
	#Asteroid.containers = (asteroids, updatable, drawable)
	#AsteroidField.containers = (updatable)
	#Shot.containers = (shots,updatable, drawable)

	player = Player(SCREEN_WIDTH/2,SCREEN_HEIGHT/2,player_id)
	#asteroidField = AsteroidField()


	dt = 0
	while True :
		for event in pygame.event.get():
    			if event.type == pygame.QUIT:
        			return
				
		updatable.update(dt,sock)

		# for asteroid in asteroids:
		# 	if asteroid.collides_with(player):
		# 		print("Game over!")
		# 		sys.exit()
		# 	for shot in shots:
		# 		if shot.collides_with(asteroid):
		# 			asteroid.split()
		# 			shot.kill()


		for player_data in game_state.get("players", []):
			pid = player_data["id"]
			pos = player_data["position"]
			rot = player_data["rotation"]
			radius = player_data.get("radius", PLAYER_RADIUS)

    		# couleur pour différencier toi des autres (non utilisé ici mais possible plus tard)
			color = "red" if pid == player_id else "white"
			if pid not in players_by_id:
    		    # Créer une instance Player (hérite de CircleShape)
				player = Player(pos["x"], pos["y"],pid)
				player.rotation = rot
				player.radius = radius
				players_by_id[pid] = player
			else:
				    # Mettre à jour la position/rotation
				player = players_by_id[pid]
				player.position.x = pos["x"]
				player.position.y = pos["y"]
				player.rotation = rot
				player.radius = radius 

		screen.fill("black")


		for obj in drawable: 
			obj.draw(screen)
		
		pygame.display.flip()
		
		# limit the framerate to 60 FPS
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

# comment on peut crée un mode multiplayer qui permet de deux player de player dans un single gameplay donc comment faire (je besoin de travaillé avec socket with go et socket en create my own protocol)
