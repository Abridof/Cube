# AI Cognition Engine Makefile
# 提供常用的开发、测试和构建命令

.PHONY: help install dev test lint format clean build docs run-examples structure verify

help:
@echo "AI Cognition Engine - 可用命令:"
@echo ""
@echo "  install       安装生产依赖"
@echo "  dev           安装开发依赖"
@echo "  test          运行测试"
@echo "  test-cov      运行测试并生成覆盖率报告"
@echo "  lint          运行代码检查"
@echo "  format        格式化代码"
@echo "  type-check    运行类型检查"
@echo "  clean         清理构建文件"
@echo "  build         构建分发包"
@echo "  verify        验证项目结构"

install:
pip install -e .

dev:
pip install -e ".[dev]"

test:
pytest tests/ -v

test-cov:
pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

lint:
flake8 src/ tests/ --max-line-length=100 --ignore=E501,W503

format:
black src/ tests/ --line-length=100

type-check:
mypy src/ --ignore-missing-imports

clean:
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} +
rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

build:
python -m build

docs:
@echo "文档生成功能待实现..."

verify:
@echo "验证项目结构..."
@test -d src/core && echo "OK: src/core 存在" || echo "FAIL: src/core 缺失"
@test -d src/modules && echo "OK: src/modules 存在" || echo "FAIL: src/modules 缺失"
@test -d src/utils && echo "OK: src/utils 存在" || echo "FAIL: src/utils 缺失"
@test -d src/experiments && echo "OK: src/experiments 存在" || echo "FAIL: src/experiments 缺失"
@test -d tests && echo "OK: tests 存在" || echo "FAIL: tests 缺失"
@test -f pyproject.toml && echo "OK: pyproject.toml 存在" || echo "FAIL: pyproject.toml 缺失"
@echo "验证完成!"
