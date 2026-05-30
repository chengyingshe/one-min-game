"""《相府鱼美人》剧本杀 — 完整剧本数据"""

# ============================================================
# 角色定义
# ============================================================

CHARACTERS = {
    "hunter": {
        "id": "hunter",
        "name": "除妖人",
        "gender": "男",
        "age": 27,
        "surface_identity": "风流倜傥的除妖师",
        "true_identity": "人类骗子，完全不会除妖",
        "color": [255, 220, 50],  # 金色
        "emoji": "🎭",
    },
    "maid": {
        "id": "maid",
        "name": "丫鬟",
        "gender": "女",
        "age": 18,
        "surface_identity": "娇小可爱的侍女",
        "true_identity": "人类，家道中落的少女",
        "color": [255, 150, 180],  # 粉色
        "emoji": "👧",
    },
    "swordsman": {
        "id": "swordsman",
        "name": "剑客",
        "gender": "男",
        "age": 25,
        "surface_identity": "自称剑术精湛",
        "true_identity": "⭐ 鱼妖（鲤鱼精）",
        "color": [100, 180, 255],  # 蓝色
        "emoji": "🗡️",
    },
    "cook": {
        "id": "cook",
        "name": "女厨",
        "gender": "女",
        "age": 20,
        "surface_identity": "自称会做家常菜",
        "true_identity": "身份存疑，从不烧鱼",
        "color": [100, 220, 100],  # 绿色
        "emoji": "🍳",
    },
}

CHARACTER_IDS = list(CHARACTERS.keys())

# ============================================================
# 角色私密剧本
# ============================================================

PRIVATE_SCRIPTS = {
    "hunter": {
        "role": "除妖人（人类骗子）",
        "secret": "你完全不会除妖，只是冒充除妖师行骗敛财的普通人。",
        "backstory": """你在十里坡扮乞丐行骗，喜欢吹笛子。你曾把骗来的钱给了穷困的丫鬟（少有的善举）。

遇到蛇妖时你吓得抱头蹲下，事后谎称是自己吓退了蛇妖。

来相府后你发现千金小姐是绝色美女，经常躲在厨房偷窥。

**真正喜欢你的是相府千金小姐**，而非丫鬟。""",
        "must_hide": [
            "自己是骗子",
            "遇到蛇妖时吓坏了",
            "偷偷喜欢千金小姐",
            "经常躲在厨房偷窥",
        ],
        "knowledge": [
            "你曾把骗来的钱给丫鬟",
            "来相府的经过",
            "在十里坡遇到蛇妖（你吓坏了但假装镇定）",
        ],
    },
    "maid": {
        "role": "丫鬟（人类少女）",
        "secret": "你对吹笛子的除妖人一见钟情。",
        "backstory": """你原本家境不错，后家道中落沦为乞丐在十里坡流浪。

你对吹笛子的除妖人一见钟情，把馒头分给他。

目睹"除妖人赶走蛇妖"后更加倾心（实际是剑客暗中出手）。

追随除妖人来到相府，路上结识白衣剑客并成为朋友。

在相府发现除妖人和女厨关系亲密，心碎想要放弃。

不知道每晚门前的菜肴其实是剑客偷偷放的。""",
        "must_hide": [
            "你暗恋除妖人",
            "你给了除妖人馒头",
            "你因为除妖人和女厨的关系而心碎",
        ],
        "knowledge": [
            "在十里坡遇到除妖人",
            "来相府的经过",
            "剑客是路上认识的朋友",
            "每晚门前出现菜肴（不知道是谁放的）",
        ],
    },
    "swordsman": {
        "role": "剑客（⭐ 鱼妖/鲤鱼精）",
        "secret": "你是相府水池中消失的红色大鲤鱼所化。你暗恋丫鬟，因为喜欢的对象是女性，所以化身为男性人形。",
        "backstory": """你是那条消失的红色大鲤鱼。经常偷跑出十里坡游荡，曾咬过女厨。

因暗恋丫鬟而变身为人形（男性），跟随她来到相府。

曾在十里坡暗中出手打伤蛇妖，救了丫鬟和除妖人。

在相府利用女厨对你的好感，把女厨做的菜偷偷放在丫鬟门前。

故意安排丫鬟撞见除妖人和女厨在一起，离间两人关系。""",
        "must_hide": [
            "自己是鱼妖（鲤鱼精）",
            "暗恋丫鬟所以化身为男性",
            "在十里坡打伤蛇妖救了他们",
            "暗中操控一切（送菜、离间）",
        ],
        "knowledge": [
            "十里坡的水池",
            "来相府的经过",
            "和丫鬟在路上认识",
            "在十里坡遇到过蛇妖",
        ],
    },
    "cook": {
        "role": "女厨（身份存疑）",
        "secret": "你自称会做家常菜，但**从来不烧鱼**。这可能是最大的疑点。",
        "backstory": """你自称会做家常菜，厨艺很好。

你对除妖人很友好，经常给他做菜。

**核心疑点：从来不烧鱼。**

对剑客有好感，经常去剑客宿舍。

宿舍里有除妖人的脚印和一口锅。

身上只有一本菜谱。

你为什么从不烧鱼？你是否知道某些秘密？""",
        "must_hide": [
            "从来不烧鱼的真正原因",
            "你和剑客之间到底是什么关系",
            "你身上那本菜谱的真正内容",
        ],
        "knowledge": [
            "你的厨艺",
            "你对除妖人的友好",
            "你对剑客的好感",
            "相府水池的情况",
        ],
    },
}

