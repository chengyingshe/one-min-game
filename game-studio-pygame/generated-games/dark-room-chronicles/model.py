"""游戏引擎 — 状态机、阶段管理、评分"""

import copy
from cases import ALL_CASES

# 游戏阶段
PHASE_MENU = "menu"
PHASE_CASE_INTRO = "case_intro"
PHASE_EXPLORE = "explore"
PHASE_INTERROGATE_SELECT = "interrogate_select"
PHASE_INTERROGATE_READ = "interrogate_read"
PHASE_INTERROGATE_POINT = "interrogate_point"
PHASE_INTERROGATE_RESULT = "interrogate_result"
PHASE_DEDUCE = "deduce"
PHASE_VERDICT = "verdict"
PHASE_CASE_SELECT = "case_select"
PHASE_SECRET_NOTE = "secret_note"
PHASE_ENDING = "ending"


def _wrap_text(text, chars_per_line):
    """手动换行"""
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        while len(paragraph) > chars_per_line:
            cut = paragraph[:chars_per_line].rfind("，")
            if cut == -1:
                cut = paragraph[:chars_per_line].rfind("。")
            if cut == -1:
                cut = paragraph[:chars_per_line].rfind("、")
            if cut == -1:
                cut = chars_per_line - 1
            lines.append(paragraph[: cut + 1])
            paragraph = paragraph[cut + 1:]
        if paragraph:
            lines.append(paragraph)
    return lines


