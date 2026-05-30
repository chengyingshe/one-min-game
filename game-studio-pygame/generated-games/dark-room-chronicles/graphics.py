"""视觉资源生成器 — 房间布局、角色立绘、氛围背景"""

import pygame
import os

# ============ 配色方案 ============
C_BG = (12, 8, 24)
C_PANEL = (18, 14, 32)
C_PANEL_LIGHT = (28, 22, 48)
C_WALL = (60, 50, 45)
C_WALL_DARK = (40, 32, 28)
C_FLOOR = (22, 18, 16)
C_FURNITURE = (50, 38, 28)
C_FURNITURE_LIGHT = (70, 55, 40)
C_DOOR = (90, 70, 45)
C_WINDOW = (30, 40, 80)
C_BODY = (180, 40, 40)
C_EVIDENCE = (0, 200, 220)
C_EVIDENCE_FOUND = (80, 180, 80)
C_EVIDENCE_HIDDEN = (180, 120, 220)
C_CURSOR = (255, 220, 60)
C_HIGHLIGHT = (255, 220, 60)
C_TEXT_DIM = (120, 110, 100)
C_BLOOD = (140, 20, 20)
C_SNOW = (200, 210, 230)
C_FIRE = (200, 100, 30)

CJK_CANDIDATES = [
    "notosanscjksc", "notosanscjk", "notoserifcjksc",
    "pingfangsc", "hiraginosansgb", "stheitimedium",
    "stheitilight", "songti", "arialunicodems",
    "microsoftyahei", "simsun", "wenquanyimicrohei",
]


def _get_cjk_font(size):
    pygame.font.init()
    available = pygame.font.get_fonts()
    for c in CJK_CANDIDATES:
        if c in available:
            return pygame.font.SysFont(c, size)
    return pygame.font.Font(None, size)


def _draw_rounded_rect(surf, color, rect, radius=8):
    x, y, w, h = rect
    pygame.draw.rect(surf, color, (x + radius, y, w - 2 * radius, h))
    pygame.draw.rect(surf, color, (x, y + radius, w, h - 2 * radius))
    for cx, cy in [(x + radius, y + radius), (x + w - radius, y + radius),
                   (x + radius, y + h - radius), (x + w - radius, y + h - radius)]:
        pygame.draw.circle(surf, color, (cx, cy), radius)


