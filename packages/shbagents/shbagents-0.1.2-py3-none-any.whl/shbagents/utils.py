from dataclasses import asdict
import json
import logging
from typing import Any

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)


class AgentError(Exception):
    """智能体相关异常的基类
    
    这是所有智能体异常的基类，提供统一的错误处理机制。
    """

    def __init__(self, message):
        """初始化异常
        
        Args:
            message: 错误消息
        """
        super().__init__(message)
        self.message = message
        logger.error(message)

    def dict(self) -> dict[str, str]:
        """将异常转换为字典格式
        
        Returns:
            包含异常类型和消息的字典
        """
        return {"type": self.__class__.__name__, "message": str(self.message)}


class AgentParsingError(AgentError):
    """智能体解析错误时抛出的异常"""
    pass


class AgentExecutionError(AgentError):
    """智能体执行错误时抛出的异常"""
    pass


class AgentMaxStepsError(AgentError):
    """智能体达到最大步数限制时抛出的异常"""
    pass


class AgentGenerationError(AgentError):
    """智能体生成错误时抛出的异常"""
    pass


def get_dict_from_nested_dataclasses(obj, ignore_key=None):
    """从嵌套的数据类对象中获取字典表示
    
    Args:
        obj: 要转换的对象
        ignore_key: 要忽略的键名
        
    Returns:
        转换后的字典
    """
    def convert(obj):
        # 如果对象是数据类，递归转换其字段
        if hasattr(obj, "__dataclass_fields__"):
            return {k: convert(v) for k, v in asdict(obj).items() if k != ignore_key}
        return obj

    return convert(obj)



def make_json_serializable(obj: Any) -> Any:
    """递归函数，将对象转换为JSON可序列化格式"""
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        # 如果字符串看起来像 JSON 对象或数组，尝试解析为 JSON
        if isinstance(obj, str):
            try:
                if (obj.startswith("{") and obj.endswith("}")) or (obj.startswith("[") and obj.endswith("]")):
                    parsed = json.loads(obj)
                    return make_json_serializable(parsed)
            except json.JSONDecodeError:
                pass
        return obj
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    elif hasattr(obj, "__dict__"):
        # 对于自定义对象，将其__dict__转换为可序列化格式
        return {"_type": obj.__class__.__name__, **{k: make_json_serializable(v) for k, v in obj.__dict__.items()}}
    else:
        # 对于其他任何类型，转换为字符串
        return str(obj)