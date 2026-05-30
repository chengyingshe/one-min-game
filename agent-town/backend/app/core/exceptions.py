class AgentError(Exception):
    """Agent 运行时异常基类"""
    pass


class ToolNotFoundError(AgentError):
    """工具未注册"""
    pass


class LLMCallError(AgentError):
    """LLM 调用失败"""
    pass


class MemoryStoreError(AgentError):
    """记忆存储失败"""
    pass