def _draw_gradient_v(surf, rect, color_top, color_bot):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(h - 1, 1)
        r = int(color_top[0] + (color_bot[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bot[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bot[2] - color_top[2]) * t)
        pygame.draw.line(surf, (r, g, b), (x, y + i), (x + w, y + i))


class GraphicsManager:
    def __init__(self):
        self.font_lg = _get_cjk_font(28)
        self.font_md = _get_cjk_font(18)
        self.font_sm = _get_cjk_font(14)
        self.font_xs = _get_cjk_font(12)
        self.portraits = {}
        self.rooms = {}
        self.backgrounds = {}
        self._generate_all()

    def _generate_all(self):
        self._gen_portraits()
        self._gen_rooms()
        self._gen_backgrounds()

    # ============ 角色立绘 (noir剪影风格) ============
    def _gen_portraits(self):
        portraits = {
            # 案一
            "wife": ("陈夫人·苏婉清", (180, 140, 160), self._draw_portrait_wife),
            "secretary": ("林秘书·林志远", (140, 160, 120), self._draw_portrait_secretary),
            "butler": ("赵管家·赵德全", (160, 150, 130), self._draw_portrait_butler),
            # 案二
            "fan": ("粉丝·周小燕", (200, 160, 180), self._draw_portrait_fan),
            "doctor": ("孙医生·孙立群", (150, 170, 190), self._draw_portrait_doctor),
            "manager": ("旅馆主·何雪峰", (170, 150, 130), self._draw_portrait_manager),
            "stranger": ("神秘客·方远", (100, 100, 120), self._draw_portrait_stranger),
            # 案三
            "apprentice": ("学徒·梅小曼", (180, 160, 200), self._draw_portrait_apprentice),
            "lawyer": ("律师·钱柏然", (160, 170, 150), self._draw_portrait_lawyer),
            "doctor3": ("医生·孙立群", (150, 170, 190), self._draw_portrait_doctor),
            "groundskeeper": ("守塔人·老吴", (140, 130, 120), self._draw_portrait_groundskeeper),
            "assistant_chen": ("助理·陈诗雨", (190, 170, 160), self._draw_portrait_assistant),
        }
        for pid, (name, accent, draw_fn) in portraits.items():
            surf = pygame.Surface((240, 320), pygame.SRCALPHA)
            self._draw_portrait_base(surf, accent)
            draw_fn(surf, accent)
            label = self.font_sm.render(name, True, (220, 210, 200))
            surf.blit(label, ((240 - label.get_width()) // 2, 290))
            self.portraits[pid] = surf

    def _draw_portrait_base(self, surf, accent):
        # 深色圆形背景
        pygame.draw.circle(surf, (20, 16, 30), (120, 130), 105)
        pygame.draw.circle(surf, (30, 24, 45), (120, 130), 100)
        # 头部轮廓
        pygame.draw.ellipse(surf, (45, 38, 55), (70, 40, 100, 120))
        # 身体
        pygame.draw.ellipse(surf, (35, 30, 45), (55, 145, 130, 100))

    def _draw_portrait_wife(self, surf, accent):
        # 发髻
        pygame.draw.circle(surf, (40, 35, 30), (120, 75), 35)
        pygame.draw.circle(surf, (50, 42, 35), (120, 60), 18)
        # 项链
        pygame.draw.circle(surf, (220, 200, 180), (120, 168), 4)
        pygame.draw.arc(surf, (220, 200, 180), (100, 158, 40, 20), 0.2, 2.9, 2)

    def _draw_portrait_secretary(self, surf, accent):
        # 眼镜
        pygame.draw.circle(surf, accent, (100, 90), 12, 2)
        pygame.draw.circle(surf, accent, (140, 90), 12, 2)
        pygame.draw.line(surf, accent, (112, 90), (128, 90), 2)
        # 汗滴
        pygame.draw.circle(surf, (100, 160, 220), (155, 75), 3)

    def _draw_portrait_butler(self, surf, accent):
        # 领结
        pygame.draw.polygon(surf, (60, 50, 50), [(110, 155), (120, 162), (130, 155), (120, 170)])
        # 胡子
        pygame.draw.arc(surf, (80, 70, 60), (95, 105, 50, 25), 3.14, 6.28, 2)

    def _draw_portrait_fan(self, surf, accent):
        # 马尾
        pygame.draw.line(surf, accent, (155, 60), (170, 100), 5)
        # 书
        pygame.draw.rect(surf, (120, 90, 60), (155, 190, 35, 25))
        pygame.draw.line(surf, (80, 60, 40), (172, 190), (172, 215), 1)

    def _draw_portrait_doctor(self, surf, accent):
        # 眼镜
        pygame.draw.circle(surf, accent, (100, 88), 11, 2)
        pygame.draw.circle(surf, accent, (140, 88), 11, 2)
        pygame.draw.line(surf, accent, (111, 88), (129, 88), 2)
        # 听诊器
        pygame.draw.circle(surf, accent, (120, 185), 6, 2)
        pygame.draw.arc(surf, accent, (95, 170, 50, 30), 0, 3.14, 2)

    def _draw_portrait_manager(self, surf, accent):
        # 发际线后退
        pygame.draw.ellipse(surf, (50, 44, 38), (75, 45, 90, 60))
        # 宽脸
        pygame.draw.ellipse(surf, (45, 38, 55), (70, 42, 100, 115))

    def _draw_portrait_stranger(self, surf, accent):
        # 兜帽阴影
        pygame.draw.ellipse(surf, (15, 12, 22), (65, 35, 110, 100))
        # 眼睛 - 犀利
        pygame.draw.line(surf, accent, (95, 88), (115, 85), 3)
        pygame.draw.line(surf, accent, (125, 85), (145, 88), 3)

    def _draw_portrait_apprentice(self, surf, accent):
        # 长发
        pygame.draw.ellipse(surf, (50, 42, 55), (65, 45, 45, 100))
        pygame.draw.ellipse(surf, (50, 42, 55), (130, 45, 45, 100))
        # 项链吊坠
        pygame.draw.circle(surf, accent, (120, 175), 5)

    def _draw_portrait_lawyer(self, surf, accent):
        # 眼镜
        pygame.draw.rect(surf, accent, (88, 82, 24, 16), 2)
        pygame.draw.rect(surf, accent, (128, 82, 24, 16), 2)
        pygame.draw.line(surf, accent, (112, 90), (128, 90), 2)
        # 公文包
        pygame.draw.rect(surf, (80, 65, 45), (148, 195, 30, 22), border_radius=3)

    def _draw_portrait_groundskeeper(self, surf, accent):
        # 帽子
        pygame.draw.rect(surf, (50, 45, 35), (78, 35, 84, 15))
        pygame.draw.rect(surf, (60, 52, 40), (68, 48, 104, 8))
        # 皱纹
        for y in [98, 102]:
            pygame.draw.line(surf, (60, 52, 48), (92, y), (112, y), 1)
            pygame.draw.line(surf, (60, 52, 48), (128, y), (148, y), 1)

    def _draw_portrait_assistant(self, surf, accent):
        # 短发干练
        pygame.draw.ellipse(surf, (45, 38, 50), (72, 42, 96, 60))
        # 坚毅眼神
        pygame.draw.circle(surf, accent, (100, 88), 4)
        pygame.draw.circle(surf, accent, (140, 88), 4)
        # 胸牌
        pygame.draw.rect(surf, accent, (130, 175, 20, 14))
        pygame.draw.rect(surf, (20, 16, 30), (133, 178, 14, 8))

    # ============ 房间布局 ============
    def _gen_rooms(self):
        self.rooms[1] = self._gen_room_study()
        self.rooms[2] = self._gen_room_hotel()
        self.rooms[3] = self._gen_room_tower()

    def _gen_room_study(self):
        """案一 - 书房俯视图"""
        s = pygame.Surface((380, 340), pygame.SRCALPHA)
        s.fill((0, 0, 0, 0))
        # 地板
        pygame.draw.rect(s, C_FLOOR, (20, 20, 340, 300))
        # 墙壁
        pygame.draw.rect(s, C_WALL, (20, 20, 340, 8))  # 上
        pygame.draw.rect(s, C_WALL, (20, 20, 8, 300))   # 左
        pygame.draw.rect(s, C_WALL, (352, 20, 8, 300))  # 右
        pygame.draw.rect(s, C_WALL, (20, 312, 155, 8))   # 下左
        pygame.draw.rect(s, C_WALL, (225, 312, 135, 8))  # 下右
        # 门
        pygame.draw.rect(s, C_DOOR, (175, 310, 50, 12))
        self._label(s, "门", 185, 296, self.font_xs, C_DOOR)
        # 书架 (上墙)
        pygame.draw.rect(s, C_FURNITURE_LIGHT, (30, 28, 320, 30))
        self._label(s, "书架", 165, 30, self.font_xs, C_TEXT_DIM)
        # 书桌
        pygame.draw.rect(s, C_FURNITURE, (50, 100, 130, 70))
        self._label(s, "书桌", 85, 125, self.font_xs, C_TEXT_DIM)
        # 壁炉
        pygame.draw.rect(s, (80, 40, 20), (290, 100, 60, 55))
        pygame.draw.rect(s, C_FIRE, (298, 108, 44, 38))
        self._label(s, "壁炉", 298, 88, self.font_xs, C_TEXT_DIM)
        # 椅子
        pygame.draw.rect(s, C_FURNITURE, (80, 170, 50, 40))
        # 尸体
        pygame.draw.line(s, C_BODY, (95, 225), (115, 250), 4)
        pygame.draw.line(s, C_BODY, (115, 225), (95, 250), 4)
        self._label(s, "尸体", 80, 255, self.font_xs, C_BODY)

        evidence_markers = {
            "teacup": (120, 240),
            "will": (75, 110),
            "ashes": (320, 120),
            "bookshelf": (190, 42),
            "mail_slot": (190, 306),
            "phone": (110, 130),
            "secretary_desk": (300, 200),
        }
        return {"surface": s, "evidence": evidence_markers}

    def _gen_room_hotel(self):
        """案二 - 旅馆客房俯视图"""
        s = pygame.Surface((380, 340), pygame.SRCALPHA)
        s.fill((0, 0, 0, 0))
        pygame.draw.rect(s, C_FLOOR, (20, 20, 340, 300))
        # 墙壁
        pygame.draw.rect(s, C_WALL, (20, 20, 340, 8))
        pygame.draw.rect(s, C_WALL, (20, 20, 8, 300))
        pygame.draw.rect(s, C_WALL, (352, 20, 8, 300))
        pygame.draw.rect(s, C_WALL, (20, 312, 135, 8))
        pygame.draw.rect(s, C_WALL, (225, 312, 135, 8))
        # 门
        pygame.draw.rect(s, C_DOOR, (155, 310, 70, 12))
        self._label(s, "门", 175, 296, self.font_xs, C_DOOR)
        # 窗户 (上墙，外面暴风雪)
        pygame.draw.rect(s, C_WINDOW, (100, 22, 180, 20))
        for i in range(0, 180, 20):
            pygame.draw.circle(s, C_SNOW, (105 + i, 28), 3)
        self._label(s, "窗户(暴风雪)", 140, 10, self.font_xs, C_SNOW)
        # 床
        pygame.draw.rect(s, (60, 50, 70), (30, 80, 100, 150))
        self._label(s, "床", 60, 150, self.font_xs, C_TEXT_DIM)
        # 书桌
        pygame.draw.rect(s, C_FURNITURE, (220, 80, 120, 60))
        self._label(s, "书桌", 252, 100, self.font_xs, C_TEXT_DIM)
        # 壁炉
        pygame.draw.rect(s, (80, 40, 20), (290, 220, 55, 50))
        pygame.draw.rect(s, C_FIRE, (298, 228, 38, 34))
        self._label(s, "壁炉", 290, 210, self.font_xs, C_TEXT_DIM)
        # 床头柜
        pygame.draw.rect(s, C_FURNITURE, (135, 80, 40, 35))
        self._label(s, "柜", 140, 88, self.font_xs, C_TEXT_DIM)
        # 尸体
        pygame.draw.line(s, C_BODY, (255, 155), (275, 180), 4)
        pygame.draw.line(s, C_BODY, (275, 155), (255, 180), 4)
        self._label(s, "尸体", 245, 182, self.font_xs, C_BODY)

        evidence_markers = {
            "manuscript": (260, 95),
            "suitcase": (50, 250),
            "diary": (50, 265),
            "fireplace2": (317, 240),
            "medicine": (142, 92),
            "corridor": (190, 310),
            "hidden_letter": (310, 255),
        }
        return {"surface": s, "evidence": evidence_markers}

    def _gen_room_tower(self):
        """案三 - 钟楼密室俯视图"""
        s = pygame.Surface((380, 340), pygame.SRCALPHA)
        s.fill((0, 0, 0, 0))
        pygame.draw.rect(s, C_FLOOR, (20, 20, 340, 300))
        # 墙壁 (圆形房间用八角形近似)
        pygame.draw.rect(s, C_WALL, (20, 20, 340, 8))
        pygame.draw.rect(s, C_WALL, (20, 20, 8, 300))
        pygame.draw.rect(s, C_WALL, (352, 20, 8, 300))
        pygame.draw.rect(s, C_WALL, (20, 312, 340, 8))
        # 钟楼机械
        pygame.draw.circle(s, (50, 45, 40), (190, 60), 30, 3)
        pygame.draw.circle(s, (40, 35, 30), (190, 60), 25, 2)
        self._label(s, "钟楼机关", 155, 50, self.font_xs, C_TEXT_DIM)
        # 藏品柜
        pygame.draw.rect(s, C_FURNITURE_LIGHT, (30, 130, 80, 100))
        self._label(s, "藏品柜", 38, 170, self.font_xs, C_TEXT_DIM)
        # 太师椅
        pygame.draw.rect(s, C_FURNITURE, (150, 160, 80, 60))
        self._label(s, "太师椅", 155, 178, self.font_xs, C_TEXT_DIM)
        # 棋盘桌
        pygame.draw.rect(s, (70, 60, 50), (280, 130, 60, 60))
        # 棋盘格
        for i in range(4):
            for j in range(4):
                c = (90, 80, 65) if (i + j) % 2 == 0 else (50, 42, 35)
                pygame.draw.rect(s, c, (288 + i * 12, 138 + j * 12, 12, 12))
        self._label(s, "棋盘", 293, 120, self.font_xs, C_TEXT_DIM)
        # 暗门
        pygame.draw.rect(s, (60, 50, 70), (30, 260, 50, 10))
        self._label(s, "暗门", 30, 248, self.font_xs, C_TEXT_DIM)
        # 药瓶位置 (床头柜)
        pygame.draw.rect(s, C_FURNITURE, (280, 260, 40, 35))
        self._label(s, "柜", 288, 268, self.font_xs, C_TEXT_DIM)
        # 尸体 (坐在椅子上)
        pygame.draw.circle(s, C_BODY, (190, 175), 12)
        self._label(s, "尸体", 175, 192, self.font_xs, C_BODY)

        evidence_markers = {
            "chessboard": (310, 160),
            "collection": (70, 180),
            "letters": (70, 210),
            "clock_mechanism": (190, 60),
            "medicine_bottle": (300, 270),
            "secret_room": (55, 265),
            "final_letter": (55, 280),
        }
        return {"surface": s, "evidence": evidence_markers}

    def _label(self, surf, text, x, y, font, color):
        rendered = font.render(text, True, color)
        surf.blit(rendered, (x, y))

    def draw_evidence_markers(self, target, room_data, discovered, hidden_clues, cursor_id, available_ids):
        """在房间图上绘制证据标记点"""
        ev = room_data["evidence"]
        frame_tick = pygame.time.get_ticks()
        pulse = abs((frame_tick % 1000) - 500) / 500.0  # 0~1 pulse

        for eid, (ex, ey) in ev.items():
            if eid in discovered:
                color = C_EVIDENCE_FOUND
                radius = 6
            elif eid in hidden_clues:
                color = C_EVIDENCE_HIDDEN
                radius = 5 + int(pulse * 2)
            elif eid in available_ids:
                color = C_EVIDENCE
                radius = 5 + int(pulse * 3)
            else:
                continue

            # 光晕
            glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            glow_alpha = int(40 + pulse * 30)
            pygame.draw.circle(glow_surf, (*color, glow_alpha), (15, 15), 14)
            target.blit(glow_surf, (ex - 15, ey - 15))
            # 实心点
            pygame.draw.circle(target, color, (ex, ey), radius)

        # 光标高亮
        if cursor_id and cursor_id in ev:
            cx, cy = ev[cursor_id]
            pygame.draw.circle(target, C_CURSOR, (cx, cy), 12, 2)
            pygame.draw.circle(target, (*C_CURSOR, 80), (cx, cy), 16, 1)

    # ============ 氛围背景 ============
    def _gen_backgrounds(self):
        self.backgrounds["menu"] = self._bg_menu()
        self.backgrounds["noir"] = self._bg_noir()
        self.backgrounds["interrogation"] = self._bg_interrogation()
        self.backgrounds["verdict"] = self._bg_verdict()

    def _bg_menu(self):
        s = pygame.Surface((800, 600))
        _draw_gradient_v(s, (0, 0, 800, 600), (8, 4, 20), (20, 12, 35))
        # 放大镜图标
        pygame.draw.circle(s, (30, 25, 50), (400, 260), 60, 3)
        pygame.draw.line(s, (30, 25, 50), (445, 310), (480, 345), 4)
        # 雨滴效果
        import random
        random.seed(42)
        for _ in range(30):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            length = random.randint(8, 20)
            pygame.draw.line(s, (25, 20, 40), (x, y), (x - 2, y + length), 1)
        return s

    def _bg_noir(self):
        s = pygame.Surface((800, 600))
        _draw_gradient_v(s, (0, 0, 800, 600), (10, 8, 20), (18, 14, 28))
        return s

    def _bg_interrogation(self):
        s = pygame.Surface((800, 600))
        _draw_gradient_v(s, (0, 0, 800, 600), (18, 8, 12), (28, 14, 18))
        # 百叶窗阴影
        for y in range(0, 600, 30):
            pygame.draw.line(s, (25, 12, 15), (0, y), (800, y), 1)
        return s

    def _bg_verdict(self):
        s = pygame.Surface((800, 600))
        _draw_gradient_v(s, (0, 0, 800, 600), (15, 5, 8), (30, 12, 18))
        return s

    # ============ UI 组件 ============
    def draw_panel(self, target, rect, border_color=None, title=None):
        """绘制半透明面板"""
        x, y, w, h = rect
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((15, 12, 25, 220))
        _draw_rounded_rect(panel, (15, 12, 25, 220), (0, 0, w, h), 6)
        target.blit(panel, (x, y))
        if border_color:
            pygame.draw.rect(target, border_color, (x, y, w, h), 2, border_radius=6)
        if title:
            lbl = self.font_md.render(title, True, C_HIGHLIGHT if border_color == C_HIGHLIGHT else C_EVIDENCE)
            target.blit(lbl, (x + 12, y + 6))
            pygame.draw.line(target, border_color or C_EVIDENCE, (x + 8, y + 30), (x + w - 8, y + 30), 1)

    def draw_progress_bar(self, target, x, y, w, h, ratio, color=C_EVIDENCE):
        pygame.draw.rect(target, (30, 25, 45), (x, y, w, h), border_radius=3)
        fill_w = int(w * min(ratio, 1.0))
        if fill_w > 0:
            pygame.draw.rect(target, color, (x, y, fill_w, h), border_radius=3)
