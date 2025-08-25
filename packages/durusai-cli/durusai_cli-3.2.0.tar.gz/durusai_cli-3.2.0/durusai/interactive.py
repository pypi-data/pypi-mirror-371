"""
Простой интерактивный режим для DurusAI CLI
"""
from typing import Optional, List, Dict, Any
import sys

from .config import Config
from .api_client import SyncDurusAIClient
from .exceptions import AuthenticationError, NetworkError
from .local_file_ops import LocalFileOperations, detect_file_command, format_file_list, extract_project_structure, extract_file_path, parse_bash_commands, execute_bash_command
from .simple_console import colored_print, show_welcome, show_help, show_session_stats, show_exit_stats, simple_input


class InteractiveMode:
    """Простой интерактивный режим чата с AI - как обычный терминал"""
    
    def __init__(self, client: SyncDurusAIClient, config: Config, 
                 default_model: Optional[str] = None):
        self.client = client
        self.config = config
        
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
        self.last_response = ""  # Для команды /copy
        self.auto_execute = True  # Автоматическое выполнение AI команд
    
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
            show_help()
        
        elif command == '/clear':
            self.conversation_history.clear()
            colored_print("✅ История разговора очищена", "green")
        
        elif command == '/model':
            if args:
                self.current_model = args[0]
                colored_print(f"✅ Модель изменена на: {self.current_model}", "green")
            else:
                colored_print(f"📋 Текущая модель: {self.current_model}", "cyan")
        
        elif command == '/history':
            self.show_history()
        
        elif command == '/stats':
            show_session_stats(self.session_stats["queries"], self.session_stats["total_tokens"])
        
        elif command == '/copy':
            if self.last_response:
                filename = args[0] if args else "last_response.md"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(self.last_response)
                    colored_print(f"✅ Ответ сохранен в: {filename}", "green")
                except Exception as e:
                    colored_print(f"❌ Ошибка сохранения: {e}", "red")
            else:
                colored_print("❌ Нет ответа для сохранения", "yellow")
        
        elif command == '/auto':
            self.auto_execute = not self.auto_execute
            status = "включено" if self.auto_execute else "отключено"
            colored_print(f"🔧 Автоисполнение AI команд {status}", "cyan")
        
        else:
            colored_print(f"❓ Неизвестная команда: {command}", "red")
            colored_print("💡 Используйте /help для списка команд", "yellow")
        
        return True
    
    def show_history(self):
        """Показать историю разговора"""
        if not self.conversation_history:
            colored_print("📭 История пуста", "yellow")
            return
        
        print("\n📜 История разговора:")
        print("=" * 50)
        
        for i, entry in enumerate(self.conversation_history, 1):
            print(f"\n🔷 Запрос #{i}:")
            print(entry["query"])
            print(f"\n🤖 Ответ ({entry['model']}):")
            print(entry["response"])
            print("-" * 50)
    
    def analyze_project_structure(self, directory: str) -> str:
        """Анализ структуры проекта в директории"""
        try:
            from pathlib import Path
            dir_path = Path(directory)
            
            info = []
            
            # Проверяем тип проекта
            if (dir_path / ".git").exists():
                info.append("Git repository")
            
            if (dir_path / "package.json").exists():
                info.append("Node.js project")
            
            if (dir_path / "requirements.txt").exists():
                info.append("Python project with requirements")
            
            if (dir_path / "pyproject.toml").exists():
                info.append("Python project with pyproject.toml")
            
            if (dir_path / "setup.py").exists():
                info.append("Python package")
            
            # Анализируем содержимое
            files = list(dir_path.iterdir())
            py_files = [f for f in files if f.suffix == '.py']
            js_files = [f for f in files if f.suffix in ['.js', '.ts']]
            
            if py_files:
                info.append(f"Python files: {len(py_files)}")
            if js_files:
                info.append(f"JavaScript/TypeScript files: {len(js_files)}")
            
            return "; ".join(info) if info else "Empty directory"
            
        except Exception:
            return "Unknown structure"
    
    def handle_file_command(self, file_command: Dict[str, Any]):
        """Обработать файловую команду локально"""
        command = file_command["command"]
        args = file_command.get("args", [])
        
        try:
            if command == "pwd":
                current_dir = self.file_ops.pwd()
                colored_print(f"📁 Текущая директория: {current_dir}", "cyan")
            
            elif command == "ls":
                show_details = "-la" in args or "-lah" in args or "-al" in args
                path = None
                
                for arg in args:
                    if not arg.startswith('-'):
                        path = arg
                        break
                
                files_info = self.file_ops.ls(path, show_hidden=show_details)
                formatted_output = format_file_list(files_info)
                print(formatted_output)
            
            elif command == "cd":
                if not args:
                    colored_print("❌ Укажите директорию для перехода", "red")
                    return
                
                result = self.file_ops.cd(args[0])
                if result.get("success"):
                    colored_print(f"✅ {result['message']}", "green")
                else:
                    colored_print(f"❌ {result['error']}", "red")
            
            elif command == "tree":
                path = args[0] if args else None
                result = self.file_ops.tree(path)
                if result.get("success"):
                    print(result["tree"])
                else:
                    colored_print(f"❌ {result['error']}", "red")
            
            elif command == "smart_file_operation":
                # Универсальная обработка файловых операций через 3 AI модели
                query = args[0] if args else ""
                current_dir = self.file_ops.pwd()
                
                # Анализируем структуру проекта
                project_info = self.analyze_project_structure(current_dir)
                
                # Формируем контекстный запрос для 3 AI моделей
                smart_prompt = f"""Ты работаешь как Claude Code в локальной директории пользователя.

ТЕКУЩАЯ ДИРЕКТОРИЯ: {current_dir}
СТРУКТУРА ПРОЕКТА: {project_info}

ПОЛЬЗОВАТЕЛЬ ПРОСИТ: {query}

ИНСТРУКЦИЯ: 
1. Анализируй запрос - что нужно создать/изменить
2. Определи правильную директорию для файлов
3. Создай код с правильными именами файлов
4. Используй формат ```python filename.py

ОБЯЗАТЕЛЬНО: создавай файлы в текущей директории {current_dir}, НЕ в /app/workspace!

Создай полный код проекта:"""

                colored_print("🤖 Анализ через 3 AI модели (Claude/GPT/Gemini)...", "blue")
                
                # Отправляем на 3 AI модели
                result = self.client.query(
                    prompt=smart_prompt,
                    model=self.current_model
                )
                
                response = result["response"]
                
                # Выводим ответ AI как простой текст
                print(response)
                self.last_response = response
                
                # Парсим и создаем файлы локально
                project_structure = extract_project_structure(response)
                
                if project_structure['has_project']:
                    colored_print("\n🔧 Создаю файлы локально в текущей директории...", "yellow")
                    
                    # Создаем директории проекта
                    for dir_name in project_structure['directories']:
                        result_dir = self.file_ops.mkdir(dir_name, parents=True)
                        if result_dir.get("success"):
                            colored_print(f"✅ Создана директория: {current_dir}/{dir_name}", "green")
                    
                    # Создаем файлы в текущей директории
                    created_files = []
                    for file_info in project_structure['files']:
                        filename = file_info['filename']
                        content = file_info['content']
                        
                        # Определяем путь
                        if project_structure['directories']:
                            project_dir = project_structure['directories'][0]
                            file_path = f"{project_dir}/{filename}"
                        else:
                            file_path = filename
                        
                        result_file = self.file_ops.write_file(file_path, content)
                        if result_file.get("success"):
                            full_path = f"{current_dir}/{file_path}"
                            colored_print(f"✅ Создан файл: {full_path}", "green")
                            created_files.append(full_path)
                    
                    if created_files:
                        colored_print(f"\n🎉 Проект создан локально в: {current_dir}", "green")
                        colored_print(f"📁 Создано файлов: {len(created_files)}", "cyan")
                
                # Статистика
                tokens_used = result.get("tokens_used", {}).get("total", 0)
                model_used = result.get("model_used", self.current_model)
                self.session_stats["queries"] += 1
                self.session_stats["total_tokens"] += tokens_used
                
                if tokens_used > 0:
                    print(f"\nТокены: {tokens_used} | Модель: {model_used}")
                
                return True
        
        except Exception as e:
            colored_print(f"❌ Ошибка выполнения команды: {e}", "red")
    
    def handle_query(self, query: str):
        """Обработать пользовательский запрос"""
        try:
            # Проверяем, является ли запрос файловой командой
            file_command = detect_file_command(query)
            
            if file_command:
                # Выполняем файловую операцию локально
                self.handle_file_command(file_command)
                return True
            
            # Все запросы отправляем к AI с контекстом локальной директории
            colored_print("🤖 Обработка запроса...", "blue")
            
            # Добавляем контекст текущей директории для AI
            current_dir = self.file_ops.pwd()
            project_info = self.analyze_project_structure(current_dir)
            
            # Формируем запрос с полным контекстом
            contextual_prompt = f"""Ты работаешь как Claude Code в локальной директории пользователя.

ТЕКУЩАЯ ДИРЕКТОРИЯ: {current_dir}
СТРУКТУРА ПРОЕКТА: {project_info}

ПОЛЬЗОВАТЕЛЬ ПРОСИТ: {query}

ИНСТРУКЦИЯ: Анализируй запрос и выполняй нужные действия:
- Для вопросов - отвечай как AI консультант
- Для файловых операций - давай инструкции с кодом
- ВСЕГДА работай в контексте директории {current_dir}
- НЕ упоминай Docker или /app/workspace

Выполни запрос пользователя:"""

            result = self.client.query(
                prompt=contextual_prompt,
                model=self.current_model
            )
            
            # Показываем ответ
            response = result["response"]
            model_used = result.get("model_used", self.current_model)
            tokens_used = result.get("tokens_used", {}).get("total", 0)
            
            # Выводим ответ как простой текст
            print(response)
            self.last_response = response
            
            # Парсим и выполняем команды из ответа AI
            commands = parse_bash_commands(response)
            if commands:
                colored_print(f"\n🔧 Найдено команд для выполнения: {len(commands)}", "yellow")
                
                for cmd_info in commands:
                    command = cmd_info['command']
                    colored_print(f"▶️ {command}", "cyan")
                    
                    if self.auto_execute:
                        # Автоматическое выполнение
                        result = execute_bash_command(command, self.file_ops)
                        if result.get("success"):
                            colored_print(f"✅ {result.get('message', 'Выполнено')}", "green")
                        else:
                            colored_print(f"❌ {result.get('error', 'Ошибка')}", "red")
                    else:
                        # Спрашиваем подтверждение
                        try:
                            confirm = input(f"Выполнить команду '{command}'? (y/n): ")
                            if confirm.lower() in ['y', 'yes', 'да']:
                                result = execute_bash_command(command, self.file_ops)
                                if result.get("success"):
                                    colored_print(f"✅ {result.get('message', 'Выполнено')}", "green")
                                else:
                                    colored_print(f"❌ {result.get('error', 'Ошибка')}", "red")
                        except (EOFError, KeyboardInterrupt):
                            colored_print("❌ Отменено", "yellow")
                            break
            
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
                print(f"\nТокены: {tokens_used} | Модель: {model_used}")
            
        except AuthenticationError:
            colored_print("❌ Токен истек, выход из интерактивного режима", "red")
            return False
        
        except NetworkError as e:
            colored_print(f"🌐 Ошибка сети: {e}", "red")
            return True
        
        except Exception as e:
            colored_print(f"💥 Ошибка: {e}", "red")
            return True
        
        return True
    
    def run(self):
        """Запустить интерактивный режим"""
        show_welcome()
        
        try:
            while True:
                try:
                    # Простой терминальный ввод с поддержкой readline
                    user_input = simple_input()
                    
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
                    
                    print()  # Пустая строка для читаемости
                    
                except KeyboardInterrupt:
                    colored_print("\n💡 Используйте /quit для выхода", "yellow")
                    continue
                    
        except (EOFError, KeyboardInterrupt):
            pass
        
        # Показываем статистику при выходе
        show_exit_stats(self.session_stats["queries"], self.session_stats["total_tokens"])