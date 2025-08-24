# DurusAI Native CLI - Demo Guide

🎯 Демонстрация работы нативного CLI клиента DurusAI

## Установка

### 1. Установка из исходного кода

```bash
# Клонирование и переход в директорию
git clone <repository>
cd durusai_native_cli

# Установка в development режиме
pip install -e .

# Или установка с полными зависимостями
pip install -e ".[full]"
```

### 2. Проверка установки

```bash
# Проверить версию
durusai --version

# Показать справку
durusai --help

# Проверить здоровье API (если сервер запущен)
durusai health
```

## Запуск API сервера

Перед использованием CLI нужно запустить API сервер:

```bash
# Из корневой директории проекта
cd ..
./start-cli-api.sh

# Проверить что API работает
curl http://localhost:8080/cli/api/v1/health
```

## Основные команды

### Аутентификация

```bash
# Вход в систему
durusai login

# Вход с указанием пользователя
durusai login --username admin

# Вход с использованием профиля
durusai login --profile work

# Проверить текущего пользователя
durusai whoami

# Выход из системы
durusai logout

# Выход из всех профилей
durusai logout --all
```

### Запросы к AI

```bash
# Простой запрос
durusai query "Explain Python decorators"

# Запрос с указанием модели
durusai query "Write a FastAPI endpoint" --model claude-3-sonnet

# Запрос с параметрами
durusai query "Generate Python code" --max-tokens 2000 --temperature 0.7

# Отключить рендеринг Markdown
durusai query "Show me code" --no-markdown
```

### Интерактивный режим

```bash
# Запуск интерактивного чата
durusai chat

# Чат с конкретной моделью
durusai chat --model gpt-4
```

В интерактивном режиме доступны команды:
- `/help` - справка
- `/model <name>` - смена модели
- `/models` - список моделей
- `/clear` - очистка истории
- `/history` - показать историю
- `/stats` - статистика сессии
- `/export chat.md` - экспорт разговора
- `/quit` - выход

### Информация и статистика

```bash
# Показать доступные модели
durusai models

# Статистика использования
durusai stats

# Конфигурация
durusai config --list

# Изменение настроек
durusai config api_endpoint "https://api.durusai.com"
durusai config settings.default_model "claude-3-haiku"
```

## Примеры использования

### 1. Быстрые запросы

```bash
# Объяснение кода
durusai query "Explain this Python function: def fibonacci(n): ..."

# Генерация кода
durusai query "Create a REST API endpoint for user registration with FastAPI"

# Отладка ошибок
durusai query "I'm getting this error: TypeError: 'NoneType' object is not callable"
```

### 2. Работа с файлами

```bash
# Анализ файла (через перенаправление)
durusai query "Review this code for bugs" < my_script.py

# Batch обработка
for file in *.py; do
    durusai query "Summarize this code: $(cat $file)" > "${file%.py}_summary.md"
done
```

### 3. Интерактивная сессия

```bash
durusai chat
```

Пример диалога:
```
durusai> Hello! I need help with Python async/await

🤖 AI Response:
I'd be happy to help you with Python's async/await! This is for asynchronous programming...

durusai> /model gpt-4

✅ Модель изменена на: gpt-4

durusai> Can you show me a practical example?

🤖 AI Response:
Here's a practical example of async/await in Python...

durusai> /export async_tutorial.md

✅ Разговор экспортирован в: async_tutorial.md

durusai> /quit

👋 До свидания!
```

## Конфигурация

### Файлы конфигурации

DurusAI создает следующую структуру в домашней директории:

```
~/.durusai/
├── config.json         # Основная конфигурация
├── profiles/           # Профили пользователей
│   ├── default.json
│   └── work.json
├── cache/             # Кеш ответов
├── history/           # История команд
└── logs/             # Логи приложения
```

### Переменные окружения

```bash
# API endpoint
export DURUSAI_API_ENDPOINT="https://api.durusai.com"

# Токен для автоматической аутентификации
export DURUSAI_API_TOKEN="your-token-here"

# Альтернативная директория конфигурации
export DURUSAI_CONFIG_DIR="/custom/config/path"

# Профиль по умолчанию
export DURUSAI_PROFILE="work"
```

## Интеграция в рабочий процесс

### 1. Shell aliases

```bash
# В ~/.bashrc или ~/.zshrc
alias ai='durusai query'
alias chat='durusai chat'
alias aihelp='durusai query "How to"'

# Использование
ai "Convert this to TypeScript: const obj = { name: 'test' }"
aihelp "deploy FastAPI app to Docker"
```

### 2. Git hooks

```bash
#!/bin/bash
# В .git/hooks/pre-commit
files=$(git diff --cached --name-only --diff-filter=A,M | grep '\.py$')
for file in $files; do
    if [ -f "$file" ]; then
        durusai query "Quick code review: $(cat $file)" > "${file%.py}_review.txt"
    fi
done
```

### 3. VS Code integration

```json
{
    "terminal.integrated.profiles.linux": {
        "DurusAI Chat": {
            "path": "durusai",
            "args": ["chat"]
        }
    }
}
```

## Troubleshooting

### Общие проблемы

1. **Ошибка подключения к API**
   ```bash
   durusai health
   # Проверить что API сервер запущен
   ```

2. **Проблемы с аутентификацией**
   ```bash
   durusai logout
   durusai login
   ```

3. **Сброс конфигурации**
   ```bash
   rm -rf ~/.durusai
   durusai config --list  # Пересоздаст конфигурацию
   ```

### Debug режим

```bash
# Включить подробные логи
export DURUSAI_LOG_LEVEL=DEBUG

# Показать больше информации
durusai --verbose query "test"
```

## Сравнение с другими CLI

| Функция | DurusAI CLI | OpenAI CLI | Claude CLI |
|---------|-------------|------------|------------|
| Несколько моделей | ✅ | ❌ | ❌ |
| Интерактивный чат | ✅ | ❌ | ✅ |
| Безопасное хранение токенов | ✅ | ✅ | ✅ |
| Streaming ответы | ✅ | ✅ | ✅ |
| История разговоров | ✅ | ❌ | ❌ |
| Статистика использования | ✅ | ❌ | ❌ |
| Профили пользователей | ✅ | ❌ | ❌ |
| Markdown рендеринг | ✅ | ❌ | ✅ |
| Экспорт разговоров | ✅ | ❌ | ❌ |

## Разработка и вклад

### Setup для разработки

```bash
git clone <repository>
cd durusai_native_cli
pip install -e ".[dev]"
```

### Тестирование

```bash
# Unit тесты
python -m pytest tests/

# Валидация структуры
python validate_structure.py

# Интеграционные тесты
python test_against_api.py
```

### Сборка пакета

```bash
# Сборка wheel
python -m build

# Проверка пакета
python -m twine check dist/*

# Публикация (для maintainers)
python -m twine upload dist/*
```

---

Создано командой DurusAI 🤖