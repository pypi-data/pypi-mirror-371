"""
SHB Agent - 通用的多模型智能体框架

这个框架支持：
- 多种 LLM 模型 (OpenAI, Anthropic, etc.)
- 灵活的工具调用系统
- 基于文本解析的通用工具调用
- 丰富的日志和监控

主要类：
- Agent: 智能体主类
- Tool: 工具类
- @tool: 工具装饰器
- OpenAIModel: OpenAI 模型接口

使用示例：
    from shb_agent import Agent, OpenAIModel, tool
    
    @tool
    def add_numbers(a: float, b: float) -> float:
        '''两数相加'''
        return a + b
    
    model = OpenAIModel(model_id="gpt-4")
    agent = Agent(model=model, tools=[add_numbers])
    
    result = agent.run("计算 3.5 + 2.7")
"""

from ._version import __version__
__author__ = "huangbaocheng"
__license__ = "MIT"

# 导入主要类和函数
from .agents import Agent, MultiStepAgent
from .model import OpenAIModel, ChatMessage, MessageRole
from .tool import Tool, tool
from .prompt import PromptTemplates
from .default_tools import FinalAnswerTool
from .utils import AgentError, AgentExecutionError, AgentGenerationError
from .monitoring import AgentLogger

# 定义公开的 API
__all__ = [
    # 版本信息
    "__version__",
    "__author__", 
    "__license__",
    
    # 核心类
    "Agent",
    "MultiStepAgent",
    
    # 模型相关
    "OpenAIModel",
    "ChatMessage", 
    "MessageRole",
    
    # 工具相关
    "Tool",
    "tool",
    "FinalAnswerTool",
    
    # 提示模板
    "PromptTemplates",
    
    # 错误类
    "AgentError",
    "AgentExecutionError", 
    "AgentGenerationError",
    
    # 日志
    "AgentLogger",
]