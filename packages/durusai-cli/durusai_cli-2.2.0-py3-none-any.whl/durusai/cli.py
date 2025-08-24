"""
Основной CLI интерфейс для DurusAI
"""
import sys
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

from . import __version__
from .config import Config
from .auth import AuthManager
from .api_client import SyncDurusAIClient
from .exceptions import DurusAIError, AuthenticationError, NetworkError
from .interactive import InteractiveMode
from .updater import UpdateManager


# Создаем основное приложение
app = typer.Typer(
    name="durusai",
    help="🤖 DurusAI Native CLI - AI-powered assistant",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()


def version_callback(value: bool):
    """Показать версию"""
    if value:
        console.print(f"DurusAI CLI v{__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(None, "--version", "-v", callback=version_callback, 
                                         help="Показать версию"),
    endpoint: Optional[str] = typer.Option(None, "--endpoint", "-e", 
                                         help="API endpoint"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", 
                                        help="Профиль пользователя"),
):
    """🤖 DurusAI Native CLI - AI-powered assistant"""
    # Настраиваем глобальную конфигурацию
    config = Config()
    
    if endpoint:
        config.set_api_endpoint(endpoint)
    
    if profile:
        config.set_default_profile(profile)
    
    # Если команда не указана, пытаемся запустить интерактивный режим
    if ctx.invoked_subcommand is None:
        auth_manager = AuthManager(config)
        
        # Проверяем авторизацию
        if not auth_manager.is_authenticated(profile):
            console.print("👋 [blue]Добро пожаловать в DurusAI CLI![/blue]")
            console.print("❌ Вы не авторизованы", style="red")
            console.print("💡 Используйте [green]durusai login[/green] для входа", style="yellow")
            console.print()
            console.print("📚 Доступные команды:")
            console.print("   [green]durusai login[/green]     - войти в систему")
            console.print("   [green]durusai --help[/green]    - показать справку")
            raise typer.Exit(1)
        
        # Пользователь авторизован - запускаем интерактивный режим
        console.print("🚀 [blue]Запуск интерактивного режима...[/blue]")
        console.print("💡 Используйте [green]/help[/green] для справки или [green]/quit[/green] для выхода")
        console.print()
        
        # Получаем аутентифицированный клиент
        client = auth_manager.get_authenticated_client(profile)
        if not client:
            console.print("❌ Не удалось создать API клиент", style="red")
            raise typer.Exit(1)
        
        # Запускаем интерактивный режим
        interactive_mode = InteractiveMode(client, config, None)
        interactive_mode.run()


@app.command()
def login(
    username: Optional[str] = typer.Option(None, "--username", "-u", 
                                         help="Имя пользователя"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", 
                                        help="Профиль для сохранения"),
):
    """🔑 Войти в систему DurusAI"""
    config = Config()
    auth_manager = AuthManager(config)
    
    success = auth_manager.login(username=username, profile=profile)
    if not success:
        raise typer.Exit(1)


@app.command()
def logout(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", 
                                        help="Профиль для выхода"),
    all_profiles: bool = typer.Option(False, "--all", "-a", 
                                    help="Выйти из всех профилей"),
):
    """👋 Выйти из системы DurusAI"""
    config = Config()
    auth_manager = AuthManager(config)
    
    auth_manager.logout(profile=profile, all_profiles=all_profiles)


@app.command()
def whoami(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", 
                                        help="Профиль для проверки"),
):
    """👤 Показать информацию о текущем пользователе"""
    config = Config()
    auth_manager = AuthManager(config)
    
    user_info = auth_manager.whoami(profile=profile)
    if not user_info:
        raise typer.Exit(1)


