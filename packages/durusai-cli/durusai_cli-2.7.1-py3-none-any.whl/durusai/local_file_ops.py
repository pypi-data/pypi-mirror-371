"""
Локальные файловые операции для DurusAI CLI
Выполняются на машине пользователя, а не на сервере
"""
import os
import shutil
import stat
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class LocalFileOperations:
    """Менеджер локальных файловых операций"""
    
    def __init__(self):
        self.current_dir = Path.cwd()
    
    def pwd(self) -> str:
        """Получить текущую директорию"""
        return str(self.current_dir.resolve())
    
    def ls(self, path: Optional[str] = None, show_hidden: bool = False) -> Dict[str, Any]:
        """Список файлов в директории"""
        try:
            target_path = Path(path) if path else self.current_dir
            
            if not target_path.exists():
                return {"error": f"Путь '{target_path}' не существует"}
            
            if not target_path.is_dir():
                return {"error": f"'{target_path}' не является директорией"}
            
            files = []
            for item in target_path.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                stat_info = item.stat()
                files.append({
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": stat_info.st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "permissions": stat.filemode(stat_info.st_mode),
                    "path": str(item)
                })
            
            # Сортируем: директории сначала, потом по имени
            files.sort(key=lambda x: (x["type"] != "dir", x["name"].lower()))
            
            return {
                "current_dir": str(target_path.resolve()),
                "files": files,
                "total_count": len(files)
            }
            
        except PermissionError:
            return {"error": "Нет доступа к директории"}
        except Exception as e:
            return {"error": f"Ошибка: {str(e)}"}
    
    def cd(self, path: str) -> Dict[str, Any]:
        """Сменить текущую директорию"""
        try:
            new_path = Path(path).resolve()
            
            if not new_path.exists():
                return {"error": f"Директория '{path}' не существует"}
            
            if not new_path.is_dir():
                return {"error": f"'{path}' не является директорией"}
            
            self.current_dir = new_path
            os.chdir(str(new_path))
            
            return {
                "success": True,
                "new_dir": str(new_path),
                "message": f"Перешли в директорию: {new_path}"
            }
            
        except PermissionError:
            return {"error": "Нет доступа к директории"}
        except Exception as e:
            return {"error": f"Ошибка: {str(e)}"}
    
    def mkdir(self, path: str, parents: bool = False) -> Dict[str, Any]:
        """Создать директорию"""
        try:
            new_path = Path(path)
            
            if new_path.exists():
                return {"error": f"Путь '{path}' уже существует"}
            
            new_path.mkdir(parents=parents, exist_ok=False)
            
            return {
                "success": True,
                "created": str(new_path.resolve()),
                "message": f"Директория создана: {new_path}"
            }
            
        except PermissionError:
            return {"error": "Нет прав для создания директории"}
        except Exception as e:
            return {"error": f"Ошибка: {str(e)}"}
    
    def cat(self, path: str, lines: Optional[int] = None) -> Dict[str, Any]:
        """Прочитать содержимое файла"""
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                return {"error": f"Файл '{path}' не существует"}
            
            if not file_path.is_file():
                return {"error": f"'{path}' не является файлом"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if lines:
                content_lines = content.split('\n')[:lines]
                content = '\n'.join(content_lines)
            
            return {
                "success": True,
                "content": content,
                "file_path": str(file_path.resolve()),
                "size": file_path.stat().st_size
            }
            
        except UnicodeDecodeError:
            return {"error": "Файл содержит недопустимые символы (бинарный файл?)"}
        except PermissionError:
            return {"error": "Нет доступа к файлу"}
        except Exception as e:
            return {"error": f"Ошибка: {str(e)}"}
    
    def write_file(self, path: str, content: str, append: bool = False) -> Dict[str, Any]:
        """Записать содержимое в файл"""
        try:
            file_path = Path(path)
            
            # Создаем родительские директории если нужно
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": str(file_path.resolve()),
                "message": f"Файл {'дописан' if append else 'создан'}: {file_path}",
                "size": file_path.stat().st_size
            }
            
        except PermissionError:
            return {"error": "Нет прав для записи файла"}
        except Exception as e:
            return {"error": f"Ошибка: {str(e)}"}
    
    def rm(self, path: str, recursive: bool = False, force: bool = False) -> Dict[str, Any]:
        """Удалить файл или директорию с поддержкой wildcards"""
        try:
            import glob
            
            # Если путь содержит wildcard
            if '*' in path or '?' in path or '[' in path:
                # Используем glob для поиска файлов
                matches = glob.glob(path)
                
                if not matches:
                    return {"error": f"Файлы по паттерну '{path}' не найдены"}
                
                deleted_count = 0
                errors = []
                
                for match_path in matches:
                    result = self.rm(match_path, recursive, force)
                    if result.get("success"):
                        deleted_count += 1
                    else:
                        errors.append(f"{match_path}: {result.get('error')}")
                
                if errors and not force:
                    return {"error": f"Удалено {deleted_count} файлов, ошибки: {'; '.join(errors)}"}
                else:
                    return {
                        "success": True,
                        "message": f"Удалено файлов: {deleted_count}"
                    }
            
            # Обычное удаление одного файла/директории
            target_path = Path(path)
            
            if not target_path.exists():
                if force:
                    return {"success": True, "message": f"Файл не существует (игнорировано): {path}"}
                else:
                    return {"error": f"Путь '{path}' не существует"}
            
            if target_path.is_file():
                target_path.unlink()
                return {
                    "success": True,
                    "message": f"Файл удален: {path}"
                }
            
            elif target_path.is_dir():
                if recursive:
                    shutil.rmtree(target_path)
                    return {
                        "success": True,
                        "message": f"Директория удалена: {path}"
                    }
                else:
                    try:
                        target_path.rmdir()
                        return {
                            "success": True,
                            "message": f"Пустая директория удалена: {path}"
                        }
                    except OSError:
                        return {"error": f"Директория не пуста. Используйте рекурсивное удаление (-r)"}
            
        except PermissionError:
            return {"error": "Нет прав для удаления"}
        except Exception as e:
            return {"error": f"Ошибка: {str(e)}"}
    
    def cp(self, src: str, dst: str) -> Dict[str, Any]:
        """Копировать файл или директорию"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                return {"error": f"Источник '{src}' не существует"}
            
            if src_path.is_file():
                # Если целевой путь - директория, копируем файл в неё
                if dst_path.is_dir():
                    dst_path = dst_path / src_path.name
                
                shutil.copy2(src_path, dst_path)
                return {
                    "success": True,
                    "message": f"Файл скопирован: {src} → {dst_path}"
                }
            
            elif src_path.is_dir():
                shutil.copytree(src_path, dst_path)
                return {
                    "success": True,
                    "message": f"Директория скопирована: {src} → {dst_path}"
                }
                
        except PermissionError:
            return {"error": "Нет прав для копирования"}
        except FileExistsError:
            return {"error": f"Целевой путь '{dst}' уже существует"}
        except Exception as e:
            return {"error": f"Ошибка: {str(e)}"}
    
    def mv(self, src: str, dst: str) -> Dict[str, Any]:
        """Переместить/переименовать файл или директорию"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                return {"error": f"Источник '{src}' не существует"}
            
            # Если целевой путь - существующая директория, перемещаем в неё
            if dst_path.is_dir():
                dst_path = dst_path / src_path.name
            
            shutil.move(str(src_path), str(dst_path))
            
            return {
                "success": True,
                "message": f"Перемещено: {src} → {dst_path}"
            }
            
        except PermissionError:
            return {"error": "Нет прав для перемещения"}
        except Exception as e:
            return {"error": f"Ошибка: {str(e)}"}
    
    def tree(self, path: Optional[str] = None, max_depth: int = 3) -> Dict[str, Any]:
        """Показать структуру директории в виде дерева"""
        try:
            root_path = Path(path) if path else self.current_dir
            
            if not root_path.exists():
                return {"error": f"Путь '{path}' не существует"}
            
            if not root_path.is_dir():
                return {"error": f"'{path}' не является директорией"}
            
            def build_tree(current_path: Path, depth: int = 0, prefix: str = "") -> List[str]:
                if depth > max_depth:
                    return []
                
                items = []
                try:
                    children = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                    
                    for i, child in enumerate(children):
                        is_last = i == len(children) - 1
                        current_prefix = "└── " if is_last else "├── "
                        next_prefix = "    " if is_last else "│   "
                        
                        icon = "📁" if child.is_dir() else "📄"
                        items.append(f"{prefix}{current_prefix}{icon} {child.name}")
                        
                        if child.is_dir() and depth < max_depth:
                            items.extend(build_tree(child, depth + 1, prefix + next_prefix))
                            
                except PermissionError:
                    items.append(f"{prefix}├── ❌ [Permission Denied]")
                
                return items
            
            tree_lines = [f"📁 {root_path.name}/"]
            tree_lines.extend(build_tree(root_path))
            
            return {
                "success": True,
                "tree": "\n".join(tree_lines),
                "root_path": str(root_path.resolve())
            }
            
        except Exception as e:
            return {"error": f"Ошибка: {str(e)}"}


