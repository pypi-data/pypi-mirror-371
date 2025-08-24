# SHB Agent 🤖

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://pypi.org/project/shb-agent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/shb-agent.svg)](https://badge.fury.io/py/shb-agent)

一个通用的多模型智能体框架，支持灵活的工具调用和多种 LLM 模型。

## ✨ 特性

- 🔧 **灵活的工具系统**: 支持 `@tool` 装饰器和传统 Tool 对象
- 🤖 **多模型支持**: 支持 OpenAI、Anthropic 等多种 LLM 模型
- 📝 **通用工具调用**: 基于文本解析，不依赖特定模型的 function calling
- 📊 **丰富的日志**: 显示智能体思考过程和执行步骤
- 🔄 **智能检测**: 自动检测最终答案并结束任务
- 🎯 **易于使用**: 简洁的 API 设计

## 🚀 快速开始

### 安装

```bash
pip install shbagents
```

### 基本使用

```python
from shbagents import Agent, OpenAIModel, tool

# 使用 @tool 装饰器定义工具
@tool
def add_numbers(a: float, b: float) -> float:
    """两数相加"""
    return a + b

@tool
def compare_numbers(a: float, b: float) -> str:
    """比较两个数的大小"""
    if a > b:
        return f"{a} 比 {b} 大"
    elif a < b:
        return f"{a} 比 {b} 小"
    else:
        return f"{a} 和 {b} 相等"

# 创建模型
model = OpenAIModel(model_id="gpt-4")

# 创建智能体，直接传递装饰过的函数
agent = Agent(
    model=model,
    tools=[add_numbers, compare_numbers]
)

# 运行任务
result = agent.run("计算 3.5 + 2.7，然后比较结果与 6 的大小")
print(result)
```

### 高级使用

#### 混合工具定义

```python
from shb_agent import Agent, Tool, tool

# 方式1: @tool 装饰器
@tool
def calculate(expression: str) -> float:
    """计算数学表达式"""
    return eval(expression)  # 注意：实际使用中应该用更安全的计算方法

# 方式2: 传统 Tool 对象
def format_number(number: float) -> str:
    """格式化数字"""
    return f"{number:.2f}"

format_tool = Tool(
    name="format_number",
    description="格式化数字为两位小数",
    func=format_number,
    arguments=[("number", "float")],
    outputs="str"
)

# 混合使用两种方式
agent = Agent(
    model=model,
    tools=[
        calculate,    # @tool 装饰的函数
        format_tool   # Tool 对象
    ]
)
```

#### 自定义提示模板

```python
from shb_agent import PromptTemplates

custom_templates = {
    "system_prompt": """你是一个专业的数学助手。
    使用以下工具来帮助解决数学问题：{{ tools }}
    
    调用工具格式：
    思考: [你的推理过程]
    调用工具: tool_name(参数1=值1, 参数2=值2)
    """,
    # ... 其他模板
}

agent = Agent(
    model=model,
    tools=[calculate],
    prompt_templates=custom_templates
)
```

## 📖 详细文档

### 工具定义

#### 使用 @tool 装饰器（推荐）

```python
@tool
def search_web(query: str, max_results: int = 5) -> list:
    """搜索网页"""
    # 实际的搜索逻辑
    return ["结果1", "结果2", "结果3"]
```

#### 使用 Tool 类

```python
def search_web(query: str, max_results: int = 5) -> list:
    """搜索网页"""
    return ["结果1", "结果2", "结果3"]

search_tool = Tool(
    name="search_web",
    description="搜索网页",
    func=search_web,
    arguments=[
        ("query", "str"),
        ("max_results", "int")
    ],
    outputs="list"
)
```

### 模型支持

目前支持的模型：

- **OpenAI**: `OpenAIModel(model_id="gpt-4")`
- 更多模型支持即将推出...

### 日志系统

智能体提供详细的执行日志：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 步骤 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 智能体正在思考和决策...
💭 智能体思考: 用户需要我计算两个数字的和
🔧 调用工具: add_numbers
   参数: a=3.5, b=2.7
📤 工具结果: 6.2
```

## 🛠️ 开发

### 从源码安装

```bash
git clone https://github.com/huangbaocheng/shb-agent.git
cd shb-agent
pip install -e .
```

### 运行示例

```bash
make run-example
```

## 📋 要求

- Python 3.8+
- openai>=1.0.0
- rich>=13.0.0
- 其他依赖见 `requirements.txt`

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🔗 链接

- [GitHub 仓库](https://github.com/huangbaocheng/shb-agent)
- [PyPI 包](https://pypi.org/project/shb-agent/)
- [问题报告](https://github.com/huangbaocheng/shb-agent/issues)

## 📈 路线图

- [ ] 支持更多 LLM 模型 (Anthropic, Gemini, etc.)
- [ ] 添加流式输出支持
- [ ] 改进工具调用性能
- [ ] 添加更多内置工具
- [ ] Web UI 界面

---

如果这个项目对你有帮助，请给个 ⭐️ Star！