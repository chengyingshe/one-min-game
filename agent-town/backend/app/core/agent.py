from abc import ABC, abstractmethod

from app.core.config import AgentConfig
from app.core.message import Message
from app.core.tool import Tool
from app.llm.base import BaseLLM


class Agent(ABC):
    """Agent 基类 — HelloAgents 核心抽象

    所有 Agent (NPCAgent, PlayerAgent, WorldAgent) 继承此类,
    通过 register_tool() 注入能力, 通过 run() 处理输入。
    """

    def __init__(self, name: str, config: AgentConfig, llm: BaseLLM):
        self.name = name
        self.config = config
        self.llm = llm
        self.tools: dict[str, Tool] = {}

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    @abstractmethod
    async def run(self, input_message: Message) -> Message: ...
