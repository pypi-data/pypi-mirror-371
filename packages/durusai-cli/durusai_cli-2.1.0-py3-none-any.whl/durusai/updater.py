"""
Система автоматических обновлений для DurusAI CLI
"""
import os
import sys
import json
import subprocess
from typing import Optional, List, Dict, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import httpx
from packaging import version

from .config import Config
from .exceptions import NetworkError


class UpdateChecker:
    """Проверка и установка обновлений DurusAI CLI"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.github_api = "https://api.github.com/repos/durusai/cli"
        self.pypi_api = "https://pypi.org/pypi/durusai/json"
        self.current_version = self._get_current_version()
        self.update_check_file = self.config.config_dir / "last_update_check.json"
    
    def _get_current_version(self) -> str:
        """Получить текущую версию CLI"""
        try:
            from . import __version__
            return __version__
        except ImportError:
            return "1.0.0"
    
    def _should_check_updates(self) -> bool:
        """Определить нужно ли проверять обновления"""
        # Проверяем настройки
        if not self.config.get("settings.auto_update", True):
            return False
        
        # Проверяем когда последний раз проверяли
        if not self.update_check_file.exists():
            return True
        
        try:
            with open(self.update_check_file, 'r') as f:
                data = json.load(f)
            
            last_check = datetime.fromisoformat(data.get("last_check", "2020-01-01"))
            check_interval = timedelta(hours=data.get("check_interval_hours", 24))
            
            return datetime.now() >= last_check + check_interval
            
        except (json.JSONDecodeError, KeyError, ValueError):
            return True
    
    def _save_update_check(self, latest_version: Optional[str] = None):
        """Сохранить информацию о последней проверке"""
        data = {
            "last_check": datetime.now().isoformat(),
            "check_interval_hours": 24,
            "current_version": self.current_version,
            "latest_version": latest_version
        }
        
        try:
            with open(self.update_check_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass  # Не критично если не удалось сохранить
    
    def check_pypi_version(self) -> Optional[str]:
        """Проверить последнюю версию на PyPI"""
        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(self.pypi_api)
                
                if response.status_code == 200:
                    data = response.json()
                    return data["info"]["version"]
                    
        except (httpx.RequestError, KeyError, json.JSONDecodeError):
            pass
        
        return None
    
    def check_github_version(self) -> Optional[Dict[str, Any]]:
        """Проверить последний релиз на GitHub"""
        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(f"{self.github_api}/releases/latest")
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "version": data["tag_name"].lstrip("v"),
                        "url": data["html_url"],
                        "published_at": data["published_at"],
                        "body": data["body"],
                        "assets": [
                            {
                                "name": asset["name"],
                                "download_url": asset["browser_download_url"],
                                "size": asset["size"]
                            }
                            for asset in data["assets"]
                        ]
                    }
                    
        except (httpx.RequestError, KeyError, json.JSONDecodeError):
            pass
        
        return None
    
    def compare_versions(self, current: str, latest: str) -> int:
        """Сравнить версии. Возвращает: -1 (старше), 0 (равны), 1 (новее)"""
        try:
            current_ver = version.parse(current)
            latest_ver = version.parse(latest)
            
            if current_ver < latest_ver:
                return -1
            elif current_ver > latest_ver:
                return 1
            else:
                return 0
                
        except Exception:
            # Fallback на строковое сравнение
            if current < latest:
                return -1
            elif current > latest:
                return 1
            else:
                return 0
    
    def check_for_updates(self, force: bool = False) -> Optional[Dict[str, Any]]:
        """Проверить наличие обновлений"""
        if not force and not self._should_check_updates():
            return None
        
        # Проверяем PyPI
        pypi_version = self.check_pypi_version()
        
        # Проверяем GitHub
        github_info = self.check_github_version()
        github_version = github_info["version"] if github_info else None
        
        # Определяем последнюю версию
        latest_version = pypi_version or github_version
        
        if not latest_version:
            self._save_update_check()
            return None
        
        # Сравниваем версии
        comparison = self.compare_versions(self.current_version, latest_version)
        
        # Сохраняем информацию о проверке
        self._save_update_check(latest_version)
        
        if comparison < 0:  # Доступно обновление
            return {
                "available": True,
                "current_version": self.current_version,
                "latest_version": latest_version,
                "pypi_version": pypi_version,
                "github_info": github_info,
                "update_methods": self._get_update_methods()
            }
        
        return {
            "available": False,
            "current_version": self.current_version,
            "latest_version": latest_version
        }
    
    def _get_update_methods(self) -> List[Dict[str, str]]:
        """Получить доступные методы обновления"""
        methods = []
        
        # PyPI обновление
        methods.append({
            "name": "PyPI (рекомендуется)",
            "command": "pip install --upgrade durusai",
            "description": "Обновление через PyPI"
        })
        
        # pip install с --user
        methods.append({
            "name": "PyPI (user install)",
            "command": "pip install --user --upgrade durusai",
            "description": "Обновление в пользовательскую директорию"
        })
        
        # pipx обновление
        methods.append({
            "name": "pipx",
            "command": "pipx upgrade durusai",
            "description": "Обновление через pipx (если установлено)"
        })
        
        return methods
    
    def install_update(self, method: str = "pip") -> bool:
        """Установить обновление"""
        try:
            if method == "pip":
                cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "durusai"]
            elif method == "pip-user":
                cmd = [sys.executable, "-m", "pip", "install", "--user", "--upgrade", "durusai"]
            elif method == "pipx":
                cmd = ["pipx", "upgrade", "durusai"]
            else:
                return False
            
            # Выполняем обновление
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return True
            else:
                print(f"❌ Ошибка обновления: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout при обновлении")
            return False
        except Exception as e:
            print(f"❌ Ошибка при обновлении: {e}")
            return False


class UpdateManager:
    """Менеджер обновлений с UI"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.checker = UpdateChecker(config)
    
    def check_and_notify(self, force: bool = False, interactive: bool = True) -> bool:
        """Проверить обновления и уведомить пользователя"""
        try:
            update_info = self.checker.check_for_updates(force)
            
            if not update_info:
                if force:
                    print("🔍 Не удалось проверить обновления")
                return False
            
            if not update_info["available"]:
                if force:
                    print(f"✅ У вас последняя версия: {update_info['current_version']}")
                return False
            
            # Показываем информацию об обновлении
            self._show_update_notification(update_info)
            
            if interactive:
                return self._prompt_for_update(update_info)
            
            return True
            
        except Exception as e:
            if force:
                print(f"❌ Ошибка проверки обновлений: {e}")
            return False
    
    def _show_update_notification(self, update_info: Dict[str, Any]):
        """Показать уведомление об обновлении"""
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        
        current = update_info["current_version"]
        latest = update_info["latest_version"]
        
        message = f"🆕 [bold green]Доступно обновление![/bold green]\n\n"
        message += f"Текущая версия: [red]{current}[/red]\n"
        message += f"Новая версия: [green]{latest}[/green]\n\n"
        
        # Добавляем информацию о GitHub релизе если есть
        github_info = update_info.get("github_info")
        if github_info:
            published = github_info.get("published_at", "").split("T")[0]
            message += f"Дата релиза: [dim]{published}[/dim]\n"
            
            # Краткое описание изменений
            body = github_info.get("body", "")
            if body and len(body) < 200:
                message += f"\nИзменения:\n[dim]{body[:200]}[/dim]\n"
        
        message += f"\n💡 Используйте [cyan]durusai update[/cyan] для обновления"
        
        console.print(Panel(
            message,
            title="🚀 DurusAI CLI Update",
            border_style="green"
        ))
    
    def _prompt_for_update(self, update_info: Dict[str, Any]) -> bool:
        """Предложить пользователю обновиться"""
        from rich.prompt import Confirm
        
        if Confirm.ask("\n❓ Обновиться сейчас?", default=False):
            return self._interactive_update(update_info)
        
        return False
    
    def _interactive_update(self, update_info: Dict[str, Any]) -> bool:
        """Интерактивное обновление"""
        from rich.console import Console
        from rich.prompt import IntPrompt
        
        console = Console()
        
        methods = update_info["update_methods"]
        
        console.print("\n🔧 Выберите метод обновления:")
        for i, method in enumerate(methods, 1):
            console.print(f"[{i}] {method['name']} - {method['description']}")
        
        try:
            choice = IntPrompt.ask(
                "Ваш выбор",
                choices=[str(i) for i in range(1, len(methods) + 1)],
                default=1
            )
            
            selected_method = methods[choice - 1]
            console.print(f"\n🔄 Выполнение: [cyan]{selected_method['command']}[/cyan]")
            
            # Выполняем обновление
            if choice == 1:
                success = self.checker.install_update("pip")
            elif choice == 2:
                success = self.checker.install_update("pip-user")
            elif choice == 3:
                success = self.checker.install_update("pipx")
            else:
                success = False
            
            if success:
                console.print("✅ [green]Обновление установлено успешно![/green]")
                console.print("🔄 [yellow]Перезапустите CLI для применения изменений[/yellow]")
                return True
            else:
                console.print("❌ [red]Ошибка при обновлении[/red]")
                console.print("💡 Попробуйте обновить вручную или обратитесь в поддержку")
                return False
                
        except KeyboardInterrupt:
            console.print("\n🚫 Обновление отменено")
            return False
        except Exception as e:
            console.print(f"\n❌ Ошибка: {e}")
            return False


def check_updates_on_startup(config: Optional[Config] = None, quiet: bool = True):
    """Проверить обновления при запуске CLI (в фоне)"""
    if quiet:
        # Тихая проверка в фоне
        try:
            manager = UpdateManager(config)
            manager.check_and_notify(force=False, interactive=False)
        except:
            pass  # Игнорируем ошибки при тихой проверке
    else:
        # Показываем результат
        manager = UpdateManager(config)
        return manager.check_and_notify(force=True, interactive=True)