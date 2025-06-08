package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"net"
	"sync"
	"time"
)

// Constants - mêmes valeurs que votre jeu Python
const (
	SCREEN_WIDTH          = 1280
	SCREEN_HEIGHT         = 720
	SHOT_RADIUS           = 5
	PLAYER_SHOOT_SPEED    = 500
	PLAYER_SHOOT_COOLDOWN = 0.5
	PLAYER_RADIUS         = 20
	ASTEROID_MIN_RADIUS   = 20
	ASTEROID_KINDS        = 3
	ASTEROID_SPAWN_RATE   = 0.8
	ASTEROID_MAX_RADIUS   = ASTEROID_MIN_RADIUS * ASTEROID_KINDS
	PLAYER_TURN_SPEED     = 300
	PLAYER_SPEED_RUN      = 200
	MAX_PLAYERS           = 2
	TICK_RATE             = 60 // FPS du serveur
	SERVER_PORT           = "8080"
)

// Vector2 représente un vecteur 2D
type Vector2 struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
}

func (v Vector2) Add(other Vector2) Vector2 {
	return Vector2{X: v.X + other.X, Y: v.Y + other.Y}
}

func (v Vector2) Multiply(scalar float64) Vector2 {
	return Vector2{X: v.X * scalar, Y: v.Y * scalar}
}

func (v Vector2) Rotate(degrees float64) Vector2 {
	radians := degrees * math.Pi / 180
	cos := math.Cos(radians)
	sin := math.Sin(radians)
	return Vector2{
		X: v.X*cos - v.Y*sin,
		Y: v.X*sin + v.Y*cos,
	}
}

func (v Vector2) Distance(other Vector2) float64 {
	dx := v.X - other.X
	dy := v.Y - other.Y
	return math.Sqrt(dx*dx + dy*dy)
}

// Player représente un joueur
type Player struct {
	ID         string        `json:"id"`
	Position   Vector2       `json:"position"`
	Velocity   Vector2       `json:"velocity"`
	Rotation   float64       `json:"rotation"`
	Radius     float64       `json:"radius"`
	Alive      bool          `json:"alive"`
	Score      int           `json:"score"`
	ShootTimer float64       `json:"-"`
	Inputs     PlayerInputs  `json:"-"`
	Connection net.Conn      `json:"-"`
	Writer     *bufio.Writer `json:"-"`
	Reader     *bufio.Reader `json:"-"`
}

// PlayerInputs stocke l'état des touches
type PlayerInputs struct {
	Left     bool `json:"left"`
	Right    bool `json:"right"`
	Forward  bool `json:"forward"`
	Backward bool `json:"backward"`
	Shoot    bool `json:"shoot"`
}

// Asteroid représente un astéroïde
type Asteroid struct {
	Position Vector2 `json:"position"`
	Velocity Vector2 `json:"velocity"`
	Radius   float64 `json:"radius"`
}

// Shot représente un projectile
type Shot struct {
	Position Vector2 `json:"position"`
	Velocity Vector2 `json:"velocity"`
	Radius   float64 `json:"radius"`
	OwnerID  string  `json:"owner_id"`
}

// GameState contient tout l'état du jeu
type GameState struct {
	Players   []*Player   `json:"players"`
	Asteroids []*Asteroid `json:"asteroids"`
	Shots     []*Shot     `json:"shots"`
	Timestamp int64       `json:"timestamp"`
}

// Messages pour la communication socket
type Message struct {
	Type string      `json:"type"`
	Data interface{} `json:"data"`
}

type InputMessage struct {
	PlayerID string       `json:"player_id"`
	Inputs   PlayerInputs `json:"inputs"`
}

type WelcomeMessage struct {
	PlayerID string `json:"player_id"`
	Status   string `json:"status"`
}

// GameServer gère le serveur de jeu
type GameServer struct {
	players       map[string]*Player
	gameState     *GameState
	asteroidField *AsteroidField
	mutex         sync.RWMutex
	running       bool
	listener      net.Listener
}

// AsteroidField gère la génération d'astéroïdes
type AsteroidField struct {
	SpawnTimer float64
	Edges      []AsteroidEdge
}

type AsteroidEdge struct {
	Direction    Vector2
	PositionFunc func(float64) Vector2
}

