package game

func HitGround(bird Bird, height int) bool {
	playHeight := height - 2
	return bird.Y >= float64(playHeight)
}

func HitPipe(bird Bird, pipes []Pipe) bool {
	for _, p := range pipes {
		if bird.X == p.X {
			gapBottom := p.GapTop + p.GapLen
			if int(bird.Y) < p.GapTop || int(bird.Y) >= gapBottom {
				return true
			}
		}
	}
	return false
}

func CheckCollision(bird Bird, pipes []Pipe, height int) bool {
	return HitGround(bird, height) || HitPipe(bird, pipes)
}
