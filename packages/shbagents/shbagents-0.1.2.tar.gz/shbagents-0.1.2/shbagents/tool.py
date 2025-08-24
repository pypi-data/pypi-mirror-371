# 导入检查函数的模块，用于获取函数签名信息
import inspect
# 导入类型提示相关功能
from typing import get_type_hints, Optional


class Tool:
    """
    一个工具的类，用于包装函数并提供工具的文本描述
    
    属性:
        name (str): 工具的名称
        description (str): 工具功能的文本描述
        func (callable): 该工具包装的函数
        arguments (list): 参数列表
        outputs (str or list): 被包装函数的返回类型
    """
    def __init__(self, 
                 name: str,           # 工具名称
                 description: str,    # 工具描述
                 arguments: list,     # 参数列表
                 outputs: str,        # 输出类型
                 func: Optional[callable] = None, # 可调用的函数对象
    ):      
        """
        初始化工具对象
        """
        self.name = name                # 设置工具名称
        self.description = description  # 设置工具描述
        self.func = func                # 设置被包装的函数
        self.arguments = arguments      # 设置参数列表
        self.outputs = outputs          # 设置输出类型

    def to_string(self) -> str:
        """
        返回工具的字符串表示形式，
        包括工具名称、描述、参数和输出类型
        """
        # 将参数列表转换为字符串格式：参数名: 参数类型
        args_str = ", ".join([
            f"{arg_name}: {arg_type}" 
            for arg_name, arg_type 
            in self.arguments
        ])
        
        # 返回格式化的工具信息字符串
        return (
            f"工具名称: {self.name},"          # 工具名称
            f" 描述: {self.description}," # 工具描述
            f" 参数: {args_str},"          # 参数信息
            f" 输出: {self.outputs}"         # 输出类型
        )

    def __call__(self, *args, **kwargs):
        """
        使工具对象可以像函数一样被调用
        将提供的参数传递给底层函数并执行
        """
        # 调用被包装的函数并返回结果
        return self.func(*args, **kwargs)


def tool(func):
    """
    装饰器：将函数自动转换为 Tool 实例
    """
    # 1. 获取函数签名信息（参数名、默认值等）
    sig = inspect.signature(func)
    
    # 2. 获取函数的类型提示信息
    type_hints = get_type_hints(func)
    
    # 3. 提取参数信息
    arguments = []
    for param_name, param in sig.parameters.items():
        # 从类型提示中获取参数类型，如果没有则默认为 'any'
        param_type = type_hints.get(param_name, 'any')
        
        # 处理类型名称的显示
        if hasattr(param_type, '__name__'):
            type_str = param_type.__name__  # 如：int, str, float
        else:
            type_str = str(param_type)      # 如：List[int], Optional[str]
        
        # 添加到参数列表：(参数名, 参数类型)
        arguments.append((param_name, type_str))
    
    # 4. 提取返回类型信息
    return_type = type_hints.get('return', 'any')
    if hasattr(return_type, '__name__'):
        output_str = return_type.__name__
    else:
        output_str = str(return_type)
    
    # 5. 提取函数的文档字符串作为描述
    description = func.__doc__.strip() if func.__doc__ else "没有提供描述"
    
    # 6. 创建 Tool 实例
    tool_instance = Tool(
        name=func.__name__,         # 函数名作为工具名
        description=description,     # 文档字符串作为描述
        func=func,                  # 原始函数
        arguments=arguments,        # 自动提取的参数信息
        outputs=output_str          # 自动提取的返回类型
    )
    
    # 7. 将 Tool 实例存储在函数属性上
    func._tool_instance = tool_instance      # 存储 Tool 实例
    func.to_string = tool_instance.to_string # 添加信息展示方法
    func.__call__ = tool_instance.__call__   # 保持可调用性
    
    # 8. 返回增强后的函数
    return func