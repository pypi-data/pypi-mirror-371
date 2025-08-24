"""
Базовые тесты для DurusAI CLI
"""
import pytest
import sys
from pathlib import Path

# Добавляем путь к пакету
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_import():
    """Тест импорта основных модулей"""
    # Основной пакет
    import durusai
    assert durusai.__version__ is not None
    
    # Основные компоненты
    from durusai import Config, AuthManager, DurusAIClient
    
    # Проверяем что классы определены
    assert Config is not None
    assert AuthManager is not None  
    assert DurusAIClient is not None

def test_config_creation():
    """Тест создания конфигурации"""
    from durusai import Config
    
    config = Config()
    assert config is not None
    assert config.get_api_endpoint() is not None
    assert config.get_default_profile() is not None

def test_version():
    """Тест версии"""
    import durusai
    
    version = durusai.__version__
    assert isinstance(version, str)
    assert len(version.split('.')) >= 2  # Минимум X.Y

def test_cli_entry_point():
    """Тест что CLI entry point определен"""
    try:
        from durusai.cli import main
        assert main is not None
        assert callable(main)
    except ImportError:
        pytest.fail("CLI entry point not found")

def test_api_client_creation():
    """Тест создания API клиента"""
    from durusai import DurusAIClient, Config
    
    config = Config()
    client = DurusAIClient(config)
    
    assert client is not None
    assert client.base_url is not None
    assert client.timeout > 0