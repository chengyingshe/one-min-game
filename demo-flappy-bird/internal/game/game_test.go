package game

import (
	"math/rand"
	"testing"
	"time"
)

func testParams() DiffParams {
	return Params(DiffNormal)
}

func TestGravity(t *testing.T) {
	p := testParams()
	bird := Bird{X: 10, Y: 10.0, Vy: 0}
	ApplyGravity(&bird, p.Gravity)
	if bird.Vy != p.Gravity {
		t.Errorf("expected Vy=%f, got Vy=%f", p.Gravity, bird.Vy)
	}
	if bird.Y <= 10.0 {
		t.Errorf("expected bird to fall, Y=%f", bird.Y)
	}

	oldY := bird.Y
	ApplyGravity(&bird, p.Gravity)
	if bird.Y <= oldY {
		t.Errorf("expected bird to keep falling, Y=%f <= oldY=%f", bird.Y, oldY)
	}
}

func TestFlap(t *testing.T) {
	p := testParams()
	bird := Bird{X: 10, Y: 10.0, Vy: 5.0}
	Flap(&bird, p.FlapImpulse)
	if bird.Vy != p.FlapImpulse {
		t.Errorf("expected Vy=%f after flap, got Vy=%f", p.FlapImpulse, bird.Vy)
	}
}

func TestPipeMovement(t *testing.T) {
	p := testParams()
	pipes := []Pipe{
		{X: 20, GapTop: 5, GapLen: 6, Passed: false},
		{X: 10, GapTop: 3, GapLen: 6, Passed: true},
	}
	result := UpdatePipes(pipes, p.PipeSpeed)
	if len(result) != 2 {
		t.Errorf("expected 2 pipes, got %d", len(result))
	}
	if result[0].X != 19 {
		t.Errorf("expected pipe at X=19, got X=%d", result[0].X)
	}
	if result[1].X != 9 {
		t.Errorf("expected pipe at X=9, got X=%d", result[1].X)
	}
}

func TestOffscreenPipeRemoved(t *testing.T) {
	pipes := []Pipe{
		{X: -3, GapTop: 5, GapLen: 6, Passed: true},
		{X: 10, GapTop: 3, GapLen: 6, Passed: false},
	}
	result := UpdatePipes(pipes, 1)
	if len(result) != 1 {
		t.Errorf("expected 1 pipe after removal, got %d", len(result))
	}
	if result[0].X != 9 {
		t.Errorf("expected pipe at X=9, got X=%d", result[0].X)
	}
}

func TestScoring(t *testing.T) {
	pipes := []Pipe{
		{X: 9, GapTop: 5, GapLen: 6, Passed: false},
		{X: 15, GapTop: 3, GapLen: 6, Passed: false},
	}
	birdX := 10
	score, pipes := ScorePipes(pipes, birdX)
	if score != 1 {
		t.Errorf("expected score=1, got score=%d", score)
	}
	if !pipes[0].Passed {
		t.Error("first pipe should be marked as passed")
	}
	if pipes[1].Passed {
		t.Error("second pipe should not be passed yet")
	}

	score2, pipes := ScorePipes(pipes, birdX)
	if score2 != 0 {
		t.Errorf("expected score=0 on second call, got score=%d", score2)
	}
}

func TestCollisionGround(t *testing.T) {
	bird := Bird{X: 10, Y: 22.0, Vy: 1}
	if !HitGround(bird, 24) {
		t.Error("expected ground collision at Y=22 with height=24")
	}
}

func TestCeilingClamp(t *testing.T) {
	p := testParams()
	bird := Bird{X: 10, Y: 2.0, Vy: -5.0}
	ApplyGravity(&bird, p.Gravity)
	if bird.Y < 0 {
		t.Errorf("bird should be clamped at ceiling, got Y=%f", bird.Y)
	}
	if bird.Vy < 0 {
		t.Errorf("velocity should be reset at ceiling, got Vy=%f", bird.Vy)
	}
}

