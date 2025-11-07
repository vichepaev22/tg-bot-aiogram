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

1. Создайте виртуальное окружение и активируйте его.

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

2. Установите зависимости:

   ```bash
   pip install --upgrade pip
   pip install -e .
   ```

3. Подготовьте переменные окружения и запустите бота:

   ```bash
   cp .env.example .env  # один раз, затем укажите TELEGRAM_BOT_TOKEN
   python -m app.main
   ```

## Частые ошибки

- Не задан `TELEGRAM_BOT_TOKEN` в файле `.env`.
- Используются импорты из `aiogram` 2.x (например, `from aiogram.dispatcher import Dispatcher`) вместо подхода с роутерами v3 (`from aiogram import Router`, `Dispatcher`).
- Виртуальное окружение не активировано, из-за чего Python не видит установленные зависимости.
- Зависимости не установлены перед запуском (ошибка `ModuleNotFoundError`).

## Синхронизация с GitHub

Если нужно перенести проект в репозиторий на GitHub:

1. Создайте пустой репозиторий на GitHub (без README, `.gitignore` и т.п.).
2. Добавьте удалённый репозиторий и отправьте изменения:

   ```bash
   git remote add origin https://github.com/<ваш_логин>/<имя_репозитория>.git
   git push -u origin work
   ```

   Если вы предпочитаете основную ветку `main`, сначала переименуйте локальную ветку:

   ```bash
   git branch -m work main
   git push -u origin main
   ```

3. Чтобы клонировать проект на другой машине:

   ```bash
   git clone https://github.com/<ваш_логин>/<имя_репозитория>.git
   cd <имя_репозитория>
   ```

   При необходимости переключитесь на нужную ветку (например, `work` или `main`).
