.PHONY: lint format isort typecheck all

lint:
	uv run flake8

format:
	uv run black src

isort:
	uv run python -m isort src

typecheck:
	uv run mypy

# Запуск всех инструментов
all: lint format isort typecheck 