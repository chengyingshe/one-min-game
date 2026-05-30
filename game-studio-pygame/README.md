# PyGame Game Studio

AI 驱动的图形化小游戏自动生成系统。用户用自然语言描述游戏创意，系统自动生成、构建并运行一个可玩的 PyGame 游戏。

> **Vibe Hacks #04** 参赛作品 — 主题：「1 分钟小游戏」| 截止日期：2026-05-30

## 系统架构

```
Claude Code（推理、设计、调试）
    → MCP Server（16 个工具，文件操作/构建/运行/验证）
        → PyGame Runtime SDK（14+ 模块，渲染/物理/碰撞/实体/场景）
            → PyGame（SDL2 图形、输入、音频）

Playground 平台：
    Next.js 前端 → FastAPI 后端 → Docker 游戏运行器 → PyGame 无头渲染
```

## 目录结构

```
game-studio-pygame/
├── apps/
│   ├── mcp-server/              # Python MCP 服务器（16 个工具）
│   ├── playground-api/          # FastAPI 后端（游戏上传/运行/截图）
│   └── playground-web/          # Next.js 前端（游戏展示/社区投票）
├── runtime/
│   └── pygame-sdk/              # PyGame 运行时 SDK（14+ 模块）
├── templates/                   # 游戏模板
│   ├── flappy/                  # Flappy Bird 类型
│   ├── shooter/                 # 生存射击类型
│   └── platformer/              # 平台跳跃类型
├── generated-games/             # AI 生成的游戏输出
├── skills/                      # Claude Code 技能约束
├── docker/                      # Docker 配置
│   ├── docker-compose.yml       # 容器编排
│   └── game-runner/             # 游戏沙箱运行器
└── docs/                        # 架构文档 & DSL Schema
```

## 技术栈

| 层级           | 技术         | 核心依赖                            |
| -------------- | ------------ | ----------------------------------- |
| MCP Server     | Python 3.11+ | mcp, pyyaml                         |
| Runtime SDK    | Python 3.11+ | pygame, dataclasses                 |
| 游戏模板       | Python       | pygame-sdk (本地)                   |
| Playground API | Python 3.11+ | FastAPI, SQLAlchemy, Docker, Pillow |
| Playground Web | Next.js 15   | React 19, Tailwind CSS 4            |
| 部署           | Docker       | docker-compose                      |

## PyGame SDK 模块

SDK 提供 24 个模块，覆盖游戏开发全流程：

- **核心**：entity, scene, tick, config, difficulty
- **渲染**：renderer, styles, camera, screenshot
- **物理**：physics, collision, force, raycast, spatial, material
- **游戏逻辑**：score, input, pathfind, patterns, dungeon, world, ai

## 快速开始

### 环境要求

- Python 3.11+
- PyGame 2.x
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
make templates                  # 全部模板
make template-test-flappy       # 单个模板

# MCP 服务器
make mcp-server                 # 构建
make mcp-test                   # 测试

# Playground 平台
make playground-build           # 构建 Docker 镜像
make playground-up              # 启动服务
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

- 创建项目 → 生成游戏代码 → 构建 → 运行 → 验证 → 截图 → 调优

### 2. 通过 Playground 平台

访问 `http://localhost:3080`，在 Web 界面上传游戏或浏览社区作品。

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
  easy: { enemy_speed: 1.5, spawn_rate: 90, player_hp: 6 }
  normal: { enemy_speed: 3.0, spawn_rate: 60, player_hp: 4 }
  hard: { enemy_speed: 4.5, spawn_rate: 40, player_hp: 2 }
```

## MCP 工具列表

| 工具               | 功能               |
| ------------------ | ------------------ |
| create_project     | 创建游戏项目目录   |
| scaffold_template  | 从模板生成脚手架   |
| create_game        | 一键创建完整游戏   |
| apply_game_spec    | 应用 YAML 游戏规格 |
| build_game         | 构建游戏           |
| run_game           | 运行游戏           |
| validate_gameplay  | 验证游戏可玩性     |
| capture_frame      | 捕获游戏帧数据     |
| capture_screenshot | 截取游戏截图       |
| tune_balance       | 调整难度平衡       |
| list_sdk_api       | 列出 SDK API       |
| read_game_file     | 读取游戏文件       |
| write_game_file    | 写入游戏文件       |
| list_templates     | 列出可用模板       |
| generate_readme    | 生成游戏说明       |
| check_environment  | 检查运行环境       |

## 设计原则

- **60 秒一局** — 快节奏，"再来一局" 循环
- **单手可玩** — 简单操控，极低上手门槛
- **一句话规则** — 玩家无需教程
- **渐进难度** — 2-3 秒安全期，逐步提升挑战
- **三档难度** — easy / normal / hard，覆盖不同玩家水平

## 评委标准

- 现场由 100+ 真实用户投票
- 真的好玩奖：一等奖 ¥10,000 / 二等奖 ¥5,000 / 三等奖 ¥3,000
- AI 创意奖 ¥1,000 / 社区人气奖 ¥1,000
- 游戏需具备上瘾性、反直觉设计、AI 元素
