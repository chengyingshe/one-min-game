from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.config import AgentConfig
from app.llm.deepseek_llm import DeepSeekLLM
from app.storage.database import SessionLocal, init_db
from app.storage.qdrant_client import get_qdrant


# -- Lifespan: setup & teardown --
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Init database tables
    init_db()

    # Init Qdrant
    qdrant = get_qdrant()
    qdrant.init_collection()

    # Create LLM
    llm = DeepSeekLLM()

    # Create tools
    from app.tools.emotion_tool import EmotionTool
    from app.tools.memory_tool import MemoryTool
    from app.tools.dialogue_tool import DialogueTool
    from app.tools.trade_tool import TradeTool
    from app.tools.schedule_tool import ScheduleTool
    from app.tools.world_tool import WorldTool

    memory_tool = MemoryTool(llm)
    emotion_tool = EmotionTool()
    dialogue_tool = DialogueTool(llm)
    trade_tool = TradeTool(llm)
    schedule_tool = ScheduleTool()
    world_tool = WorldTool(SessionLocal)

    # Create agents
    from app.agents.npc_agent import NPCAgent
    from app.agents.world_agent import WorldAgent

    agent_config = AgentConfig()

    npc_agents = [
        NPCAgent(1, {
            "name": "林黛玉", "source": "红楼梦", "occupation": "诗人",
            "personality": {"tags": ["聪慧敏感", "多愁善感", "才华横溢", "孤傲", "细腻"],
                           "extraversion": 25, "agreeableness": 60},
            "current_location": "书院", "current_emotion": "neutral",
            "speaking_style": "文雅含蓄，用词考究，时常引用诗词",
        }, llm, agent_config),
        NPCAgent(2, {
            "name": "孙悟空", "source": "西游记", "occupation": "护卫",
            "personality": {"tags": ["自信豪迈", "桀骜不驯", "重情重义", "机灵"],
                           "extraversion": 90, "agreeableness": 55},
            "current_location": "集市", "current_emotion": "happy",
            "speaking_style": "直爽豪迈，自称'俺老孙'，爱开玩笑",
        }, llm, agent_config),
        NPCAgent(3, {
            "name": "张飞", "source": "三国演义", "occupation": "护卫",
            "personality": {"tags": ["豪爽粗犷", "忠心耿耿", "勇猛", "爱喝酒"],
                           "extraversion": 85, "agreeableness": 65},
            "current_location": "茶馆", "current_emotion": "happy",
            "speaking_style": "嗓门大，说话直来直去，自称'俺'",
        }, llm, agent_config),
    ]

    # Register tools to each NPC agent
    for agent in npc_agents:
        agent.register_tool(memory_tool)
        agent.register_tool(emotion_tool)
        agent.register_tool(dialogue_tool)
        agent.register_tool(trade_tool)

    world_agent = WorldAgent(llm, agent_config)
    world_agent.register_tool(world_tool)
    world_agent.register_tool(schedule_tool)
    world_agent.register_tool(memory_tool)

    # Create simulation engine
    from app.core.simulation import SimulationEngine
    simulation_engine = SimulationEngine(npc_agents, world_agent, SessionLocal)

    # Store in app state
    app.state.llm = llm
    app.state.npc_agents = npc_agents
    app.state.world_agent = world_agent
    app.state.player_agents = {}
    app.state.db_session_factory = SessionLocal
    app.state.qdrant = qdrant
    app.state.simulation_engine = simulation_engine

    # Start simulation
    await simulation_engine.start()

    yield

    # Cleanup
    await simulation_engine.stop()


# -- FastAPI app --
app = FastAPI(
    title="Agent Town - 时空杂货镇",
    description="AI Agent 社交模拟游戏 API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from app.routes.game import router as game_router
from app.routes.characters import router as characters_router
from app.routes.dialogue import router as dialogue_router
from app.routes.trade import router as trade_router
from app.routes.memories import router as memories_router
from app.routes.relationships import router as relationships_router
from app.routes.websocket import router as websocket_router

app.include_router(game_router)
app.include_router(characters_router)
app.include_router(dialogue_router)
app.include_router(trade_router)
app.include_router(memories_router)
app.include_router(relationships_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {"name": "Agent Town API", "version": "0.1.0", "status": "running"}
