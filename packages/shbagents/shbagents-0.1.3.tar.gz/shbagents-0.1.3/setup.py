#!/usr/bin/env python3
"""
SHB Agent - 通用的多模型智能体框架
"""

from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取版本信息
def read_version():
    try:
        version_file = os.path.join(os.path.dirname(__file__), "shbagents", "_version.py")
        with open(version_file, "r", encoding="utf-8") as fh:
            version_code = fh.read()
        version_globals = {}
        exec(version_code, version_globals)
        return version_globals["__version__"]
    except Exception as e:
        # 如果读取失败，使用默认版本
        print(f"Warning: Could not read version from shbagents/_version.py: {e}")
        return "0.1.2"

# 读取 requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith('#')]

setup(
    name="shbagents",
    version=read_version(),
    author="huangbaocheng",
    author_email="huangbaocheng@example.com",  # 请替换为你的邮箱
    description="通用的多模型智能体框架，支持工具调用和多种LLM模型",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*", "examples*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
        ]
    },
    keywords=[
        "llm", "agent", "ai", "artificial-intelligence", 
        "openai", "tool-calling", "multi-model", "chatbot"
    ],
    include_package_data=True,
    zip_safe=False,
)