class GameModel:
    def __init__(self):
        self.phase = PHASE_MENU
        self.unlocked_cases = [1]
        self.current_case_idx = 0
        self.case_data = None
        # 勘查
        self.discovered_clues = set()
        self.explore_items = []
        self.explore_cursor = 0
        self.explore_scroll = 0
        self.current_item_desc = None
        self.showing_description = False
        # 审讯
        self.suspect_idx = 0
        self.testimony_idx = 0
        self.found_contradictions = set()
        self.total_contradictions = 0
        self.pointing_mode = False
        self.point_cursor = 0
        self.contradiction_result = None
        self.contradiction_timer = 0
        # 推理
        self.deduce_step = 0
        self.deduce_cursor = 0
        self.deduce_answers = []
        # 评分
        self.scores = {}
        # 通用
        self.msg_timer = 0
        self.msg_text = ""
        self.text_scroll = 0
        self.max_text_scroll = 0

    def start_case(self, case_idx):
        self.current_case_idx = case_idx
        self.case_data = copy.deepcopy(ALL_CASES[case_idx])
        self.discovered_clues = set()
        self.found_contradictions = set()
        self.deduce_answers = []
        self.deduce_step = 0
        self.explore_cursor = 0
        self.explore_scroll = 0
        self.showing_description = False
        self.current_item_desc = None
        self.text_scroll = 0
        self.total_contradictions = 0
        for s in self.case_data["suspects"]:
            for t in s["testimonies"]:
                self.total_contradictions += len(t.get("contradictions", {}))
        self._build_explore_items()
        self.phase = PHASE_CASE_INTRO

    def _build_explore_items(self):
        self.explore_items = []
        for scene in self.case_data["scenes"]:
            if scene.get("auto"):
                continue
            self.explore_items.append(scene)

    def get_available_items(self):
        result = []
        for item in self.explore_items:
            req = item.get("requires")
            if req is None or req in self.discovered_clues:
                result.append(item)
        return result

    def handle_event(self, event_type, key=None):
        handler = {
            PHASE_MENU: self._handle_menu,
            PHASE_CASE_INTRO: self._handle_intro,
            PHASE_EXPLORE: self._handle_explore,
            PHASE_INTERROGATE_SELECT: self._handle_interrogate_select,
            PHASE_INTERROGATE_READ: self._handle_interrogate_read,
            PHASE_INTERROGATE_POINT: self._handle_interrogate_point,
            PHASE_INTERROGATE_RESULT: self._handle_interrogate_result,
            PHASE_DEDUCE: self._handle_deduce,
            PHASE_VERDICT: self._handle_verdict,
            PHASE_CASE_SELECT: self._handle_case_select,
            PHASE_SECRET_NOTE: self._handle_secret_note,
            PHASE_ENDING: self._handle_ending,
        }.get(self.phase)
        if handler:
            handler(event_type, key)

    def _handle_menu(self, event_type, key):
        if event_type == "action" and key == "primary":
            self.phase = PHASE_CASE_SELECT

    def _handle_intro(self, event_type, key):
        if event_type == "action" and key == "primary":
            self.phase = PHASE_EXPLORE
            self.text_scroll = 0

    def _handle_explore(self, event_type, key):
        if self.showing_description:
            if event_type == "action" and key == "primary":
                self.showing_description = False
                self.text_scroll = 0
            elif event_type == "action" and key == "up":
                self.text_scroll = max(0, self.text_scroll - 1)
            elif event_type == "action" and key == "down":
                self.text_scroll += 1
            return

        items = self.get_available_items()
        if not items:
            if event_type == "action" and key == "primary":
                self.phase = PHASE_INTERROGATE_SELECT
                self.suspect_idx = 0
            return

        if event_type == "action" and key == "up":
            self.explore_cursor = max(0, self.explore_cursor - 1)
            if self.explore_cursor < self.explore_scroll:
                self.explore_scroll = self.explore_cursor
        elif event_type == "action" and key == "down":
            self.explore_cursor = min(len(items) - 1, self.explore_cursor + 1)
            if self.explore_cursor >= self.explore_scroll + 10:
                self.explore_scroll = self.explore_cursor - 9
        elif event_type == "action" and key == "primary":
            item = items[self.explore_cursor]
            self.discovered_clues.add(item["id"])
            self.current_item_desc = item
            self.showing_description = True
            self.text_scroll = 0
            self._check_hidden_unlocks()
        elif event_type == "action" and key == "secondary":
            self.phase = PHASE_INTERROGATE_SELECT
            self.suspect_idx = 0

    def _check_hidden_unlocks(self):
        pass

    def _handle_interrogate_select(self, event_type, key):
        n = len(self.case_data["suspects"])
        if event_type == "action" and key == "up":
            self.suspect_idx = max(0, self.suspect_idx - 1)
        elif event_type == "action" and key == "down":
            self.suspect_idx = min(n - 1, self.suspect_idx + 1)
        elif event_type == "action" and key == "primary":
            self.testimony_idx = 0
            self.text_scroll = 0
            self.phase = PHASE_INTERROGATE_READ
        elif event_type == "action" and key == "secondary":
            self.phase = PHASE_DEDUCE
            self.deduce_step = 0
            self.deduce_cursor = 0

    def _handle_interrogate_read(self, event_type, key):
        suspect = self.case_data["suspects"][self.suspect_idx]
        testimonies = suspect["testimonies"]
        if event_type == "action" and key == "primary":
            testimony = testimonies[self.testimony_idx]
            contradictions = testimony.get("contradictions", {})
            if contradictions:
                self.phase = PHASE_INTERROGATE_POINT
                self.point_cursor = 0
                self.pointing_mode = True
            else:
                self.testimony_idx += 1
                if self.testimony_idx >= len(testimonies):
                    self.testimony_idx = 0
                    self.phase = PHASE_INTERROGATE_SELECT
        elif event_type == "action" and key == "secondary":
            self.phase = PHASE_INTERROGATE_SELECT
        elif event_type == "action" and key == "right":
            self.testimony_idx = min(len(testimonies) - 1, self.testimony_idx + 1)
        elif event_type == "action" and key == "left":
            self.testimony_idx = max(0, self.testimony_idx - 1)

    def _handle_interrogate_point(self, event_type, key):
        if event_type == "action" and key == "up":
            self.point_cursor = max(0, self.point_cursor - 1)
        elif event_type == "action" and key == "down":
            suspect = self.case_data["suspects"][self.suspect_idx]
            testimony = suspect["testimonies"][self.testimony_idx]
            n = len(testimony["statements"])
            self.point_cursor = min(n - 1, self.point_cursor + 1)
        elif event_type == "action" and key == "primary":
            suspect = self.case_data["suspects"][self.suspect_idx]
            testimony = suspect["testimonies"][self.testimony_idx]
            contradictions = testimony.get("contradictions", {})
            sel = self.point_cursor
            if sel in contradictions:
                self.found_contradictions.add((suspect["id"], self.testimony_idx, sel))
                info = contradictions[sel]
                self.contradiction_result = ("correct", info["explanation"])
            else:
                self.contradiction_result = ("wrong", "这句话没有矛盾。")
            self.phase = PHASE_INTERROGATE_RESULT
            self.contradiction_timer = 0
        elif event_type == "action" and key == "secondary":
            self.phase = PHASE_INTERROGATE_READ

    def _handle_interrogate_result(self, event_type, key):
        if event_type == "action" and key == "primary":
            self.contradiction_result = None
            suspect = self.case_data["suspects"][self.suspect_idx]
            if self.testimony_idx >= len(suspect["testimonies"]) - 1:
                self.testimony_idx = 0
                self.phase = PHASE_INTERROGATE_SELECT
            else:
                self.testimony_idx += 1
                self.phase = PHASE_INTERROGATE_READ

    def _handle_deduce(self, event_type, key):
        questions = self.case_data["deduction"]["questions"]
        q = questions[self.deduce_step]
        if event_type == "action" and key == "up":
            self.deduce_cursor = max(0, self.deduce_cursor - 1)
        elif event_type == "action" and key == "down":
            self.deduce_cursor = min(len(q["options"]) - 1, self.deduce_cursor + 1)
        elif event_type == "action" and key == "primary":
            self.deduce_answers.append(self.deduce_cursor)
            self.deduce_step += 1
            self.deduce_cursor = 0
            if self.deduce_step >= len(questions):
                self._calculate_score()
                self.phase = PHASE_VERDICT
                self.text_scroll = 0

    def _calculate_score(self):
        total_clues = len([s for s in self.case_data["scenes"] if not s.get("auto")])
        found_ratio = len(self.discovered_clues) / max(total_clues, 1)
        explore_score = int(30 * found_ratio)

        interrogate_score = int(30 * len(self.found_contradictions) / max(self.total_contradictions, 1))

        questions = self.case_data["deduction"]["questions"]
        deduce_score = 0
        for i, ans in enumerate(self.deduce_answers):
            if ans == questions[i]["answer"]:
                deduce_score += 40 // len(questions)
        if len(self.deduce_answers) == len(questions):
            remaining = 40 - (40 // len(questions)) * len(questions)
            deduce_score += remaining

        total = explore_score + interrogate_score + deduce_score
        self.scores[self.case_data["id"]] = {
            "explore": explore_score,
            "interrogate": interrogate_score,
            "deduce": deduce_score,
            "total": total,
        }

    def _handle_verdict(self, event_type, key):
        if event_type == "action" and key == "primary":
            truth_lines = self.case_data["truth"]
            if self.text_scroll < len(truth_lines) - 5:
                self.text_scroll += 5
            else:
                if self.case_data.get("secret_note"):
                    self.phase = PHASE_SECRET_NOTE
                else:
                    self._finish_case()
        elif event_type == "action" and key == "up":
            self.text_scroll = max(0, self.text_scroll - 3)
        elif event_type == "action" and key == "secondary":
            self._finish_case()

    def _finish_case(self):
        case_id = self.case_data["id"]
        if case_id < 3:
            next_id = case_id + 1
            if next_id not in self.unlocked_cases:
                self.unlocked_cases.append(next_id)
            self.phase = PHASE_CASE_SELECT
        else:
            self.phase = PHASE_ENDING

    def _handle_secret_note(self, event_type, key):
        if event_type == "action" and key == "primary":
            self._finish_case()

    def _handle_case_select(self, event_type, key):
        if event_type == "action" and key == "up":
            self.current_case_idx = max(0, self.current_case_idx - 1)
        elif event_type == "action" and key == "down":
            self.current_case_idx = min(len(self.unlocked_cases) - 1, self.current_case_idx + 1)
        elif event_type == "action" and key == "primary":
            case_num = self.unlocked_cases[self.current_case_idx]
            self.start_case(case_num - 1)

    def _handle_ending(self, event_type, key):
        if event_type == "action" and key == "primary":
            self.phase = PHASE_MENU

    def get_grade(self, case_id):
        s = self.scores.get(case_id, {})
        total = s.get("total", 0)
        if total >= 90:
            return "S"
        elif total >= 75:
            return "A"
        elif total >= 50:
            return "B"
        else:
            return "C"
