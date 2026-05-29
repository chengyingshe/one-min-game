# 实现文档：命令行 Flappy Bird

## 1. 项目目标

做一个可以在终端直接运行的 Flappy Bird：

- 按 `Space` 或 `↑` 起跳
- 小鸟会受重力持续下落
- 管道从右向左移动
- 碰到管道或地面就失败
- 通过一根管子加 1 分
- 支持 `q` 退出，`r` 重开
- 最好能在小窗口里也正常显示

你的比赛主题是“等待时间小游戏”，所以这个版本应该追求：

- **启动快**
- **规则秒懂**
- **一局 30 到 60 秒**
- **键位尽量少**

---

## 2. 总体架构

建议按下面四层来拆：

### A. Game Model

保存所有游戏状态：

- 屏幕宽高
- 鸟的位置与速度
- 管道列表
- 得分
- 游戏状态：`ready / playing / gameover / paused`
- 上一次刷新时间
- 随机数种子

### B. Game Update

所有变化都从这里进入：

- 键盘输入
- 定时 tick
- 窗口大小变化
- 重开游戏

### C. Game View

把当前状态渲染成终端字符串：

- 背景
- 小鸟
- 管道
- 得分
- 提示信息
- Game Over 文案

### D. Game Commands

用 command 产生异步消息：

- 定时器消息
- 延迟生成下一根管道
- 重开后重置一帧

