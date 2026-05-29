package game

func ApplyGravity(bird *Bird, gravity float64) {
	bird.Vy += gravity
	bird.Y += bird.Vy
	if bird.Y < 0 {
		bird.Y = 0
		bird.Vy = 0
	}
}

func Flap(bird *Bird, impulse float64) {
	bird.Vy = impulse
}