def detect_file_command(query: str) -> Optional[Dict[str, Any]]:
    """Определить, является ли запрос файловой командой"""
    query_lower = query.lower().strip()
    
    # Команды текущей директории
    if query_lower in ['pwd', 'где я', 'текущая директория', 'current directory']:
        return {"command": "pwd", "args": []}
    
    # Команды списка файлов
    if query_lower in ['ls', 'dir', 'список файлов', 'файлы', 'покажи файлы']:
        return {"command": "ls", "args": []}
    
    if query_lower in ['ls -la', 'ls -lah', 'ls -al', 'подробный список']:
        return {"command": "ls", "args": ["-la"]}
    
    if query_lower.startswith('ls '):
        args = query_lower[3:].strip()
        return {"command": "ls", "args": [args] if args else []}
    
    # Команды смены директории
    if query_lower.startswith('cd '):
        path = query[3:].strip()
        return {"command": "cd", "args": [path]}
    
    if query_lower.startswith('перейди в '):
        path = query[10:].strip()
        return {"command": "cd", "args": [path]}
    
    # Команды создания директории
    if query_lower.startswith('mkdir '):
        path = query[6:].strip()
        return {"command": "mkdir", "args": [path]}
    
    if query_lower.startswith('создай папку '):
        path = query[13:].strip()
        return {"command": "mkdir", "args": [path]}
    
    # Команды чтения файлов
    if query_lower.startswith('cat '):
        path = query[4:].strip()
        return {"command": "cat", "args": [path]}
    
    if query_lower.startswith('покажи содержимое '):
        path = query[18:].strip()
        return {"command": "cat", "args": [path]}
    
    # Команда дерева
    if query_lower in ['tree', 'дерево', 'структура']:
        return {"command": "tree", "args": []}
    
    if query_lower.startswith('tree '):
        path = query[5:].strip()
        return {"command": "tree", "args": [path]}
    
    # Команды удаления с улучшенным парсингом
    if query_lower.startswith('rm '):
        # Парсим rm с флагами
        parts = query[3:].strip().split()
        recursive = False
        force = False
        files_to_remove = []
        
        for part in parts:
            if part.startswith('-'):
                if 'r' in part or 'R' in part:
                    recursive = True
                if 'f' in part:
                    force = True
            else:
                files_to_remove.append(part)
        
        return {"command": "rm", "args": files_to_remove, "recursive": recursive, "force": force}
    
    # Естественные команды удаления
    natural_delete_patterns = [
        'удали все файлы', 'удалить все файлы', 'очисти директорию', 'очистить директорию',
        'delete all files', 'remove all files', 'clean directory', 'clear folder',
        'удали файлы', 'удалить файлы', 'remove files', 'delete files'
    ]
    
    for pattern in natural_delete_patterns:
        if pattern in query_lower:
            if 'все' in query_lower or 'all' in query_lower:
                return {"command": "rm", "args": ["*"], "recursive": True, "force": False}
            else:
                return {"command": "rm_interactive", "args": [query]}
    
    if query_lower.startswith('удали '):
        path = query[6:].strip()
        return {"command": "rm", "args": [path], "recursive": False, "force": False}
    
    # Команды копирования
    if query_lower.startswith('cp '):
        args = query[3:].strip().split()
        if len(args) >= 2:
            return {"command": "cp", "args": args}
    
    # Команды перемещения
    if query_lower.startswith('mv '):
        args = query[3:].strip().split()
        if len(args) >= 2:
            return {"command": "mv", "args": args}
    
    # Все файловые команды (создание, рефакторинг, чтение)
    file_operation_patterns = [
        # Создание
        'создай файл', 'создать файл', 'напиши код', 'создай код',
        'создай проект', 'создать проект', 'создай игру', 'создать игру', 
        'создай приложение', 'создать приложение', 'write file', 'create file',
        'создай скрипт', 'создать скрипт', 'напиши программу',
        'проект игры', 'игру в', 'игру на', 'приложение на',
        'программу на', 'код для', 'скрипт для', 'создай', 'напиши',
        'в этой директории создай', 'создай в', 'создать в',
        'сделай тут', 'сделай код', 'сделай игру', 'сделать код',
        'тут код', 'здесь код', 'код игры', 'игры в', 'игры на',
        'make code', 'write code', 'create code', 'build game',
        'сделай приложение', 'сделать приложение',
        
        # Рефакторинг и редактирование
        'рефактор', 'рефакторинг', 'улучши код', 'улучшить код', 'исправь код',
        'исправить код', 'переписать код', 'переписи код', 'оптимизируй',
        'сделай рефактор', 'refactor', 'improve code', 'fix code',
        'обнови код', 'обновить код', 'модифицируй', 'изменить код',
        
        # Чтение и анализ файлов  
        'читай файл', 'прочитай файл', 'покажи файл', 'анализируй файл',
        'read file', 'show file', 'analyze file', 'проанализируй',
        'что в файле', 'содержимое файла', 'file content',
        
        # Работа с конкретными файлами
        'файл main.py', 'файл .py', '.py находится', 'в файле',
        'с файлом', 'для файла', 'этот файл'
    ]
    
    if any(phrase in query_lower for phrase in file_operation_patterns):
        # Определяем тип операции
        if any(word in query_lower for word in ['рефактор', 'улучши', 'исправь', 'оптимизируй', 'refactor', 'improve', 'fix']):
            return {"command": "refactor", "args": [query]}
        elif any(word in query_lower for word in ['читай', 'прочитай', 'покажи', 'анализируй', 'read', 'show', 'analyze']):
            return {"command": "read_and_analyze", "args": [query]}
        else:
            return {"command": "create_project", "args": [query]}
    
    # Команды записи в файл
    if query_lower.startswith('echo ') and ' > ' in query:
        parts = query[5:].split(' > ', 1)
        if len(parts) == 2:
            return {"command": "write", "args": [parts[0].strip(), parts[1].strip()]}
    
    return None


