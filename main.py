# import pygame
# from constants import *
# from player import Player
# from asteroid import Asteroid
# from asteroidfield import AsteroidField
# from shot import Shot
# import sys
# from socketserverconfig import connect_to_server,listen_to_server
# import threading


# def main():
# 	#connect to server
# 	sock, player_id = connect_to_server()
# 	#state game
# 	game_state = {} 
# 	players_by_id = {}

# 	def update_game_state(state):
# 		nonlocal game_state
# 		game_state = state

# 	threading.Thread(
# 	    target=listen_to_server,
# 	    args=(sock, update_game_state),
# 	    daemon=True
# 	).start()

# 	pygame.init()
# 	screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
# 	clock = pygame.time.Clock()
  
# 	updatable = pygame.sprite.Group()
# 	drawable = pygame.sprite.Group()
# 	#asteroids = pygame.sprite.Group()
# 	#shots = pygame.sprite.Group()

# 	Player.containers = (updatable, drawable)
# 	#Asteroid.containers = (asteroids, updatable, drawable)
# 	#AsteroidField.containers = (updatable)
# 	#Shot.containers = (shots,updatable, drawable)

# 	player = Player(SCREEN_WIDTH/2,SCREEN_HEIGHT/2,player_id)
# 	#asteroidField = AsteroidField()


# 	dt = 0
# 	while True :
# 		for event in pygame.event.get():
#     			if event.type == pygame.QUIT:
#         			return
				
# 		updatable.update(dt,sock)

# 		# for asteroid in asteroids:
# 		# 	if asteroid.collides_with(player):
# 		# 		print("Game over!")
# 		# 		sys.exit()
# 		# 	for shot in shots:
# 		# 		if shot.collides_with(asteroid):
# 		# 			asteroid.split()
# 		# 			shot.kill()


# 		for player_data in game_state.get("players", []):
# 			pid = player_data["id"]
# 			pos = player_data["position"]
# 			rot = player_data["rotation"]
# 			radius = player_data.get("radius", PLAYER_RADIUS)

#     		# couleur pour différencier toi des autres (non utilisé ici mais possible plus tard)
# 			color = "red" if pid == player_id else "white"
# 			if pid not in players_by_id:
#     		    # Créer une instance Player (hérite de CircleShape)
# 				player = Player(pos["x"], pos["y"],pid)
# 				player.rotation = rot
# 				player.radius = radius
# 				players_by_id[pid] = player
# 			else:
# 				    # Mettre à jour la position/rotation
# 				player = players_by_id[pid]
# 				player.position.x = pos["x"]
# 				player.position.y = pos["y"]
# 				player.rotation = rot
# 				player.radius = radius 

# 		screen.fill("black")


# 		for obj in drawable: 
# 			obj.draw(screen)
		
# 		pygame.display.flip()
		
# 		# limit the framerate to 60 FPS
# 		dt = clock.tick(60) / 1000

# if __name__ == "__main__":
# 	main()

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

import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
import sys
from socketserverconfig import connect_to_server, listen_to_server
import threading

def main():
    # Connexion au serveur
    sock, player_id = connect_to_server()
    
    # État du jeu
    game_state = {}
    players_by_id = {}
    shots_by_id = {}
    asteroids_by_id = {}
    
    def update_game_state(state):
        nonlocal game_state
        game_state = state
    
    # Démarrer le thread d'écoute
    threading.Thread(
        target=listen_to_server,
        args=(sock, update_game_state),
        daemon=True
    ).start()
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    
    Player.containers = (updatable, drawable)
    Shot.containers = (shots,updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    
    local_player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, player_id,color=(255, 255, 255))
    players_by_id[player_id] = local_player
    
    dt = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        if player_id in players_by_id:
            players_by_id[player_id].update(dt, sock)
        
        sync_players_with_server_state(game_state, players_by_id, drawable, updatable,player_id)
        sync_player_shots(game_state, shots_by_id, drawable, updatable,player_id)

        screen.fill("black")
        for obj in drawable:
            obj.draw(screen)
        
        pygame.display.flip()
        
        #dans notre cas dt on n'utilise pas dt dnas le calcule comme précedent car tous il gerer dans le server go
        dt = clock.tick(60) / 1000