# ============================================================
# 线索系统
# ============================================================

# 公开线索（游戏开始时自动展示）
PUBLIC_CLUES = [
    {
        "id": "snake_demon",
        "name": "十里坡蛇妖的证词",
        "category": "public",
        "description": "蛇妖说：「鲤鱼精为了喜欢的人打伤了我。」",
        "inference": "鲤鱼精（剑客）为保护喜欢的人出手，说明鲤鱼精喜欢某人。",
        "scene": "slope",
    },
    {
        "id": "young_lady_diary",
        "name": "小姐日记",
        "category": "public",
        "description": "相府小姐的日常记录，提到最近府中来了几位奇怪的客人。",
        "inference": "辅助信息，帮助了解相府情况。",
        "scene": "mansion",
    },
    {
        "id": "koi_fish",
        "name": "池塘小鲤鱼的证词",
        "category": "public",
        "description": "小鲤鱼说：「鲤鱼精最有心机，总骗鱼食吃。」",
        "inference": "鲤鱼精（剑客）狡猾有心机，擅长伪装和操控。",
        "scene": "pool",
    },
]

# 宿舍线索（投票决定查谁）
DORM_CLUES = {
    "hunter": {
        "id": "dorm_hunter",
        "name": "除妖人宿舍",
        "target": "hunter",
        "category": "dorm",
        "description": "在除妖人宿舍发现：长笛 + 捉妖器具。",
        "inference": "长笛和捉妖器具都是维持「除妖师」人设的道具，说明他可能是骗子。",
        "scene": "dorm_hunter",
    },
    "maid": {
        "id": "dorm_maid",
        "name": "丫鬟宿舍",
        "target": "maid",
        "category": "dorm",
        "description": "在丫鬟宿舍发现：破衣服 + 菜肴香味。",
        "inference": "有人偷偷在丫鬟门前放菜（实际是剑客所为），丫鬟的家境不好。",
        "scene": "dorm_maid",
    },
    "swordsman": {
        "id": "dorm_swordsman",
        "name": "剑客宿舍",
        "target": "swordsman",
        "category": "dorm",
        "description": "在剑客宿舍发现：女厨脚印 + 长剑。",
        "inference": "女厨经常来找剑客，说明两人关系密切。",
        "scene": "dorm_swordsman",
    },
    "cook": {
        "id": "dorm_cook",
        "name": "女厨宿舍",
        "target": "cook",
        "category": "dorm",
        "description": "在女厨宿舍发现：除妖人脚印 + 一口锅。",
        "inference": "除妖人经常去（实为偷窥小姐路过），但为什么有锅？",
        "scene": "dorm_cook",
    },
}