def extract_file_path(query: str) -> Optional[str]:
    """Извлечь путь к файлу из запроса пользователя"""
    import re
    
    # Паттерны для поиска путей к файлам
    path_patterns = [
        r'файл\s+([^\s]+\.py)',              # файл main.py
        r'([^\s]*\.py)\s+находится',         # main.py находится
        r'находится\s+в\s+([^\s]+/[^\s]*)',  # находится в /path/file
        r'/([^\s]+\.py)',                    # /path/to/file.py
        r'([a-zA-Z_][a-zA-Z0-9_]*\.py)',     # любой .py файл
        r'([^\s]+/[^\s]*\.py)',              # path/file.py
    ]
    
    for pattern in path_patterns:
        matches = re.findall(pattern, query, re.IGNORECASE)
        for match in matches:
            # Очищаем путь
            file_path = match.strip().rstrip(',').rstrip('.')
            if file_path and '.' in file_path:
                return file_path
    
    return None


def format_file_list(files_info: Dict[str, Any]) -> str:
    """Форматировать список файлов для отображения"""
    if "error" in files_info:
        return f"❌ {files_info['error']}"
    
    files = files_info["files"]
    current_dir = files_info["current_dir"]
    
    if not files:
        return f"📁 Директория пуста: {current_dir}"
    
    result = [f"📁 Файлы в {current_dir}:"]
    
    for file_info in files:
        icon = "📁" if file_info["type"] == "dir" else "📄"
        name = file_info["name"]
        size = f" ({file_info['size']} bytes)" if file_info["type"] == "file" and file_info["size"] > 0 else ""
        modified = file_info["modified"]
        
        result.append(f"   {icon} {name}{size} | {modified}")
    
    result.append(f"\nВсего элементов: {files_info['total_count']}")
    
    return "\n".join(result)


