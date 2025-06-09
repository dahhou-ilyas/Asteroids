package main

import (
	"math"
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

func main() {

}
