"""
Конфигурация и настройки для DurusAI CLI
"""
import os
import json
import keyring
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet


class Config:
    """Менеджер конфигурации DurusAI CLI"""
    
    def __init__(self):
        # Определяем директорию конфигурации
        self.config_dir = Path.home() / ".durusai"
        self.config_file = self.config_dir / "config.json"
        self.profiles_dir = self.config_dir / "profiles"
        self.cache_dir = self.config_dir / "cache"
        self.history_dir = self.config_dir / "history"
        self.logs_dir = self.config_dir / "logs"
        
        # Создаем директории если их нет
        for directory in [self.config_dir, self.profiles_dir, self.cache_dir, 
                         self.history_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True, parents=True)
        
        # Инициализируем шифрование для токенов
        self._init_encryption()
        
        # Загружаем конфигурацию
        self.config = self._load_config()
    
    def _init_encryption(self):
        """Инициализация системы шифрования токенов"""
        try:
            # Пытаемся получить ключ из системного keyring
            encryption_key = keyring.get_password("durusai-cli", "encryption_key")
            
            if not encryption_key:
                # Генерируем новый ключ
                key = Fernet.generate_key()
                encryption_key = key.decode()
                keyring.set_password("durusai-cli", "encryption_key", encryption_key)
            
            self.fernet = Fernet(encryption_key.encode())
            
        except Exception as e:
            # Fallback - сохраняем ключ в файле (менее безопасно)
            key_file = self.config_dir / ".encryption_key"
            
            if key_file.exists():
                encryption_key = key_file.read_text().strip()
            else:
                key = Fernet.generate_key()
                encryption_key = key.decode()
                key_file.write_text(encryption_key)
                key_file.chmod(0o600)  # Только владелец может читать
            
            self.fernet = Fernet(encryption_key.encode())
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Ошибка загрузки конфига: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Конфигурация по умолчанию"""
        return {
            "version": "1.0.0",
            "api_endpoint": "http://localhost:15080",
            "default_profile": "default",
            "settings": {
                "timeout": 30,
                "retry_count": 3,
                "stream_responses": True,
                "cache_ttl": 3600,
                "auto_update": True,
                "show_token_usage": True,
                "default_model": "durusai",
                "max_history_size": 1000
            },
            "display": {
                "use_colors": True,
                "show_timestamps": False,
                "markdown_rendering": True,
                "pager_enabled": True
            }
        }
    
    def save(self):
        """Сохранить конфигурацию в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"❌ Ошибка сохранения конфига: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение конфигурации"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Установить значение конфигурации"""
        keys = key.split('.')
        config = self.config
        
        # Навигация до предпоследнего ключа
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # Установка значения
        config[keys[-1]] = value
        self.save()
    
    def get_api_endpoint(self) -> str:
        """Получить API endpoint"""
        return self.get("api_endpoint", "http://localhost:8080")
    
    def set_api_endpoint(self, endpoint: str):
        """Установить API endpoint"""
        self.set("api_endpoint", endpoint)
    
    def encrypt_token(self, token: str) -> str:
        """Зашифровать токен"""
        return self.fernet.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Расшифровать токен"""
        return self.fernet.decrypt(encrypted_token.encode()).decode()
    
    def save_token(self, profile: str, access_token: str, refresh_token: Optional[str] = None):
        """Безопасно сохранить токены"""
        try:
            # Используем keyring для максимальной безопасности
            keyring.set_password("durusai-cli", f"{profile}_access", access_token)
            
            if refresh_token:
                keyring.set_password("durusai-cli", f"{profile}_refresh", refresh_token)
                
        except Exception as e:
            # Fallback - зашифрованное хранение в файле
            profile_file = self.profiles_dir / f"{profile}.json"
            profile_data = {}
            
            if profile_file.exists():
                try:
                    with open(profile_file, 'r') as f:
                        profile_data = json.load(f)
                except:
                    profile_data = {}
            
            profile_data.update({
                "access_token_encrypted": self.encrypt_token(access_token),
                "refresh_token_encrypted": self.encrypt_token(refresh_token) if refresh_token else None,
                "last_updated": str(Path().cwd())  # timestamp будет добавлен в следующих версиях
            })
            
            with open(profile_file, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            profile_file.chmod(0o600)  # Только владелец может читать
    
    def get_token(self, profile: str) -> Optional[str]:
        """Получить access токен для профиля"""
        try:
            # Сначала пробуем keyring
            token = keyring.get_password("durusai-cli", f"{profile}_access")
            if token:
                return token
                
        except Exception:
            pass
        
        # Fallback - расшифровываем из файла
        profile_file = self.profiles_dir / f"{profile}.json"
        if profile_file.exists():
            try:
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
                
                encrypted_token = profile_data.get("access_token_encrypted")
                if encrypted_token:
                    return self.decrypt_token(encrypted_token)
                    
            except Exception:
                pass
        
        return None
    
    def get_refresh_token(self, profile: str) -> Optional[str]:
        """Получить refresh токен для профиля"""
        try:
            # Сначала пробуем keyring
            token = keyring.get_password("durusai-cli", f"{profile}_refresh")
            if token:
                return token
                
        except Exception:
            pass
        
        # Fallback - расшифровываем из файла  
        profile_file = self.profiles_dir / f"{profile}.json"
        if profile_file.exists():
            try:
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
                
                encrypted_token = profile_data.get("refresh_token_encrypted")
                if encrypted_token:
                    return self.decrypt_token(encrypted_token)
                    
            except Exception:
                pass
        
        return None
    
    def delete_tokens(self, profile: str):
        """Удалить токены для профиля"""
        try:
            keyring.delete_password("durusai-cli", f"{profile}_access")
            keyring.delete_password("durusai-cli", f"{profile}_refresh")
        except:
            pass
        
        # Удаляем файл профиля
        profile_file = self.profiles_dir / f"{profile}.json"
        if profile_file.exists():
            profile_file.unlink()
    
    def list_profiles(self) -> list[str]:
        """Список сохраненных профилей"""
        profiles = set()
        
        # Профили из keyring (сложно получить список, пропускаем)
        
        # Профили из файлов
        for profile_file in self.profiles_dir.glob("*.json"):
            profiles.add(profile_file.stem)
        
        return sorted(list(profiles))
    
    def get_default_profile(self) -> str:
        """Получить профиль по умолчанию"""
        return self.get("default_profile", "default")
    
    def set_default_profile(self, profile: str):
        """Установить профиль по умолчанию"""
        self.set("default_profile", profile)