func NewAsteroidField() *AsteroidField {
	return &AsteroidField{
		SpawnTimer: 0,
		Edges: []AsteroidEdge{
			{
				Direction: Vector2{X: 1, Y: 0},
				PositionFunc: func(t float64) Vector2 {
					return Vector2{X: -ASTEROID_MAX_RADIUS, Y: t * SCREEN_HEIGHT}
				},
			},
			{
				Direction: Vector2{X: -1, Y: 0},
				PositionFunc: func(t float64) Vector2 {
					return Vector2{X: SCREEN_WIDTH + ASTEROID_MAX_RADIUS, Y: t * SCREEN_HEIGHT}
				},
			},
			{
				Direction: Vector2{X: 0, Y: 1},
				PositionFunc: func(t float64) Vector2 {
					return Vector2{X: t * SCREEN_WIDTH, Y: -ASTEROID_MAX_RADIUS}
				},
			},
			{
				Direction: Vector2{X: 0, Y: -1},
				PositionFunc: func(t float64) Vector2 {
					return Vector2{X: t * SCREEN_WIDTH, Y: SCREEN_HEIGHT + ASTEROID_MAX_RADIUS}
				},
			},
		},
	}
}

func NewGameServer() *GameServer {
	return &GameServer{
		players: make(map[string]*Player),
		gameState: &GameState{
			Players:   make([]*Player, 0),
			Asteroids: make([]*Asteroid, 0),
			Shots:     make([]*Shot, 0),
		},
		asteroidField: NewAsteroidField(),
		running:       true,
	}
}

func (gs *GameServer) Start() error {
	listener, err := net.Listen("tcp", ":"+SERVER_PORT)
	if err != nil {
		return fmt.Errorf("erreur création listener: %v", err)
	}

	gs.listener = listener
	log.Printf("Serveur TCP démarré sur port %s", SERVER_PORT)

	// Démarrer la boucle de jeu
	go gs.gameLoop()

	// Accepter les connexions
	for gs.running {
		conn, err := listener.Accept()
		if err != nil {
			if gs.running {
				log.Printf("Erreur acceptation connexion: %v", err)
			}
			continue
		}

		go gs.handleConnection(conn)
	}

	return nil
}

func (gs *GameServer) handleConnection(conn net.Conn) {
	defer conn.Close()

	gs.mutex.Lock()
	if len(gs.players) >= MAX_PLAYERS {
		gs.mutex.Unlock()
		// Envoyer message d'erreur
		errorMsg := Message{
			Type: "error",
			Data: map[string]string{"message": "Serveur plein"},
		}
		gs.sendMessage(conn, errorMsg)
		return
	}

	// Créer nouveau joueur
	playerID := fmt.Sprintf("player_%d", len(gs.players)+1)
	reader := bufio.NewReader(conn)
	writer := bufio.NewWriter(conn)

	player := &Player{
		ID:         playerID,
		Position:   Vector2{X: SCREEN_WIDTH / 2, Y: SCREEN_HEIGHT / 2},
		Velocity:   Vector2{X: 0, Y: 0},
		Rotation:   0,
		Radius:     PLAYER_RADIUS,
		Alive:      true,
		Score:      0,
		ShootTimer: 0,
		Connection: conn,
		Writer:     writer,
		Reader:     reader,
	}

	// Positionner le deuxième joueur différemment
	if len(gs.players) == 1 {
		player.Position = Vector2{X: SCREEN_WIDTH / 4, Y: SCREEN_HEIGHT / 2}
	}

	gs.players[playerID] = player
	gs.updatePlayersList()
	gs.mutex.Unlock()

	log.Printf("Nouveau joueur connecté: %s (%s)", playerID, conn.RemoteAddr())

	// Envoyer message de bienvenue
	welcomeMsg := Message{
		Type: "welcome",
		Data: WelcomeMessage{
			PlayerID: playerID,
			Status:   "connected",
		},
	}

	if err := gs.sendMessageToPlayer(player, welcomeMsg); err != nil {
		log.Printf("Erreur envoi message bienvenue: %v", err)
		gs.removePlayer(playerID)
		return
	}

	// Écouter les messages du client
	for {
		line, err := reader.ReadString('\n')
		if err != nil {
			log.Printf("Erreur lecture message de %s: %v", playerID, err)
			break
		}

		var msg Message
		if err := json.Unmarshal([]byte(line), &msg); err != nil {
			log.Printf("Erreur parsing message de %s: %v", playerID, err)
			continue
		}

		if msg.Type == "input" {
			// Convertir les données en InputMessage
			inputData, _ := json.Marshal(msg.Data)
			var inputMsg InputMessage
			if err := json.Unmarshal(inputData, &inputMsg); err != nil {
				log.Printf("Erreur parsing input de %s: %v", playerID, err)
				continue
			}

			gs.mutex.Lock()
			if player, exists := gs.players[inputMsg.PlayerID]; exists {
				player.Inputs = inputMsg.Inputs
			}
			gs.mutex.Unlock()
		}
	}

	// Nettoyer à la déconnexion
	gs.removePlayer(playerID)
	log.Printf("Joueur déconnecté: %s", playerID)
}

