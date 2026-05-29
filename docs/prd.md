# Terminal Game Studio PRD

## 基于 Claude Code + MCP 的 Terminal 小游戏开发系统

---

# 1. 项目概述

## 1.1 项目名称

# Terminal Game Studio

备选名称：

* IdleShell
* npc.sh
* Terminal Tavern
* vibequest
* GameForge

---

# 1.2 项目定位

Terminal Game Studio 是一个：

# 基于 Claude Code + MCP 的 Terminal 小游戏开发工作流系统

系统允许用户：

* 使用自然语言描述游戏创意
* 通过 Claude Code 自动完成游戏设计
* 自动生成基于 Shell / Terminal 的小游戏
* 自动构建、调试、运行游戏
* 基于统一 Runtime 快速迭代

---

# 1.3 核心目标

本项目不是：

❌ “AI 自动生成代码”

而是：

# “AI 驱动的 Terminal 游戏开发工作流”

系统核心：

* Claude Code 负责推理与规划
* MCP 提供开发工具能力
* Runtime 提供稳定游戏引擎
* Skill 提供设计行为约束

---

# 1.4 核心场景

## 场景一：等待时间小游戏

开发者在：

* Claude Code
* Cursor
* Gemini CLI
* Copilot Agent

等待代码生成期间：

自动游玩 terminal 小游戏。

---

## 场景二：AI 自动生成小游戏

用户输入：

```text id="8csl4s"
做一个赛博朋克钓鱼游戏
```

Claude Code：

* 自动设计玩法
* 自动生成项目
* 自动编译
* 自动运行

---

## 场景三：AI 自动迭代游戏

Claude：

```text id="p9t2pv"
我觉得敌人刷新速度太快，
我帮你降低 20%
```

自动：

* 修改配置
* Build
* Run
* 测试

---

# 2. 产品目标

---

# 2.1 核心目标

## MVP 阶段

实现：

* Claude Code 自动生成 Terminal 小游戏
* 基于 MCP 的工作流系统
* 基于 BubbleTea 的统一 Runtime
* 游戏模板系统
* 游戏 DSL 系统

---

## 中期目标

实现：

* 自动游戏平衡
* 自动玩法优化
* 自动 Debug
* 自动测试

---

## 长期目标

构建：

# Terminal AI Game Ecosystem

即：

* AI 生成
* AI 测试
* AI 调优
* AI 演化

---

# 2.2 用户价值

## 对开发者

将：

```text id="z8mdmf"
等待时间
```

转化为：

```text id="wdjlwm"
娱乐时间
```

---

## 对 AI Coding 用户

提供：

* 低中断娱乐
* 无需切换窗口
* 保持 terminal workflow

---

## 对 AI Agent 生态

构建：

# AI 原生小游戏开发平台

---

# 3. 产品架构

---

# 3.1 总体架构

```text id="jlwm4x"
┌──────────────────────────┐
│ Claude Code              │
│                          │
│ - 推理                   │
│ - 游戏设计               │
│ - 代码修改               │
│ - Debug                  │
└─────────────┬────────────┘
              │ MCP
              ▼
┌──────────────────────────┐
│ Terminal Game MCP        │
│                          │
│ - create_project         │
│ - scaffold_template      │
│ - apply_game_spec        │
│ - build_game             │
│ - run_game               │
│ - validate_gameplay      │
│ - capture_frame          │
└─────────────┬────────────┘
              ▼
┌──────────────────────────┐
│ BubbleTea Runtime SDK    │
│                          │
│ - Renderer               │
│ - Physics                │
│ - Input                  │
│ - Entity System          │
│ - Animation              │
└──────────────────────────┘
```

---

# 3.2 架构原则

---

## 原则一

# Claude 负责思考

包括：

* 游戏设计
* 玩法设计
* 参数调整
* Debug

---

## 原则二

# MCP 负责执行

包括：

* 文件创建
* 模板复制
* Build
* Run

---

## 原则三

# Runtime 负责稳定

包括：

* 游戏循环
* 渲染
* 输入
* 物理系统

---

# 4. 系统模块设计

---

# 4.1 Claude Skill System

Skill 用于：

# 约束 Claude 的行为

---

## Skill 列表

### game-design.md

约束：

* 60 秒小游戏
* 单手操作
* 简单规则
* ASCII 风格

---

### runtime-rules.md

约束：

* 必须使用 BubbleTea Runtime
* 不允许重写 Engine
* 通过配置扩展

---

### game-balance.md

约束：

* 难度渐进
* 避免瞬间死亡
* 前 15 秒简单

---

# 4.2 MCP Server

MCP 为 Claude 提供：

# 游戏开发工具链

---

## MCP Tool 列表

---

### create_project

创建游戏项目。

输入：

```json id="9yjlwm"
{
  "name": "cyber-fishing"
}
```

---

### list_templates

返回：

```text id="jlwm0c"
flappy
shooter
rogue
typing
idle
```

---

### scaffold_template

复制模板。

---

### apply_game_spec

将 DSL 注入 Runtime。

---

### build_game

执行：

```bash id="jlwm1d"
go build
```

---

### run_game

启动 terminal 游戏。

---

### validate_gameplay

自动检测：

* 是否崩溃
* 是否能得分
* 是否卡死

---

### capture_frame

获取 terminal 截图。

供 Claude 分析。

---

### tune_balance

自动调整：

* enemy speed
* gravity
* spawn rate

---

# 4.3 Runtime SDK

---

# Runtime 是整个系统的稳定核心

---

## 技术栈

### Go

### BubbleTea

官方：

