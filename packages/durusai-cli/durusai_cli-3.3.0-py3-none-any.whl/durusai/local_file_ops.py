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
    """Минимальная детекция - только основные навигационные команды"""
    query_lower = query.lower().strip()
    
    # ТОЛЬКО основные навигационные команды - остальное AI обрабатывает
    if query_lower in ['pwd', 'где я']:
        return {"command": "pwd", "args": []}
    
    if query_lower in ['ls', 'покажи файлы'] or query_lower.startswith('ls '):
        return {"command": "ls", "args": []}
    
    # ВСЕ остальное отправляется на AI
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
    
    # Улучшенные паттерны для блоков кода
    patterns = [
        # Python файлы с именами
        r'```python\s+([^\n]+\.py)\n(.*?)```',  # ```python filename.py
        r'```py\s+([^\n]+\.py)\n(.*?)```',      # ```py filename.py
        
        # Python блоки без имен - угадываем имя по контексту
        r'```python\n(.*?)```',  # ```python (без имени)
        r'```py\n(.*?)```',      # ```py (без имени)
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, ai_response, re.DOTALL | re.IGNORECASE)
        for match in matches:
            if len(match) == 2:
                # Есть имя файла
                filename = match[0].strip().rstrip(':').strip()
                content = match[1].strip()
            elif len(match) == 1:
                # Нет имени - угадываем по контексту
                content = match[0].strip()
                if 'tetris' in ai_response.lower() or 'тетрис' in ai_response.lower():
                    filename = 'tetris.py'
                elif 'chess' in ai_response.lower() or 'шахмат' in ai_response.lower():
                    filename = 'chess.py'
                elif 'checkers' in ai_response.lower() or 'шашк' in ai_response.lower():
                    filename = 'checkers.py'
                elif 'card' in ai_response.lower() or 'карт' in ai_response.lower():
                    filename = 'cards.py'
                elif 'calculator' in ai_response.lower() or 'калькулятор' in ai_response.lower():
                    filename = 'calculator.py'
                else:
                    filename = 'main.py'
            else:
                continue
            
            # Очищаем имя файла
            filename = re.sub(r'^[^\w\.]', '', filename)
            
            if filename and content and not any(f['filename'] == filename for f in files):
                files.append({
                    'filename': filename,
                    'content': content
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


def parse_bash_commands(ai_response: str) -> List[Dict[str, str]]:
    """Извлечь bash команды из ответа AI для выполнения"""
    import re
    
    commands = []
    
    # Паттерны для поиска bash команд
    bash_patterns = [
        r'```bash\n(.*?)```',      # ```bash
        r'```shell\n(.*?)```',     # ```shell  
        r'```\n(cd .*?)```',       # ```cd command
        r'```\n(mkdir .*?)```',    # ```mkdir command
        r'```\n(rm .*?)```',       # ```rm command
        r'```\n(mv .*?)```',       # ```mv command
        r'```\n(cp .*?)```',       # ```cp command
    ]
    
    for pattern in bash_patterns:
        matches = re.findall(pattern, ai_response, re.DOTALL | re.IGNORECASE)
        for match in matches:
            # Разбиваем на отдельные команды по строкам
            lines = match.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    commands.append({
                        'command': line,
                        'type': 'bash'
                    })
    
    # Также ищем прямые команды в тексте
    direct_patterns = [
        r'^(cd [^\n]+)',
        r'^(mkdir [^\n]+)', 
        r'^(rm [^\n]+)',
        r'^(mv [^\n]+)',
        r'^(cp [^\n]+)',
    ]
    
    for pattern in direct_patterns:
        matches = re.findall(pattern, ai_response, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            if not any(c['command'] == match for c in commands):
                commands.append({
                    'command': match,
                    'type': 'direct'
                })
    
    return commands


def execute_bash_command(command: str, file_ops) -> Dict[str, Any]:
    """Выполнить bash команду через LocalFileOperations"""
    parts = command.strip().split()
    if not parts:
        return {"error": "Пустая команда"}
    
    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    try:
        if cmd == 'cd':
            if args:
                return file_ops.cd(args[0])
            else:
                return {"error": "cd: отсутствует аргумент"}
        
        elif cmd == 'mkdir':
            if args:
                return file_ops.mkdir(args[0], parents=True)
            else:
                return {"error": "mkdir: отсутствует аргумент"}
        
        elif cmd == 'rm':
            if args:
                # Парсим флаги rm
                recursive = False
                force = False
                files = []
                
                for arg in args:
                    if arg.startswith('-'):
                        if 'r' in arg:
                            recursive = True
                        if 'f' in arg:
                            force = True
                    else:
                        files.append(arg)
                
                if files:
                    return {"requires_confirmation": True, "command": command, "args": files, "recursive": recursive, "force": force}
                else:
                    return {"error": "rm: не указаны файлы для удаления"}
            else:
                return {"error": "rm: отсутствуют аргументы"}
        
        elif cmd == 'mv':
            if len(args) >= 2:
                return file_ops.mv(args[0], args[1])
            else:
                return {"error": "mv: нужны источник и назначение"}
        
        elif cmd == 'cp':
            if len(args) >= 2:
                return file_ops.cp(args[0], args[1])
            else:
                return {"error": "cp: нужны источник и назначение"}
        
        else:
            return {"error": f"Команда '{cmd}' не поддерживается"}
    
    except Exception as e:
        return {"error": f"Ошибка выполнения '{command}': {str(e)}"}