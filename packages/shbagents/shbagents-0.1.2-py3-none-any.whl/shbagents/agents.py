
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time
from typing import Any, Callable, Generator, Literal
import warnings

from rich.text import Text

# 导入智能体类型处理函数
from .agent_types import handle_agent_output_types
# 导入内存相关类和步骤类
from .memory import ActionStep, AgentMemory, FinalAnswerStep, PlanningStep, SystemPromptStep, TaskStep, ToolCall, ToolOutput
# 导入模型相关类
from .model import ChatMessage, ChatMessageStreamDelta, Model
# 导入监控和日志相关
from .monitoring import YELLOW_HEX, AgentLogger
# 导入提示模板相关
from .prompt import PromptTemplates, get_react_default_prompt_templates, populate_template
# 导入默认工具
from .default_tools import FinalAnswerTool
# 导入工具基类
from .tool import Tool
# 导入工具函数和异常类
from .utils import AgentError, AgentExecutionError, AgentGenerationError, AgentMaxStepsError, AgentParsingError


@dataclass
class ActionOutput:
    """动作输出数据类
    
    Attributes:
        output: 输出内容
        is_final_answer: 是否为最终答案
    """
    output: Any
    is_final_answer: bool


@dataclass
class RunResult:
    """
    持有关于代理运行的扩展信息。

    Attributes:
        output (Any | None): 代理运行的最终输出，如果可用。
        state (Literal["success", "max_steps_error"]): 代理运行后的最终状态。
        steps (list[dict]): 代理的记忆，作为步骤列表。
        token_usage (TokenUsage | None): 运行期间使用的令牌数量。
        timing (Timing): 代理运行的计时细节：开始时间、结束时间、持续时间。
        messages (list[dict]): 代理的记忆，作为消息列表。
    """

    output: Any | None
    state: Literal["success", "max_steps_error"]
    steps: list[dict]

    def __init__(self, output=None, state=None, steps=None, token_usage=None, timing=None, messages=None):
        # 处理已弃用的 'messages' 参数
        if messages is not None:
            if steps is not None:
                raise ValueError("不能同时指定 'messages' 和 'steps' 参数。请使用 'steps' 参数。")
            steps = messages

        # 字段初始化
        self.output = output
        self.state = state
        self.steps = steps
        self.token_usage = token_usage
        self.timing = timing


