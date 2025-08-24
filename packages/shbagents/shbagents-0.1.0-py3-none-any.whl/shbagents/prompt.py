
from typing import Any, TypedDict

from jinja2 import Template, StrictUndefined


class PlanningPromptTemplate(TypedDict):
    """
    规划提示词。

    参数:
        plan: 初始计划提示词。
        update_plan_pre_messages: 更新计划前消息提示词。
        update_plan_post_messages: 更新计划后消息提示词。
    """

    initial_plan: str
    update_plan_pre_messages: str
    update_plan_post_messages: str


class ManagedAgentPromptTemplate(TypedDict):
    """
    管理代理提示词。

    参数:
        task: 任务提示词。
        report: 报告提示词。
    """

    task: str
    report: str


class FinalAnswerPromptTemplate(TypedDict):
    """
    最终答案提示词。

    参数:
        pre_messages: 前消息提示词。
        post_messages: 后消息提示词。
    """

    pre_messages: str
    post_messages: str


class PromptTemplates(TypedDict):
    """
    Agent 的提示模板。

    参数:
        system_prompt: 系统提示词。
        planning: 规划提示词。
        managed_agent: 管理代理提示词。
        final_answer: 最终答案提示词。
    """

    system_prompt: str
    planning: PlanningPromptTemplate
    managed_agent: ManagedAgentPromptTemplate
    final_answer: FinalAnswerPromptTemplate


def populate_template(template: str, variables: dict[str, Any]) -> str:
    """使用变量填充Jinja2模板
    
    Args:
        template: Jinja2模板字符串
        variables: 用于填充模板的变量字典
        
    Returns:
        填充后的字符串
        
    Raises:
        Exception: 当模板渲染失败时
    """
    compiled_template = Template(template, undefined=StrictUndefined)
    try:
        return compiled_template.render(**variables)
    except Exception as e:
        raise Exception(f" Jinja 模板渲染错误: {type(e).__name__}: {e}")

def get_react_default_prompt_templates() -> PromptTemplates:
    """获取提示模板
    
    Returns:
        提示模板
    """
    return {
        "system_prompt": """你是一个有用的 AI 助手。你可以使用以下工具来帮助完成任务：
<tools>
  {{ tools }}
</tools>

<important>
重要：如果存在需要使用工具来完成任务的情况，你必须使用工具来完成任务，不能直接给出答案！如果你已经完成了任务，必须使用 final_answer 工具提供答案！
</important>

<call_tool>
调用工具的格式：

思考: [你的推理过程]
调用工具: tool_name(参数1=值1, 参数2=值2)
</call_tool>

<example>
示例对话：
用户: 9.11 比 9.8 大么？

<your_response>
你的回应：
思考: 用户询问两个数字的大小比较，我需要使用 compare_numbers 工具来比较这两个数字
调用工具: compare_numbers(a=9.11, b=9.8)
</your_response>

<tool_result>
[工具执行后，系统返回结果]
</tool_result>

<your_response>
你的下一个回应：
思考: 根据比较工具的结果，我现在可以回答用户的问题了
调用工具: final_answer(answer="不是，根据比较结果，9.11比9.8小")
</your_response>

</example>

<rules>
记住：每当你完成任务时，必须使用 final_answer 工具提供答案！

注意事项：
1. 必须先调用相关工具获取结果，再使用 final_answer 提供答案
2. 不要直接猜测或计算，一定要调用工具  
3. 格式必须完全按照示例：调用工具: tool_name(参数=值)
4. 重要：任务完成后，你必须调用 final_answer 工具，不能直接说答案
5. 如果你不调用 final_answer 工具，任务就不会结束
</rules>

""",
                "planning": {
                    "initial_plan": "制定计划来解决任务：{{ task }}",
                    "update_plan_pre_messages": "更新计划基于以下信息：",
                    "update_plan_post_messages": "请更新计划："
                },
                "managed_agent": {
                    "task": "执行任务：{{ task }}",
                    "report": "报告结果：{{ result }}"
                },
                "final_answer": {
                    "pre_messages": "基于以上信息, 如果可以回答用户的问题, 请提供最终答案",
                    "post_messages": "提供最终答案："
                }
            }