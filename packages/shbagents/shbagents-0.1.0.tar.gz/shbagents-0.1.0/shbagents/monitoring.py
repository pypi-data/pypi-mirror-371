from enum import IntEnum
import json
import re

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.rule import Rule


def escape_code_brackets(text: str) -> str:
    """转义代码段中的方括号，同时保留Rich样式标记。
    
    Args:
        text: 需要转义的文本
        
    Returns:
        转义后的文本
    """

    def replace_bracketed_content(match):
        """替换方括号内容的内部函数"""
        content = match.group(1)
        cleaned = re.sub(
            r"bold|red|green|blue|yellow|magenta|cyan|white|black|italic|dim|\s|#[0-9a-fA-F]{6}", "", content
        )
        return f"\\[{content}\\]" if cleaned.strip() else f"[{content}]"

    return re.sub(r"\[([^\]]*)\]", replace_bracketed_content, text)


class LogLevel(IntEnum):
    """日志级别枚举"""
    OFF = -1  # 无输出
    ERROR = 0  # 仅错误
    INFO = 1  # 正常输出（默认）
    DEBUG = 2  # 详细输出


YELLOW_HEX = "#d4b702"  # 黄色十六进制颜色值

class AgentLogger:
    """智能体日志记录器
    
    用于记录和显示智能体运行过程中的各种信息，支持不同的日志级别和丰富的输出格式。
    
    Attributes:
        level: 日志级别
        console: Rich控制台实例
    """
    
    def __init__(self, level: LogLevel = LogLevel.INFO, console: Console | None = None):
        """初始化智能体日志记录器
        
        Args:
            level: 日志级别，默认为INFO
            console: Rich控制台实例，如果为None则创建新实例
        """
        self.level = level
        if console is None:
            self.console = Console(highlight=False)
        else:
            self.console = console

    def log(self, *args, level: int | str | LogLevel = LogLevel.INFO, **kwargs) -> None:
        """向控制台记录消息

        Args:
            *args: 要记录的消息参数
            level: 日志级别，默认为INFO
            **kwargs: 其他传递给console.print的参数
        """
        if isinstance(level, str):
            level = LogLevel[level.upper()]
        if level <= self.level:
            self.console.print(*args, **kwargs)

    def log_error(self, error_message: str) -> None:
        """记录错误消息
        
        Args:
            error_message: 错误消息内容
        """
        self.log(escape_code_brackets(error_message), style="bold red", level=LogLevel.ERROR)

    def log_rule(self, title: str, level: int = LogLevel.INFO) -> None:
        """记录分隔线规则
        
        Args:
            title: 分隔线标题
            level: 日志级别
        """
        self.log(
            Rule(
                "[bold]" + title,
                characters="━",
                style=YELLOW_HEX,
            ),
            level=level
        )

    def log_task(self, content: str, subtitle: str, title: str | None = None, level: LogLevel = LogLevel.INFO) -> None:
        """记录任务信息面板
        
        Args:
            content: 任务内容
            subtitle: 副标题
            title: 主标题，可选
            level: 日志级别
        """
        self.log(
            Panel(
                f"\n[bold]{escape_code_brackets(content)}\n",
                title="[bold]新运行" + (f" - {title}" if title else ""),
                subtitle=subtitle,
                border_style=YELLOW_HEX,
                subtitle_align="left",
            ),
            level=level,
        )

    def log_messages(self, messages: list[dict], level: LogLevel = LogLevel.DEBUG) -> None:
        """记录消息列表
        
        Args:
            messages: 要记录的消息列表
            level: 日志级别，默认为DEBUG
        """
        messages_as_string = "\n".join([json.dumps(dict(message), indent=4) for message in messages])
        self.log(
            Syntax(
                messages_as_string,
                lexer="markdown",
                theme="github-dark",
                word_wrap=True,
            ),
            level=level,
        )