class MultiStepAgent(ABC):
    """多步骤智能体抽象基类
    
    这是一个抽象基类，用于实现能够执行多个步骤来完成任务的智能体。
    智能体可以使用工具、模型和提示模板来解决复杂任务。
    
    Attributes:
        tools: 智能体可用的工具列表
        model: 用于生成响应的模型
        prompt_templates: 提示模板
        instructions: 智能体指令
        max_steps: 最大执行步数
        name: 智能体名称
        description: 智能体描述
        memory: 智能体内存
    """
  
    def __init__(
            self,
            tools: list[Tool],
            model: Model,
            prompt_templates: PromptTemplates | None = None,
            instructions: str | None = None,
            max_steps: int = 20,
            name: str | None = None,
            description: str | None = None,
            logger: AgentLogger | None = None,
        ):
        """初始化多步骤智能体
        
        Args:
            tools: 智能体可用的工具列表
            model: 用于生成响应的模型
            prompt_templates: 提示模板，可选
            instructions: 智能体指令，可选
            max_steps: 最大执行步数，默认20
            name: 智能体名称，可选
            description: 智能体描述，可选
            logger: 日志记录器，可选
        """
        self.tools = tools
        self.model = model
        self.prompt_templates = prompt_templates
        self.instructions = instructions
        self.max_steps = max_steps
        self.name = name
        self.description = description
        self.memory = AgentMemory(self.system_prompt)
        self.logger = logger or AgentLogger()
        self.interrupt_switch = False  # 初始化中断开关

    @property
    def system_prompt(self) -> str:
        """获取系统提示
        
        Returns:
            系统提示字符串
        """
        return self.initialize_system_prompt()
    
    @abstractmethod
    def initialize_system_prompt(self) -> str:
        """在子类中实现"""
        pass
    
    def run(
            self,
            task: str,
            stream: bool = False,
            reset: bool = True,
            max_steps: int | None = None,
            return_full_result: bool | None = None,
        ) -> Any | RunResult:
            """
            为给定任务运行代理。

            Args:
                task: 任务。
                stream (`bool`): 是否以流模式运行。
                    如果为 `True`，返回一个生成器，在执行每个步骤时产出该步骤。你必须迭代这个生成器来处理各个步骤（例如，使用 for 循环或 `next()`）。
                    如果为 `False`，内部执行所有步骤，完成后只返回最终答案。
                reset (`bool`): 是否重置对话或从上次运行继续。
                additional_args (`dict`, *可选*): 你想传递给代理运行的任何其他变量，例如图像或数据框。给它们清晰的名称！
                max_steps (`int`, *可选*): 代理解决任务可以采取的最大步骤数。如果未提供，将使用代理的默认值。
                return_full_result (`bool`, *可选*): 是否返回完整的 [`RunResult`] 对象或只返回最终答案输出。
                    如果为 `None`（默认），使用代理的 `self.return_full_result` 设置。

            示例:
            ```py
            from shbagents import Agent
            agent = Agent(tools=[])
            agent.run(" 2 的 3.7384 次方的结果是什么？")
            ```
            """
            max_steps = max_steps or self.max_steps
            self.task = task

            self.memory.system_prompt = SystemPromptStep(system_prompt=self.system_prompt)
            if reset:
                self.memory.reset()

            name = self.name if hasattr(self, "name") else None
            model_name = self.model.model_id if hasattr(self.model, 'model_id') else ''
            self.logger.log_task(
                content=self.task.strip(),
                subtitle=f"{type(self.model).__name__} - {model_name}",
                title=name,
            )
            self.logger.log_messages(messages=self.memory.get_full_steps())
            self.memory.steps.append(TaskStep(task=self.task))

            if getattr(self, "python_executor", None):
                self.python_executor.send_variables(variables=self.state)
                self.python_executor.send_tools({**self.tools, **self.managed_agents})

            if stream:
                # 步骤通过生成器在执行时返回以供迭代。
                return self._run_stream(task=self.task, max_steps=max_steps)
            
            # 输出仅在最后一步返回。我们只查看最后一步。
            steps = list(self._run_stream(task=self.task, max_steps=max_steps))
            assert isinstance(steps[-1], FinalAnswerStep)
            output = steps[-1].output

            return_full_result = return_full_result if return_full_result is not None else self.return_full_result
            # 返回完整结果
            if return_full_result:
                last_step = self.memory.steps[-1]
                last_step_error = getattr(last_step, "error", None)
                if self.memory.steps and isinstance(last_step_error, AgentMaxStepsError):
                    state = "max_steps_error"
                else:
                    state = "success"
                
                step_dicts = self.memory.get_full_steps()

                return RunResult(
                    output=output,
                    steps=step_dicts,
                    state=state,
                )

            return output
    
    def _run_stream(self, task: str, max_steps: int) -> Generator[ActionStep | PlanningStep | FinalAnswerStep | ChatMessageStreamDelta, None, None]:
        """流式运行智能体
        
        Args:
            task: 任务描述
            max_steps: 最大步骤数
            
        Yields:
            智能体执行的各个步骤
        """
        self.step_number = 1
        returned_final_answer = False
        while not returned_final_answer and self.step_number <= max_steps:

            if self.interrupt_switch:
                raise AgentError("智能体被中断。", self.logger)

            # 开始动作步骤！
            action_step = ActionStep(
                step_number=self.step_number
            )
            # 记录步骤开始
            self.logger.log_rule(f"步骤 {self.step_number}")
            self.logger.log(Text(f"🤖 智能体正在思考和决策...", style="dim"))
            # 流式生成输出
            try:
                for output in self._step_stream(action_step):
                    # 产出所有结果
                    yield output
                    # 如果输出是最终答案，则记录最终答案
                    if isinstance(output, ActionOutput) and output.is_final_answer:
                        final_answer = output.output
                        self.logger.log(
                            Text(f"最终答案: {final_answer}", style=f"bold {YELLOW_HEX}"),
                        )
                        returned_final_answer = True
                        action_step.is_final_answer = True
            
            except AgentGenerationError as exception:
                # 智能体生成错误不是由模型错误引起的，而是实现错误：所以我们应该抛出它们并退出。
                raise exception
            except AgentError as exception:
                # 其他 AgentError 类型是由模型引起的，所以我们应该记录它们并迭代。
                action_step.error = exception
            finally:
                self._finalize_step(action_step)
                self.memory.steps.append(action_step)
                yield action_step
                self.step_number += 1

        if not returned_final_answer and self.step_number == max_steps + 1:
            final_answer = self._handle_max_steps_reached(task)
            yield action_step
        yield FinalAnswerStep(handle_agent_output_types(final_answer))
    
    def _step_stream(self, memory_step: ActionStep) -> Generator[ChatMessageStreamDelta | ToolCall | ToolOutput | ActionOutput, None, None]:
        """
        在 ReAct 框架中执行一个步骤：智能体思考、行动并观察结果。
        如果启用了流式传输，在运行期间产出 ChatMessageStreamDelta。
        最后，如果步骤不是最终步骤则产出 None，否则产出最终答案。
        
        Args:
            memory_step: 内存步骤
            
        Yields:
            聊天消息流增量、工具调用、工具输出或动作输出
        """
        raise NotImplementedError("此方法应在子类中实现")

    

    def interrupt(self):
        """中断智能体执行"""
        self.interrupt_switch = True
    
    def _finalize_step(self, memory_step: ActionStep | PlanningStep):
        """
        完成步骤
        
        Args:
            memory_step: 内存步骤
        """
        pass
    
    def _handle_max_steps_reached(self, task: str) -> Any:
        """处理达到最大步骤数的情况
        
        Args:
            task: 任务描述
            
        Returns:
            最终答案内容
        """
        # 获取智能体提供的最终答案
        final_answer = self.provide_final_answer(task)
        # 创建最终内存步骤，标记为达到最大步骤数错误
        final_memory_step = ActionStep(
            step_number=self.step_number,
            error=AgentMaxStepsError("达到最大步骤数。", self.logger),
        )
        # 设置动作输出为最终答案内容
        final_memory_step.action_output = final_answer.content
        # 完成步骤处理
        self._finalize_step(final_memory_step)
        # 将步骤添加到内存中
        self.memory.steps.append(final_memory_step)
        # 返回最终答案内容
        return final_answer.content
    
    def provide_final_answer(self, task: str) -> ChatMessage:
        """提供最终答案
        
        Args:
            task: 任务描述
            
        Returns:
            包含最终答案的聊天消息
        """
        from .model import MessageRole
        return ChatMessage(
            role=MessageRole.ASSISTANT,
            content="由于达到最大步骤数限制，无法继续执行任务。"
        )
    
    def write_memory_to_messages(self,) -> list[ChatMessage]:
        """
        从内存中读取过去的 LLM 输出、动作和观察或错误，转换为一系列消息，
        可用作 LLM 的输入。添加一些关键词（如PLAN、error等）来帮助 LLM。
        """
        messages = self.memory.system_prompt.to_messages()
        for memory_step in self.memory.steps:
            messages.extend(memory_step.to_messages())
        return messages


