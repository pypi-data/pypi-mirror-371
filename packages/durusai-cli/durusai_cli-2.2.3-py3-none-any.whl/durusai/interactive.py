"""
Интерактивный REPL режим для DurusAI CLI
"""
from typing import Optional, List, Dict, Any
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
import sys

from .config import Config
from .api_client import SyncDurusAIClient
from .exceptions import AuthenticationError, NetworkError


class InteractiveMode:
    """Интерактивный режим чата с AI"""
    
    def __init__(self, client: SyncDurusAIClient, config: Config, 
                 default_model: Optional[str] = None):
        self.client = client
        self.config = config
        self.console = Console()
        
        # Настройки сессии
        self.current_model = default_model or config.get("settings.default_model", "claude-3-sonnet-20240229")
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_stats = {
            "queries": 0,
            "total_tokens": 0
        }
        
        # Стиль для prompt_toolkit
        self.style = Style.from_dict({
            'prompt': '#00aa00 bold',
            'input': '#ffffff',
            'completion-menu.completion': 'bg:#008888 #ffffff',
            'completion-menu.completion.current': 'bg:#00aaaa #000000',
            'scrollbar.background': 'bg:#88aaaa',
            'scrollbar.button': 'bg:#222222',
        })
        
        # Автодополнение команд
        self.completer = WordCompleter([
            '/help', '/quit', '/exit', '/clear', '/history',
            '/model', '/models', '/stats', '/save', '/load',
            '/settings', '/export'
        ])
        
        # Key bindings
        self.bindings = KeyBindings()
        
        @self.bindings.add('c-c')
        def _(event):
            """Ctrl+C - прерывание"""
            event.app.exit(exception=KeyboardInterrupt)
        
        @self.bindings.add('c-d')
        def _(event):
            """Ctrl+D - выход"""
            event.app.exit()
        
        # Создаем сессию
        self.session = PromptSession(
            completer=self.completer,
            style=self.style,
            key_bindings=self.bindings,
            mouse_support=True,
            complete_style='multi-column'
        )
    
    def show_welcome(self):
        """Показать приветствие в стиле Claude"""
        # Минималистичное приветствие без больших рамок
        self.console.print(f"🤖 [bold blue]DurusAI[/bold blue]")
        self.console.print(f"[dim]Модель: {self.current_model} | Команды: /help, /model, /quit[/dim]")
        self.console.print()
    
    def show_help(self):
        """Показать справку"""
        help_table = Table(title="📋 Доступные команды", show_header=True, header_style="bold blue")
        help_table.add_column("Команда", style="green", no_wrap=True)
        help_table.add_column("Описание", style="white")
        help_table.add_column("Пример", style="dim")
        
        commands = [
            ("/help", "Показать эту справку", "/help"),
            ("/model <name>", "Сменить AI модель", "/model gpt-4"),
            ("/models", "Показать доступные модели", "/models"),
            ("/clear", "Очистить историю разговора", "/clear"),
            ("/history", "Показать историю разговора", "/history"),
            ("/stats", "Показать статистику сессии", "/stats"),
            ("/settings", "Показать настройки", "/settings"),
            ("/export", "Экспортировать разговор", "/export chat.md"),
            ("/quit, /exit", "Выйти из интерактивного режима", "/quit"),
            ("Ctrl+C", "Прервать текущий запрос", ""),
            ("Ctrl+D", "Быстрый выход", ""),
        ]
        
        for cmd, desc, example in commands:
            help_table.add_row(cmd, desc, example)
        
        self.console.print(help_table)
    
    def process_command(self, text: str) -> bool:
        """Обработать команду. Возвращает False если нужно выйти"""
        if not text.startswith('/'):
            return True
        
        parts = text.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in ['/quit', '/exit']:
            return False
        
        elif command == '/help':
            self.show_help()
        
        elif command == '/clear':
            self.conversation_history.clear()
            self.console.print("✅ История разговора очищена", style="green")
        
        elif command == '/model':
            if args:
                self.current_model = args[0]
                self.console.print(f"✅ Модель изменена на: [cyan]{self.current_model}[/cyan]")
            else:
                self.console.print(f"📋 Текущая модель: [cyan]{self.current_model}[/cyan]")
        
        elif command == '/models':
            self.show_models()
        
        elif command == '/history':
            self.show_history()
        
        elif command == '/stats':
            self.show_session_stats()
        
        elif command == '/settings':
            self.show_settings()
        
        elif command == '/export':
            filename = args[0] if args else "chat_export.md"
            self.export_conversation(filename)
        
        else:
            self.console.print(f"❓ Неизвестная команда: [red]{command}[/red]")
            self.console.print("💡 Используйте [green]/help[/green] для списка команд")
        
        return True
    
    def show_models(self):
        """Показать доступные модели"""
        try:
            result = self.client.get_models()
            models = result.get("models", [])
            
            if not models:
                self.console.print("❌ Модели не найдены", style="red")
                return
            
            table = Table(title="🤖 Доступные модели")
            table.add_column("ID", style="cyan")
            table.add_column("Название", style="green")
            table.add_column("Статус")
            table.add_column("Описание", style="dim")
            
            for model in models:
                status = "✅" if model.get("available") else "❌"
                current = "👈" if model.get("id") == self.current_model else ""
                
                table.add_row(
                    f"{model.get('id', '')} {current}",
                    model.get("name", ""),
                    status,
                    model.get("description", "")
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"❌ Ошибка получения моделей: {e}", style="red")
    
    def show_history(self):
        """Показать историю разговора"""
        if not self.conversation_history:
            self.console.print("📭 История пуста", style="yellow")
            return
        
        self.console.print("📜 [bold blue]История разговора[/bold blue]")
        self.console.print()
        
        for i, entry in enumerate(self.conversation_history, 1):
            # Вопрос пользователя
            self.console.print(f"[bold blue]#{i} Вопрос:[/bold blue]")
            self.console.print(Panel(entry["query"], border_style="blue", padding=(0, 1)))
            
            # Ответ AI
            self.console.print(f"[bold green]#{i} Ответ ({entry['model']}):[/bold green]")
            try:
                self.console.print(Panel(Markdown(entry["response"]), border_style="green", padding=(0, 1)))
            except:
                self.console.print(Panel(entry["response"], border_style="green", padding=(0, 1)))
            
            self.console.print()
    
    def show_session_stats(self):
        """Показать статистику сессии"""
        self.console.print("📊 [bold blue]Статистика сессии[/bold blue]")
        self.console.print(f"   Запросов: [cyan]{self.session_stats['queries']}[/cyan]")
        self.console.print(f"   Токенов: [cyan]{self.session_stats['total_tokens']:,}[/cyan]")
        self.console.print(f"   Модель: [yellow]{self.current_model}[/yellow]")
    
    def show_settings(self):
        """Показать текущие настройки"""
        self.console.print("⚙️ [bold blue]Настройки сессии[/bold blue]")
        self.console.print(f"   Модель: [yellow]{self.current_model}[/yellow]")
        self.console.print(f"   API endpoint: [dim]{self.config.get_api_endpoint()}[/dim]")
        self.console.print(f"   Timeout: [cyan]{self.config.get('settings.timeout')}с[/cyan]")
        self.console.print(f"   Stream responses: [cyan]{self.config.get('settings.stream_responses')}[/cyan]")
    
    def export_conversation(self, filename: str):
        """Экспортировать разговор в файл"""
        if not self.conversation_history:
            self.console.print("📭 Нечего экспортировать", style="yellow")
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# DurusAI Conversation Export\n\n")
                f.write(f"**Model:** {self.current_model}\n")
                f.write(f"**Total queries:** {self.session_stats['queries']}\n")
                f.write(f"**Total tokens:** {self.session_stats['total_tokens']:,}\n\n")
                f.write("---\n\n")
                
                for i, entry in enumerate(self.conversation_history, 1):
                    f.write(f"## Query #{i}\n\n")
                    f.write(f"**User:** {entry['query']}\n\n")
                    f.write(f"**AI ({entry['model']}):**\n\n")
                    f.write(f"{entry['response']}\n\n")
                    f.write("---\n\n")
            
            self.console.print(f"✅ Разговор экспортирован в: [cyan]{filename}[/cyan]")
            
        except Exception as e:
            self.console.print(f"❌ Ошибка экспорта: {e}", style="red")
    
    def handle_query(self, query: str):
        """Обработать пользовательский запрос"""
        try:
            # Отправляем запрос
            self.console.print("🤖 [dim]Обработка запроса...[/dim]")
            
            result = self.client.query(
                prompt=query,
                model=self.current_model
            )
            
            # Показываем ответ
            response = result["response"]
            model_used = result.get("model_used", self.current_model)
            tokens_used = result.get("tokens_used", {}).get("total", 0)
            
            # Рендерим ответ в минималистичном стиле Claude
            try:
                self.console.print(Markdown(response))
            except:
                self.console.print(response)
            
            # Обновляем статистику
            self.session_stats["queries"] += 1
            self.session_stats["total_tokens"] += tokens_used
            
            # Сохраняем в историю
            self.conversation_history.append({
                "query": query,
                "response": response,
                "model": model_used,
                "tokens": tokens_used
            })
            
            # Показываем краткую статистику
            if tokens_used > 0:
                self.console.print(f"[dim]Токены: {tokens_used} | Модель: {model_used}[/dim]")
            
        except AuthenticationError:
            self.console.print("❌ Токен истек, выход из интерактивного режима", style="red")
            return False
        
        except NetworkError as e:
            self.console.print(f"🌐 Ошибка сети: {e}", style="red")
            return True  # Продолжаем работу
        
        except Exception as e:
            self.console.print(f"💥 Ошибка: {e}", style="red")
            return True  # Продолжаем работу
        
        return True
    
    def run(self):
        """Запустить интерактивный режим"""
        self.show_welcome()
        
        try:
            while True:
                try:
                    # Получаем пользовательский ввод
                    user_input = self.session.prompt(
                        HTML('<prompt>durusai> </prompt>'),
                        multiline=False
                    )
                    
                    # Проверяем на None (Ctrl+D или другие случаи)
                    if user_input is None:
                        break
                    
                    text = user_input.strip()
                    
                    if not text:
                        continue
                    
                    # Обрабатываем команды
                    if text.startswith('/'):
                        if not self.process_command(text):
                            break
                    else:
                        # Обрабатываем как запрос к AI
                        if not self.handle_query(text):
                            break
                    
                    self.console.print()  # Пустая строка для читаемости
                    
                except KeyboardInterrupt:
                    self.console.print("\n⚠️ Прервано пользователем")
                    if confirm("\nВыйти из интерактивного режима?"):
                        break
                    self.console.print()
                
                except EOFError:
                    break
        
        except Exception as e:
            self.console.print(f"\n💥 Критическая ошибка: {e}", style="red")
        
        finally:
            # Прощание
            if self.session_stats["queries"] > 0:
                self.console.print(Panel.fit(
                    f"📊 Статистика сессии:\n"
                    f"   Запросов: [cyan]{self.session_stats['queries']}[/cyan]\n"
                    f"   Токенов: [cyan]{self.session_stats['total_tokens']:,}[/cyan]\n\n"
                    f"👋 [yellow]До свидания![/yellow]",
                    title="🎯 Завершение сессии",
                    border_style="blue"
                ))
            else:
                self.console.print("👋 [yellow]До свидания![/yellow]")