package game

import (
	"fmt"
	"math/rand"
	"time"

	tea "github.com/charmbracelet/bubbletea"
)

type GameState int

const (
	StateReady GameState = iota
	StatePlaying
	StatePaused
	StateGameOver
)

type Difficulty int

const (
	DiffEasy   Difficulty = 1
	DiffNormal Difficulty = 2
	DiffHard   Difficulty = 3
)

func (d Difficulty) String() string {
	switch d {
	case DiffEasy:
		return "Easy"
	case DiffNormal:
		return "Normal"
	case DiffHard:
		return "Hard"
	default:
		return "?"
	}
}

type DiffParams struct {
	Gravity       float64
	FlapImpulse   float64
	PipeSpeed     int
	PipeGap       int
	SpawnInterval  int
	GraceFrames   int
}

func Params(d Difficulty) DiffParams {
	switch d {
	case DiffEasy:
		return DiffParams{Gravity: 0.12, FlapImpulse: -1.8, PipeSpeed: 1, PipeGap: 10, SpawnInterval: 35, GraceFrames: 35}
	case DiffNormal:
		return DiffParams{Gravity: 0.18, FlapImpulse: -2.2, PipeSpeed: 1, PipeGap: 8, SpawnInterval: 30, GraceFrames: 25}
	case DiffHard:
		return DiffParams{Gravity: 0.28, FlapImpulse: -3.0, PipeSpeed: 2, PipeGap: 6, SpawnInterval: 24, GraceFrames: 15}
	default:
		return Params(DiffNormal)
	}
}

const (
	TickInterval = 60 * time.Millisecond
	BirdX        = 10
	MinWidth     = 40
	MinHeight    = 18
)

type Bird struct {
	X  int
	Y  float64
	Vy float64
}

type Pipe struct {
	X      int
	GapTop int
	GapLen int
	Passed bool
}

type Model struct {
	Width      int
	Height     int
	Bird       Bird
	Pipes      []Pipe
	Score      int
	Best       int
	State      GameState
	Frame      int
	Rand       *rand.Rand
	Difficulty Difficulty
}

func NewModel() Model {
	return Model{
		Width:      60,
		Height:     24,
		Bird:       Bird{X: BirdX, Y: 12},
		Rand:       rand.New(rand.NewSource(time.Now().UnixNano())),
		State:      StateReady,
		Difficulty: DiffNormal,
	}
}

func (m Model) Init() tea.Cmd {
	return tea.Tick(TickInterval, func(t time.Time) tea.Msg {
		return tickMsg(t)
	})
}

func (m *Model) Reset() {
	m.Bird = Bird{X: BirdX, Y: float64(m.Height) / 2}
	m.Pipes = nil
	m.Score = 0
	m.Frame = 0
	m.State = StateReady
}

func (m Model) params() DiffParams {
	return Params(m.Difficulty)
}

func (m Model) StatusLine() string {
	return fmt.Sprintf("Difficulty: %s (1/2/3 to change)", m.Difficulty)
}

type tickMsg time.Time
