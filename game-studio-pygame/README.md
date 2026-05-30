# PyGame Game Studio

AI 驱动的图形化小游戏自动生成平台。用自然语言描述游戏创意，系统自动生成、构建并运行一个可玩的 PyGame 游戏，并通过 Playground 平台分享与对战。

> **Vibe Hacks #04** 参赛作品 — 主题：「1 分钟小游戏」

## 系统架构

```
Claude Code（推理、设计、调试）
    → MCP Server（21 个工具，文件操作/构建/运行/验证/上传）
        → PyGame Runtime SDK（25+ 模块，渲染/物理/碰撞/实体/场景/AI）
            → PyGame（SDL2 图形、输入、音频）

Playground 平台：
    Next.js (:3080) ←WebSocket→ FastAPI (:8080) → Docker Runner → PyGame 无头渲染
```

## 目录结构

```
game-studio-pygame/
├── apps/
│   ├── mcp-server/              # Python MCP 服务器（21 个工具）
│   │   └── src/pygame_studio_mcp/
│   │       ├── server.py            # 入口，工具分发
│   │       ├── tools/               # 各工具实现（21 个）
│   │       └── lib/                 # DSL 解析、路径、平衡调优
│   ├── playground-api/          # FastAPI 后端
│   │   └── app/
│   │       ├── routes/              # REST + WebSocket 路由
│   │       │   ├── games.py             # 游戏 CRUD + 评分
│   │       │   ├── upload.py            # ZIP 上传
│   │       │   ├── runner.py            # Docker 游戏运行
│   │       │   ├── ws_play.py           # 单人实时游戏串流
│   │       │   ├── ws_mystery.py        # AI 猜谜多人模式
│   │       │   ├── ws_multiplayer.py    # 多人对战模式
│   │       │   └── rooms.py             # 房间管理
│   │       └── services/            # 业务逻辑层
│   └── playground-web/          # Next.js 15 前端
│       └── src/
│           ├── app/                 # 页面路由
│           │   ├── page.tsx             # 游戏大厅/画廊
│           │   ├── play/[name]/         # 单人游戏页面
│           │   ├── play-multiplayer/    # 多人对战大厅
│           │   ├── mystery/[roomId]/    # AI 猜谜房间
│           │   └── upload/              # 上传页面
│           ├── components/          # UI 组件
│           │   ├── GamePlayer.tsx       # Canvas 游戏渲染器
│           │   ├── GameCard.tsx         # 游戏卡片
│           │   ├── MultiplayerLobby.tsx # 多人大厅
│           │   └── UploadForm.tsx       # 上传表单
│           └── lib/                 # API 客户端
├── runtime/
│   └── pygame-sdk/              # PyGame 运行时 SDK（25+ 模块）
│       └── pygame_sdk/
├── templates/                   # 游戏模板（3 种类型）
│   ├── flappy/                      # Flappy Bird 类型
│   ├── shooter/                     # 生存射击类型
│   └── platformer/                  # 平台跳跃类型
├── generated-games/             # AI 生成的游戏
│   ├── wild-survivors/              # 荒野求生
│   ├── contra-rush/                 # 魂斗罗冲刺
│   ├── dark-room-chronicles/        # 暗室编年史
│   ├── fish-beauty-mystery/         # 鱼美人之谜
│   └── zombie-fps/                  # 丧尸 FPS
├── skills/                      # Claude Code 技能约束
├── docker/                      # Docker 配置
│   ├── docker-compose.yml           # 容器编排（web + api + runner）
│   └── game-runner/                 # 游戏沙箱运行器
└── docs/                        # 架构文档 & DSL Schema
```

## 技术栈

| 层级 | 技术 | 核心依赖 |
|------|------|----------|
| MCP Server | Python 3.11+ | mcp, pyyaml, httpx |
| Runtime SDK | Python 3.11+ | pygame, dataclasses |
| 游戏模板 | Python | pygame-sdk (本地) |
| Playground API | Python 3.11+ | FastAPI, SQLAlchemy, Docker, Pillow |
| Playground Web | Next.js 15 | React 19, Tailwind CSS 4, TypeScript |
| 部署 | Docker | docker-compose |

## PyGame SDK 模块

SDK 提供 25+ 个模块，覆盖游戏开发全流程：

- **核心**：entity, scene, tick, config, difficulty
- **渲染**：renderer, styles, camera, screenshot
- **物理**：physics, collision, force, raycast, spatial, material
- **游戏逻辑**：score, input, pathfind, patterns, dungeon, world, ai
- **高级**：vector, multiplayer, llm (LLM 集成)

## 快速开始

### 环境要求

- Python 3.11+
- PyGame 2.5+
- Docker & Docker Compose（Playground 平台）
- Node.js 18+（Playground 前端）

### 安装

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 MCP 服务器（可编辑模式）
cd apps/mcp-server && pip install -e . && cd ../..

# 安装前端依赖
cd apps/playground-web && npm install && cd ../..
```

### 常用命令

```bash
# SDK 测试
make sdk-test

# 模板测试
make template-test-flappy       # Flappy 模板
make template-test-shooter      # Shooter 模板
make template-test-platformer   # Platformer 模板

# MCP 服务器
make mcp-server                 # 构建
make mcp-test                   # 测试