* [Bubble Tea](https://github.com/charmbracelet/bubbletea?utm_source=chatgpt.com)
* [Lip Gloss](https://github.com/charmbracelet/lipgloss?utm_source=chatgpt.com)

---

# Runtime 模块

---

## Renderer

负责：

* ASCII 渲染
* Terminal 动画
* ANSI Color

---

## Physics

负责：

* movement
* gravity
* collision

---

## Input

负责：

* keyboard
* pause
* restart

---

## Entity System

统一实体：

* Player
* Enemy
* Bullet
* Obstacle

---

## Scene System

统一：

* Menu
* Gameplay
* GameOver

---

# 5. Game DSL 设计

---

# 5.1 设计目标

DSL 用于：

# 让 Claude 设计游戏

而不是：

# 直接喷代码

---

# 5.2 DSL 示例

```yaml id="jlwm2e"
name: zombie-survival

genre: shooter

screen:
  width: 80
  height: 24

player:
  symbol: "@"
  hp: 5

enemy:
  symbol: "Z"
  speed: 2

controls:
  move: arrows
  attack: auto

gameplay:
  objective: survive
  duration: 60s

difficulty:
  scaling: linear
```

---

# 5.3 DSL 职责

DSL 只负责：

* 游戏规则
* 参数
* 配置

---

# Runtime 负责：

* 游戏执行
* 渲染
* 输入
* 动画

---

# 6. Template System

---

# 6.1 设计目标

避免：

```text id="jlwm3f"
Claude 每次重新发明轮子
```

---

# 6.2 模板类型

---

## flappy

Flappy Bird 类型。

---

## shooter

生存射击类型。

---

## rogue

Roguelike 类型。

---

## typing

打字类型。

---

## idle

挂机类型。

---

# 6.3 模板结构

```text id="jlwm4g"
templates/
 └── shooter/
      ├── main.go
      ├── renderer.go
      ├── physics.go
      ├── entities.go
      └── config.yaml
```

---

# 7. Claude Code 工作流

---

# 7.1 工作流

```text id="jlwm5h"
用户需求
    ↓
Claude 分析
    ↓
选择模板
    ↓
生成 DSL
    ↓
调用 MCP
    ↓
Build
    ↓
Run
    ↓
Debug
```

---

# 7.2 示例流程

用户：

```text id="jlwm6i"
做一个 ninja survival game
```

---

Claude：

## Step 1

调用：

```text id="jlwm7j"
list_templates()
```

---

## Step 2

选择：

```text id="jlwm8k"
shooter
```

---

## Step 3

生成：

```yaml id="jlwm9l"
player:
  symbol: N
enemy:
  symbol: O
```

---

## Step 4

调用：

```text id="jlwm0m"
apply_game_spec()
```

---

## Step 5

Build。

---

## Step 6

失败则自动修复。

---

# 8. 自动修复系统

---

# 8.1 设计目标

利用 Claude Code：

# 自动 Debug

---

# 8.2 工作流

```text id="jlwm1n"
go build
    ↓
读取错误
    ↓
Claude 修复
    ↓
重新 build
```

---

# 8.3 优势

实现：

# AI 自治开发循环

---

# 9. TUI 系统

---

# 9.1 独立模式

用户：

```bash id="jlwm2o"
game-designer
```

---

# 9.2 TUI 页面

---

## 首页

输入游戏 idea。

---

## Spec 页面

显示 DSL。

---

## Build 页面

显示生成日志。

---

## Run 页面

启动游戏。

---

# 10. 项目目录结构

```text id="jlwm3p"
terminal-game-studio/
│
├── apps/
│   ├── mcp-server/
│   └── tui/
│
├── runtime/
│   └── bubbletea-sdk/
│
├── templates/
│   ├── flappy/
│   ├── shooter/
│   ├── rogue/
│   ├── typing/
│   └── idle/
│
├── skills/
│   ├── game-design.md
│   ├── runtime-rules.md
│   └── game-balance.md
│
├── generated-games/
│
└── docs/
```

---

# 11. 技术选型

---

# MCP Server

## TypeScript

原因：

* MCP SDK 完整
* 文件系统方便
* Claude 生态成熟

---

# Runtime

## Go + BubbleTea

原因：

* Terminal 动画优秀
* AI 易生成
* 性能好

---

# TUI

## Ink

官方：

[Ink](https://github.com/vadimdemedes/ink?utm_source=chatgpt.com)

---

# 12. MVP 范围

---

# 第一阶段仅支持：

## 游戏类型

* Flappy
* Shooter
* Rogue-lite

---

# 功能

* 模板生成
* Build
* Run
* Claude 自动 Debug

---

# 不做：

* 联网
* 音频
* 多人
* 图形化 GUI

---

# 13. 风险与挑战

---

# 风险一

Claude 生成逻辑失控。

---

# 解决方案

严格：

* Runtime
* Template
* DSL

---

# 风险二

游戏不可玩。

---

# 解决方案

加入：

* validate_gameplay
* auto balance

---

# 风险三

Build 失败率高。

---

# 解决方案

Claude 自动修复循环。

---

# 14. 未来规划

---

# Phase 1

Terminal Game Runtime。

---

# Phase 2

MCP Tooling。

---

# Phase 3

Claude Auto Debug。

---

# Phase 4

AI Gameplay Testing。

---

# Phase 5

AI 自动设计新玩法。

---

# 15. 最终愿景

Terminal Game Studio 最终目标不是：

# “AI 写小游戏”

而是：

# “构建 AI 原生 Terminal 游戏生态”

在未来：

* Claude 在写代码
* 用户在 terminal 玩游戏
* AI 自动调优玩法
* AI 自动生成新内容

形成：

# “等待时间娱乐系统” 🚀
