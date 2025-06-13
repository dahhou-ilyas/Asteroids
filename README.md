# Multiplayer Asteroids Game

A real-time multiplayer Asteroids game built with Python (Pygame) client and Go server using TCP sockets.

## Project Structure

```
.
├── README.md
├── requirements.txt          # Python dependencies
├── .gitignore
├── constants.py             # Game constants shared between client and server
├── socketserverconfig.py    # Client socket configuration and networking
├── main.py                  # Main client game loop
├── player.py                # Player class implementation
├── shot.py                  # Shot/bullet class implementation
├── asteroid.py              # Asteroid class implementation
├── asteroidfield.py         # Asteroid spawning logic
├── circleshape.py           # Base class for circular game objects
└── server/
    ├── go.mod
    ├── server.go            # Go TCP server implementation
    └── .idea/               # IDE configuration files
```

## Features

- **Real-time multiplayer**: Up to 2 players can play simultaneously
- **Authoritative server**: Game logic runs on Go server for consistency
- **Client-side prediction**: Smooth gameplay with client-side rendering
- **TCP networking**: Reliable connection using custom JSON protocol
- **Collision detection**: Players vs asteroids, shots vs asteroids
- **Dynamic asteroid spawning**: Asteroids spawn from screen edges
- **Asteroid splitting**: Large asteroids split into smaller ones when shot
- **Score tracking**: Players earn points for destroying asteroids

## Requirements

### Client (Python)
- Python 3.8+
- pygame 2.6.1

### Server (Go)
- Go 1.24.2+

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/dahhou-ilyas/Asteroids.git
cd Asteroids
```

### 2. Set up Python client
```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set up Go server
```bash
cd server
go mod tidy
```

## Running the Game

### 1. Start the server
```bash
cd server
go run server.go
```
The server will start on port 8080 and display:
```
Serveur TCP démarré sur port 8080
```

### 2. Start client(s)
In separate terminal(s):
```bash
python main.py
```

Each client will connect to the server and receive a unique player ID.

## Game Controls

- **Arrow Keys**: 
  - ↑/↓: Move forward/backward
  - ←/→: Rotate left/right
- **Spacebar**: Shoot
- **ESC/Close Window**: Quit game

## Network Protocol

The game uses a custom JSON-based protocol over TCP:

### Client to Server Messages
```json
{
  "type": "input",
  "data": {
    "player_id": "player_1",
    "inputs": {
      "left": false,
      "right": true,
      "forward": true,
      "backward": false,
      "shoot": false
    }
  }
}
```

### Server to Client Messages
```json
{
  "type": "game_state",
  "data": {
    "players": [...],
    "shots": [...],
    "asteroids": [...],
    "timestamp": 1234567890
  }
}
```

## Architecture

### Client Side ([`main.py`](main.py))
- Handles rendering and input capture
- Connects to server using [`socketserverconfig.py`](socketserverconfig.py)
- Synchronizes game state from server
- Manages local player sprites and drawing

### Server Side ([`server/server.go`](server/server.go))
- Authoritative game loop running at 60 FPS
- Handles player connections and disconnections
- Processes player inputs and updates game state
- Manages collision detection and physics
- Broadcasts game state to all connected clients

### Game Objects
- **[`Player`](player.py)**: Triangle-shaped ships with rotation and movement
- **[`Shot`](shot.py)**: Projectiles fired by players
- **[`Asteroid`](asteroid.py)**: Circular obstacles that split when hit
- **[`CircleShape`](circleshape.py)**: Base class for collision detection

## Configuration

Game constants are defined in [`constants.py`](constants.py):
- Screen dimensions: 1280x720
- Player speed, rotation speed, shoot cooldown
- Asteroid spawn rates and sizes
- Physics parameters

## Development

### Adding Features
1. Update constants in [`constants.py`](constants.py) if needed
2. Modify server logic in [`server/server.go`](server/server.go)
3. Update client synchronization in [`main.py`](main.py)
4. Test with multiple clients

### Known Limitations
- Maximum 2 players (configurable in server)
- No player respawning system
- Basic collision detection
- No persistent scoring system

## Troubleshooting

### Connection Issues
- Ensure server is running on port 8080
- Check firewall settings
- Verify server address in [`socketserverconfig.py`](socketserverconfig.py)

### Performance Issues
- Server runs at 60 FPS - reduce `TICK_RATE` if needed
- Client rendering is independent of server tick rate
- Network latency may affect responsiveness

## Future Enhancements

- Player respawning system
- Power-ups and special weapons
- Persistent leaderboards
- Support for more than 2 players
- UDP networking for better performance
- Client-side prediction improvements
- Spectator mode

## License

This project is licensed under the [MIT License](LICENSE).
