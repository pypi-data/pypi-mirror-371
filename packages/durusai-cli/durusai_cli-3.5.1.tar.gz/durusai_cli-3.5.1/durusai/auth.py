"""
Менеджер аутентификации для DurusAI CLI
"""
import getpass
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt

from .config import Config
from .api_client import SyncDurusAIClient
from .exceptions import AuthenticationError, NetworkError


class AuthManager:
    """Менеджер аутентификации и сессий"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.console = Console()
    
    def login(self, username: Optional[str] = None, password: Optional[str] = None,
              profile: Optional[str] = None) -> bool:
        """Интерактивный или программный вход в систему"""
        profile = profile or self.config.get_default_profile()
        
        try:
            # Если учетные данные не предоставлены, запрашиваем интерактивно
            if not username:
                username = Prompt.ask("👤 Имя пользователя")
            
            if not password:
                password = getpass.getpass("🔑 Пароль: ")
            
            # Создаем API клиент
            with SyncDurusAIClient(self.config) as client:
                self.console.print("🔄 Аутентификация...", style="blue")
                
                # Выполняем вход
                result = client.login(username, password)
                
                # Сохраняем токены
                self.config.save_token(
                    profile=profile,
                    access_token=result["access_token"],
                    refresh_token=result.get("refresh_token")
                )
                
                # Получаем информацию о пользователе (может не быть в ответе)
                user_info = result.get("user", {})
                
                self.console.print("✅ Успешный вход!", style="green")
                self.console.print(f"👤 Пользователь: {user_info.get('username', username)}")
                self.console.print(f"👑 Роль: {user_info.get('role', 'user')}")
                self.console.print(f"📁 Профиль: {profile}")
                self.console.print(f"🔑 Токен: {result['access_token'][:20]}...")
                
                return True
                
        except AuthenticationError as e:
            self.console.print(f"❌ Ошибка аутентификации: {e}", style="red")
            return False
        
        except NetworkError as e:
            self.console.print(f"🌐 Ошибка сети: {e}", style="red")
            self.console.print("💡 Проверьте подключение к интернету и настройки API", style="yellow")
            return False
        
        except Exception as e:
            self.console.print(f"💥 Неожиданная ошибка: {e}", style="red")
            return False
    
    def logout(self, profile: Optional[str] = None, all_profiles: bool = False):
        """Выход из системы"""
        if all_profiles:
            # Выходим из всех профилей
            profiles = self.config.list_profiles()
            for prof in profiles:
                self.config.delete_tokens(prof)
            
            self.console.print("✅ Выход из всех профилей выполнен", style="green")
        else:
            profile = profile or self.config.get_default_profile()
            self.config.delete_tokens(profile)
            
            self.console.print(f"✅ Выход из профиля '{profile}' выполнен", style="green")
    
    def whoami(self, profile: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Показать информацию о текущем пользователе"""
        profile = profile or self.config.get_default_profile()
        
        # Проверяем есть ли токен
        token = self.config.get_token(profile)
        if not token:
            self.console.print(f"❌ Профиль '{profile}' не авторизован", style="red")
            self.console.print("💡 Используйте 'durusai login' для входа", style="yellow")
            return None
        
        try:
            # Создаем API клиент с токеном
            with SyncDurusAIClient(self.config) as client:
                client.set_tokens(token)
                
                # Получаем информацию о пользователе
                user_info = client.get_user_info()
                
                self.console.print("👤 Информация о пользователе:", style="blue bold")
                self.console.print(f"   Имя: {user_info.get('username')}")
                self.console.print(f"   Email: {user_info.get('email', 'не указан')}")
                self.console.print(f"   Роль: {user_info.get('role')}")
                self.console.print(f"   Активен: {'✅' if user_info.get('is_active') else '❌'}")
                self.console.print(f"   Создан: {user_info.get('created_at', 'неизвестно')}")
                self.console.print(f"   Последний вход: {user_info.get('last_login', 'неизвестно')}")
                self.console.print(f"   Профиль: {profile}")
                self.console.print(f"   API endpoint: {self.config.get_api_endpoint()}")
                
                return user_info
                
        except AuthenticationError:
            self.console.print(f"❌ Токен для профиля '{profile}' истек", style="red")
            self.console.print("💡 Используйте 'durusai login' для повторного входа", style="yellow")
            return None
        
        except NetworkError as e:
            self.console.print(f"🌐 Ошибка сети: {e}", style="red")
            return None
        
        except Exception as e:
            self.console.print(f"💥 Ошибка: {e}", style="red")
            return None
    
    def is_authenticated(self, profile: Optional[str] = None) -> bool:
        """Проверить аутентифицирован ли пользователь"""
        profile = profile or self.config.get_default_profile()
        return self.config.get_token(profile) is not None
    
    def get_authenticated_client(self, profile: Optional[str] = None) -> Optional[SyncDurusAIClient]:
        """Получить аутентифицированный API клиент"""
        profile = profile or self.config.get_default_profile()
        token = self.config.get_token(profile)
        
        if not token:
            return None
        
        client = SyncDurusAIClient(self.config)
        client.set_tokens(token, self.config.get_refresh_token(profile))
        return client