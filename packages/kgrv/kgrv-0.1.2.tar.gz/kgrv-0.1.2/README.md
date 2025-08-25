# KGRV

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python пакет для экспериментов и обучения созданию Python пакетов.

## 🎯 Описание

KGRV - это демонстрационный Python пакет, который показывает лучшие практики:
- 📦 Организации структуры Python пакета
- 📚 Документирования кода и API
- 🧪 Написания тестов
- 🚀 Публикации на PyPI
- ⚙️ Настройки инструментов разработки

## ✨ Возможности

- **Класс About** - для отображения информации о разработчике
- **Управление навыками и проектами** - добавление и просмотр
- **CLI интерфейс** - командная строка для взаимодействия
- **Демонстрационные скрипты** - примеры использования
- **Полное покрытие тестами** - unit-тесты для всех компонентов

## 🏗️ Структура проекта

```
kgrv/
├── kgrv/                   # 📦 Основной пакет (для PyPI)
│   ├── __init__.py        # Инициализация и экспорты
│   ├── about.py           # Модуль About
│   └── cli_click.py       # CLI интерфейс (click-based)
├── scripts/               # 🎮 Демонстрационные скрипты
│   ├── demo.py           # Интерактивная демонстрация
│   ├── cleanup.sh        # Скрипт очистки (Bash)
│   └── cleanup.ps1       # Скрипт очистки (PowerShell)
├── docs/                  # 📚 Документация
│   ├── publishing.md     # Руководство по публикации
│   └── publish/          # Инструкции по публикации
│       ├── cleanup-instructions.md
│       └── build-instructions.md
├── tests/                 # 🧪 Тесты
│   └── test_about.py     # Тесты для модуля about
├── pyproject.toml        # 🔧 Современная конфигурация
├── requirements.txt      # 🛠️ Зависимости для разработки
├── MANIFEST.in           # 📋 Файлы для дистрибутива
├── LICENSE               # 📄 Лицензия MIT
└── CHANGELOG.md          # 📝 История изменений
```

## 🚀 Быстрый старт

### Установка

```bash
# Клонирование репозитория
git clone https://github.com/kogriv/kgrv.git
cd kgrv

# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/Mac)
source venv/bin/activate

# Установка в режиме разработки
pip install -e .
```

### Использование

#### Python API

```python
from kgrv import About

# Создание объекта
about = About("Ваше имя")

# Вывод информации
about.print_info()

# Добавление навыков
about.add_skill("Python")
about.add_skill("Machine Learning")

# Получение данных
skills = about.get_skills()
info = about.get_info()  # Все данные в JSON формате
```

#### CLI интерфейс

```bash
# Показать помощь
kgrv --help

# Показать информацию о разработчике
kgrv info

# Показать информацию с кастомным именем
kgrv info --name "John"

# Показать информацию в JSON формате
kgrv info --format json

# Показать навыки разработчика
kgrv skills

# Показать проекты разработчика
kgrv projects

# Проверить валидность GitHub профиля
kgrv validate

# Добавить навык
kgrv add-skill

# Добавить проект
kgrv add-project

# Запустить интерактивную демонстрацию
kgrv demo
```

#### Демонстрация

```bash
# Запуск интерактивной демонстрации
python scripts/demo.py

# Или через CLI
kgrv demo
```

### 📋 Подробное описание CLI команд

#### Основные команды:

**`kgrv info`** - Показать полную информацию о разработчике
```bash
# Базовый вывод
kgrv info

# С кастомным именем
kgrv info --name "John"

# В JSON формате
kgrv info --format json

# С добавлением навыков и проектов
kgrv info --add-skill "Django" --add-project "Web App"
```

**`kgrv skills`** - Показать навыки разработчика
```bash
# Текстовый формат
kgrv skills

# JSON формат
kgrv skills --format json
```

**`kgrv projects`** - Показать проекты разработчика
```bash
# Текстовый формат
kgrv projects

# JSON формат
kgrv projects --format json
```

**`kgrv validate`** - Проверить валидность GitHub профиля
```bash
# Проверка профиля
kgrv validate

# С кастомным именем
kgrv validate --name "username"
```

#### Команды управления:

**`kgrv add-skill`** - Добавить навык
```bash
# Интерактивный ввод
kgrv add-skill

# С указанием навыка
kgrv add-skill --skill "React"
```

**`kgrv add-project`** - Добавить проект
```bash
# Интерактивный ввод
kgrv add-project

# С указанием проекта
kgrv add-project --project "E-commerce Platform"
```

**`kgrv demo`** - Интерактивная демонстрация
```bash
# Полная демонстрация функционала
kgrv demo
```

## 🧪 Тестирование

```bash
# Установка зависимостей для разработки
pip install -r requirements.txt

# Запуск тестов
python -m pytest tests/ -v

# Запуск конкретного теста
python tests/test_about.py

# Запуск с покрытием (если установлен pytest-cov)
pytest --cov=kgrv --cov-report=html
```

## 📦 Публикация на PyPI

```bash
# Очистка проекта
./scripts/cleanup.ps1  # Windows
./scripts/cleanup.sh   # Linux/Mac

# Сборка пакета
python -m build

# Проверка пакета
twine check dist/*

# Загрузка на Test PyPI
twine upload --repository testpypi dist/*

# Тестирование установки из Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kgrv

# Загрузка на PyPI
twine upload dist/*
```

Подробное руководство по публикации: [docs/publishing.md](docs/publishing.md)

## 🛠️ Разработка

### Настройка окружения

```bash
# Установка зависимостей для разработки
pip install -r requirements.txt

# Установка в режиме разработки
pip install -e .
```

### Инструменты качества кода

```bash
# Форматирование кода
black kgrv/ scripts/ tests/

# Проверка типов
mypy kgrv/

# Линтинг
flake8 kgrv/ scripts/ tests/
```

## 📚 Документация

Подробная документация доступна в папке [docs/](docs/):
- [Руководство по публикации](docs/publishing.md) - полное руководство по публикации на PyPI
- [Инструкции по очистке](docs/publish/cleanup-instructions.md) - очистка проекта перед публикацией
- [Инструкции по сборке](docs/publish/build-instructions.md) - сборка пакета

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 👨‍💻 Автор

**kogriv** - [GitHub](https://github.com/kogriv)

## 🙏 Благодарности

- Python сообществу за отличные инструменты
- Всем, кто делает open source лучше