class Agent(MultiStepAgent):
    """
    在此智能体中，工具调用将由LLM以代码格式制定，然后解析并执行。

    Args:
        tools (`list[Tool]`): 智能体可以使用的工具列表。
        model (`Model`): 用于生成智能体动作的模型。
        prompt_templates ([`~agents.PromptTemplates`], *可选*): 提示模板。

        **kwargs: 其他关键字参数。
    """

    def __init__(
        self,
        tools: list[Tool],
        model: Model,
        prompt_templates: PromptTemplates | None = None,
        add_base_tools: bool = True,
        **kwargs,
    ):
        # 处理工具列表，支持 @tool 装饰的函数和 Tool 对象混合
        processed_tools = []
        for tool in tools:
            if hasattr(tool, '_tool_instance'):
                # 这是一个被 @tool 装饰的函数，提取 Tool 实例
                processed_tools.append(tool._tool_instance)
            elif isinstance(tool, Tool):
                # 这是一个 Tool 对象，直接使用
                processed_tools.append(tool)
            else:
                raise ValueError(f"tools 列表中的项必须是 Tool 对象或被 @tool 装饰的函数，但收到: {type(tool)}")
        
        # 处理基础工具
        if add_base_tools:
            base_tools = [FinalAnswerTool()]
            processed_tools = processed_tools + base_tools
        
        tools = processed_tools
        
        # 设置默认提示模板
        if prompt_templates is None:
            prompt_templates = get_react_default_prompt_templates()
        
        super().__init__(
            tools=tools,
            model=model,
            prompt_templates=prompt_templates,
            **kwargs,
        )
        self.return_full_result = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    def cleanup(self):
        pass

    def initialize_system_prompt(self) -> str:
        system_prompt = populate_template(
            self.prompt_templates["system_prompt"],
            variables={
                "tools": [tool.to_string() for tool in self.tools],
                "custom_instructions": self.instructions
            },
        )
        return system_prompt

    def _step_stream(self, memory_step: ActionStep) -> Generator[ChatMessageStreamDelta | ToolCall | ToolOutput | ActionOutput, None, None]:
        """
        在 ReAct 框架中执行一个步骤：智能体思考、行动并观察结果。
        如果启用了流式传输，在运行期间产出 ChatMessageStreamDelta。
        最后，如果步骤不是最终步骤则产出 None，否则产出最终答案。
        """
        # 将内存转换为消息列表
        memory_messages = self.write_memory_to_messages()

        input_messages = memory_messages.copy()
        # 生成模型输出
        memory_step.model_input_messages = input_messages
        stop_sequences = ["Observation:", "Calling tools:"]

        try:
            additional_args: dict[str, Any] = {}
            chat_message: ChatMessage = self.model.generate(
                input_messages,
                stop=stop_sequences,
                **additional_args,
            )
            memory_step.model_output_message = chat_message
            output_text = chat_message.content
            memory_step.model_output = output_text
        except Exception as e:
            error_msg = f"生成模型输出时发生错误: \n {e}"
            self.logger.log_error(error_msg)
            raise AgentGenerationError(error_msg) from e

        # 解析文本中的工具调用
        tool_call_result = self._parse_and_execute_tool_call(output_text, memory_step)
        if tool_call_result:
            yield tool_call_result
            return

        # 如果没有工具调用，则视为文本响应
        if output_text:
            self.logger.log(Text(f"💭 智能体回应: {output_text}", style="dim"))
        
        observation = "执行日志:\n" + (output_text or "")
        memory_step.observations = observation
        memory_step.action_output = output_text
        
        yield ActionOutput(output=output_text, is_final_answer=False)

    def _parse_and_execute_tool_call(self, text: str, memory_step: ActionStep) -> ActionOutput | None:
        """解析文本中的工具调用并执行
        
        Args:
            text: 模型输出的文本
            memory_step: 当前内存步骤
            
        Returns:
            ActionOutput 如果找到并执行了工具调用，否则返回 None
        """
        if not text:
            return None
            
        import re
        
        # 提取思考部分
        thinking_match = re.search(r'思考[:：]\s*(.*?)(?=调用工具[:：]|$)', text, re.DOTALL)
        if thinking_match:
            thinking = thinking_match.group(1).strip()
            if thinking:
                self.logger.log(Text(f"💭 智能体思考: {thinking}", style="cyan"))
        
        # 提取工具调用 - 支持多种格式
        tool_call_patterns = [
            r'调用工具[:：]?\s*(\w+)\s*\((.*?)\)',
            r'调用\s+(\w+)\s*\((.*?)\)',
            r'执行\s*(\w+)\s*\((.*?)\)',
            r'已使用工具\s+(\w+)\s*\((.*?)\)',  # 已使用工具 compare_numbers(...)
            r'使用工具\s+(\w+)\s*\((.*?)\)',   # 使用工具 compare_numbers(...)
            r'工具调用[:：]\s*(\w+)\s*\((.*?)\)',  # 工具调用: compare_numbers(...)
        ]
        
        # 特殊处理：如果模型说"最终答案"，自动调用final_answer工具
        if "最终答案" in text and "调用工具" not in text:
            # 提取最终答案内容
            final_answer_match = re.search(r'最终答案[:：]\s*(.*?)(?:\n|$)', text)
            if final_answer_match:
                answer_content = final_answer_match.group(1).strip()
                self.logger.log(Text(f"🎯 检测到最终答案，自动调用final_answer工具", style=f"bold green"))
                
                # 查找final_answer工具
                tool = next((t for t in self.tools if t.name == "final_answer"), None)
                if tool:
                    try:
                        tool_result = tool.func(answer=answer_content)
                        self.logger.log(Text(f"✅ 最终答案: {tool_result}", style=f"bold {YELLOW_HEX}"))
                        
                        observation = f"工具执行结果:\n工具: final_answer\n参数: {{'answer': '{answer_content}'}}\n结果: {tool_result}"
                        memory_step.observations = observation
                        memory_step.action_output = tool_result
                        memory_step.tool_calls = [ToolCall(
                            name="final_answer",
                            arguments={'answer': answer_content},
                            id=f"final_answer_{self.step_number}"
                        )]
                        
                        return ActionOutput(output=tool_result, is_final_answer=True)
                    except Exception as e:
                        self.logger.log_error(f"自动调用final_answer工具时发生错误: {e}")
        
        tool_call_match = None
        for pattern in tool_call_patterns:
            tool_call_match = re.search(pattern, text)
            if tool_call_match:
                break
                
        if not tool_call_match:
            # 智能检测：如果提到工具名但没有标准格式，尝试智能提取
            for tool in self.tools:
                if tool.name in text and tool.name != "final_answer":
                    # 尝试从文本中提取参数
                    numbers = re.findall(r'[-+]?\d*\.?\d+', text)
                    if tool.name == "compare_numbers" and len(numbers) >= 2:
                        self.logger.log(Text(f"🔧 检测到工具提及，智能执行: {tool.name}", style=f"bold blue"))
                        
                        tool_args = {'a': float(numbers[0]), 'b': float(numbers[1])}
                        
                        try:
                            tool_result = tool.func(**tool_args)
                            self.logger.log(Text(f"📤 工具结果: {tool_result}", style="cyan"))
                            
                            observation = f"工具执行结果:\n工具: {tool.name}\n参数: {tool_args}\n结果: {tool_result}"
                            memory_step.observations = observation
                            memory_step.action_output = tool_result
                            memory_step.tool_calls = [ToolCall(
                                name=tool.name,
                                arguments=tool_args,
                                id=f"{tool.name}_{self.step_number}"
                            )]
                            
                            return ActionOutput(output=tool_result, is_final_answer=False)
                        except Exception as e:
                            self.logger.log_error(f"智能执行工具 {tool.name} 时发生错误: {e}")
            
            return None
            
        tool_name = tool_call_match.group(1)
        args_str = tool_call_match.group(2) if len(tool_call_match.groups()) >= 2 else ""
        
        # 解析参数
        tool_args = {}
        if args_str.strip():
            try:
                # 支持多种参数格式
                # 格式1: key=value, key=value
                arg_matches = re.findall(r'(\w+)\s*=\s*([^,]+)', args_str)
                if arg_matches:
                    for key, value in arg_matches:
                        value = value.strip().strip('"\'')
                        if value.isdigit():
                            tool_args[key] = int(value)
                        elif '.' in value and value.replace('.', '').replace('-', '').isdigit():
                            tool_args[key] = float(value)
                        else:
                            tool_args[key] = value
                else:
                    # 格式2: 尝试解析为单个参数 (对于final_answer)
                    clean_args = args_str.strip().strip('"\'')
                    if tool_name == "final_answer":
                        tool_args['answer'] = clean_args
                    elif tool_name == "compare_numbers":
                        # 尝试提取数字
                        numbers = re.findall(r'-?\d+\.?\d*', args_str)
                        if len(numbers) >= 2:
                            tool_args['a'] = float(numbers[0])
                            tool_args['b'] = float(numbers[1])
            except Exception as e:
                self.logger.log_error(f"参数解析错误: {e}")
                tool_args = {}
        
        # 查找工具
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            error_msg = f"未找到工具: {tool_name}"
            self.logger.log_error(error_msg)
            memory_step.observations = f"工具查找错误: {error_msg}"
            memory_step.action_output = error_msg
            return ActionOutput(output=error_msg, is_final_answer=False)
        
        try:
            # 显示工具调用信息
            if tool_name == "final_answer":
                self.logger.log(Text(f"🎯 提供最终答案...", style=f"bold green"))
            else:
                self.logger.log(Text(f"🔧 调用工具: {tool_name}", style=f"bold blue"))
                if tool_args:
                    args_display = ", ".join([f"{k}={v}" for k, v in tool_args.items()])
                    self.logger.log(Text(f"   参数: {args_display}", style="dim"))
            
            # 执行工具
            tool_result = tool.func(**tool_args)
            
            # 显示工具执行结果
            if tool_name == "final_answer":
                self.logger.log(Text(f"✅ 最终答案: {tool_result}", style=f"bold {YELLOW_HEX}"))
            else:
                self.logger.log(Text(f"📤 工具结果: {tool_result}", style="cyan"))
            
            # 检查是否为最终答案工具
            is_final = tool_name == "final_answer"
            
            observation = f"工具执行结果:\n工具: {tool_name}\n参数: {tool_args}\n结果: {tool_result}"
            memory_step.observations = observation
            memory_step.action_output = tool_result
            memory_step.tool_calls = [ToolCall(
                name=tool_name,
                arguments=tool_args,
                id=f"{tool_name}_{self.step_number}"
            )]
            
            return ActionOutput(output=tool_result, is_final_answer=is_final)
            
        except Exception as e:
            error_msg = f"执行工具 {tool_name} 时发生错误: {e}"
            self.logger.log_error(error_msg)
            observation = f"工具执行错误:\n工具: {tool_name}\n错误: {error_msg}"
            memory_step.observations = observation
            memory_step.action_output = error_msg
            return ActionOutput(output=error_msg, is_final_answer=False)

