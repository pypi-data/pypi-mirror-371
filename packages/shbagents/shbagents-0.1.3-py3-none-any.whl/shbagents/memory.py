
# 导入数据类相关模块
from dataclasses import asdict, dataclass
from typing import Any

# 导入模型相关类
from .model import ChatMessage, MessageRole
# 导入工具函数和异常类
from .utils import AgentError, get_dict_from_nested_dataclasses, logger, make_json_serializable


@dataclass
class ToolCall:
    """工具调用数据类
    
    Attributes:
        name: 工具名称
        arguments: 工具参数
        id: 调用ID
    """
    name: str
    arguments: Any
    id: str

    def dict(self):
        """将工具调用转换为字典格式"""
        return {
            "id": self.id,
            "type": "function",
            "function": {
                "name": self.name,
                "arguments": make_json_serializable(self.arguments)
            }
        }


@dataclass
class ToolOutput:
    """工具输出数据类
    
    Attributes:
        id: 工具输出ID
        output: 工具输出内容
        is_final_answer: 是否为最终答案
        observation: 观察结果
        tool_call: 相关的工具调用
    """
    id: str
    output: Any
    is_final_answer: bool
    observation: str
    tool_call: ToolCall


@dataclass
class MemoryStep:
    """内存步骤基类"""
    
    def dict(self):
        """将步骤转换为字典格式"""
        return asdict(self)

    def to_messages(self) -> list[ChatMessage]:
        """将步骤转换为聊天消息列表"""
        raise NotImplementedError
    
    
@dataclass
class TaskStep(MemoryStep):
    """任务步骤数据类
    
    Attributes:
        task: 任务描述
    """
    task: str
    
    def to_messages(self) -> list[ChatMessage]:
        """将任务步骤转换为聊天消息"""
        content = [
            {
                "type": "text", 
                "text": f"新任务: \n {self.task}"
            }
        ]
        return [ChatMessage(role=MessageRole.USER, content=content)]


@dataclass
class SystemPromptStep(MemoryStep):
    """系统提示步骤数据类
    
    Attributes:
        system_prompt: 系统提示内容
    """
    system_prompt: str

    def to_messages(self) -> list[ChatMessage]:
        """将系统提示步骤转换为聊天消息"""
        content = [
            {
                "type": "text", 
                "text": self.system_prompt
            }
        ]
        return [ChatMessage(role=MessageRole.SYSTEM, content=content)]


@dataclass
class FinalAnswerStep(MemoryStep):
    """最终答案步骤数据类
    
    Attributes:
        output: 输出内容
    """
    output: Any


@dataclass
class ActionStep(MemoryStep):
    """动作步骤数据类
    
    Attributes:
        step_number: 步骤编号
        model_input_messages: 模型输入消息
        tool_calls: 工具调用列表
        error: 错误信息
        model_output_message: 模型输出消息
        model_output: 模型输出内容
        observations: 观察结果
        action_output: 动作输出
        is_final_answer: 是否为最终答案
    """
    step_number: int
    model_input_messages: list[ChatMessage] | None = None
    tool_calls: list[ToolCall] | None = None
    error: AgentError | None = None
    model_output_message: ChatMessage | None = None
    model_output: str | list[dict[str, Any]] | None = None
    observations: str | None = None
    action_output: Any = None
    is_final_answer: bool = False

    def to_messages(self) -> list[ChatMessage]:
        """将动作步骤转换为聊天消息列表"""
        messages = []
        if self.model_output is not None:
            content = [ 
                {
                    "type": "text", 
                    "text": self.model_output.strip()
                }
            ]
            messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=content))

        if self.tool_calls is not None:
            content = [
                {
                    "type": "text", 
                    "text": "调用工具: \n " + str([tc.dict() for tc in self.tool_calls])
                }
            ]
            messages.append(ChatMessage(role=MessageRole.TOOL_CALL, content=content))

        if self.observations is not None:
            content = [
                {
                    "type": "text",
                    "text": f"观察结果:\n{self.observations}"
                }
            ]
            messages.append(ChatMessage(role=MessageRole.TOOL_RESPONSE, content=content))

        if self.error is not None:
            error_message = (
                "错误:\n"
                + str(self.error)
                + "\n现在让我们重试: 小心不要重复之前的错误! 如果你已经重试了几次, 尝试一个完全不同的方法.\n"
            )
            message_content = f"调用id: {self.tool_calls[0].id}\n" if self.tool_calls else ""
            message_content += error_message
            content = [
                {
                    "type": "text",
                    "text": message_content
                }
            ]
            messages.append(ChatMessage(role=MessageRole.TOOL_RESPONSE, content=content))

        return messages


@dataclass
class PlanningStep(MemoryStep):
    """规划步骤数据类
    
    Attributes:
        model_input_messages: 模型输入消息列表
        model_output_message: 模型输出消息
        plan: 规划内容
    """
    model_input_messages: list[ChatMessage]
    model_output_message: ChatMessage
    plan: str

    def dict(self):
        """将规划步骤转换为字典格式"""
        return {
            "model_input_messages": [
                make_json_serializable(get_dict_from_nested_dataclasses(msg)) for msg in self.model_input_messages
            ],
            "model_output_message": make_json_serializable(
                get_dict_from_nested_dataclasses(self.model_output_message)
            ),
            "plan": self.plan,
            "timing": self.timing.dict(),
            "token_usage": asdict(self.token_usage) if self.token_usage else None,
        }

    def to_messages(self, summary_mode: bool = False) -> list[ChatMessage]:
        """将规划步骤转换为聊天消息列表
        
        Args:
            summary_mode: 是否为摘要模式
            
        Returns:
            聊天消息列表
        """
        if summary_mode:
            return []
        return [
            ChatMessage(role=MessageRole.ASSISTANT, content=[{"type": "text", "text": self.plan.strip()}]),
            ChatMessage(
                role=MessageRole.USER, content=[{"type": "text", "text": "现在继续执行这个计划。"}]
            ),
            # 第二条消息创建角色变化，防止模型简单地继续规划消息
        ]

class AgentMemory:
    """智能体内存类，包含系统提示和智能体执行的所有步骤

    此类用于存储智能体的步骤，包括任务、动作和规划步骤。
    它允许重置内存、检索简洁或完整的步骤信息，以及重放智能体的步骤。

    Args:
        system_prompt (`str`): 智能体的系统提示，设置智能体行为的上下文和指令。

    **属性**:
        - **system_prompt** (`SystemPromptStep`) -- 智能体的系统提示步骤。
        - **steps** (`list[TaskStep | ActionStep | PlanningStep]`) -- 智能体执行的步骤列表，可以包括任务、动作和规划步骤。
    """

    def __init__(self, system_prompt: str):
        """初始化智能体内存
        
        Args:
            system_prompt: 系统提示内容
        """
        self.system_prompt: SystemPromptStep = SystemPromptStep(system_prompt=system_prompt)
        self.steps: list[TaskStep | ActionStep | PlanningStep] = []

    def reset(self):
        """重置智能体的内存，清除所有步骤并保留系统提示。"""
        self.steps = []

    def get_succinct_steps(self) -> list[dict]:
        """返回智能体步骤的简洁表示，不包括模型输入消息。
        
        Returns:
            步骤的简洁字典表示列表
        """
        return [
            {key: value for key, value in step.dict().items() if key != "model_input_messages"} for step in self.steps
        ]

    def get_full_steps(self) -> list[dict]:
        """返回智能体步骤的完整表示，包括模型输入消息。
        
        Returns:
            步骤的完整字典表示列表
        """
        if len(self.steps) == 0:
            return []
        return [step.dict() for step in self.steps]