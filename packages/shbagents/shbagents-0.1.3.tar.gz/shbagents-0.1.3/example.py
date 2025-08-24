from shbagents import Agent, OpenAIModel, tool

@tool
def compare_numbers_tool(a: float, b: float) -> str:
    """比较两个数的大小"""
    if a > b:
        return f"{a} 比 {b} 大"
    elif a < b:
        return f"{a} 比 {b} 小"
    else:
        return f"{a} 和 {b} 相等"

model = OpenAIModel(
    model_id="openai/gpt-5",
    api_key="你的 api_key"
)

agent = Agent(
    model=model,
    tools=[
        compare_numbers_tool
    ]
)

agent.run("9.11 比 9.8 大么, 请使用工具比较")