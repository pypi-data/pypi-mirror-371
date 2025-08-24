"""
DurusAI Native CLI Client
========================

Нативный CLI клиент для DurusAI, работающий через REST API.
Аналог OpenAI CLI и Claude CLI.

Основные возможности:
- Аутентификация и управление сессиями
- Запросы к AI через различные модели  
- Интерактивный REPL режим
- Безопасное хранение токенов
- Кроссплатформенность (Linux/Mac/Windows)

Использование:
    durusai login                    # Вход в систему
    durusai query "Your question"    # Одиночный запрос
    durusai chat                     # Интерактивный режим
    durusai logout                   # Выход
"""

__version__ = "1.0.0"
__author__ = "DurusAI Team"
__email__ = "support@durusai.com"
__license__ = "MIT"

# Экспорт основных классов для API
from .api_client import DurusAIClient
from .config import Config
from .auth import AuthManager

__all__ = [
    "DurusAIClient",
    "Config", 
    "AuthManager"
]