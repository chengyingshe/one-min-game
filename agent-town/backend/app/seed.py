import json

# 地图坐标常量（800x500 画布内各地点中心坐标）
LOCATION_COORDS = {
    "茶馆": (200, 320),
    "集市": (600, 320),
    "书院": (200, 120),
    "河边": (600, 120),
}

from app.storage.db_models import (
    ItemRecord,
    LocationRecord,
    NpcRecord,
    PlayerRecord,
    ScheduleRecord,
    WorldStateRecord,
)


def seed_all(db, qdrant):
    """Initialize all MVP game data."""
    _seed_locations(db)
    _seed_npcs(db)
    _seed_items(db)
    _seed_schedules(db)
    _seed_world_state(db)
    _seed_qdrant(qdrant)
    db.commit()


def _seed_locations(db):
    if db.query(LocationRecord).count() > 0:
        return
    db.add_all([
        LocationRecord(name="teahouse", display_name="茶馆", description="温暖的传统中式茶馆，烛光摇曳，木桌木椅，柜台上的茶壶冒着热气", type="social", emoji="🍵"),
        LocationRecord(name="market", display_name="集市", description="热闹的传统市集，摊位林立，彩色布篷遮阳，灯笼高挂，石板路上人来人往", type="social", emoji="🏮"),
        LocationRecord(name="academy", display_name="书院", description="清幽的书院，高挑的书架上满是古籍卷轴，书案上摆着笔墨纸砚，纸窗映着竹影", type="social", emoji="📚"),
        LocationRecord(name="riverside", display_name="河边", description="宁静的河畔，垂柳依依，远处石桥横跨，水光潋滟，夕阳余晖洒满河面", type="nature", emoji="🌿"),
    ])


def _seed_npcs(db):
    if db.query(NpcRecord).count() > 0:
        return
    db.add_all([
        NpcRecord(
            name="林黛玉", source="红楼梦", occupation="诗人",
            personality_json=json.dumps({
                "tags": ["聪慧敏感", "多愁善感", "才华横溢", "孤傲", "细腻"],
                "extraversion": 25, "agreeableness": 60,
                "openness": 85, "conscientiousness": 70, "neuroticism": 80,
            }),
            current_location="书院", current_emotion="neutral",
            speaking_style="文雅含蓄，用词考究，时常引用诗词，字里行间带着淡淡的哀愁",
            avatar_emoji="🌸",
            pos_x=LOCATION_COORDS["书院"][0], pos_y=LOCATION_COORDS["书院"][1],
            target_location="书院", is_moving=False,
        ),
        NpcRecord(
            name="孙悟空", source="西游记", occupation="护卫",
            personality_json=json.dumps({
                "tags": ["自信豪迈", "桀骜不驯", "重情重义", "机灵", "爱吹牛"],
                "extraversion": 90, "agreeableness": 55,
                "openness": 75, "conscientiousness": 40, "neuroticism": 30,
            }),
            current_location="集市", current_emotion="happy",
            speaking_style="直爽豪迈，自称'俺老孙'，爱开玩笑，语气夸张，不时炫耀自己的本领",
            avatar_emoji="🐵",
            pos_x=LOCATION_COORDS["集市"][0], pos_y=LOCATION_COORDS["集市"][1],
            target_location="集市", is_moving=False,
        ),
        NpcRecord(
            name="张飞", source="三国演义", occupation="护卫",
            personality_json=json.dumps({
                "tags": ["豪爽粗犷", "忠心耿耿", "勇猛", "粗中有细", "爱喝酒"],
                "extraversion": 85, "agreeableness": 65,
                "openness": 40, "conscientiousness": 60, "neuroticism": 45,
            }),
            current_location="茶馆", current_emotion="happy",
            speaking_style="嗓门大，说话直来直去，喜欢哈哈大笑，称自己'俺'，动不动就要和人比试",
            avatar_emoji="💪",
            pos_x=LOCATION_COORDS["茶馆"][0], pos_y=LOCATION_COORDS["茶馆"][1],
            target_location="茶馆", is_moving=False,
        ),
    ])