def parse_code_blocks(ai_response: str) -> List[Dict[str, str]]:
    """Извлечь блоки кода из ответа AI для создания файлов"""
    import re
    
    files = []
    
    # Более широкие паттерны для поиска блоков кода
    patterns = [
        # Основные Python файлы
        r'```(?:python|py)\s+([^\n]+\.py[:\s]*)\n(.*?)```',
        r'[Фф]айл\s+([^\s:]+\.py):?\s*```(?:python|py)?\n(.*?)```',
        r'([a-zA-Z_][a-zA-Z0-9_]*\.py)\s*```(?:python|py)?\n(.*?)```',
        r'[Сс]оздаем?\s+([^\s:]+\.py):?\s*```(?:python|py)?\n(.*?)```',
        
        # Ищем любые блоки кода с .py файлами (широкий поиск)
        r'```python\n([^`]+)```\s*[^\n]*([a-zA-Z_][a-zA-Z0-9_]*\.py)',
        r'```python\n(.*?)```',  # Любой Python блок
        
        # HTML/JS/CSS файлы
        r'```(?:html)\s+([^\n]+\.html[:\s]*)\n(.*?)```',
        r'[Фф]айл\s+([^\s:]+\.html):?\s*```(?:html)?\n(.*?)```',
        r'```(?:javascript|js)\s+([^\n]+\.js[:\s]*)\n(.*?)```',
        r'[Фф]айл\s+([^\s:]+\.js):?\s*```(?:javascript|js)?\n(.*?)```',
        r'```(?:css)\s+([^\n]+\.css[:\s]*)\n(.*?)```',
        r'[Фф]айл\s+([^\s:]+\.css):?\s*```(?:css)?\n(.*?)```',
        
        # Конфиг файлы  
        r'```(?:json)\s+([^\n]+\.json[:\s]*)\n(.*?)```',
        r'```(?:markdown|md)\s+([^\n]+\.md[:\s]*)\n(.*?)```',
        r'[Фф]айл\s+([^\s:]+\.(?:json|md|txt|yml|yaml|cfg)):?\s*```[^\n]*\n(.*?)```',
        
        # Универсальные паттерны
        r'```[a-zA-Z]*\n(.*?)```',  # Любой блок кода
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, ai_response, re.DOTALL | re.IGNORECASE)
        for match in matches:
            if len(match) == 2:
                filename = match[0].strip().rstrip(':').strip()
                content = match[1].strip()
            elif len(match) == 1:
                # Для паттернов без имени файла
                content = match[0].strip()
                # Пытаемся угадать имя файла из контекста
                if 'chess' in ai_response.lower() or 'шахмат' in ai_response.lower():
                    filename = 'chess_game.py'
                elif 'card' in ai_response.lower() or 'карт' in ai_response.lower():
                    filename = 'card_game.py'
                elif 'checkers' in ai_response.lower() or 'шашк' in ai_response.lower():
                    filename = 'checkers.py'
                elif 'game' in ai_response.lower() or 'игр' in ai_response.lower():
                    filename = 'game.py'
                else:
                    filename = 'main.py'
            else:
                continue
            
            # Очищаем имя файла от лишних символов
            filename = re.sub(r'^[^\w\.]', '', filename)
            
            if filename and content and not any(f['filename'] == filename for f in files):
                files.append({
                    'filename': filename,
                    'content': content
                })
    
    # Если AI упоминает конкретные файлы, но не дал блоки кода, создаем заглушки
    mentioned_files = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*\.py)', ai_response)
    for mentioned_file in mentioned_files:
        if not any(f['filename'] == mentioned_file for f in files):
            files.append({
                'filename': mentioned_file,
                'content': f'# {mentioned_file} - содержимое файла\n# Сгенерировано DurusAI CLI\n\nprint("Hello from {mentioned_file}!")\n'
            })
    
    return files


def extract_project_structure(ai_response: str) -> Dict[str, Any]:
    """Извлечь структуру проекта из ответа AI"""
    
    # Ищем директории проекта
    import re
    
    project_dirs = []
    dir_patterns = [
        r'[Дд]иректори[ия]\s+([^\s]+)\s+создана',
        r'[Сс]оздаем?\s+директори[ию]\s+([^\s]+)',
        r'mkdir\s+([^\s]+)',
        r'[Пп]апк[ауи]\s+([^\s]+)',
        r'cd\s+([^\s]+)'
    ]
    
    for pattern in dir_patterns:
        matches = re.findall(pattern, ai_response, re.IGNORECASE)
        for match in matches:
            dir_name = match.strip()
            if dir_name and dir_name not in project_dirs:
                project_dirs.append(dir_name)
    
    # Ищем блоки кода
    files = parse_code_blocks(ai_response)
    
    return {
        'directories': project_dirs,
        'files': files,
        'has_project': len(files) > 0 or len(project_dirs) > 0
    }