Bubble Tea 的更新模式正是这么设计的：`Msg` 进入 `Update`，`Update` 返回新的 model 和可选 `Cmd`，`View` 只负责展示当前状态。([GitHub](https://github.com/charmbracelet/bubbletea))

---

## 3. 目录结构建议

```text
flappy-terminal/
├── cmd/
│   └── flappy/
│       └── main.go
├── internal/
│   ├── game/
│   │   ├── model.go
│   │   ├── update.go
│   │   ├── view.go
│   │   ├── physics.go
│   │   ├── collision.go
│   │   └── pipe.go
│   ├── ui/
│   │   ├── styles.go
│   │   └── keymap.go
│   └── util/
│       └── rand.go
├── assets/
│   └── README.md
├── go.mod
└── README.md
```

如果你想最快做出可玩的 demo，也可以先把所有代码放在一个 `main.go` 里，后面再拆包。比赛阶段最重要的是先让“能玩”站稳，再让“架构”长出漂亮的羽毛。

---

## 4. 核心技术细节

### 4.1 游戏主循环

Flappy Bird 本质上是一个固定频率刷新游戏。建议每 **30ms 到 50ms** 发一次 tick：

- 30ms: 更顺滑
- 50ms: 更省终端性能，调试更轻松

在 Bubble Tea 里，可以用 `tea.Cmd` 触发下一次 tick。文档明确说明 `Cmd` 可以做 I/O 或其他异步动作，而 `Update` 负责根据收到的消息更新状态。([GitHub](https://github.com/charmbracelet/bubbletea))

### 4.2 物理模型

建议用最简洁的离散物理：

```text
velocity += gravity
y += velocity
```

按一下跳跃时：

```text
velocity = flapImpulse
```

建议参数：

- `gravity = 0.35 ~ 0.55`
- `flapImpulse = -4.5 ~ -6.0`
- `pipeSpeed = 1`
- `pipeGap = 5 ~ 7 行`
- `pipeSpawnInterval = 18 ~ 26 ticks`

关键是手感，不是现实主义。终端游戏像一只 ASCII 小鸟，宁可弹一点，也不要像坠入重力井。

### 4.3 管道生成

每根管道记录：

- `x`
- `gapY`
- `gapHeight`
- `passed` 是否已经加分

生成规则：

- 从右侧屏幕外出生
- `gapY` 在合理范围内随机
- 保证上下边界留出至少 2 行安全区

### 4.4 碰撞判定

碰撞只有三类：

1. 小鸟撞地面或天花板
2. 小鸟与管道重叠
3. 小鸟穿过管道但不在 gap 区间

建议把鸟当成一个点或一个小方块。

最简单版本：

- 鸟只有一个坐标 `(birdX, birdY)`
- 管道是整列障碍
- 当 `birdX == pipeX` 时检查 `birdY` 是否落在 gap 里

这会让实现非常快，比赛 demo 足够好。

---

## 5. Bubble Tea 中的事件设计

你可以定义几个自定义消息：

```go
type tickMsg time.Time
type restartMsg struct{}
type resizeMsg struct {
    width  int
    height int
}
```

游戏逻辑里主要处理：

- `tea.KeyPressMsg`
- `tickMsg`
- `tea.WindowSizeMsg` 或你自定义的 resize 消息

Bubble Tea 文档里明确提到，消息可以来自按键、计时器 tick 或其他 I/O 结果，这和你的游戏主循环完全吻合。([GitHub](https://github.com/charmbracelet/bubbletea))

---

## 6. 按键设计

推荐键位：

- `Space` / `↑`：跳跃
- `r`：重开
- `p`：暂停
- `q`：退出

如果你想做得更“终端游戏感”一点，可以加：

- `Enter`：开始
- `Esc`：返回菜单

Bubbles 的 key 组件适合管理这类键位映射，还能自动生成 help 文案。([GitHub](https://github.com/charmbracelet/bubbles))

---

## 7. 渲染策略

### 7.1 先简单后高级

第一版不要直接上复杂图形，建议纯 ASCII：

```text
|                              |
|            o                 |
|                              |
|       #######     #######    |
|       #     #     #     #    |
|       #     #     #     #    |
|------------------------------|
Score: 12
Space: flap   R: restart   Q: quit
```

### 7.2 渲染方式

建议先把整个屏幕写成一个二维 rune 矩阵：

- `[][]rune`
- 默认填充空格
- 依次画背景、管道、小鸟、边框、文字
- 最后把矩阵拼成字符串输出

这样做的好处：

- 逻辑清晰
- 碰撞与渲染分离
- 后面容易加特效

### 7.3 样式层

Lip Gloss 用来包：

- 标题
- 分数卡片
- Game Over 面板
- 按键说明栏

它支持 block-level 布局、padding、颜色、装饰样式，并且会自动处理终端颜色能力差异。([GitHub](https://github.com/charmbracelet/lipgloss))

---

## 8. 状态机设计

建议状态机这样分：

```text
ready -> playing -> gameover
                 ↘ paused
```

### ready

显示标题和操作提示，按空格开始。

### playing

游戏正常运行，tick 更新位置和管道。

### paused

暂停物理更新，但仍可接收按键。

### gameover

停止刷新或减速刷新，提示重开。

这会让逻辑边界非常干净，避免在 Update 里塞进一大坨 if-else 意大利面。

---

## 9. 实现步骤

### 第一步：搭骨架

- 初始化 Go module
- 引入 Bubble Tea、Lip Gloss、Bubbles
- 跑通一个最小 TUI 程序
- 确认可以监听按键并退出

### 第二步：建立 model

- 写 `GameModel`
- 先只放 bird、pipes、score、state、size
- 实现 `Init / Update / View`

### 第三步：实现 tick

- 加一个每 33ms 或 50ms 的 tick
- 每次 tick 更新重力、位置、管道移动
- 先不做碰撞，只看鸟能动起来

### 第四步：加入碰撞

- 地面碰撞
- 管道碰撞
- Game Over 状态

### 第五步：加入得分与重开

- 穿过管道后加分
- `r` 重开
- 失败后显示结果

### 第六步：美化

- Lip Gloss 做面板
- 加标题栏、分数栏、提示栏
- 统一配色和边距

### 第七步：适配终端尺寸

- 最小宽高限制
- 窗口太小时提示用户放大
- Resize 时重算布局

Bubble Tea 文档里提到 view 可以声明终端特性，且 Bubble Tea 会接管重绘逻辑，这让你做尺寸适配时不用自己手搓一套脏活。([GitHub](https://github.com/charmbracelet/bubbletea))

---

## 10. 关键文件职责

### `model.go`

定义游戏状态结构体。

### `update.go`

处理按键、tick、窗口变化、状态切换。

### `view.go`

把当前状态渲染成字符串。

### `physics.go`

重力、跳跃、速度、位移更新。

### `collision.go`

鸟与管道、地面、天花板碰撞判断。

### `pipe.go`

管道生成、移动、回收、计分。

### `styles.go`

Lip Gloss 样式配置。

### `keymap.go`

按键定义和帮助文本。

---

## 11. 推荐的最小数据结构

```go
type GameState int

const (
    StateReady GameState = iota
    StatePlaying
    StatePaused
    StateGameOver
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
    Width, Height int
    Bird          Bird
    Pipes         []Pipe
    Score         int
    State         GameState
    Frame         int
    Seed          int64
}
```

---

## 12. 推荐参数起点

```text
屏幕宽度阈值: 40
屏幕高度阈值: 18
鸟的起点: x = 10, y = height / 2
重力: 0.4
跳跃力度: -5.0
管道速度: 1
管道间隔: 22 tick
管道 gap: 6 行
刷新频率: 33ms
```

这些参数不是标准答案，而是起跑线。真正的手感要靠你边跑边调。

---

## 13. 测试建议

一定要做几个纯逻辑测试：

- 鸟在重力下是否持续下落
- 跳跃后速度是否正确重置
- 管道是否按预期左移
- 穿过管道是否加分一次
- 碰撞是否准确触发
- 重开是否清空状态

因为终端游戏最怕两种灾难：

1. 看起来能玩，但分数不对
2. 看起来能跑，但一碰管道就穿模

---

## 14. 适合比赛展示的加分项

如果时间允许，可以加这几个很值的特性：

- 开场倒计时
- 连续完美通过奖励
- 难度逐步上升
- 失败后显示历史最高分
- 小鸟换皮肤
- 彩蛋模式，比如“夜间模式”

Lip Gloss 的样式能力和 Bubble Tea 的消息驱动结构都适合承载这些扩展。([GitHub](https://github.com/charmbracelet/lipgloss))

---

## 15. 我建议你现在就按这个顺序做

1. 先用 Bubble Tea 跑一个能响应按键的空壳程序。([GitHub][1])
2. 再把鸟上下移动做出来。
3. 再加管道。
4. 再加碰撞和计分。
5. 最后用 Lip Gloss 做一层漂亮的终端外衣。([GitHub][2])

这条路最稳，也最适合“1 分钟小游戏”的比赛节奏。

如果你下一步要，我可以直接给你生成一份 **Go + Bubble Tea 的项目初始化代码和完整目录骨架**，你可以直接复制开跑。