func (gs *GameServer) removePlayer(playerID string) {
	gs.mutex.Lock()
	delete(gs.players, playerID)
	gs.updatePlayersList()
	gs.mutex.Unlock()
}

func (gs *GameServer) sendMessage(conn net.Conn, msg Message) error {
	data, err := json.Marshal(msg)
	if err != nil {
		return err
	}

	_, err = conn.Write(append(data, '\n'))
	return err
}

func (gs *GameServer) sendMessageToPlayer(player *Player, msg Message) error {
	data, err := json.Marshal(msg)
	if err != nil {
		return err
	}

	_, err = player.Writer.Write(append(data, '\n'))
	if err != nil {
		return err
	}

	return player.Writer.Flush()
}

func (gs *GameServer) updatePlayersList() {
	gs.gameState.Players = make([]*Player, 0, len(gs.players))
	for _, player := range gs.players {
		gs.gameState.Players = append(gs.gameState.Players, player)
	}
}

func (gs *GameServer) gameLoop() {
	ticker := time.NewTicker(time.Second / TICK_RATE)
	defer ticker.Stop()

	lastTime := time.Now()

	for gs.running {
		<-ticker.C

		now := time.Now()
		dt := now.Sub(lastTime).Seconds()
		lastTime = now

		gs.mutex.Lock()
		gs.updateGame(dt)
		gs.broadcastGameState()
		gs.mutex.Unlock()
	}
}

func (gs *GameServer) updateGame(dt float64) {
	// Mettre à jour les joueurs
	for _, player := range gs.players {
		if !player.Alive {
			continue
		}

		player.ShootTimer -= dt

		// Appliquer la rotation
		if player.Inputs.Left {
			player.Rotation += PLAYER_TURN_SPEED * dt
		}
		if player.Inputs.Right {
			player.Rotation -= PLAYER_TURN_SPEED * dt
		}

		// Appliquer le mouvement
		if player.Inputs.Forward {
			forward := Vector2{X: 0, Y: 1}.Rotate(player.Rotation)
			player.Position = player.Position.Add(forward.Multiply(PLAYER_SPEED_RUN * dt))
		}
		if player.Inputs.Backward {
			forward := Vector2{X: 0, Y: 1}.Rotate(player.Rotation)
			player.Position = player.Position.Add(forward.Multiply(-PLAYER_SPEED_RUN * dt))
		}

		// Wrap around screen
		gs.wrapPosition(&player.Position)

		// Tirer
		if player.Inputs.Shoot && player.ShootTimer <= 0 {
			player.ShootTimer = PLAYER_SHOOT_COOLDOWN
			forward := Vector2{X: 0, Y: 1}.Rotate(player.Rotation)
			shot := &Shot{
				Position: player.Position,
				Velocity: forward.Multiply(PLAYER_SHOOT_SPEED),
				Radius:   SHOT_RADIUS,
				OwnerID:  player.ID,
			}
			gs.gameState.Shots = append(gs.gameState.Shots, shot)
		}
	}

	// Mettre à jour les projectiles
	for i := len(gs.gameState.Shots) - 1; i >= 0; i-- {
		shot := gs.gameState.Shots[i]
		shot.Position = shot.Position.Add(shot.Velocity.Multiply(dt))

		// Supprimer si hors écran
		if shot.Position.X < -50 || shot.Position.X > SCREEN_WIDTH+50 ||
			shot.Position.Y < -50 || shot.Position.Y > SCREEN_HEIGHT+50 {
			gs.gameState.Shots = append(gs.gameState.Shots[:i], gs.gameState.Shots[i+1:]...)
		}
	}

	// Mettre à jour les astéroïdes
	for i := len(gs.gameState.Asteroids) - 1; i >= 0; i-- {
		asteroid := gs.gameState.Asteroids[i]
		asteroid.Position = asteroid.Position.Add(asteroid.Velocity.Multiply(dt))
		gs.wrapPosition(&asteroid.Position)
	}

	// Génération d'astéroïdes
	gs.asteroidField.SpawnTimer += dt
	if gs.asteroidField.SpawnTimer > ASTEROID_SPAWN_RATE {
		gs.asteroidField.SpawnTimer = 0
		gs.spawnAsteroid()
	}

	// Vérifier les collisions
	gs.checkCollisions()

	gs.gameState.Timestamp = time.Now().UnixNano() / int64(time.Millisecond)
}

func (gs *GameServer) wrapPosition(pos *Vector2) {
	if pos.X < 0 {
		pos.X = SCREEN_WIDTH
	} else if pos.X > SCREEN_WIDTH {
		pos.X = 0
	}
	if pos.Y < 0 {
		pos.Y = SCREEN_HEIGHT
	} else if pos.Y > SCREEN_HEIGHT {
		pos.Y = 0
	}
}