func TestCollisionPipe(t *testing.T) {
	pipes := []Pipe{
		{X: 10, GapTop: 5, GapLen: 6, Passed: false},
	}
	birdInGap := Bird{X: 10, Y: 7.0, Vy: 0}
	if HitPipe(birdInGap, pipes) {
		t.Error("bird in gap should not collide")
	}

	birdAboveGap := Bird{X: 10, Y: 3.0, Vy: 0}
	if !HitPipe(birdAboveGap, pipes) {
		t.Error("bird above gap should collide")
	}

	birdBelowGap := Bird{X: 10, Y: 12.0, Vy: 0}
	if !HitPipe(birdBelowGap, pipes) {
		t.Error("bird below gap should collide")
	}

	birdPastPipe := Bird{X: 11, Y: 3.0, Vy: 0}
	if HitPipe(birdPastPipe, pipes) {
		t.Error("bird past pipe should not collide")
	}
}

func TestRestart(t *testing.T) {
	m := Model{
		Width:      60,
		Height:     24,
		Bird:       Bird{X: BirdX, Y: 22.0, Vy: 5.0},
		Pipes:      []Pipe{{X: 10, GapTop: 5, GapLen: 6}},
		Score:      10,
		Best:       15,
		State:      StateGameOver,
		Frame:      100,
		Difficulty: DiffNormal,
		Rand:       rand.New(rand.NewSource(time.Now().UnixNano())),
	}
	m.Reset()
	if m.Score != 0 {
		t.Errorf("expected score=0 after reset, got %d", m.Score)
	}
	if m.State != StateReady {
		t.Errorf("expected state=Ready after reset, got %d", m.State)
	}
	if len(m.Pipes) != 0 {
		t.Errorf("expected 0 pipes after reset, got %d", len(m.Pipes))
	}
	if m.Difficulty != DiffNormal {
		t.Errorf("difficulty should persist after reset")
	}
}

func TestPipeGeneration(t *testing.T) {
	r := rand.New(rand.NewSource(42))
	for i := 0; i < 100; i++ {
		p := SpawnPipe(60, 24, 8, r)
		if p.GapTop < 2 {
			t.Errorf("gap top too close to ceiling: %d", p.GapTop)
		}
		playHeight := 24 - 2
		if p.GapTop+8 > playHeight-2 {
			t.Errorf("gap bottom too close to floor: gapTop=%d, gapBottom=%d, playHeight=%d", p.GapTop, p.GapTop+8, playHeight)
		}
		if p.Passed {
			t.Error("new pipe should not be passed")
		}
	}
}

func TestCheckCollision(t *testing.T) {
	pipes := []Pipe{
		{X: 10, GapTop: 5, GapLen: 6, Passed: false},
	}

	bird := Bird{X: 10, Y: 7.0, Vy: 0}
	if CheckCollision(bird, pipes, 24) {
		t.Error("bird in gap should not collide")
	}

	birdHitPipe := Bird{X: 10, Y: 2.0, Vy: 0}
	if !CheckCollision(birdHitPipe, pipes, 24) {
		t.Error("bird hitting pipe should collide")
	}

	birdHitGround := Bird{X: 15, Y: 23.0, Vy: 1}
	if !CheckCollision(birdHitGround, pipes, 24) {
		t.Error("bird hitting ground should collide")
	}
}

func TestDifficultyParams(t *testing.T) {
	easy := Params(DiffEasy)
	normal := Params(DiffNormal)
	hard := Params(DiffHard)

	if easy.Gravity >= normal.Gravity {
		t.Error("easy gravity should be less than normal")
	}
	if normal.Gravity >= hard.Gravity {
		t.Error("normal gravity should be less than hard")
	}
	if easy.PipeSpeed > normal.PipeSpeed {
		t.Error("easy pipe speed should not be greater than normal")
	}
	if easy.PipeGap <= normal.PipeGap {
		t.Error("easy gap should be larger than normal")
	}
	if normal.PipeGap <= hard.PipeGap {
		t.Error("normal gap should be larger than hard")
	}
}

func TestDifficultyString(t *testing.T) {
	if DiffEasy.String() != "Easy" {
		t.Errorf("expected Easy, got %s", DiffEasy.String())
	}
	if DiffNormal.String() != "Normal" {
		t.Errorf("expected Normal, got %s", DiffNormal.String())
	}
	if DiffHard.String() != "Hard" {
		t.Errorf("expected Hard, got %s", DiffHard.String())
	}
}
