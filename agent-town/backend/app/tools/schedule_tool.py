from sqlalchemy.orm import Session

from app.core.tool import Tool
from app.storage.db_models import ScheduleRecord


class ScheduleTool(Tool):
    """日程工具 — 管理 NPC 每日行程安排"""

    name = "schedule"
    description = "查询和更新 NPC 的每日行程安排，以及按时间分配位置"

    DEFAULT_SCHEDULES = {
        "林黛玉": [
            ("07:00", "起床", "书院"), ("08:00", "去茶馆喝茶", "茶馆"),
            ("10:00", "抄书写字", "书院"), ("13:00", "午饭", "茶馆"),
            ("15:00", "散步赏花", "集市"), ("18:00", "回书院", "书院"),
            ("21:00", "就寝", "书院"),
        ],
        "孙悟空": [
            ("07:00", "起床练功", "集市"), ("08:00", "帮人干活", "集市"),
            ("12:00", "午饭喝酒", "茶馆"), ("14:00", "闲逛", "集市"),
            ("17:00", "茶馆吹牛", "茶馆"), ("20:00", "回住处", "集市"),
            ("22:00", "睡觉", "集市"),
        ],
        "张飞": [
            ("07:00", "起床练武", "茶馆"), ("08:00", "茶馆护卫", "茶馆"),
            ("12:00", "午饭喝酒", "茶馆"), ("14:00", "巡街", "集市"),
            ("17:00", "回茶馆", "茶馆"), ("20:00", "喝酒", "茶馆"),
            ("22:00", "休息", "茶馆"),
        ],
    }

    def get_parameters(self) -> dict:
        return {
            "action": {"type": "string", "enum": ["get_schedule", "get_location_at", "get_all_current"]},
            "npc_id": {"type": "integer"},
            "npc_name": {"type": "string"},
            "time_slot": {"type": "string"},
        }

    async def run(self, **kwargs) -> dict:
        action = kwargs.get("action", "get_schedule")
        npc_name = kwargs.get("npc_name", "")

        if action == "get_schedule":
            return {"status": "ok", "schedule": self.DEFAULT_SCHEDULES.get(npc_name, [])}

        elif action == "get_location_at":
            time_slot = kwargs.get("time_slot", "08:00")
            schedule = self.DEFAULT_SCHEDULES.get(npc_name, [])
            location = "茶馆"
            for slot_time, activity, loc in schedule:
                if slot_time <= time_slot:
                    location = loc
                    activity_name = activity
            return {"status": "ok", "npc_name": npc_name, "time": time_slot, "location": location, "activity": activity_name}

        elif action == "get_all_current":
            time_slot = kwargs.get("time_slot", "08:00")
            result = {}
            for name, schedule in self.DEFAULT_SCHEDULES.items():
                loc = schedule[0][2]
                act = schedule[0][1]
                for slot_time, activity, location in schedule:
                    if slot_time <= time_slot:
                        loc = location
                        act = activity
                result[name] = {"location": loc, "activity": act}
            return {"status": "ok", "time": time_slot, "npcs": result}

        return {"status": "error", "message": f"Unknown action: {action}"}