func (gs *GameServer) spawnAsteroid() {
	edge := gs.asteroidField.Edges[rand.Intn(len(gs.asteroidField.Edges))]
	speed := float64(rand.Intn(61) + 40) // 40-100
	velocity := edge.Direction.Multiply(speed)

	// Rotation aléatoire
	rotationAngle := float64(rand.Intn(61) - 30) // -30 à 30
	velocity = velocity.Rotate(rotationAngle)

	position := edge.PositionFunc(rand.Float64())
	kind := rand.Intn(ASTEROID_KINDS) + 1
	radius := float64(ASTEROID_MIN_RADIUS * kind)

	asteroid := &Asteroid{
		Position: position,
		Velocity: velocity,
		Radius:   radius,
	}

	gs.gameState.Asteroids = append(gs.gameState.Asteroids, asteroid)
}

func (gs *GameServer) checkCollisions() {
	// Collisions joueurs vs astéroïdes
	for _, player := range gs.players {
		if !player.Alive {
			continue
		}
		for _, asteroid := range gs.gameState.Asteroids {
			if gs.circleCollision(player.Position, player.Radius, asteroid.Position, asteroid.Radius) {
				player.Alive = false
				log.Printf("Joueur %s est mort!", player.ID)
			}
		}
	}

	// Collisions projectiles vs astéroïdes
	for shotIdx := len(gs.gameState.Shots) - 1; shotIdx >= 0; shotIdx-- {
		shot := gs.gameState.Shots[shotIdx]

		for asteroidIdx := len(gs.gameState.Asteroids) - 1; asteroidIdx >= 0; asteroidIdx-- {
			asteroid := gs.gameState.Asteroids[asteroidIdx]

			if gs.circleCollision(shot.Position, shot.Radius, asteroid.Position, asteroid.Radius) {
				// Supprimer le projectile
				gs.gameState.Shots = append(gs.gameState.Shots[:shotIdx], gs.gameState.Shots[shotIdx+1:]...)

				// Diviser l'astéroïde
				gs.splitAsteroid(asteroidIdx)

				// Ajouter au score du joueur
				if player, exists := gs.players[shot.OwnerID]; exists {
					player.Score += 10
				}
				break
			}
		}
	}
}

func (gs *GameServer) circleCollision(pos1 Vector2, radius1 float64, pos2 Vector2, radius2 float64) bool {
	return pos1.Distance(pos2) <= radius1+radius2
}

func (gs *GameServer) splitAsteroid(index int) {
	asteroid := gs.gameState.Asteroids[index]

	// Supprimer l'astéroïde original
	gs.gameState.Asteroids = append(gs.gameState.Asteroids[:index], gs.gameState.Asteroids[index+1:]...)

	// Si trop petit, ne pas diviser
	if asteroid.Radius <= ASTEROID_MIN_RADIUS {
		return
	}

	// Créer deux nouveaux astéroïdes
	randomAngle := rand.Float64()*30 + 20 // 20-50 degrés
	newRadius := asteroid.Radius - ASTEROID_MIN_RADIUS

	velocity1 := asteroid.Velocity.Rotate(randomAngle).Multiply(1.2)
	velocity2 := asteroid.Velocity.Rotate(-randomAngle).Multiply(1.2)

	asteroid1 := &Asteroid{
		Position: asteroid.Position,
		Velocity: velocity1,
		Radius:   newRadius,
	}

	asteroid2 := &Asteroid{
		Position: asteroid.Position,
		Velocity: velocity2,
		Radius:   newRadius,
	}

	gs.gameState.Asteroids = append(gs.gameState.Asteroids, asteroid1, asteroid2)
}

func (gs *GameServer) broadcastGameState() {
	gameStateMsg := Message{
		Type: "game_state",
		Data: gs.gameState,
	}

	// Créer la liste des joueurs à supprimer (connexions fermées)
	var playersToRemove []string

	for playerID, player := range gs.players {
		err := gs.sendMessageToPlayer(player, gameStateMsg)
		if err != nil {
			log.Printf("Erreur envoi à %s: %v", playerID, err)
			playersToRemove = append(playersToRemove, playerID)
		}
	}

	// Supprimer les joueurs déconnectés
	for _, playerID := range playersToRemove {
		delete(gs.players, playerID)
		gs.updatePlayersList()
	}
}

func (gs *GameServer) Stop() {
	gs.running = false
	if gs.listener != nil {
		gs.listener.Close()
	}
}

func main() {
	rand.Seed(time.Now().UnixNano())

	server := NewGameServer()

	log.Println("Démarrage du serveur Asteroids TCP...")
	if err := server.Start(); err != nil {
		log.Fatalf("Erreur démarrage serveur: %v", err)
	}
}
