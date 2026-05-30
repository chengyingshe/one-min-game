import json
from sqlalchemy.orm import Session

from app.core.tool import Tool
from app.storage.db_models import WorldStateRecord


class WorldTool(Tool):
    """世界工具 — 管理世界时间、天气等全局状态"""

    name = "world"
    description = "查询和推进世界状态（时间、天数），触发日程更新和记忆整合"

    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    def get_parameters(self) -> dict:
        return {
            "action": {"type": "string", "enum": ["get_state", "advance_time"]},
            "hours": {"type": "integer", "description": "推进的小时数"},
        }

    async def run(self, **kwargs) -> dict:
        action = kwargs.get("action", "get_state")

        if action == "get_state":
            return self.get_state()

        elif action == "advance_time":
            hours = kwargs.get("hours", 1)
            return self.advance_time(hours)

        return {"status": "error", "message": f"Unknown action: {action}"}

    def get_state(self) -> dict:
        db = self.db_session_factory()
        try:
            state = {}
            for record in db.query(WorldStateRecord).all():
                try:
                    state[record.key] = json.loads(record.value_json)
                except (json.JSONDecodeError, TypeError):
                    state[record.key] = record.value_json
            return {
                "status": "ok",
                "current_day": state.get("current_day", 1),
                "current_time": state.get("current_time", "08:00"),
            }
        finally:
            db.close()

    def advance_time(self, hours: int) -> dict:
        db = self.db_session_factory()
        try:
            current_day = self._get_or_create_key(db, "current_day", 1)
            current_time = self._get_or_create_key(db, "current_time", "08:00")

            hour = int(current_time.split(":")[0])
            new_hour = hour + hours
            new_day = int(current_day)
            day_advanced = False

            while new_hour >= 24:
                new_hour -= 24
                new_day += 1
                day_advanced = True

            new_time = f"{new_hour:02d}:00"

            self._set_key(db, "current_day", new_day)
            self._set_key(db, "current_time", new_time)
            db.commit()

            should_consolidate = day_advanced

            return {
                "status": "ok",
                "current_day": new_day,
                "current_time": new_time,
                "day_advanced": day_advanced,
                "should_consolidate_memories": should_consolidate,
            }
        finally:
            db.close()

    def _get_or_create_key(self, db, key: str, default):
        record = db.query(WorldStateRecord).filter(WorldStateRecord.key == key).first()
        if record:
            try:
                return json.loads(record.value_json)
            except (json.JSONDecodeError, TypeError):
                return record.value_json
        db.add(WorldStateRecord(key=key, value_json=json.dumps(default)))
        db.commit()
        return default

    def _set_key(self, db, key: str, value):
        record = db.query(WorldStateRecord).filter(WorldStateRecord.key == key).first()
        if record:
            record.value_json = json.dumps(value)
        else:
            db.add(WorldStateRecord(key=key, value_json=json.dumps(value)))