def _seed_items(db):
    if db.query(ItemRecord).count() > 0:
        return
    db.add_all([
        # 林黛玉的物品
        ItemRecord(name="《葬花吟》手稿", type="collection", base_price=80,
                   description="黛玉亲笔写就的诗稿，字迹秀美，字里行间透露着淡淡的哀愁", owner_type="npc", owner_id=1),
        ItemRecord(name="玉佩", type="collection", base_price=120,
                   description="一块精致的美玉，温润细腻，据说是黛玉自幼佩戴之物", owner_type="npc", owner_id=1),
        # 孙悟空的物品
        ItemRecord(name="如意金箍棒", type="weapon", base_price=999,
                   description="定海神针，可大可小，重一万三千五百斤（此为赝品）", owner_type="npc", owner_id=2),
        ItemRecord(name="花果山的桃子", type="food", base_price=15,
                   description="来自花果山的新鲜桃子，据说吃了能延年益寿", owner_type="npc", owner_id=2),
        # 张飞的物品
        ItemRecord(name="丈八蛇矛", type="weapon", base_price=300,
                   description="张飞的成名兵器，矛尖锋利，寒光闪闪", owner_type="npc", owner_id=3),
        ItemRecord(name="陈年佳酿", type="food", base_price=50,
                   description="一坛上好的老酒，张飞珍藏已久，香气四溢", owner_type="npc", owner_id=3),
        # 商店物品
        ItemRecord(name="茶叶", type="food", base_price=5, description="一包品质不错的茶叶", owner_type="shop"),
        ItemRecord(name="竹笛", type="misc", base_price=25, description="一支手工制作的竹笛，音色清亮", owner_type="shop"),
        ItemRecord(name="宣纸", type="misc", base_price=10, description="上好的宣纸，适合书写和绘画", owner_type="shop"),
        ItemRecord(name="铜钱", type="misc", base_price=1, description="普通的铜钱，可用于交易", owner_type="shop"),
    ])


def _seed_schedules(db):
    if db.query(ScheduleRecord).count() > 0:
        return
    schedules = [
        (1, "07:00", "起床梳洗", "书院"), (1, "08:00", "去茶馆喝茶", "茶馆"),
        (1, "10:00", "抄书写字", "书院"), (1, "13:00", "午饭", "茶馆"),
        (1, "15:00", "散步赏花", "集市"), (1, "18:00", "回书院读书", "书院"),
        (1, "21:00", "就寝", "书院"),
        (2, "07:00", "起床练功", "集市"), (2, "08:00", "帮人干活", "集市"),
        (2, "12:00", "午饭喝酒", "茶馆"), (2, "14:00", "闲逛", "集市"),
        (2, "17:00", "茶馆吹牛", "茶馆"), (2, "20:00", "回住处休息", "集市"),
        (2, "22:00", "睡觉", "集市"),
        (3, "07:00", "起床练武", "茶馆"), (3, "08:00", "茶馆护卫", "茶馆"),
        (3, "12:00", "午饭喝酒", "茶馆"), (3, "14:00", "巡街", "集市"),
        (3, "17:00", "回茶馆", "茶馆"), (3, "20:00", "喝酒", "茶馆"),
        (3, "22:00", "休息", "茶馆"),
    ]
    for npc_id, time_slot, activity, location in schedules:
        db.add(ScheduleRecord(npc_id=npc_id, time_slot=time_slot, activity=activity, location=location))


def _seed_world_state(db):
    if db.query(WorldStateRecord).count() > 0:
        return
    db.add(WorldStateRecord(key="current_day", value_json="1"))
    db.add(WorldStateRecord(key="current_time", value_json="08:00"))


def _seed_qdrant(qdrant):
    """确保 Qdrant collection 存在并初始化"""
    qdrant.init_collection()
