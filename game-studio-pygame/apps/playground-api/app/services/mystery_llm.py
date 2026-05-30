"""LLM主持人 + AI角色扮演服务"""

from __future__ import annotations

from app.services.llm_service import chat
from app.services.mystery_scenario import (
    CHARACTERS,
    PRIVATE_SCRIPTS,
    PUBLIC_CLUES,
    DORM_CLUES,
    BODY_CLUES,
    TRUTH,
    DEDUCTION_CHAIN,
)

# ============================================================
# System Prompts
# ============================================================

HOST_SYSTEM_PROMPT = """你是剧本杀游戏《相府鱼美人》的主持人（法海和尚）。

故事背景：
宋朝，相府有一个开放式水池，水流连通城外十里坡。相府千金常在池边喂鱼，
其中一条红色大鲤鱼已消失半年。你（法海）察觉到鱼妖妖气，前来调查。

四位嫌疑人：除妖人、丫鬟、剑客、女厨。其中一人是鱼妖所化。

你的职责：
1. 主持游戏流程，推动剧情发展
2. 适时给出引导和提示，但不直接揭示真相
3. 用古风文雅的语言风格
4. 营造悬疑氛围

注意：
- 说话时自称"老衲"（法海自称）
- 保持神秘感和权威感
- 不要直接告诉玩家谁是鱼妖
- 引导玩家思考和讨论"""

ROLE_SYSTEM_PROMPTS: dict[str, str] = {}

for _char_id, _char_data in CHARACTERS.items():
    _script = PRIVATE_SCRIPTS[_char_id]
    ROLE_SYSTEM_PROMPTS[_char_id] = f"""你是剧本杀游戏《相府鱼美人》中的角色：{_char_data['name']}。

你的表面身份：{_char_data['surface_identity']}
你的真实身份：{_char_data['true_identity']}

你的秘密：{_script['secret']}

你的背景故事：
{_script['backstory']}

你必须隐瞒的信息：
{chr(10).join(f'- {h}' for h in _script['must_hide'])}

你知道的信息：
{chr(10).join(f'- {k}' for k in _script['knowledge'])}

角色扮演规则：
1. 始终保持角色身份，不要说"我是AI"
2. 绝不主动透露你必须隐瞒的信息
3. 如果被问到敏感问题，用角色的方式巧妙回避
4. 你的说话风格要符合角色性格
5. 用古风白话文风格
6. 回复简短，2-3句话即可
7. 可以适度表现你对其他角色的看法和感情"""

# ============================================================
# LLM Functions
# ============================================================


def host_narrate(context: str) -> str:
    """LLM 主持人旁白"""
    messages = [
        {"role": "system", "content": HOST_SYSTEM_PROMPT},
        {"role": "user", "content": f"请根据以下情境进行旁白叙述（2-4句话）：\n\n{context}"},
    ]
    result = chat(messages, temperature=0.8, max_tokens=300)
    return result["content"]


def host_opening() -> str:
    """LLM 主持人开场白"""
    messages = [
        {"role": "system", "content": HOST_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": """游戏开始。请进行开场叙述，介绍背景：
- 宋朝相府，水池连通十里坡
- 红色大鲤鱼消失半年
- 四位嫌疑人（除妖人、丫鬟、剑客、女厨）
- 其中一人是鱼妖

用古风文雅的语言，营造悬疑氛围。告诉各位角色自我介绍。""",
        },
    ]
    result = chat(messages, temperature=0.8, max_tokens=500)
    return result["content"]


def host_phase_transition(from_phase: str, to_phase: str) -> str:
    """LLM 主持人阶段转换旁白"""
    phase_desc = {
        "discuss": "自由讨论阶段。各位可以相互询问、交流信息。注意不要直接暴露自己的秘密。",
        "investigate": "搜证阶段。所有公开线索已展示。现在投票决定搜查谁的宿舍和随身物品。",
        "discuss2": "深入讨论阶段。根据已获得的线索，各位可以进一步推理和讨论。",
        "vote": "最终投票阶段。各位请投票指认你认为的鱼妖。投票前请谨慎思考。",
        "reveal": "真相即将揭晓。",
    }
    messages = [
        {"role": "system", "content": HOST_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"请宣布游戏进入{phase_desc.get(to_phase, to_phase)}阶段。用古风语言，简洁有力。",
        },
    ]
    result = chat(messages, temperature=0.7, max_tokens=300)
    return result["content"]


def host_announce_clue(clue_description: str) -> str:
    """LLM 主持人宣布发现的线索"""
    messages = [
        {"role": "system", "content": HOST_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"搜证结果发现了以下线索：{clue_description}\n\n请以主持人的身份，用古风语言向大家宣读这个发现。添加一些悬疑的评论，但不直接揭示真相。",
        },
    ]
    result = chat(messages, temperature=0.7, max_tokens=300)
    return result["content"]


def host_reveal_truth() -> str:
    """LLM 主持人揭晓真相"""
    messages = [
        {"role": "system", "content": HOST_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"请以法海的身份揭晓真相：\n\n{TRUTH}\n\n用古风文雅的语言，营造戏剧性的真相揭晓效果。",
        },
    ]
    result = chat(messages, temperature=0.8, max_tokens=600)
    return result["content"]


def role_play_speak(
    char_id: str,
    chat_history: list[dict],
    recent_messages: list[dict],
) -> str:
    """LLM AI角色发言"""
    system_prompt = ROLE_SYSTEM_PROMPTS.get(char_id, "你是一个普通角色。")

    messages = [{"role": "system", "content": system_prompt}]

    # Add recent chat history as context
    for msg in recent_messages[-12:]:  # Last 12 messages for context
        messages.append(msg)

    messages.append({
        "role": "user",
        "content": "现在轮到你说话了。请根据当前的讨论内容，以你的角色身份进行回应。2-3句话即可。",
    })

    result = chat(messages, temperature=0.85, max_tokens=200)
    return result["content"]


def role_private_script_summary(char_id: str) -> str:
    """生成角色私密剧本摘要（开场时发给该角色）"""
    script = PRIVATE_SCRIPTS[char_id]
    char = CHARACTERS[char_id]
    return f"""【你的角色】{char['name']}（{script['role']}）

【你的秘密】{script['secret']}

【你的故事】{script['backstory']}

【你必须隐瞒】
{chr(10).join(f'- {h}' for h in script['must_hide'])}

【你必须知道的线索】
{chr(10).join(f'- {k}' for k in script['knowledge'])}"""