@app.command()
def query(
    prompt: str = typer.Argument(..., help="Вопрос или запрос к AI"),
    model: Optional[str] = typer.Option(None, "--model", "-m", 
                                      help="Модель AI для использования"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", 
                                           help="Максимальное количество токенов"),
    temperature: Optional[float] = typer.Option(None, "--temperature", "-t",
                                              help="Температура генерации (0.0-2.0)"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", 
                                        help="Профиль пользователя"),
    stream: bool = typer.Option(False, "--stream", "-s",
                              help="Потоковый вывод ответа"),
    no_markdown: bool = typer.Option(False, "--no-markdown",
                                   help="Отключить рендеринг Markdown"),
):
    """💬 Отправить запрос к AI"""
    config = Config()
    auth_manager = AuthManager(config)
    
    # Проверяем аутентификацию
    if not auth_manager.is_authenticated(profile):
        console.print("❌ Вы не авторизованы", style="red")
        console.print("💡 Используйте 'durusai login' для входа", style="yellow")
        raise typer.Exit(1)
    
    # Получаем аутентифицированный клиент
    client = auth_manager.get_authenticated_client(profile)
    if not client:
        console.print("❌ Не удалось создать API клиент", style="red")
        raise typer.Exit(1)
    
    try:
        with client:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task("🤖 Обработка запроса...", total=None)
                
                # Отправляем запрос
                result = client.query(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream
                )
            
            # Показываем результат
            response_text = result["response"]
            model_used = result.get("model_used", "unknown")
            tokens_used = result.get("tokens_used", {})
            processing_time = result.get("processing_time", 0)
            
            # Форматируем ответ
            if no_markdown:
                console.print(response_text)
            else:
                try:
                    console.print(Markdown(response_text))
                except:
                    console.print(response_text)
            
            # Показываем метаинформацию если включено в настройках
            if config.get("settings.show_token_usage", True):
                console.print()
                console.print(Panel.fit(
                    f"[dim]Модель: {model_used} | "
                    f"Токены: {tokens_used.get('total', 0)} | "
                    f"Время: {processing_time:.1f}с[/dim]",
                    style="blue"
                ))
            
    except AuthenticationError:
        console.print("❌ Токен истек, требуется повторная аутентификация", style="red")
        console.print("💡 Используйте 'durusai login'", style="yellow")
        raise typer.Exit(1)
    
    except NetworkError as e:
        console.print(f"🌐 Ошибка сети: {e}", style="red")
        raise typer.Exit(1)
    
    except Exception as e:
        console.print(f"💥 Ошибка: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def interactive(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", 
                                        help="Профиль пользователя"),
    model: Optional[str] = typer.Option(None, "--model", "-m", 
                                      help="Модель AI для использования"),
):
    """💬 Интерактивный режим чата с AI"""
    config = Config()
    auth_manager = AuthManager(config)
    
    # Проверяем аутентификацию
    if not auth_manager.is_authenticated(profile):
        console.print("❌ Вы не авторизованы", style="red")
        console.print("💡 Используйте 'durusai login' для входа", style="yellow")
        raise typer.Exit(1)
    
    # Получаем аутентифицированный клиент
    client = auth_manager.get_authenticated_client(profile)
    if not client:
        console.print("❌ Не удалось создать API клиент", style="red")
        raise typer.Exit(1)
    
    # Запускаем интерактивный режим
    interactive_mode = InteractiveMode(client, config, model)
    interactive_mode.run()


@app.command()
def chat(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", 
                                        help="Профиль пользователя"),
    model: Optional[str] = typer.Option(None, "--model", "-m", 
                                      help="Модель AI для использования"),
):
    """💬 Интерактивный режим чата с AI (alias для interactive)"""
    # Просто вызываем interactive команду
    ctx = typer.Context(chat)
    ctx.invoke(interactive, profile=profile, model=model)


