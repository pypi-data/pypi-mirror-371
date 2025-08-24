
from typing import Any
from .tool import Tool


class FinalAnswerTool(Tool):
    """最终答案工具类
    
    这是一个特殊的工具，用于智能体提供最终答案。
    当智能体完成任务并准备给出最终结果时，会调用此工具。
    """
    
    def __init__(self):
        """初始化最终答案工具"""
        super().__init__(
            name="final_answer",
            description="为所给问题提供最终答案.",
            arguments=[("answer", "any")],  # 参数列表格式：(参数名, 参数类型)
            outputs="any",
            func=self.forward
        )

    def forward(self, answer: Any) -> Any:
        """执行最终答案工具
        
        Args:
            answer: 最终答案内容，可以是任何类型
            
        Returns:
            原样返回答案内容
        """
        return answer