"""渲染层 — 集成视觉资产的界面绘制"""

import pygame
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "pygame-sdk"))

from pygame_sdk import Renderer, styles
from graphics import GraphicsManager, C_BG, C_PANEL, C_HIGHLIGHT, C_EVIDENCE
from model import (
    PHASE_MENU, PHASE_CASE_INTRO, PHASE_EXPLORE,
    PHASE_INTERROGATE_SELECT, PHASE_INTERROGATE_READ,
    PHASE_INTERROGATE_POINT, PHASE_INTERROGATE_RESULT,
    PHASE_DEDUCE, PHASE_VERDICT, PHASE_CASE_SELECT,
    PHASE_SECRET_NOTE, PHASE_ENDING,
)
from cases import ALL_CASES

W, H = 800, 600
LINE_H = 22


def _wrap(text, width=36):
    lines = []
    for p in text.split("\n"):
        if not p.strip():
            lines.append("")
            continue
        while len(p) > width:
            cut = max(
                p[:width].rfind(c) for c in "，。、；：！？"
            )
            if cut == -1:
                cut = width - 1
            lines.append(p[: cut + 1])
            p = p[cut + 1:]
        if p:
            lines.append(p)
    return lines


class GameView:
    def __init__(self, renderer):
        self.r = renderer
        self.gfx = GraphicsManager()
        self.font_lg = self.gfx.font_lg
        self.font_md = self.gfx.font_md
        self.font_sm = self.gfx.font_sm
        self.font_xs = self.gfx.font_xs

    def draw(self, model):
        handler = {
            PHASE_MENU: self._draw_menu,
            PHASE_CASE_INTRO: self._draw_intro,
            PHASE_EXPLORE: self._draw_explore,
            PHASE_INTERROGATE_SELECT: self._draw_interrogate_select,
            PHASE_INTERROGATE_READ: self._draw_interrogate_read,
            PHASE_INTERROGATE_POINT: self._draw_interrogate_point,
            PHASE_INTERROGATE_RESULT: self._draw_interrogate_result,
            PHASE_DEDUCE: self._draw_deduce,
            PHASE_VERDICT: self._draw_verdict,
            PHASE_CASE_SELECT: self._draw_case_select,
            PHASE_SECRET_NOTE: self._draw_secret_note,
            PHASE_ENDING: self._draw_ending,
        }.get(model.phase)
        if handler:
            handler(model)
        self.r.present()

    def _text(self, text, x, y, color=(220, 210, 200), font=None):
        f = font or self.font_md
        rendered = f.render(text, True, color)
        self.r.screen.blit(rendered, (x, y))
        return rendered.get_height()

    def _centered(self, text, y, color=(220, 210, 200), font=None):
        f = font or self.font_md
        rendered = f.render(text, True, color)
        self.r.screen.blit(rendered, ((W - rendered.get_width()) // 2, y))
        return rendered.get_height()

    def _text_lines(self, text, x, y, color=(220, 210, 200), font=None, width=36):
        f = font or self.font_md
        lines = _wrap(text, width)
        for i, line in enumerate(lines):
            rendered = f.render(line, True, color)
            self.r.screen.blit(rendered, (x, y + i * LINE_H))
        return len(lines)

    def _draw_bottom_bar(self, text, color=(100, 90, 80)):
        pygame.draw.rect(self.r.screen, (15, 12, 25), (0, H - 32, W, 32))
        pygame.draw.line(self.r.screen, (40, 30, 55), (0, H - 32), (W, H - 32), 1)
        self._centered(text, H - 26, color, self.font_sm)

    def _draw_top_bar(self, left_text, right_text=""):
        pygame.draw.rect(self.r.screen, (18, 14, 30), (0, 0, W, 38))
        pygame.draw.line(self.r.screen, (40, 30, 55), (0, 38), (W, 38), 1)
        self._text(left_text, 12, 8, (220, 210, 200), self.font_md)
        if right_text:
            rendered = self.font_sm.render(right_text, True, C_EVIDENCE)
            self.r.screen.blit(rendered, (W - rendered.get_width() - 12, 12))

    # ============ 主菜单 ============
    def _draw_menu(self, model):
        self.r.screen.blit(self.gfx.backgrounds["menu"], (0, 0))
        self._centered("暗 室 录", 110, (220, 200, 180), self.font_lg)
        self._centered("DARK ROOM CHRONICLES", 155, (120, 110, 100), self.font_sm)

        pygame.draw.line(self.r.screen, (60, 45, 70), (250, 195), (550, 195), 1)

        self._centered("三桩密室命案，一个幕后棋手", 215, (140, 130, 120), self.font_md)
        self._centered("勘查 · 审讯 · 推理", 248, C_EVIDENCE, self.font_md)

        # 按钮样式
        btn_y = 360
        pulse = abs((pygame.time.get_ticks() % 1200) - 600) / 600.0
        alpha = int(160 + pulse * 95)
        btn_color = (alpha, int(alpha * 0.85), int(alpha * 0.6))
        self.gfx.draw_panel(self.r.screen, (280, btn_y, 240, 48), btn_color)
        self._centered("开 始 游 戏", btn_y + 10, (240, 220, 200), self.font_md)

        self._centered("↑↓ 选择  Enter 确认  Space 跳过", 540, (80, 70, 65), self.font_sm)

    # ============ 案件选择 ============
    def _draw_case_select(self, model):
        self.r.screen.blit(self.gfx.backgrounds["noir"], (0, 0))
        self._centered("选择案件", 25, (220, 200, 180), self.font_lg)
        pygame.draw.line(self.r.screen, (50, 40, 60), (100, 65), (700, 65), 1)

        y = 90
        for i, case_num in enumerate(model.unlocked_cases):
            case = ALL_CASES[case_num - 1]
            is_sel = i == model.current_case_idx

            if is_sel:
                self.gfx.draw_panel(self.r.screen, (80, y, 640, 120), C_HIGHLIGHT, case["title"])
            else:
                self.gfx.draw_panel(self.r.screen, (80, y, 640, 120), (50, 40, 60))

            title_color = C_HIGHLIGHT if is_sel else (180, 170, 160)
            self._text(case["title"], 100, y + 10, title_color, self.font_md)
            self._text(case["subtitle"], 100, y + 38, (130, 120, 110), self.font_sm)

            score = model.scores.get(case_num)
            if score:
                grade = model.get_grade(case_num)
                grade_colors = {"S": (255, 220, 60), "A": C_EVIDENCE, "B": (200, 200, 200), "C": (200, 60, 60)}
                gc = grade_colors.get(grade, (200, 200, 200))
                self._text(f"评级: {grade}  得分: {score['total']}/100", 100, y + 62, gc, self.font_sm)
                bar_y = y + 88
                self.gfx.draw_progress_bar(self.r.screen, 100, bar_y, 300, 10, score["total"] / 100, gc)
                self._text(f"勘查:{score['explore']} 审讯:{score['interrogate']} 推理:{score['deduce']}",
                           420, bar_y - 2, (120, 110, 100), self.font_xs)
            else:
                self._text("未完成", 100, y + 62, (100, 90, 80), self.font_sm)

            y += 135

        self._draw_bottom_bar("↑↓ 选择  Enter 开始案件")

    # ============ 案件介绍 ============
    def _draw_intro(self, model):
        self.r.screen.blit(self.gfx.backgrounds["noir"], (0, 0))
        case = model.case_data

        # 左侧：房间缩略图
        room = self.gfx.rooms.get(case["id"])
        if room:
            thumb = pygame.transform.scale(room["surface"], (300, 270))
            self.gfx.draw_panel(self.r.screen, (15, 60, 320, 290), (50, 40, 60))
            self.r.screen.blit(thumb, (25, 70))

        # 右侧：案情文字
        self.gfx.draw_panel(self.r.screen, (350, 60, 435, 440), (50, 40, 60), case["title"])
        self._text(case["location"], 365, 100, (140, 130, 120), self.font_sm)
        y = 130
        for line in case["intro"]:
            self._text(line, 365, y, (200, 190, 180) if not line.startswith("【") else C_HIGHLIGHT, self.font_sm, )
            y += LINE_H

        self._draw_bottom_bar("按 Enter 开始勘查现场")

    # ============ 勘查阶段（房间图+物品列表）============
    def _draw_explore(self, model):
        self.r.screen.blit(self.gfx.backgrounds["noir"], (0, 0))
        case = model.case_data
        total_clues = len([s for s in case["scenes"] if not s.get("auto")])
        self._draw_top_bar(f"{case['title']} — 勘查阶段", f"线索: {len(model.discovered_clues)}/{total_clues}")

        if model.showing_description and model.current_item_desc:
            self._draw_item_detail(model)
            return

        items = model.get_available_items()
        hidden_ids = {it["id"] for it in items if it.get("hidden")}

        # 左侧：房间布局图
        room = self.gfx.rooms.get(case["id"])
        if room:
            self.gfx.draw_panel(self.r.screen, (8, 44, 392, 360), (50, 40, 60), "案发现场")
            self.r.screen.blit(room["surface"], (18, 80))
            # 绘制证据标记点
            available_ids = {it["id"] for it in items}
            # 当前选中的物品
            cursor_id = None
            if items and model.explore_cursor < len(items):
                cursor_id = items[model.explore_cursor]["id"]
            self.gfx.draw_evidence_markers(
                self.r.screen, room, model.discovered_clues, hidden_ids, cursor_id, available_ids
            )

            # 右侧：图例
            legend_y = 410
            pygame.draw.circle(self.r.screen, C_EVIDENCE, (28, legend_y), 5)
            self._text("未调查", 40, legend_y - 7, (130, 120, 110), self.font_xs)
            pygame.draw.circle(self.r.screen, (80, 180, 80), (108, legend_y), 5)
            self._text("已调查", 120, legend_y - 7, (130, 120, 110), self.font_xs)
            pygame.draw.circle(self.r.screen, (180, 120, 220), (188, legend_y), 5)
            self._text("隐藏", 200, legend_y - 7, (130, 120, 110), self.font_xs)
            pygame.draw.circle(self.r.screen, C_HIGHLIGHT, (258, legend_y), 8, 2)
            self._text("当前", 272, legend_y - 7, (130, 120, 110), self.font_xs)

        # 右侧：可调查物品列表
        self.gfx.draw_panel(self.r.screen, (408, 44, 384, 470), (50, 40, 60), "可调查物品")

        if not items:
            self._centered("所有线索已收集完毕", 250, (140, 130, 120), self.font_md)
            self._centered("按 Enter 进入审讯", 290, (200, 190, 180), self.font_md)
        else:
            y = 82
            max_visible = 14
            scroll = model.explore_scroll
            for i, item in enumerate(items[scroll: scroll + max_visible]):
                real_idx = i + scroll
                found = item["id"] in model.discovered_clues
                hidden = item.get("hidden", False)
                is_cur = real_idx == model.explore_cursor

                if is_cur:
                    pygame.draw.rect(self.r.screen, (35, 28, 55), (418, y - 2, 364, LINE_H + 4), border_radius=4)
                    self._text("▶", 422, y, C_HIGHLIGHT, self.font_sm)

                status = ""
                color = (180, 170, 160)
                if found:
                    status = " ✓"
                    color = (80, 160, 80)
                elif hidden:
                    status = " ★"
                    color = (180, 120, 220)

                self._text(f"  {item['name']}{status}", 442, y, color, self.font_sm)
                y += LINE_H + 4

        self._draw_bottom_bar("↑↓ 选择  Enter 调查  Space 进入审讯")

    def _draw_item_detail(self, model):
        item = model.current_item_desc
        # 半透明覆盖层
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.r.screen.blit(overlay, (0, 0))

        self.gfx.draw_panel(self.r.screen, (60, 50, 680, 480), C_EVIDENCE, item["name"])

        lines = _wrap(item["description"], 34)
        max_show = 18
        scroll = min(model.text_scroll, max(0, len(lines) - max_show))
        y = 92
        for i in range(max_show):
            idx = i + scroll
            if idx < len(lines):
                self._text(lines[idx], 85, y, (210, 200, 190), self.font_md)
                y += LINE_H

        if len(lines) > max_show:
            self._draw_bottom_bar("↑ 滚动  Enter 返回")
        else:
            self._draw_bottom_bar("按 Enter 返回")

    # ============ 审讯阶段 ============
    def _draw_interrogate_select(self, model):
        self.r.screen.blit(self.gfx.backgrounds["interrogation"], (0, 0))
        case = model.case_data
        contradictions = len(model.found_contradictions)
        self._draw_top_bar(f"{case['title']} — 审讯阶段", f"矛盾: {contradictions}/{model.total_contradictions}")

        suspects = case["suspects"]
        # 角色卡片排列
        card_w = 170
        card_h = 260
        total_w = len(suspects) * card_w + (len(suspects) - 1) * 12
        start_x = (W - total_w) // 2

        for i, suspect in enumerate(suspects):
            x = start_x + i * (card_w + 12)
            y = 60
            is_sel = i == model.suspect_idx

            border = C_HIGHLIGHT if is_sel else (40, 30, 50)
            self.gfx.draw_panel(self.r.screen, (x, y, card_w, card_h), border)

            # 立绘
            portrait = self.gfx.portraits.get(suspect["id"])
            if portrait:
                p_scale = pygame.transform.scale(portrait, (140, 180))
                self.r.screen.blit(p_scale, (x + 15, y + 10))

            # 名字和角色
            name_color = C_HIGHLIGHT if is_sel else (180, 170, 160)
            self._text(suspect["name"], x + 10, y + 195, name_color, self.font_xs)
            self._text(suspect["role"], x + 10, y + 212, (120, 110, 100), self.font_xs)

            # 矛盾指示
            found = sum(1 for (sid, _, _) in model.found_contradictions if sid == suspect["id"])
            total = sum(len(t.get("contradictions", {})) for t in suspect["testimonies"])
            if found > 0:
                self._text(f"矛盾: {found}/{total}", x + 10, y + 232, C_EVIDENCE, self.font_xs)

        # 底部提示
        self._draw_bottom_bar("← → 选择嫌疑人  Enter 审讯  Space 进入推理")

    def _draw_interrogate_read(self, model):
        self.r.screen.blit(self.gfx.backgrounds["interrogation"], (0, 0))
        suspect = model.case_data["suspects"][model.suspect_idx]

        self._draw_top_bar(f"审讯: {suspect['name']}", f"证词 {model.testimony_idx + 1}/{len(suspect['testimonies'])}")

        # 左侧：大立绘
        portrait = self.gfx.portraits.get(suspect["id"])
        if portrait:
            self.gfx.draw_panel(self.r.screen, (15, 48, 250, 380), (40, 30, 50))
            self.r.screen.blit(portrait, (20, 55))
            self._text(suspect["name"], 20, 330, (200, 190, 180), self.font_sm)
            self._text(suspect["role"], 20, 350, (130, 120, 110), self.font_xs)

        # 右侧：证词面板
        testimony = suspect["testimonies"][model.testimony_idx]
        has_contra = bool(testimony.get("contradictions"))
        panel_border = (200, 80, 80) if has_contra else (50, 40, 60)
        self.gfx.draw_panel(self.r.screen, (280, 48, 505, 440), panel_border, "证词记录")

        self._text(suspect["description"], 295, 86, (130, 120, 110), self.font_xs)

        lines = _wrap(testimony["text"], 38)
        y = 115
        for line in lines:
            self._text(line, 295, y, (210, 200, 190), self.font_md)
            y += LINE_H

        if has_contra:
            pulse = abs((pygame.time.get_ticks() % 1000) - 500) / 500.0
            c = (int(200 + 55 * pulse), int(80 + 40 * pulse), int(80 + 40 * pulse))
            self._centered("⚠ 发现可疑证词！按 Enter 指认矛盾 ⚠", y + 20, c, self.font_md)
        else:
            self._centered("此段证词无明显矛盾", y + 20, (120, 110, 100), self.font_sm)

        self._draw_bottom_bar("← → 切换证词  Enter 继续  Space 返回")

    def _draw_interrogate_point(self, model):
        # 红色氛围
        self.r.screen.blit(self.gfx.backgrounds["interrogation"], (0, 0))
        # 红色叠加
        red_overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        red_overlay.fill((40, 0, 0, 60))
        self.r.screen.blit(red_overlay, (0, 0))

        suspect = model.case_data["suspects"][model.suspect_idx]
        testimony = suspect["testimonies"][model.testimony_idx]

        self._draw_top_bar(f"指认矛盾 — {suspect['name']}", "选择可疑的陈述")

        # 小立绘
        portrait = self.gfx.portraits.get(suspect["id"])
        if portrait:
            p_small = pygame.transform.scale(portrait, (100, 130))
            self.r.screen.blit(p_small, (15, 50))

        self._text("选择你认为有矛盾的陈述:", 130, 55, (220, 180, 60), self.font_md)

        y = 100
        for i, stmt in enumerate(testimony["statements"]):
            is_cur = i == model.point_cursor
            found_key = (suspect["id"], model.testimony_idx, i)
            already_found = found_key in model.found_contradictions

            if is_cur:
                pygame.draw.rect(self.r.screen, (60, 20, 20), (120, y - 4, 660, LINE_H + 8), border_radius=6)
                pygame.draw.rect(self.r.screen, (200, 80, 80), (120, y - 4, 660, LINE_H + 8), 2, border_radius=6)
                self._text("▶", 125, y, C_HIGHLIGHT, self.font_md)

            color = C_EVIDENCE if already_found else (210, 200, 190)
            self._text(stmt, 150, y, color, self.font_md)
            if already_found:
                self._text("  ✓ 已指认", 150 + len(stmt) * 16, y, C_EVIDENCE, self.font_xs)
            y += 45

        self._draw_bottom_bar("↑↓ 选择  Enter 指认  Space 取消", (200, 100, 100))

    def _draw_interrogate_result(self, model):
        self.r.screen.blit(self.gfx.backgrounds["noir"], (0, 0))
        if not model.contradiction_result:
            return

        result_type, text = model.contradiction_result
        if result_type == "correct":
            self.gfx.draw_panel(self.r.screen, (100, 80, 600, 350), C_EVIDENCE, "矛盾指认正确！")
            self._centered("✓ 指认正确！", 130, C_EVIDENCE, self.font_lg)
        else:
            self.gfx.draw_panel(self.r.screen, (100, 80, 600, 350), (180, 60, 60), "指认错误")
            self._centered("✗ 指认错误", 130, (200, 80, 80), self.font_lg)

        lines = _wrap(text, 34)
        y = 180
        for line in lines:
            self._centered(line, y, (200, 190, 180), self.font_md)
            y += LINE_H

        self._draw_bottom_bar("按 Enter 继续")

    # ============ 推理阶段 ============
    def _draw_deduce(self, model):
        self.r.screen.blit(self.gfx.backgrounds["noir"], (0, 0))
        questions = model.case_data["deduction"]["questions"]

        self._draw_top_bar("最终推理", f"问题 {model.deduce_step + 1}/{len(questions)}")

        # 进度指示
        for i in range(len(questions)):
            x = W // 2 - len(questions) * 20 + i * 40
            color = C_EVIDENCE if i < model.deduce_step else (60, 50, 70)
            if i == model.deduce_step:
                color = C_HIGHLIGHT
            pygame.draw.circle(self.r.screen, color, (x + 15, 58), 10)

        q = questions[model.deduce_step]
        self._centered(q["question"], 100, (220, 200, 180), self.font_lg)
        pygame.draw.line(self.r.screen, (50, 40, 60), (200, 140), (600, 140), 1)

        # 选项卡片
        y = 170
        for i, opt in enumerate(q["options"]):
            is_cur = i == model.deduce_cursor
            border = C_HIGHLIGHT if is_cur else (45, 38, 58)
            self.gfx.draw_panel(self.r.screen, (150, y, 500, 55), border)
            if is_cur:
                self._text("▶", 160, y + 15, C_HIGHLIGHT, self.font_md)
            self._text(f" {chr(65 + i)}. {opt}", 185, y + 15,
                        (220, 210, 200) if is_cur else (160, 150, 140), self.font_md)
            y += 70

        self._draw_bottom_bar("↑↓ 选择  Enter 确认答案")

    # ============ 结案报告 ============
    def _draw_verdict(self, model):
        self.r.screen.blit(self.gfx.backgrounds["verdict"], (0, 0))
        case = model.case_data
        score = model.scores.get(case["id"], {})
        grade = model.get_grade(case["id"])

        self._draw_top_bar(f"结案报告 — {case['title']}")

        grade_colors = {"S": (255, 220, 60), "A": C_EVIDENCE, "B": (200, 200, 200), "C": (200, 60, 60)}
        gc = grade_colors.get(grade, (200, 200, 200))

        # 大评级显示
        self._centered(f"破案评级", 55, (180, 170, 160), self.font_md)
        self._centered(grade, 80, gc, self.font_lg)
        pygame.draw.line(self.r.screen, gc, (300, 118), (500, 118), 2)

        # 分数条
        labels = [("勘查", "explore", 30), ("审讯", "interrogate", 30), ("推理", "deduce", 40)]
        bar_x = 140
        for i, (name, key, max_val) in enumerate(labels):
            y = 130 + i * 32
            val = score.get(key, 0)
            self._text(f"{name}: {val}/{max_val}", bar_x, y, (200, 190, 180), self.font_sm)
            self.gfx.draw_progress_bar(self.r.screen, bar_x + 120, y + 2, 200, 14, val / max_val, gc)

        total = score.get("total", 0)
        self._text(f"总分: {total}/100", bar_x + 350, 146, gc, self.font_md)

        pygame.draw.line(self.r.screen, (50, 40, 60), (20, 230), (W - 20, 230), 1)
        self._text("案件真相:", 15, 240, C_HIGHLIGHT, self.font_md)

        truth = case["truth"]
        y = 268
        max_y = H - 40
        scroll = model.text_scroll
        for i, line in enumerate(truth):
            if i < scroll:
                continue
            if y >= max_y:
                self._centered("... Enter 翻页 ...", y, (100, 90, 80), self.font_sm)
                break
            color = (210, 200, 190)
            if line.startswith("【"):
                color = C_HIGHLIGHT
            elif line.startswith("——"):
                color = C_EVIDENCE
            self._text(line, 20, y, color, self.font_sm)
            y += LINE_H - 2

        self._draw_bottom_bar("↑ 回看  Enter 翻页/结束  Space 跳过")

    # ============ 暗线笔记 ============
    def _draw_secret_note(self, model):
        self.r.screen.blit(self.gfx.backgrounds["verdict"], (0, 0))
        red_overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        red_overlay.fill((30, 0, 0, 40))
        self.r.screen.blit(red_overlay, (0, 0))

        self.gfx.draw_panel(self.r.screen, (100, 100, 600, 350), C_EVIDENCE, "暗线笔记")
        self._centered("暗线笔记", 130, C_HIGHLIGHT, self.font_lg)
        pygame.draw.line(self.r.screen, C_EVIDENCE, (200, 165), (600, 165), 1)

        note = model.case_data.get("secret_note", "")
        lines = _wrap(note, 34)
        y = 185
        for line in lines:
            self._centered(line, y, C_EVIDENCE, self.font_md)
            y += LINE_H

        self._draw_bottom_bar("按 Enter 继续")

    # ============ 结局 ============
    def _draw_ending(self, model):
        self.r.screen.blit(self.gfx.backgrounds["menu"], (0, 0))

        self._centered("暗 室 录", 60, (220, 200, 180), self.font_lg)
        self._centered("—— 全剧终 ——", 100, C_EVIDENCE, self.font_md)
        pygame.draw.line(self.r.screen, (50, 40, 60), (200, 135), (600, 135), 1)

        y = 160
        total_score = 0
        for cid in [1, 2, 3]:
            case = ALL_CASES[cid - 1]
            grade = model.get_grade(cid)
            score = model.scores.get(cid, {}).get("total", 0)
            total_score += score
            gc = (255, 220, 60) if grade == "S" else (C_EVIDENCE if grade == "A" else (180, 170, 160))
            self._text(f"{case['title']}: {grade} ({score}分)", 250, y, gc, self.font_md)
            y += 35

        avg = total_score // 3
        overall = "S" if avg >= 90 else ("A" if avg >= 75 else ("B" if avg >= 50 else "C"))
        oc = (255, 220, 60) if overall == "S" else (C_EVIDENCE if overall == "A" else (200, 200, 200))

        pygame.draw.line(self.r.screen, (50, 40, 60), (250, y + 10), (550, y + 10), 1)
        self._centered(f"综合得分: {total_score}/300", y + 25, (200, 190, 180), self.font_md)
        self._centered(f"侦探等级: {overall}", y + 60, oc, self.font_lg)

        self._draw_bottom_bar("按 Enter 返回主菜单")