@app.command()
def models(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", 
                                        help="Профиль пользователя"),
):
    """🔧 Показать доступные модели AI"""
    config = Config()
    auth_manager = AuthManager(config)
    
    # Проверяем аутентификацию
    if not auth_manager.is_authenticated(profile):
        console.print("❌ Вы не авторизованы", style="red")
        console.print("💡 Используйте 'durusai login' для входа", style="yellow")
        raise typer.Exit(1)
    
    # Получаем аутентифицированный клиент
    client = auth_manager.get_authenticated_client(profile)
    if not client:
        console.print("❌ Не удалось создать API клиент", style="red")
        raise typer.Exit(1)
    
    try:
        with client:
            result = client.get_models()
            models = result.get("models", [])
            
            if not models:
                console.print("❌ Модели не найдены", style="red")
                return
            
            table = Table(title="🤖 Доступные модели AI")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Название", style="green")
            table.add_column("Провайдер", style="yellow")
            table.add_column("Статус", justify="center")
            table.add_column("Контекст", justify="right")
            table.add_column("Описание", style="dim")
            
            for model in models:
                status = "✅" if model.get("available") else "❌"
                context_length = f"{model.get('context_length', 0):,}"
                
                table.add_row(
                    model.get("id", ""),
                    model.get("name", ""),
                    model.get("provider", ""),
                    status,
                    context_length,
                    model.get("description", "")
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"💥 Ошибка получения моделей: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def stats(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", 
                                        help="Профиль пользователя"),
):
    """📊 Показать статистику использования"""
    config = Config()
    auth_manager = AuthManager(config)
    
    # Проверяем аутентификацию
    if not auth_manager.is_authenticated(profile):
        console.print("❌ Вы не авторизованы", style="red")
        console.print("💡 Используйте 'durusai login' для входа", style="yellow")
        raise typer.Exit(1)
    
    # Получаем аутентифицированный клиент  
    client = auth_manager.get_authenticated_client(profile)
    if not client:
        console.print("❌ Не удалось создать API клиент", style="red")
        raise typer.Exit(1)
    
    try:
        with client:
            result = client.get_stats()
            
            console.print("📊 [bold blue]Статистика использования[/bold blue]")
            console.print()
            console.print(f"📈 Всего запросов: [bold]{result.get('total_requests', 0)}[/bold]")
            console.print(f"🎯 Всего токенов: [bold]{result.get('total_tokens', 0):,}[/bold]")
            console.print(f"📅 Запросов сегодня: [bold]{result.get('requests_today', 0)}[/bold]")
            console.print(f"🎯 Токенов сегодня: [bold]{result.get('tokens_today', 0):,}[/bold]")
            
            remaining = result.get('remaining_quota')
            if remaining is not None:
                console.print(f"⏳ Осталось квоты: [bold]{remaining:,}[/bold]")
            
            # Статистика по моделям
            tokens_by_model = result.get('tokens_by_model', {})
            if tokens_by_model:
                console.print()
                console.print("[bold blue]Использование по моделям:[/bold blue]")
                
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Модель", style="cyan")
                table.add_column("Токены", justify="right", style="green")
                
                for model, tokens in tokens_by_model.items():
                    table.add_row(model, f"{tokens:,}")
                
                console.print(table)
                
    except Exception as e:
        console.print(f"💥 Ошибка получения статистики: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def config(
    key: Optional[str] = typer.Argument(None, help="Ключ конфигурации"),
    value: Optional[str] = typer.Argument(None, help="Значение для установки"),
    list_all: bool = typer.Option(False, "--list", "-l", 
                                help="Показать всю конфигурацию"),
):
    """⚙️ Управление конфигурацией"""
    config_obj = Config()
    
    if list_all:
        console.print("⚙️ [bold blue]Текущая конфигурация[/bold blue]")
        console.print()
        
        # Основные настройки
        console.print(f"🌐 API Endpoint: [cyan]{config_obj.get_api_endpoint()}[/cyan]")
        console.print(f"👤 Профиль по умолчанию: [yellow]{config_obj.get_default_profile()}[/yellow]")
        console.print()
        
        # Настройки
        settings = config_obj.get("settings", {})
        console.print("[bold blue]Настройки:[/bold blue]")
        for key, value in settings.items():
            console.print(f"   {key}: [green]{value}[/green]")
        
        # Отображение
        display = config_obj.get("display", {})
        console.print()
        console.print("[bold blue]Отображение:[/bold blue]")
        for key, value in display.items():
            console.print(f"   {key}: [green]{value}[/green]")
        
        return
    
    if key and value:
        # Устанавливаем значение
        try:
            # Пытаемся распарсить как JSON для булевых/числовых значений
            import json
            try:
                parsed_value = json.loads(value)
            except:
                parsed_value = value  # Строковое значение
            
            config_obj.set(key, parsed_value)
            console.print(f"✅ Установлено [cyan]{key}[/cyan] = [green]{parsed_value}[/green]")
            
        except Exception as e:
            console.print(f"❌ Ошибка установки конфигурации: {e}", style="red")
            raise typer.Exit(1)
    
    elif key:
        # Показываем значение
        value = config_obj.get(key)
        if value is not None:
            console.print(f"[cyan]{key}[/cyan] = [green]{value}[/green]")
        else:
            console.print(f"❌ Ключ [cyan]{key}[/cyan] не найден", style="red")
            raise typer.Exit(1)
    
    else:
        console.print("❓ Укажите ключ для просмотра или ключ и значение для установки")
        console.print("💡 Используйте --list для показа всей конфигурации")


@app.command()
def health(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", 
                                        help="Профиль пользователя"),
):
    """🏥 Проверить состояние API"""
    config = Config()
    
    try:
        with SyncDurusAIClient(config) as client:
            result = client.health_check()
            
            status = result.get("status", "unknown")
            service = result.get("service", "unknown")
            version = result.get("version", "unknown")
            
            if status == "healthy":
                console.print("✅ API здоров и работает", style="green")
                console.print(f"🔧 Сервис: {service}")
                console.print(f"📦 Версия: {version}")
            else:
                console.print(f"⚠️ Статус API: {status}", style="yellow")
            
    except NetworkError:
        console.print(f"❌ API недоступен: {config.get_api_endpoint()}", style="red")
        console.print("💡 Проверьте подключение и настройки endpoint", style="yellow")
        raise typer.Exit(1)
    
    except Exception as e:
        console.print(f"💥 Ошибка проверки: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def update(
    check_only: bool = typer.Option(False, "--check", "-c",
                                  help="Только проверить наличие обновлений"),
    force: bool = typer.Option(False, "--force", "-f",
                             help="Принудительная проверка обновлений"),
):
    """🔄 Проверить и установить обновления CLI"""
    config = Config()
    update_manager = UpdateManager(config)
    
    try:
        if check_only:
            # Только проверка
            update_info = update_manager.checker.check_for_updates(force=True)
            
            if not update_info:
                console.print("🔍 Не удалось проверить обновления", style="yellow")
                return
            
            if update_info["available"]:
                current = update_info["current_version"]
                latest = update_info["latest_version"]
                console.print(f"🆕 Доступно обновление: [red]{current}[/red] → [green]{latest}[/green]")
                console.print("💡 Используйте [cyan]durusai update[/cyan] для установки")
            else:
                console.print("✅ У вас последняя версия", style="green")
        
        else:
            # Проверка и установка
            success = update_manager.check_and_notify(force=force, interactive=True)
            if not success and force:
                console.print("ℹ️ Обновления не требуются", style="blue")
    
    except Exception as e:
        console.print(f"❌ Ошибка при проверке обновлений: {e}", style="red")
        raise typer.Exit(1)


def main():
    """Entry point для CLI"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n👋 До свидания!", style="yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n💥 Неожиданная ошибка: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()