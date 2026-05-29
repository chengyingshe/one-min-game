package game

import (
	"time"

	tea "github.com/charmbracelet/bubbletea"
)

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.Width = msg.Width
		m.Height = msg.Height
		return m, nil

	case tea.KeyMsg:
		return m.handleKey(msg)

	case tickMsg:
		return m.handleTick()
	}

	return m, nil
}

func (m Model) handleKey(msg tea.KeyMsg) (tea.Model, tea.Cmd) {
	switch msg.String() {
	case "q", "ctrl+c":
		return m, tea.Quit

	case "1":
		if m.State == StateReady || m.State == StateGameOver {
			m.Difficulty = DiffEasy
			return m, nil
		}
	case "2":
		if m.State == StateReady || m.State == StateGameOver {
			m.Difficulty = DiffNormal
			return m, nil
		}
	case "3":
		if m.State == StateReady || m.State == StateGameOver {
			m.Difficulty = DiffHard
			return m, nil
		}

	case "r":
		if m.State == StateGameOver || m.State == StateReady {
			best := m.Best
			m.Reset()
			m.Best = best
			return m, nil
		}
	case "p":
		if m.State == StatePlaying {
			m.State = StatePaused
			return m, nil
		} else if m.State == StatePaused {
			m.State = StatePlaying
			return m, nil
		}
	case " ", "up":
		if m.State == StateReady {
			m.State = StatePlaying
			p := m.params()
			Flap(&m.Bird, p.FlapImpulse)
			return m, scheduleTick()
		}
		if m.State == StatePlaying {
			p := m.params()
			Flap(&m.Bird, p.FlapImpulse)
			return m, nil
		}
		if m.State == StateGameOver {
			best := m.Best
			m.Reset()
			m.Best = best
			return m, nil
		}
	}
	return m, nil
}

func (m Model) handleTick() (tea.Model, tea.Cmd) {
	if m.State != StatePlaying {
		return m, scheduleTick()
	}

	p := m.params()
	m.Frame++

	ApplyGravity(&m.Bird, p.Gravity)

	m.Pipes = UpdatePipes(m.Pipes, p.PipeSpeed)

	if m.Frame%p.SpawnInterval == 0 {
		m.Pipes = append(m.Pipes, SpawnPipe(m.Width, m.Height, p.PipeGap, m.Rand))
	}

	scored, pipes := ScorePipes(m.Pipes, m.Bird.X)
	m.Score += scored
	m.Pipes = pipes

	if m.Frame > p.GraceFrames && CheckCollision(m.Bird, m.Pipes, m.Height) {
		m.State = StateGameOver
		if m.Score > m.Best {
			m.Best = m.Score
		}
		return m, scheduleTick()
	}

	return m, scheduleTick()
}

func scheduleTick() tea.Cmd {
	return tea.Tick(TickInterval, func(t time.Time) tea.Msg {
		return tickMsg(t)
	})
}
