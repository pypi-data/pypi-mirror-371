"""
Простая замена Rich Console для обычного терминального вывода
"""

class Colors:
    """ANSI цветовые коды для терминала"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Цвета текста
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Цвета фона
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


def colored_print(text: str, color: str = "", style: str = ""):
    """Простой цветной вывод"""
    ansi_color = ""
    
    if color == "red":
        ansi_color = Colors.RED
    elif color == "green":
        ansi_color = Colors.GREEN
    elif color == "yellow":
        ansi_color = Colors.YELLOW
    elif color == "blue":
        ansi_color = Colors.BLUE
    elif color == "cyan":
        ansi_color = Colors.CYAN
    
    if style == "bold":
        ansi_color += Colors.BOLD
    elif style == "dim":
        ansi_color += Colors.DIM
    
    if ansi_color:
        print(f"{ansi_color}{text}{Colors.RESET}")
    else:
        print(text)


def show_welcome():
    """Приветственное сообщение"""
    print("🚀 Запуск интерактивного режима...")
    print("💡 Используйте /help для справки или /quit для выхода")
    print()
    print("🤖 DurusAI")
    print("Модель: durusai | Команды: /help, /model, /quit")
    print()


def show_help():
    """Показать справку"""
    print("\n📚 Доступные команды:")
    print()
    
    commands = [
        ("/help", "Показать эту справку"),
        ("/quit, /exit", "Выйти из интерактивного режима"),
        ("/clear", "Очистить историю разговора"),
        ("/history", "Показать историю разговора"),
        ("/stats", "Показать статистику сессии"),
        ("/copy", "Сохранить последний ответ в файл"),
        ("ls", "Показать файлы в директории"),
        ("cd path", "Перейти в директорию"),
        ("pwd", "Показать текущую директорию"),
        ("rm file", "Удалить файл"),
        ("mkdir dir", "Создать директорию"),
        ("tree", "Показать дерево файлов"),
    ]
    
    for cmd, desc in commands:
        print(f"   {Colors.CYAN}{cmd:<15}{Colors.RESET} {desc}")
    print()


def show_session_stats(queries: int, tokens: int):
    """Статистика сессии"""
    print(f"\n📊 Статистика сессии:")
    print(f"   Запросов: {Colors.CYAN}{queries}{Colors.RESET}")
    print(f"   Токенов: {Colors.CYAN}{tokens:,}{Colors.RESET}")


def show_exit_stats(queries: int, tokens: int):
    """Статистика при выходе"""
    border = "─" * 30
    print(f"\n╭─ 🎯 Завершение сессии {border[25:]}╮")
    print(f"│ 📊 Статистика сессии:        │")
    print(f"│    Запросов: {queries:<15} │")
    print(f"│    Токенов: {tokens:<16,} │")
    print(f"│                              │")
    print(f"│ 👋 До свидания!              │")
    print(f"╰{'─' * 32}╯")


def simple_input(prompt: str = "durusai> ") -> str:
    """Простой ввод с readline поддержкой"""
    try:
        import readline  # Для истории команд
    except ImportError:
        pass
    
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return "/quit"