# 身上线索（投票决定查谁）
BODY_CLUES = {
    "hunter": {
        "id": "body_hunter",
        "name": "搜查除妖人身上",
        "target": "hunter",
        "category": "body",
        "description": "除妖人身上带着：写着爱慕小姐的日记。",
        "inference": "除妖人喜欢小姐，不是丫鬟。如果鲤鱼精喜欢的是女性，除妖人动机不符。",
        "scene": "search_hunter",
    },
    "maid": {
        "id": "body_maid",
        "name": "搜查丫鬟身上",
        "target": "maid",
        "category": "body",
        "description": "丫鬟身上带着：喜欢除妖人的日记。",
        "inference": "丫鬟单恋除妖人，感情线明确。",
        "scene": "search_maid",
    },
    "swordsman": {
        "id": "body_swordsman",
        "name": "搜查剑客身上",
        "target": "swordsman",
        "category": "body",
        "description": "剑客身上带着：写着「大好生活在等着我」的日记。",
        "inference": "剑客对未来充满期待，暗示他对追求丫鬟有信心。",
        "scene": "search_swordsman",
    },
    "cook": {
        "id": "body_cook",
        "name": "搜查女厨身上",
        "target": "cook",
        "category": "body",
        "description": "女厨身上带着：一本菜谱。",
        "inference": "无明显指向。但「从不烧鱼」仍是疑点。",
        "scene": "search_cook",
    },
}

# ============================================================
# 推理真相
# ============================================================

TRUTH = """【真相揭晓】

剑客 = 鱼妖（鲤鱼精）！

他原本是相府水池中消失的红色大鲤鱼，因为遇到丫鬟后心生爱慕，
变身成了男性人形（因为喜欢的对象是女性），跟随丫鬟来到相府。

推理逻辑链：
1. 蛇妖说「鲤鱼精为了喜欢的人打伤我」→ 鲤鱼精喜欢某人
2. 鱼妖特性：根据心仪对象性别决定化身性别 → 喜欢女性 → 化身为男性
3. 嫌疑锁定男性角色：除妖人 或 剑客
4. 排除除妖人：日记写着喜欢小姐（动机不符），遇蛇妖时抱头蹲下（不可能打伤蛇妖）
5. 锁定剑客：日记「大好生活在等着我」，小鲤鱼说「鲤鱼精有心机」，
   女厨从不烧鱼（可能知道剑客是鱼妖）

剑客 = 鲤鱼精 ✅"""

DEDUCTION_CHAIN = [
    "蛇妖证词：鲤鱼精为了喜欢的人打伤了我 → 鲤鱼精喜欢某人，且为保护TA出手",
    "鱼妖特性 — 根据心仪对象性别决定化身性别 → 喜欢女性 → 化身为男性",
    "嫌疑锁定男性角色：除妖人 或 剑客",
    "排除除妖人 → 日记写喜欢小姐（动机不符）+ 遇蛇妖时抱头蹲下（不可能打伤蛇妖）",
    "锁定剑客 → 日记大好生活在等着我 + 小鲤鱼说鲤鱼精有心机 + 女厨从不烧鱼",
    "结论：剑客 = 鲤鱼精 ✅",
]

# ============================================================
# 游戏阶段
# ============================================================

PHASE_LOBBY = "lobby"
PHASE_ROLE_SELECT = "role_select"
PHASE_INTRO = "intro"
PHASE_DISCUSS = "discuss"
PHASE_INVESTIGATE = "investigate"
PHASE_DISCUSS2 = "discuss2"
PHASE_VOTE = "vote"
PHASE_REVEAL = "reveal"

PHASES = [
    PHASE_LOBBY,
    PHASE_ROLE_SELECT,
    PHASE_INTRO,
    PHASE_DISCUSS,
    PHASE_INVESTIGATE,
    PHASE_DISCUSS2,
    PHASE_VOTE,
    PHASE_REVEAL,
]

PHASE_DESCRIPTIONS = {
    PHASE_LOBBY: "等待玩家加入...",
    PHASE_ROLE_SELECT: "选择你的角色",
    PHASE_INTRO: "故事即将开始...",
    PHASE_DISCUSS: "自由讨论 — 了解彼此，寻找线索",
    PHASE_INVESTIGATE: "搜证阶段 — 投票决定搜查对象",
    PHASE_DISCUSS2: "深入讨论 — 根据线索推理",
    PHASE_VOTE: "最终投票 — 指认鱼妖",
    PHASE_REVEAL: "真相揭晓",
}

# ============================================================
# 游戏模式
# ============================================================

MODE_SOLO = "solo"
MODE_MULTI = "multi"
