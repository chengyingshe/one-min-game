"""《相府鱼美人》PyGame 场景渲染器

纯视觉渲染，接收 stdin JSON 指令，输出帧到 stdout。
通过 game_stream_runner.py 流式传输到浏览器。

协议：
  stdin  ← {"scene": "mansion"}       — 渲染相府场景
  stdin  ← {"scene": "pool"}          — 渲染水池场景
  stdin  ← {"scene": "slope"}         — 渲染十里坡
  stdin  ← {"scene": "dorm_hunter"}  — 渲染除妖人宿舍
  stdin  ← {"scene": "dorm_maid"}     — 渲染丫鬟宿舍
  stdin  ← {"scene": "dorm_swordsman"} — 渲染剑客宿舍
  stdin  ← {"scene": "dorm_cook"}     — 渲染女厨宿舍
  stdin  ← {"scene": "search_hunter"} — 渲染搜查除妖人
  stdin  ← {"scene": "reveal"}        — 渲染真相揭晓
"""
from __future__ import annotations

import json
import sys
import os
import time
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "pygame-sdk"))

import pygame

W, H = 800, 600

# ============================================================
# Colors (古风配色)
# ============================================================

C_BG = (45, 35, 55)
C_PAPER = (235, 220, 195)
C_PAPER_DARK = (210, 195, 170)
C_INK = (35, 25, 20)
C_INK_LIGHT = (80, 65, 50)
C_RED = (180, 50, 50)
C_GOLD = (220, 180, 80)
C_WATER = (60, 100, 140)
C_WATER_LIGHT = (80, 140, 180)
C_ROOF = (120, 60, 50)
C_WALL = (160, 140, 120)
C_WOOD = (100, 70, 45)
C_GRASS = (70, 110, 55)
C_STONE = (140, 135, 125)
C_FOG = (180, 175, 170)

# Character colors (match scenario.py)
CHAR_COLORS = {
    "hunter": (255, 220, 50),
    "maid": (255, 150, 180),
    "swordsman": (100, 180, 255),
    "cook": (100, 220, 100),
}

CJK_CANDIDATES = [
    "notosanscjksc", "notosanscjk", "pingfangsc", "hiraginosansgb",
    "stheitimedium", "songti", "arialunicodems", "microsoftyahei",
    "wenquanyimicrohei", "droidsansfallback",
]


def _get_cjk_font(size):
    pygame.font.init()
    available = pygame.font.get_fonts()
    for c in CJK_CANDIDATES:
        if c in available:
            return pygame.font.SysFont(c, size)
    return pygame.font.Font(None, size)


def _wrap(text, width=28):
    lines = []
    for p in text.split("\n"):
        if not p.strip():
            lines.append("")
            continue
        while len(p) > width:
            cut = max(p[:width].rfind(c) for c in "，。、；：！？ ")
            if cut == -1:
                cut = width - 1
            lines.append(p[:cut + 1])
            p = p[cut + 1:]
        if p:
            lines.append(p)
    return lines


class SceneRenderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_lg = _get_cjk_font(32)
        self.font_md = _get_cjk_font(20)
        self.font_sm = _get_cjk_font(16)
        self.font_xs = _get_cjk_font(13)
        self.font_title = _get_cjk_font(48)
        self.current_scene = "title"
        self.transition_alpha = 0
        self._input_queue: list[dict] = []
        self._lock = threading.Lock()

    def queue_scene(self, scene_name: str, **kwargs):
        with self._lock:
            self._input_queue.append({"scene": scene_name, **kwargs})

    def get_next_scene(self):
        with self._lock:
            if self._input_queue:
                return self._input_queue.pop(0)
        return None

    def draw(self):
        cmd = self.get_next_scene()
        if cmd:
            self.current_scene = cmd["scene"]

        handler = {
            "title": self._draw_title,
            "mansion": self._draw_mansion,
            "pool": self._draw_pool,
            "slope": self._draw_slope,
            "dorm_hunter": self._draw_dorm_hunter,
            "dorm_maid": self._draw_dorm_maid,
            "dorm_swordsman": self._draw_dorm_swordsman,
            "dorm_cook": self._draw_dorm_cook,
            "search_hunter": self._draw_search_hunter,
            "search_maid": self._draw_search_maid,
            "search_swordsman": self._draw_search_swordsman,
            "search_cook": self._draw_search_cook,
            "reveal": self._draw_reveal,
        }.get(self.current_scene, self._draw_title)
        if handler:
            handler()

    def _text(self, text, x, y, color=C_INK, font=None):
        f = font or self.font_md
        rendered = f.render(text, True, color)
        self.screen.blit(rendered, (x, y))

    def _centered(self, text, y, color=C_INK, font=None):
        f = font or self.font_md
        rendered = f.render(text, True, color)
        self.screen.blit(rendered, ((W - rendered.get_width()) // 2, y))

    def _draw_gradient(self, c_top, c_bot):
        for y in range(H):
            t = y / max(H - 1, 1)
            r = int(c_top[0] + (c_bot[0] - c_top[0]) * t)
            g = int(c_top[1] + (c_bot[1] - c_top[1]) * t)
            b = int(c_top[2] + (c_bot[2] - c_top[2]) * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (W, y))

    def _draw_paper_bg(self):
        """古风纸质背景"""
        self.screen.fill(C_PAPER)
        # Subtle texture lines
        for y in range(0, H, 3):
            pygame.draw.line(self.screen, C_PAPER_DARK, (0, y), (W, y), 1)

    def _draw_character_portrait(self, char_id, x, y, size=120):
        """绘制角色简笔肖像"""
        color = CHAR_COLORS.get(char_id, C_INK)
        # Head
        pygame.draw.circle(self.screen, color, (x, y), size // 4)
        # Body
        pygame.draw.ellipse(self.screen, color, (x - size // 3, y + size // 3, size * 2 // 3, size // 2))
        # Name label
        names = {"hunter": "除妖人", "maid": "丫鬟", "swordsman": "剑客", "cook": "女厨"}
        self._text(names.get(char_id, "?"), x - 20, y + size // 2 + size // 3, C_INK, self.font_sm)

    # ============================================================
    # Scene implementations
    # ============================================================

    def _draw_title(self):
        self._draw_paper_bg()
        # Title
        self._centered("相府鱼美人", 80, C_RED, self.font_title)
        self._centered("—— 剧本杀 ——", 150, C_INK_LIGHT, self.font_lg)

        pygame.draw.line(self.screen, C_INK_LIGHT, (200, 210), (600, 210), 2)

        # Scene description
        desc_lines = [
            "宋朝·相府·鱼妖传说",
            "",
            "法海和尚察觉到鱼妖妖气，",
            "来到相府调查。",
            "",
            "四位嫌疑人，一个隐藏的真相。",
            "谁是鱼妖所化？",
        ]
        y = 240
        for line in desc_lines:
            self._centered(line, y, C_INK, self.font_md)
            y += 28

        # Character previews
        chars = ["hunter", "maid", "swordsman", "cook"]
        names = {"hunter": "除妖人", "maid": "丫鬟", "swordsman": "剑客", "cook": "女厨"}
        start_x = 140
        for i, cid in enumerate(chars):
            x = start_x + i * 160
            self._draw_character_portrait(cid, x + 40, 470, 80)
            self._centered(names[cid], 530, CHAR_COLORS[cid], self.font_sm)

    def _draw_mansion(self):
        """相府大门场景"""
        self._draw_paper_bg()

        # Roof
        pts = [(150, 150), (400, 60), (650, 150)]
        pygame.draw.polygon(self.screen, C_ROOF, pts)
        pygame.draw.lines(self.screen, C_INK, True, pts, 2)

        # Pillars
        for x in [200, 400, 600]:
            pygame.draw.rect(self.screen, C_RED, (x - 10, 150, 20, 300))
            pygame.draw.rect(self.screen, C_INK, (x - 10, 150, 20, 300), 1)

        # Walls
        pygame.draw.rect(self.screen, C_WALL, (190, 180, 40, 250))
        pygame.draw.rect(self.screen, C_WALL, (570, 180, 40, 250))

        # Door
        pygame.draw.rect(self.screen, C_WOOD, (340, 200, 120, 250))
        pygame.draw.rect(self.screen, C_INK, (340, 200, 120, 250), 2)
        # Door handles
        pygame.draw.circle(self.screen, C_GOLD, (390, 320), 5)
        pygame.draw.circle(self.screen, C_GOLD, (410, 320), 5)

        # Sign
        pygame.draw.rect(self.screen, C_PAPER_DARK, (340, 155, 120, 35))
        self._centered("相 府", 160, C_RED, self.font_md)

        # Ground
        pygame.draw.rect(self.screen, C_STONE, (0, 450, W, 150))
        # Steps
        for i in range(3):
            pygame.draw.rect(self.screen, C_STONE, (320 + i * 10, 450 - i * 15, 140 - i * 20, 15 + i * 15))
            pygame.draw.rect(self.screen, C_INK, (320 + i * 10, 450 - i * 15, 140 - i * 20, 15 + i * 15), 1)

        # Decorative text
        self._centered("—— 宋朝·相府 ——", 20, C_INK_LIGHT, self.font_lg)

    def _draw_pool(self):
        """水池场景"""
        self._draw_paper_bg()

        # Water surface
        pygame.draw.ellipse(self.screen, C_WATER, (150, 200, 500, 200))
        # Ripples
        t = pygame.time.get_ticks() / 1000
        for i in range(5):
            rx = 400 + int(40 * (i % 3 - 1))
            ry = 300 + int(20 * (i % 2 - 1))
            r = int(20 + 10 * abs(((t + i * 0.5) % 2) - 1))
            pygame.draw.circle(self.screen, C_WATER_LIGHT, (rx, ry), r, 1)

        # Lotus / koi hint
        self._centered("锦 鲤", 280, C_RED, self.font_lg)
        # Small red circle (koi)
        pygame.draw.circle(self.screen, C_RED, (380, 310), 8)

        # Bridge
        pygame.draw.arc(self.screen, C_WOOD, (200, 220, 400, 100), 0.2, 2.9, 4)

        # Banks
        pygame.draw.rect(self.screen, C_GRASS, (0, 400, W, 200))
        # Stones around pool
        for x in range(150, 650, 30):
            h = 5 + (x * 7) % 8
            pygame.draw.ellipse(self.screen, C_STONE, (x, 195 - h // 2, 25, h))

        # Moon
        pygame.draw.circle(self.screen, C_GOLD, (650, 80), 40)
        pygame.draw.circle(self.screen, C_PAPER, (660, 70), 35)

        self._centered("—— 相府水池 · 连通十里坡 ——", 20, C_INK_LIGHT, self.font_md)

    def _draw_slope(self):
        """十里坡场景"""
        self._draw_paper_bg()

        # Mountain path
        pts = [(0, 300), (200, 200), (400, 250), (600, 180), (800, 280)]
        pygame.draw.lines(self.screen, C_INK_LIGHT, False, pts, 3)
        for i in range(len(pts) - 1):
            pygame.draw.line(self.screen, C_GRASS, (pts[i][0], pts[i][1] + 15), (pts[i + 1][0], pts[i + 1][1] + 15), 30)

        # Trees
        for x in [100, 300, 500, 700]:
            y = 150 + (x % 5) * 20
            pygame.draw.rect(self.screen, C_WOOD, (x - 5, y, 10, 60))
            pygame.draw.circle(self.screen, C_GRASS, (x, y - 10), 30)
            pygame.draw.circle(self.screen, (50, 90, 40), (x, y - 10), 22)

        # Snake hint
        t = pygame.time.get_ticks() / 800
        sx = 350 + int(20 * abs(((t % 2) - 1)))
        pygame.draw.circle(self.screen, C_RED, (sx, 240), 12)
        self._text("蛇妖出没", sx - 20, 260, C_RED, self.font_xs)

        # Title
        self._centered("—— 十里坡 ——", 20, C_INK_LIGHT, self.font_lg)

        # Fog effect
        for i in range(20):
            fx = (i * 47 + int(t * 10)) % W
            fy = 350 + (i * 13) % 100
            pygame.draw.circle(self.screen, (*C_FOG, 60), (fx, fy), 20)

    def _draw_dorm_base(self, char_id, items_desc, search=False):
        """宿舍场景基础"""
        color = CHAR_COLORS.get(char_id, C_INK)
        names = {"hunter": "除妖人宿舍", "maid": "丫鬟宿舍", "swordsman": "剑客宿舍", "cook": "女厨宿舍"}
        search_names = {"hunter": "搜查除妖人", "maid": "搜查丫鬟", "swordsman": "搜查剑客", "cook": "搜查女厨"}
        title = search_names[char_id] if search else names[char_id]

        self._draw_paper_bg()

        # Room frame
        pygame.draw.rect(self.screen, C_WALL, (100, 100, 600, 350))
        pygame.draw.rect(self.screen, C_INK, (100, 100, 600, 350), 3)

        # Floor
        pygame.draw.rect(self.screen, C_WOOD, (100, 380, 600, 70))
        for i in range(12):
            pygame.draw.line(self.screen, C_INK_LIGHT, (100 + i * 50, 380), (100 + i * 50, 450), 1)

        # Door
        pygame.draw.rect(self.screen, C_WOOD, (340, 200, 120, 250))
        pygame.draw.rect(self.screen, C_INK, (340, 200, 120, 250), 2)
        pygame.draw.circle(self.screen, C_GOLD, (395, 330), 4)

        # Character portrait
        self._draw_character_portrait(char_id, 400, 140, 80)

        # Items
        self._centered(f"—— {title} ——", 30, C_INK_LIGHT, self.font_lg)

        y = 470
        for item in items_desc:
            self._centered(f"• {item}", y, color, self.font_sm)
            y += 24

    def _draw_dorm_hunter(self):
        self._draw_dorm_base("hunter", ["长笛", "捉妖器具"])

    def _draw_dorm_maid(self):
        self._draw_dorm_base("maid", ["破旧衣服", "菜肴香味"])

    def _draw_dorm_swordsman(self):
        self._draw_dorm_base("swordsman", ["女厨脚印", "长剑"])

    def _draw_dorm_cook(self):
        self._draw_dorm_base("cook", ["除妖人脚印", "一口锅"])

    def _draw_search_hunter(self):
        self._draw_dorm_base("hunter", ["发现：写着爱慕小姐的日记"], search=True)

    def _draw_search_maid(self):
        self._draw_dorm_base("maid", ["发现：喜欢除妖人的日记"], search=True)

    def _draw_search_swordsman(self):
        self._draw_dorm_base("swordsman", ["发现：写有「大好生活在等着我」的日记"], search=True)

    def _draw_search_cook(self):
        self._draw_dorm_base("cook", ["发现：一本菜谱"], search=True)

    def _draw_reveal(self):
        """真相揭晓场景"""
        # Dark dramatic background
        self._draw_gradient((20, 10, 30), (50, 25, 40))

        # Spotlight on swordsman
        t = pygame.time.get_ticks() / 1000
        pulse = abs(((t % 2) - 1))
        glow_r = int(60 + 20 * pulse)
        pygame.draw.circle(self.screen, (glow_r, glow_r, glow_r + 20), (400, 220), 100, 3)

        self._draw_character_portrait("swordsman", 400, 180, 100)

        self._centered("真相揭晓", 40, C_GOLD, self.font_title)
        self._centered("剑客 = 鱼妖（鲤鱼精）", 320, C_RED, self.font_lg)

        desc_lines = [
            "他原本是相府水池中消失的红色大鲤鱼",
            "因暗恋丫鬟，化身为男性人形",
            "暗中操控一切，离间众人",
        ]
        y = 380
        for line in desc_lines:
            self._centered(line, y, C_FOG, self.font_sm)
            y += 24
