from abc import ABC, abstractmethod


class Tool(ABC):
    """工具基类 — 万物皆为工具 (Memory, Dialogue, Trade...)

    HelloAgents 设计哲学: 所有能力统一抽象为 Tool,
    通过 Agent.register_tool() 注入, 实现开闭原则。
    """

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def get_parameters(self) -> dict: ...

    @abstractmethod
    async def run(self, **kwargs) -> dict: ...