def sync_players_with_server_state(game_state, players_by_id, drawable, updatable,player_id):
    """Synchronise les joueurs locaux avec l'état du serveur"""
    
    # Récupérer les joueurs du serveur
    server_players = game_state.get("players", [])
    server_player_ids = {p["id"] for p in server_players}
    
    # Supprimer les joueurs qui ne sont plus sur le serveur
    players_to_remove = []
    for pid in players_by_id:
        if pid not in server_player_ids:
            players_to_remove.append(pid)
    
    for pid in players_to_remove:
        player_to_remove = players_by_id[pid]
        player_to_remove.kill()  # Supprime des groupes sprite
        del players_by_id[pid]
        print(f"Joueur {pid} supprimé")
    
    # Créer ou mettre à jour les joueurs
    for player_data in server_players:
        pid = player_data["id"]
        pos = player_data["position"]
        rot = player_data["rotation"]
        radius = player_data.get("radius", PLAYER_RADIUS)
        alive = player_data.get("alive", True)
        
        if pid == player_id:
             color = (255, 255, 255)
        else:
             color = (0, 255, 0)
        
        if pid not in players_by_id:
            # Créer un nouveau joueur et l'ajouter aux groupes
            new_player = Player(pos["x"], pos["y"], pid,color=color)
            new_player.rotation = rot
            new_player.radius = radius
            players_by_id[pid] = new_player
            
            # S'assurer qu'il est dans les bons groupes
            if new_player not in drawable:
                drawable.add(new_player)
            if new_player not in updatable:
                updatable.add(new_player)
                
            print(f"Nouveau joueur créé: {pid}")
        else:
            # Mettre à jour le joueur existant
            existing_player = players_by_id[pid]
            existing_player.position.x = pos["x"]
            existing_player.position.y = pos["y"]
            existing_player.rotation = rot
            existing_player.radius = radius
            existing_player.color = color
            
            # Gérer l'état vivant/mort
            if not alive and existing_player.alive:
                existing_player.alive = False
                print(f"Joueur {pid} est mort")
            elif alive and not existing_player.alive:
                existing_player.alive = True
                print(f"Joueur {pid} est ressuscité")
                
def sync_player_shots(game_state, shots_by_id, drawable, updatable,player_id):
    """Synchronise les tirs avec l'état du serveur"""
    server_shots = game_state.get("shots", [])
    
    #  ID unique pour chaque tir basé sur sa position et vélocité
    current_server_shots = set()
    
    for shot_data in server_shots:
        # ID unique basé sur les propriétés du tir
        shot_id = f"{shot_data['position']['x']:.1f}_{shot_data['position']['y']:.1f}_{shot_data['velocity']['x']:.1f}_{shot_data['velocity']['y']:.1f}_{shot_data['owner_id']}"
        current_server_shots.add(shot_id)
        
        # Si ce tir n'existe pas encore localement, le créer
        if shot_id not in shots_by_id:
            if shot_data['owner_id'] == player_id:
                 color = (255, 255, 255)
            else:
                color = (0, 255, 0)
            
            new_shot = Shot(
                shot_data["position"]["x"],
                shot_data["position"]["y"], 
                shot_data["radius"],
                 color = color
                
            )
            new_shot.velocity = pygame.Vector2(
                shot_data["velocity"]["x"], 
                shot_data["velocity"]["y"]
            )
            
            shots_by_id[shot_id] = new_shot
            drawable.add(new_shot)
            updatable.add(new_shot)
        else:
            # Mettre à jour la position du tir existant
            existing_shot = shots_by_id[shot_id]
            existing_shot.position.x = shot_data["position"]["x"]
            existing_shot.position.y = shot_data["position"]["y"]
    
    # Supprimer les tirs qui ne sont plus sur le serveur
    shots_to_remove = []
    for shot_id in shots_by_id:
        if shot_id not in current_server_shots:
            shots_to_remove.append(shot_id)
    
    for shot_id in shots_to_remove:
        shot_to_remove = shots_by_id[shot_id]
        shot_to_remove.kill()  # Supprime des groupes sprite
        del shots_by_id[shot_id]
        

def sync_asteroids_with_server_state(game_state, asteroids_by_id, drawable, updatable):
    """Synchronise les astroid avec l'état du serveur"""
    server_asteroids = game_state.get("asteroids", [])
    current_server_asteroids = set()
    for asteroid_data in server_asteroids : 
        asteroid_id = f"{asteroid_data['position']['x']:.0f}_{asteroid_data['position']['y']:.0f}_{asteroid_data['radius']:.0f}_{asteroid_data['velocity']['x']:.1f}_{asteroid_data['velocity']['y']:.1f}"
        current_server_asteroids.add(asteroid_id)
        if asteroid_id not in asteroids_by_id:
            new_asteroid = Asteroid(
                asteroid_data["position"]["x"],
                asteroid_data["position"]["y"],
                asteroid_data["radius"]
            )
            new_asteroid.velocity = pygame.Vector2(
                asteroid_data["velocity"]["x"],
                asteroid_data["velocity"]["y"]
            )
            asteroids_by_id[asteroid_id] = new_asteroid
            drawable.add(new_asteroid)
            updatable.add(new_asteroid)
        else:
            existing_asteroid = asteroids_by_id[asteroid_id]
            existing_asteroid.position.x = asteroid_data["position"]["x"]
            existing_asteroid.position.y = asteroid_data["position"]["y"]
            existing_asteroid.velocity.x = asteroid_data["velocity"]["x"]
            existing_asteroid.velocity.y = asteroid_data["velocity"]["y"]
            existing_asteroid.radius = asteroid_data["radius"]
        asteroids_to_remove = []
        for asteroid_id in asteroids_by_id:
            if asteroid_id not in current_server_asteroids:
                asteroids_to_remove.append(asteroid_id)
        for asteroid_id in asteroids_to_remove:
            asteroid_to_remove = asteroids_by_id[asteroid_id]
            asteroid_to_remove.kill()
            del asteroids_by_id[asteroid_id]    

    
        
if __name__ == "__main__":
    main()
    
# I need to add astroid for 