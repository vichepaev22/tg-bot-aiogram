# Telegram Bot on aiogram v3

Минимальная структура проекта для Telegram-бота на базе `aiogram` v3.

## Структура проекта

```
app/
├── core/
│   └── config.py
├── handlers/
│   ├── __init__.py
│   └── start.py
├── __init__.py
└── main.py
.env.example
pyproject.toml
README.md
```

## Подготовка окружения

1) Создайте виртуальное окружение и активируйте его.

   Linux/macOS:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2) Установите зависимости:

   ```bash
   pip install --upgrade pip
   pip install -e .
   ```

3) Подготовьте переменные окружения и запустите бота:

   ```bash
   cp .env.example .env  # один раз, затем укажите TELEGRAM_BOT_TOKEN
   python -m app.main
   ```

## Частые ошибки

- Не задан `TELEGRAM_BOT_TOKEN` в файле `.env`.
- Используются импорты из `aiogram` 2.x (например, `from aiogram.dispatcher import Dispatcher`) вместо подхода с роутерами v3 (`from aiogram import Router`, `Dispatcher`).
- Виртуальное окружение не активировано, из-за чего Python не видит установленные зависимости.
- Зависимости не установлены перед запуском (ошибка `ModuleNotFoundError`).

## Загрузка проекта на GitHub

1. Создайте пустой репозиторий на GitHub и скопируйте URL (например,
   `https://github.com/<username>/tg-bot-aiogram.git`).
2. Убедитесь, что локально все файлы добавлены в Git и закоммичены:

   ```bash
   git status       # рабочее дерево должно быть чистым
   git log --oneline
   ```

   Если есть несохранённые изменения, выполните:

   ```bash
   git add .
   git commit -m "Initial aiogram v3 scaffold"
   ```

3. Привяжите локальный репозиторий к GitHub и отправьте коммиты:

   ```bash
   git remote add origin https://github.com/<username>/tg-bot-aiogram.git
   git branch -M main
   git push -u origin main
   ```

4. Для последующих обновлений выполняйте стандартный цикл:

   ```bash
   git pull --rebase origin main   # подтянуть изменения из GitHub
   # ... вносите правки ...
   git add .
   git commit -m "Describe your change"
   git push
   ```

5. Чтобы клонировать проект на другой машине, используйте:

   ```bash
   git clone https://github.com/<username>/tg-bot-aiogram.git
   cd tg-bot-aiogram
   ```