# Playground 平台
make playground-build           # 构建 Docker 镜像
make playground-up              # 启动服务（Web :3080, API :8080）
make playground-down            # 停止服务

# 全部测试
make test-all

# 清理生成文件
make clean
```

## 使用方式

### 1. 通过 Claude Code + MCP

在 Claude Code 中配置 `.mcp.json`，然后直接用自然语言描述游戏：

```
"帮我做一个太空射击游戏，玩家控制飞船躲避陨石并射击外星人"
```

Claude Code 会调用 MCP 工具自动完成：

1. **创建项目** (`create_project` / `create_game`)
2. **生成代码** (`write_game_file` / `scaffold_template` / `apply_game_spec`)
3. **构建验证** (`build_game` → `validate_gameplay`)
4. **截图预览** (`capture_screenshot`)
5. **难度调优** (`tune_balance`)
6. **上传分享** (`upload_to_playground`)

### 2. 通过 Playground 平台

启动服务后访问 `http://localhost:3080`：

- **首页** `/` — 游戏画廊，浏览所有游戏
- **上传** `/upload` — 上传自定义游戏 ZIP
- **单人游戏** `/play/[name]` — 通过 WebSocket 实时串流玩游戏
- **多人对战** `/play-multiplayer` — 创建/加入多人游戏房间
- **AI 猜谜** `/mystery/[roomId]` — AI 驱动的互动猜谜游戏

## 游戏模式

### 单人游戏

浏览器通过 WebSocket 连接 FastAPI，服务端在 Docker 容器中运行 PyGame 无头渲染，逐帧推送 base64 JPEG 到前端 Canvas 渲染。

### 多人对战

多人游戏房间模式，支持创建房间、邀请加入，实时对战。

### AI 猜谜

集成 LLM 的互动猜谜游戏，AI 实时生成谜题并与玩家互动。

## 游戏 DSL

游戏通过 YAML 配置描述，不硬编码参数：

```yaml
name: zombie-survival
genre: shooter
screen:
  width: 800
  height: 600
  fps: 60
player:
  symbol: "@"
  hp: 5
  color: [255, 255, 0]
difficulty:
  easy:   { enemy_speed: 1.5, spawn_rate: 90, player_hp: 6 }
  normal: { enemy_speed: 3.0, spawn_rate: 60, player_hp: 4 }
  hard:   { enemy_speed: 4.5, spawn_rate: 40, player_hp: 2 }
```

## MCP 工具列表（21 个）

### 项目与代码

| 工具 | 功能 |
|------|------|
| `create_project` | 创建游戏项目目录 |
| `create_game` | 一键创建完整游戏 |
| `scaffold_template` | 从模板生成脚手架 |
| `list_templates` | 列出可用模板 |
| `write_game_file` | 写入游戏文件 |
| `read_game_file` | 读取游戏文件 |
| `apply_game_spec` | 应用 YAML 游戏规格 |
| `add_llm_to_game` | 为游戏添加 LLM 集成 |

### 构建与运行

| 工具 | 功能 |
|------|------|
| `build_game` | 语法检查 + 安装依赖 |
| `run_game` | 无头运行游戏 |
| `validate_gameplay` | 3 秒崩溃测试 |
| `capture_frame` | 捕获游戏帧（stdout） |
| `capture_screenshot` | 截取游戏截图（PNG） |

### 调试与调优

| 工具 | 功能 |
|------|------|
| `tune_balance` | 自然语言调整难度 |
| `list_sdk_api` | 列出 SDK API |
| `check_environment` | 检查运行环境 |

### Playground 平台

| 工具 | 功能 |
|------|------|
| `upload_to_playground` | ZIP 打包并上传 |
| `list_playground_games` | 列出平台游戏 |
| `get_playground_game` | 获取游戏详情 |
| `download_from_playground` | 下载平台游戏 |
| `delete_playground_game` | 删除平台游戏 |
| `generate_readme` | 生成游戏 README |

## 设计原则

- **60 秒一局** — 快节奏，"再来一局" 循环
- **单手可玩** — ≤4 个操作键，极低上手门槛
- **一句话规则** — 玩家无需教程
- **渐进难度** — 2-3 秒安全期，逐步提升挑战
- **三档难度** — easy / normal / hard，覆盖不同玩家水平
- **即时重开** — 游戏结束秒开下一局
- **可见得分** — 实时分数显示，驱动竞争

## Interactive Game Streaming 协议

浏览器通过 WebSocket 与服务端实时交互：

```
Browser (Canvas + keyboard) <--WS JSON--> FastAPI /ws/play/{name} --> PyGame headless
```

- `game_stream_runner.py`: Monkey-patch `Renderer.present()` 将帧流式传输为 base64 JPEG（~15KB/帧，~15 FPS）
- `GamePlayer.tsx`: Canvas 渲染器 + 键盘捕获，状态机: idle → connecting → playing → gameover
- 协议消息: `ready`（画布尺寸）、`frame`（base64 JPEG）、`gameover`、`keydown`/`keyup`（输入）

## 评委标准

- 现场由 100+ 真实用户投票
- 真的好玩奖：一等奖 ¥10,000 / 二等奖 ¥5,000 / 三等奖 ¥3,000
- AI 创意奖 ¥1,000 / 社区人气奖 ¥1,000
- 游戏需具备上瘾性、反直觉设计、AI 元素
