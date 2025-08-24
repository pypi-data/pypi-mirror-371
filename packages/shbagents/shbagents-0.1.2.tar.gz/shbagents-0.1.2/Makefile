# 安装依赖
install:
	pip install -r requirements.txt

# 运行示例
run-example:
	python example.py

# 清理构建文件
clean:
	rm -rf dist/ build/ *.egg-info/ __pycache__/ .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# 构建包
build: clean
	python -m build

# 发布补丁版本
release-patch:
	./release.sh patch

# 发布次版本  
release-minor:
	./release.sh minor

# 发布主版本
release-major:
	./release.sh major

# 发布到测试PyPI
release-test:
	./release.sh patch --test

# 模拟发布
release-dry-run:
	./release.sh patch --dry-run

# 查看当前版本
version:
	python -c "from shbagents._version import __version__; print(__version__)"

# 安装开发依赖
install-dev:
	pip install -e ".[dev]"

# 运行测试
test:
	python -c "from shbagents import Agent, OpenAIModel, tool; print('✅ 导入测试成功')"

# 帮助信息
help:
	@echo "可用命令:"
	@echo "  install        - 安装依赖"
	@echo "  run-example    - 运行示例"
	@echo "  clean          - 清理构建文件"
	@echo "  build          - 构建包"
	@echo "  version        - 查看当前版本"
	@echo "  test           - 运行基础测试"
	@echo "  release-patch  - 发布补丁版本"
	@echo "  release-minor  - 发布次版本"
	@echo "  release-major  - 发布主版本"
	@echo "  release-test   - 发布到测试PyPI"
	@echo "  release-dry-run- 模拟发布"
	@echo "  install-dev    - 安装开发依赖"

.PHONY: install run-example clean build version test help release-patch release-minor release-major release-test release-dry-run install-dev