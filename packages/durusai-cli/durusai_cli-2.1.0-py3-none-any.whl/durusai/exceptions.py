"""
Исключения для DurusAI CLI
"""


class DurusAIError(Exception):
    """Базовое исключение для DurusAI CLI"""
    pass


class DurusAIAPIError(DurusAIError):
    """Ошибка API DurusAI"""
    pass


class AuthenticationError(DurusAIAPIError):
    """Ошибка аутентификации"""
    pass


class NetworkError(DurusAIError):
    """Ошибка сети"""
    pass


class ServerError(DurusAIAPIError):
    """Ошибка сервера"""
    pass


class ValidationError(DurusAIAPIError):
    """Ошибка валидации данных"""
    pass


class ConfigurationError(DurusAIError):
    """Ошибка конфигурации"""
    pass