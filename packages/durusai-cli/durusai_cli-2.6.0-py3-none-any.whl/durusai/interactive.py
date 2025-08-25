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
from .local_file_ops import LocalFileOperations, detect_file_command, format_file_list, extract_project_structure, extract_file_path


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
        
        # Локальные файловые операции
        self.file_ops = LocalFileOperations()
        
        # Настройки отображения
        self.use_pager = config.get("display.pager_enabled", True)
        self.last_response = ""  # Для команды /copy
        
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
            '/settings', '/export', '/pager', '/copy'
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
            ("/pager", "Переключить пейджер для длинных ответов", "/pager"),
            ("/copy", "Сохранить последний ответ в файл", "/copy response.md"),
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
        
        elif command == '/pager':
            self.use_pager = not self.use_pager
            status = "включен" if self.use_pager else "отключен"
            self.console.print(f"📄 Пейджер {status}")
        
        elif command == '/copy':
            if self.last_response:
                # Сохраняем последний ответ в файл
                filename = args[0] if args else "last_response.md"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(self.last_response)
                    self.console.print(f"✅ Ответ сохранен в: [cyan]{filename}[/cyan]")
                except Exception as e:
                    self.console.print(f"❌ Ошибка сохранения: {e}", style="red")
            else:
                self.console.print("❌ Нет ответа для сохранения", style="yellow")
        
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
    
    def print_with_pager(self, content: str, is_markdown: bool = True):
        """Вывод контента с поддержкой пейджера для длинного текста"""
        lines = content.split('\n')
        
        # Если текст длинный и пейджер включен, используем пейджер
        if len(lines) > 20 and self.use_pager:
            try:
                from rich.pager import Pager
                if is_markdown:
                    with Pager():
                        self.console.print(Markdown(content))
                else:
                    with Pager():
                        self.console.print(content)
            except:
                # Fallback на обычный вывод
                if is_markdown:
                    try:
                        self.console.print(Markdown(content))
                    except:
                        self.console.print(content)
                else:
                    self.console.print(content)
        else:
            # Обычный вывод для коротких ответов
            if is_markdown:
                try:
                    self.console.print(Markdown(content))
                except:
                    self.console.print(content)
            else:
                self.console.print(content)
        
        # Сохраняем для команды /copy
        self.last_response = content
    
    def handle_file_command(self, file_command: Dict[str, Any]):
        """Обработать файловую команду локально"""
        command = file_command["command"]
        args = file_command["args"]
        
        try:
            if command == "pwd":
                current_dir = self.file_ops.pwd()
                self.console.print(f"📁 Текущая директория: [cyan]{current_dir}[/cyan]")
            
            elif command == "ls":
                show_details = "-la" in args or "-lah" in args or "-al" in args
                path = None
                
                # Извлекаем путь из аргументов
                for arg in args:
                    if not arg.startswith('-'):
                        path = arg
                        break
                
                files_info = self.file_ops.ls(path, show_hidden=show_details)
                formatted_output = format_file_list(files_info)
                self.console.print(formatted_output)
            
            elif command == "cd":
                if not args:
                    self.console.print("❌ Укажите директорию для перехода", style="red")
                    return
                
                result = self.file_ops.cd(args[0])
                if result.get("success"):
                    self.console.print(f"✅ {result['message']}", style="green")
                else:
                    self.console.print(f"❌ {result['error']}", style="red")
            
            elif command == "mkdir":
                if not args:
                    self.console.print("❌ Укажите имя директории", style="red")
                    return
                
                result = self.file_ops.mkdir(args[0], parents=True)
                if result.get("success"):
                    self.console.print(f"✅ {result['message']}", style="green")
                else:
                    self.console.print(f"❌ {result['error']}", style="red")
            
            elif command == "cat":
                if not args:
                    self.console.print("❌ Укажите имя файла", style="red")
                    return
                
                result = self.file_ops.cat(args[0])
                if result.get("success"):
                    self.console.print(f"📄 [cyan]{result['file_path']}[/cyan]:")
                    self.console.print(Panel(result["content"], border_style="blue"))
                else:
                    self.console.print(f"❌ {result['error']}", style="red")
            
            elif command == "tree":
                path = args[0] if args else None
                result = self.file_ops.tree(path)
                if result.get("success"):
                    self.console.print(result["tree"])
                else:
                    self.console.print(f"❌ {result['error']}", style="red")
            
            elif command == "rm":
                if not file_command.get("args"):
                    self.console.print("❌ Укажите файлы для удаления", style="red")
                    return
                
                files_to_remove = file_command["args"]
                recursive = file_command.get("recursive", False)
                force = file_command.get("force", False)
                
                # Проверка на опасные операции
                if "*" in " ".join(files_to_remove) and not force:
                    # Показываем что будет удалено
                    import glob
                    all_matches = []
                    for pattern in files_to_remove:
                        if "*" in pattern:
                            matches = glob.glob(pattern)
                            all_matches.extend(matches)
                        else:
                            all_matches.append(pattern)
                    
                    if all_matches:
                        self.console.print("⚠️ [yellow]Будут удалены следующие файлы:[/yellow]")
                        for match in all_matches[:10]:  # Показываем первые 10
                            self.console.print(f"   📄 {match}")
                        if len(all_matches) > 10:
                            self.console.print(f"   ... и еще {len(all_matches) - 10} файлов")
                        
                        from prompt_toolkit.shortcuts import confirm
                        if not confirm("Продолжить удаление?"):
                            self.console.print("❌ Операция отменена", style="yellow")
                            return
                
                # Удаляем файлы
                for file_path in files_to_remove:
                    result = self.file_ops.rm(file_path, recursive=recursive, force=force)
                    if result.get("success"):
                        self.console.print(f"✅ {result['message']}", style="green")
                    else:
                        self.console.print(f"❌ {result['error']}", style="red")
            
            elif command == "cp":
                if len(args) < 2:
                    self.console.print("❌ Укажите источник и назначение", style="red")
                    return
                
                result = self.file_ops.cp(args[0], args[1])
                if result.get("success"):
                    self.console.print(f"✅ {result['message']}", style="green")
                else:
                    self.console.print(f"❌ {result['error']}", style="red")
            
            elif command == "mv":
                if len(args) < 2:
                    self.console.print("❌ Укажите источник и назначение", style="red")
                    return
                
                result = self.file_ops.mv(args[0], args[1])
                if result.get("success"):
                    self.console.print(f"✅ {result['message']}", style="green")
                else:
                    self.console.print(f"❌ {result['error']}", style="red")
            
            elif command == "create_project":
                # Для команд создания проектов используем AI, но с контекстом локальной директории
                query = args[0] if args else ""
                current_dir = self.file_ops.pwd()
                
                self.console.print("🤖 [dim]Генерирую код локально...[/dim]")
                
                # Формируем запрос с контекстом локальной работы
                local_prompt = f"""ВАЖНО: Ты работаешь как Claude Code - создавай файлы локально в текущей директории пользователя.

Текущая директория пользователя: {current_dir}

ИНСТРУКЦИЯ: Создай файлы локально используя обычные команды создания файлов. НЕ используй Docker или контейнеры.

Пользователь просит: {query}

Создай проект прямо в текущей директории пользователя."""

                # Отправляем запрос к AI
                result = self.client.query(
                    prompt=local_prompt,
                    model=self.current_model
                )
                
                # Показываем AI ответ с пейджером
                response = result["response"]
                self.print_with_pager(response, is_markdown=True)
                
                # Проверяем, есть ли файлы для создания в ответе
                project_structure = extract_project_structure(response)
                
                if project_structure['has_project']:
                    self.console.print("\n🔧 [yellow]Создаю файлы локально...[/yellow]")
                    
                    # Создаем директории
                    for dir_name in project_structure['directories']:
                        result_dir = self.file_ops.mkdir(dir_name, parents=True)
                        if result_dir.get("success"):
                            self.console.print(f"✅ Создана директория: [cyan]{dir_name}[/cyan]")
                        else:
                            self.console.print(f"⚠️ Директория {dir_name}: {result_dir.get('error', 'уже существует')}")
                    
                    # Создаем файлы
                    for file_info in project_structure['files']:
                        filename = file_info['filename']
                        content = file_info['content']
                        
                        # Если есть директория проекта, создаем файл в ней
                        if project_structure['directories']:
                            project_dir = project_structure['directories'][0]
                            file_path = f"{project_dir}/{filename}"
                        else:
                            file_path = filename
                        
                        result_file = self.file_ops.write_file(file_path, content)
                        if result_file.get("success"):
                            self.console.print(f"✅ Создан файл: [green]{file_path}[/green]")
                        else:
                            self.console.print(f"❌ Ошибка создания {file_path}: {result_file.get('error')}")
                    
                    self.console.print(f"\n🎉 [green]Проект создан локально в директории: {self.file_ops.pwd()}[/green]")
                
                # Обновляем статистику
                tokens_used = result.get("tokens_used", {}).get("total", 0)
                model_used = result.get("model_used", self.current_model)
                
                self.session_stats["queries"] += 1
                self.session_stats["total_tokens"] += tokens_used
                
                if tokens_used > 0:
                    self.console.print(f"\n[dim]Токены: {tokens_used} | Модель: {model_used}[/dim]")
                
                return True
            
            elif command == "write":
                if len(args) < 2:
                    self.console.print("❌ Укажите содержимое и имя файла", style="red")
                    return
                
                content = args[0]
                filename = args[1]
                
                result = self.file_ops.write_file(filename, content)
                if result.get("success"):
                    self.console.print(f"✅ {result['message']}", style="green")
                else:
                    self.console.print(f"❌ {result['error']}", style="red")
            
            elif command == "refactor":
                # Рефакторинг существующего файла
                query = args[0] if args else ""
                file_path = extract_file_path(query)
                
                if file_path:
                    # Читаем существующий файл
                    file_result = self.file_ops.cat(file_path)
                    if file_result.get("success"):
                        current_code = file_result["content"]
                        self.console.print(f"📄 Читаю файл: [cyan]{file_path}[/cyan]")
                        
                        # Отправляем код на рефакторинг через AI
                        refactor_prompt = f"""Прочитай и улучши этот Python код:

```python
{current_code}
```

Сделай рефакторинг:
1. Улучши структуру и читаемость
2. Добавь комментарии  
3. Оптимизируй код
4. Следуй PEP 8

Верни ТОЛЬКО улучшенный код в формате ```python"""

                        self.console.print("🤖 [dim]Рефакторинг через 3 AI модели...[/dim]")
                        
                        result = self.client.query(
                            prompt=refactor_prompt,
                            model=self.current_model
                        )
                        
                        response = result["response"]
                        
                        # Парсим улучшенный код
                        project_structure = extract_project_structure(response)
                        if project_structure['files']:
                            improved_code = project_structure['files'][0]['content']
                            backup_path = f"{file_path}.backup"
                            
                            # Создаем бэкап
                            self.file_ops.cp(file_path, backup_path)
                            self.console.print(f"💾 Бэкап создан: [yellow]{backup_path}[/yellow]")
                            
                            # Сохраняем улучшенный код
                            write_result = self.file_ops.write_file(file_path, improved_code)
                            if write_result.get("success"):
                                self.console.print(f"✅ Рефакторинг завершен: [green]{file_path}[/green]")
                            else:
                                self.console.print(f"❌ Ошибка сохранения: {write_result.get('error')}")
                        else:
                            self.print_with_pager(response, is_markdown=True)
                        
                        # Статистика
                        tokens_used = result.get("tokens_used", {}).get("total", 0)
                        model_used = result.get("model_used", self.current_model)
                        self.session_stats["queries"] += 1
                        self.session_stats["total_tokens"] += tokens_used
                        if tokens_used > 0:
                            self.console.print(f"\n[dim]Токены: {tokens_used} | Модель: {model_used}[/dim]")
                    else:
                        self.console.print(f"❌ Не удалось прочитать файл: {file_result.get('error')}")
                else:
                    self.console.print("❌ Не удалось найти путь к файлу в запросе")
            
            elif command == "read_and_analyze":
                # Чтение и анализ файла
                query = args[0] if args else ""
                file_path = extract_file_path(query)
                
                if file_path:
                    file_result = self.file_ops.cat(file_path)
                    if file_result.get("success"):
                        self.console.print(f"📄 [cyan]{file_result['file_path']}[/cyan]:")
                        self.console.print(Panel(file_result["content"], border_style="blue"))
                        
                        # Анализ через AI если запрашивается
                        if any(word in query.lower() for word in ['анализируй', 'analyze', 'что делает', 'объясни']):
                            analyze_prompt = f"Проанализируй код и объясни что он делает:\n\n```python\n{file_result['content']}\n```"
                            
                            self.console.print("\n🤖 [dim]Анализирую код через AI...[/dim]")
                            result = self.client.query(prompt=analyze_prompt, model=self.current_model)
                            
                            try:
                                self.console.print(Markdown(result["response"]))
                            except:
                                self.console.print(result["response"])
                            
                            # Статистика
                            tokens_used = result.get("tokens_used", {}).get("total", 0)
                            model_used = result.get("model_used", self.current_model)
                            self.session_stats["queries"] += 1
                            self.session_stats["total_tokens"] += tokens_used
                            if tokens_used > 0:
                                self.console.print(f"\n[dim]Токены: {tokens_used} | Модель: {model_used}[/dim]")
                    else:
                        self.console.print(f"❌ Не удалось прочитать файл: {file_result.get('error')}")
                else:
                    self.console.print("❌ Не удалось найти путь к файлу в запросе")
        
        except Exception as e:
            self.console.print(f"❌ Ошибка выполнения команды: {e}", style="red")
    
    def handle_query(self, query: str):
        """Обработать пользовательский запрос"""
        try:
            # Проверяем, является ли запрос файловой командой
            file_command = detect_file_command(query)
            
            if file_command:
                # Выполняем файловую операцию локально
                self.handle_file_command(file_command)
                return True
            
            # Если не файловая команда, отправляем к AI
            self.console.print("🤖 [dim]Обработка запроса...[/dim]")
            
            result = self.client.query(
                prompt=query,
                model=self.current_model
            )
            
            # Показываем ответ
            response = result["response"]
            model_used = result.get("model_used", self.current_model)
            tokens_used = result.get("tokens_used", {}).get("total", 0)
            
            # Рендерим ответ с пейджером
            self.print_with_pager(response, is_markdown=True)
            
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