from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    temperature: float = 0.8
    max_tokens: int = 500
    max_history: int = 20
    memory_search_limit: int = 5
    debug: bool = False
    extra: dict = field(default_factory=dict)
