package game

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/lipgloss"
)

var (
	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#FAFAFA")).
			Background(lipgloss.Color("#7D56F4")).
			Padding(0, 2)

	scoreStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FFFF00")).
			Bold(true)

	gameOverStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#FF6B6B")).
			Background(lipgloss.Color("#333333")).
			Padding(1, 3)

	hintStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#888888"))

	graceStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#00FF00")).
			Bold(true)

	diffEasyStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#00FF00"))

	diffNormalStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FFFF00"))

	diffHardStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FF4444"))

	pipeChar = '#'
	birdChar = '>'
	ground   = '-'
)

func diffStyle(d Difficulty) lipgloss.Style {
	switch d {
	case DiffEasy:
		return diffEasyStyle
	case DiffNormal:
		return diffNormalStyle
	case DiffHard:
		return diffHardStyle
	default:
		return diffNormalStyle
	}
}

func (m Model) View() string {
	if m.Width < MinWidth || m.Height < MinHeight {
		return fmt.Sprintf("\n  Terminal too small!\n  Need at least %dx%d, got %dx%d\n", MinWidth, MinHeight, m.Width, m.Height)
	}

	playWidth := m.Width
	playHeight := m.Height - 2
	p := m.params()

	buf := make([][]rune, playHeight)
	for y := range buf {
		buf[y] = make([]rune, playWidth)
		for x := range buf[y] {
			buf[y][x] = ' '
		}
	}

	for _, pipe := range m.Pipes {
		if pipe.X >= 0 && pipe.X < playWidth {
			for y := 0; y < playHeight; y++ {
				if y < pipe.GapTop || y >= pipe.GapTop+pipe.GapLen {
					buf[y][pipe.X] = pipeChar
				}
			}
		}
	}

	birdY := int(m.Bird.Y)
	if birdY >= 0 && birdY < playHeight && m.Bird.X < playWidth {
		buf[birdY][m.Bird.X] = birdChar
	}

	var lines []string
	for y := 0; y < playHeight; y++ {
		lines = append(lines, string(buf[y]))
	}
	lines = append(lines, strings.Repeat(string(ground), playWidth))

	statusLine := ""
	if m.Frame <= p.GraceFrames && m.State == StatePlaying {
		statusLine = graceStyle.Render("  Keep pressing SPACE to fly!")
	} else {
		diffText := diffStyle(m.Difficulty).Render(fmt.Sprintf("[%s]", m.Difficulty))
		scoreText := scoreStyle.Render(fmt.Sprintf("Score: %d", m.Score))
		bestText := fmt.Sprintf("  Best: %d", m.Best)
		statusLine = diffText + " " + scoreText + bestText + hintStyle.Render("   Space: flap  R: restart  Q: quit")
	}
	lines = append(lines, statusLine)

	switch m.State {
	case StateReady:
		diffText := diffStyle(m.Difficulty).Render(fmt.Sprintf("  Current: %s  ", m.Difficulty))
		overlay := titleStyle.Render("  Flappy Bird  ") +
			"\n\n" +
			"  1: " + diffEasyStyle.Render("Easy") +
			"   2: " + diffNormalStyle.Render("Normal") +
			"   3: " + diffHardStyle.Render("Hard") +
			"\n" + diffText +
			"\n\n  Press SPACE to flap and fly" +
			"\n  Keep pressing SPACE to stay airborne!" +
			"\n  Avoid pipes, don't hit the ground" +
			"\n\n  Press SPACE to start"
		return lipgloss.NewStyle().Padding(playHeight/2-6, playWidth/4).Render(overlay)
	case StateGameOver:
		diffText := diffStyle(m.Difficulty).Render(fmt.Sprintf("  Difficulty: %s  ", m.Difficulty))
		overlay := gameOverStyle.Render(
			fmt.Sprintf("  GAME OVER  \n  Score: %d  Best: %d  \n  Press SPACE or R to restart  ", m.Score, m.Best)) +
			"\n" + diffText + hintStyle.Render("  Press 1/2/3 to change difficulty")
		return lipgloss.NewStyle().Padding(playHeight/2-5, playWidth/2-20).Render(overlay)
	case StatePaused:
		overlay := titleStyle.Render("  PAUSED  ") + "\n  Press P to resume"
		return lipgloss.NewStyle().Padding(playHeight/2-2, playWidth/2-8).Render(overlay)
	}

	return strings.Join(lines, "\n")
}
