package game

import "math/rand"

func SpawnPipe(width, height, gapLen int, r *rand.Rand) Pipe {
	playHeight := height - 2
	minTop := 2
	maxTop := playHeight - gapLen - 2
	if maxTop < minTop {
		maxTop = minTop
	}
	gapTop := minTop + r.Intn(maxTop-minTop+1)

	return Pipe{
		X:      width,
		GapTop: gapTop,
		GapLen: gapLen,
		Passed: false,
	}
}

func UpdatePipes(pipes []Pipe, speed int) []Pipe {
	for i := range pipes {
		pipes[i].X -= speed
	}
	i := 0
	for _, p := range pipes {
		if p.X >= -2 {
			pipes[i] = p
			i++
		}
	}
	return pipes[:i]
}

func ScorePipes(pipes []Pipe, birdX int) (int, []Pipe) {
	score := 0
	for i := range pipes {
		if !pipes[i].Passed && pipes[i].X < birdX {
			pipes[i].Passed = true
			score++
		}
	}
	return score, pipes
}
