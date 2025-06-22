# Makefile для 3D QR Code Generator

.PHONY: help install install-dev test lint format clean build run examples

# Переменные
PYTHON := python3
PIP := pip3
VENV := venv
SRC_DIR := src
TEST_DIR := tests
OUTPUT_DIR := output

# Цвета для вывода
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Показать справку
	@echo "$(BLUE)3D QR Code Generator - Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)Доступные команды:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Установить зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(PIP) install -r requirements.txt

install-dev: ## Установить зависимости для разработки
	@echo "$(GREEN)Установка зависимостей для разработки...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov black flake8 mypy

venv: ## Создать виртуальное окружение
	@echo "$(GREEN)Создание виртуального окружения...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(YELLOW)Активируйте окружение: source $(VENV)/bin/activate$(NC)"

test: ## Запустить тесты
	@echo "$(GREEN)Запуск тестов...$(NC)"
	$(PYTHON) -m pytest $(TEST_DIR) -v

test-cov: ## Запустить тесты с покрытием
	@echo "$(GREEN)Запуск тестов с покрытием...$(NC)"
	$(PYTHON) -m pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term

lint: ## Проверить код линтером
	@echo "$(GREEN)Проверка кода линтером...$(NC)"
	$(PYTHON) -m flake8 $(SRC_DIR) main.py
	$(PYTHON) -m mypy $(SRC_DIR) main.py

format: ## Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	$(PYTHON) -m black $(SRC_DIR) main.py

format-check: ## Проверить форматирование
	@echo "$(GREEN)Проверка форматирования...$(NC)"
	$(PYTHON) -m black --check $(SRC_DIR) main.py

clean: ## Очистить временные файлы
	@echo "$(GREEN)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf $(OUTPUT_DIR)/*

build: ## Собрать пакет
	@echo "$(GREEN)Сборка пакета...$(NC)"
	$(PYTHON) -m build

run: ## Запустить с настройками по умолчанию
	@echo "$(GREEN)Запуск генератора 3D QR-кода...$(NC)"
	$(PYTHON) main.py --verbose

run-example: ## Запустить с примером синего свечения
	@echo "$(GREEN)Запуск с примером синего свечения...$(NC)"
	$(PYTHON) main.py --config settings/examples/blue_glow.json --verbose

run-neon: ## Запустить с неоновым стилем
	@echo "$(GREEN)Запуск с неоновым стилем...$(NC)"
	$(PYTHON) main.py --config settings/examples/neon_style.json --verbose

run-custom: ## Запустить с пользовательскими параметрами
	@echo "$(GREEN)Запуск с пользовательскими параметрами...$(NC)"
	$(PYTHON) main.py --text "Custom QR Code" --primary-color "#ff6600" --inner-color "#00ffff" --verbose

examples: ## Создать все примеры
	@echo "$(GREEN)Создание всех примеров...$(NC)"
	@mkdir -p $(OUTPUT_DIR)/examples
	$(PYTHON) main.py --config settings/default.json --output-dir $(OUTPUT_DIR)/examples --filename default --verbose
	$(PYTHON) main.py --config settings/examples/blue_glow.json --output-dir $(OUTPUT_DIR)/examples --filename blue_glow --verbose
	$(PYTHON) main.py --config settings/examples/neon_style.json --output-dir $(OUTPUT_DIR)/examples --filename neon_style --verbose

animation: ## Создать анимацию
	@echo "$(GREEN)Создание анимации...$(NC)"
	$(PYTHON) main.py --animation --frames 36 --verbose

demo: ## Демонстрация возможностей
	@echo "$(GREEN)Демонстрация возможностей 3D QR Generator...$(NC)"
	@mkdir -p $(OUTPUT_DIR)/demo
	$(PYTHON) main.py --text "https://github.com/denissilantev64/3Dqr" --primary-color "#0066cc" --inner-color "#ff3366" --output-dir $(OUTPUT_DIR)/demo --filename github_qr --formats png html obj --verbose
	$(PYTHON) main.py --text "Hello, 3D World!" --primary-color "#ff0066" --inner-color "#00ff66" --output-dir $(OUTPUT_DIR)/demo --filename hello_world --height 0.8 --glow-intensity 1.2 --verbose

install-system: ## Установить в систему
	@echo "$(GREEN)Установка в систему...$(NC)"
	$(PIP) install .

uninstall: ## Удалить из системы
	@echo "$(GREEN)Удаление из системы...$(NC)"
	$(PIP) uninstall 3dqr-generator

check: lint test ## Полная проверка кода

all: clean install test lint examples ## Выполнить все основные задачи

# Информация о проекте
info: ## Показать информацию о проекте
	@echo "$(BLUE)3D QR Code Generator$(NC)"
	@echo "$(YELLOW)Версия:$(NC) 1.0.0"
	@echo "$(YELLOW)Автор:$(NC) Denis Silantev"
	@echo "$(YELLOW)Лицензия:$(NC) MIT"
	@echo "$(YELLOW)Python:$(NC) $(shell $(PYTHON) --version)"
	@echo "$(YELLOW)Директория:$(NC) $(shell pwd)"

# Быстрые команды для разработки
dev-setup: venv install-dev ## Настройка окружения для разработки
	@echo "$(GREEN)Окружение для разработки готово!$(NC)"

dev-test: format lint test ## Быстрая проверка для разработки
	@echo "$(GREEN)Проверка завершена!$(NC)"