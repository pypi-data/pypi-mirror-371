
# 导入类型提示
from typing import Any

# 导入日志记录器
from .utils import logger


class AgentType:
    """
    抽象类，用于重新实现以定义智能体可以返回的类型。

    这些对象有三个目的：

    - 它们表现的得像它们意图表示的类型，例如，文本的字符串，图像的 PIL.Image.Image
    - 它们可以被字符串化：str(object) 以返回定义对象的字符串
    - 它们应该在 ipython notebooks/colab/jupyter 中正确显示
    """

    def __init__(self, value):
        """初始化智能体类型
        
        Args:
            value: 要包装的值
        """
        self._value = value

    def __str__(self):
        """返回对象的字符串表示"""
        return self.to_string()

    def to_raw(self):
        """返回原始值
        
        Returns:
            包装的原始值
        """
        logger.error(
            "这是一个未知类型的原始 AgentType。在笔记本中的显示和字符串转换将不可靠"
        )
        return self._value

    def to_string(self) -> str:
        """返回对象的字符串表示
        
        Returns:
            对象的字符串表示
        """
        logger.error(
            "这是一个未知类型的原始 AgentType。在笔记本中的显示和字符串转换将不可靠"
        )
        return str(self._value)


class AgentText(AgentType, str):
    """
    智能体返回的文本类型。表现得像一个字符串。
    """

    def to_raw(self):
        """返回原始文本值
        
        Returns:
            原始文本字符串
        """
        return self._value

    def to_string(self):
        """返回文本的字符串表示
        
        Returns:
            文本字符串
        """
        return str(self._value)

# 智能体类型映射字典
_AGENT_TYPE_MAPPING = {"string": AgentText}

def handle_agent_output_types(output: Any, output_type: str | None = None) -> Any:
    """处理智能体输出类型
    
    根据指定的输出类型或者自动推断的类型，将输出转换为适当的 AgentType 子类。
    
    Args:
        output: 要处理的输出值
        output_type: 指定的输出类型，可选
        
    Returns:
        处理后的输出，可能是AgentType子类实例
    """
    if output_type in _AGENT_TYPE_MAPPING:
        # 如果类已定义输出，我们可以根据类定义直接映射
        decoded_outputs = _AGENT_TYPE_MAPPING[output_type](output)
        return decoded_outputs

    # 如果类没有定义输出，那么我们根据类型进行映射
    if isinstance(output, str):
        return AgentText(output)
    return output
