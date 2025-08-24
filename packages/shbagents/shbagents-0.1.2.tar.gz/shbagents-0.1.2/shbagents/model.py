from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .tool import Tool


@dataclass
class ChatMessageToolCallFunction:
    """聊天消息中工具调用函数的数据类
    
    Attributes:
        arguments: 函数参数
        name: 函数名称
        description: 函数描述，可选
    """
    arguments: Any
    name: str
    description: str | None = None


@dataclass
class ChatMessageToolCallStreamDelta:
    """表示生成期间工具调用的流式增量数据
    
    Attributes:
        index: 索引，可选
        id: 调用ID，可选
        type: 调用类型，可选
        function: 函数信息，可选
    """

    index: int | None = None
    id: str | None = None
    type: str | None = None
    function: ChatMessageToolCallFunction | None = None



@dataclass
class ChatMessageStreamDelta:
    """聊天消息流式增量数据类
    
    Attributes:
        content: 内容增量，可选
        tool_calls: 工具调用增量列表，可选
    """
    content: str | None = None
    tool_calls: list[ChatMessageToolCallStreamDelta] | None = None


class MessageRole(str, Enum):
    """消息的角色"""
    # 用户
    USER = "user"
    # 助手
    ASSISTANT = "assistant"
    # 系统
    SYSTEM = "system"
    # 工具调用
    TOOL_CALL = "tool-call"
    # 工具响应
    TOOL_RESPONSE = "tool-response"

    @classmethod
    def roles(cls):
        """返回所有可用的角色值"""
        return [r.value for r in cls]
    
    @classmethod
    def is_tool_message(cls, role: str):
        """返回是否为工具消息"""
        return role == cls.TOOL_RESPONSE.value or role == cls.TOOL_CALL.value


@dataclass
class ChatMessage:
    """聊天消息数据类
    
    Attributes:
        role: 消息角色
        content: 消息内容
        tool_calls: 工具调用列表
    """
    role: MessageRole
    content: str | list[dict[str, Any]] | None = None
    tool_calls: list[dict[str, Any]] | None = None


class Model:
    """所有语言模型实现的基类。

    这个抽象类定义了所有模型实现必须遵循的核心接口，以便与代理一起工作。它提供了消息处理、工具集成和模型配置的通用功能，同时允许子类实现其特定的生成逻辑。

    参数：
    - model_id (`str`):
        服务器上使用的模型标识符（例如 "gpt-4o"）。
    - **kwargs:
      转发给底层模型完成调用的其他关键字参数。

    注意：
    这是一个抽象基类。子类必须实现 `generate()` 方法以提供实际的模型推理能力。

    示例：
    ```python
    class CustomModel(Model):
        def generate(self, messages, **kwargs):
            # 针对模型具体实现
            pass
    ```
    """

    def __init__(
        self,
        model_id: str,
        **kwargs,
    ):
        """初始化模型
        
        Args:
            model_id: 模型标识符
            **kwargs: 其他参数
        """
        self.model_id = model_id
        self.kwargs = kwargs
    
    @abstractmethod
    def generate(
        self,
        messages: list[ChatMessage],
        **kwargs,
    ) -> ChatMessage:
        """处理输入消息并返回模型的响应。

        参数:
            messages (`list[ChatMessage]`):
                要处理的消息列表。每个对象应该具有结构 `{"role": "用户/系统", "content": "消息内容"}`。
            **kwargs:
                要传递给底层模型的其他关键字参数。

        返回:
            `ChatMessage`: 包含模型响应的聊天消息对象。
        """
        raise NotImplementedError("这个方法必须在子类中实现")

    def __call__(self, *args, **kwargs):
        """使模型可调用，委托给generate方法"""
        return self.generate(*args, **kwargs)


class OpenAIModel(Model):
    """OpenAI模型

    参数:
        model_id (`str`):
            服务器上使用的模型标识符（例如 "gpt-4o"）。
        api_base (`str`, *可选*):
            OpenAI 兼容 API 服务器的基础 URL。
        api_key (`str`, *可选*):
            用于身份验证的 API 密钥。
        **kwargs:
            要传递给底层 OpenAI API 完成调用的其他关键字参数，例如 `temperature`。
    """

    def __init__(
        self,
        model_id: str,
        api_base: str | None = None,
        api_key: str | None = None,
        **kwargs,
    ):
        """初始化OpenAI模型
        
        Args:
            model_id: 模型标识符
            api_base: API 基础 URL，可选
            api_key: API 密钥，可选
            **kwargs: 其他参数
        """
        self.client_kwargs = {
            "api_key": api_key,
            "base_url": api_base,
        }
        super().__init__(
            model_id=model_id,
            **kwargs,
        )

    def create_client(self):
        """创建OpenAI客户端
        
        Returns:
            OpenAI客户端实例
            
        Raises:
            ModuleNotFoundError: 如果未安装openai包
        """
        try:
            import openai
        except ModuleNotFoundError as exception:
            raise ModuleNotFoundError(
                "请安装 'openai' 扩展包以使用 OpenAIModel：`pip install openai`"
            ) from exception

        return openai.OpenAI(**self.client_kwargs)
    
    def generate(
        self,
        messages: list[ChatMessage | dict],
        **kwargs,
    ) -> ChatMessage:
        """生成模型响应
        
        Args:
            messages: 输入消息列表
            **kwargs: 其他参数
            
        Returns:
            模型生成的聊天消息
        """
        completion_kwargs = {
            **self.kwargs,
            **kwargs,
            "model": self.model_id,
        }
        messages_list = [
            {
                "role": "user" if MessageRole.is_tool_message(message.role) else message.role, 
                "content": message.content
            }
            for message in messages
        ]
        completion_kwargs["messages"] = messages_list
        
        client = self.create_client()
        try:
            # 创建聊天补全请求
            response = client.chat.completions.create(**completion_kwargs)
        except Exception as e:
            error_msg = f"生成模型输出时发生错误: \n {e}"
            raise Exception(error_msg) from e
        
        # 提取响应消息
        message = response.choices[0].message
        
        # 创建聊天消息对象
        chat_message = ChatMessage(
            role=message.role,
            content=message.content,
        )
        return chat_message