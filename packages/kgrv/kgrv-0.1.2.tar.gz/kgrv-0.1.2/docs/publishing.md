# Руководство по публикации Python пакета на PyPI

Пошаговое руководство по подготовке и публикации Python пакета на PyPI на примере пакета KGRV.

## 📋 Требования к структуре пакета

### Обязательные файлы

1. **Основной пакет** - папка с кодом:
   ```
   kgrv/
   ├── __init__.py      # Версия, метаданные, экспорты
   ├── about.py         # Основной функционал
   └── cli_click.py     # CLI интерфейс
   ```

2. **Конфигурационные файлы**:
   ```
   pyproject.toml       # Современная конфигурация (ОБЯЗАТЕЛЬНО!)
   MANIFEST.in          # Файлы для включения в дистрибутив
   ```

3. **Документация**:
   ```
   README.md            # Описание проекта
   LICENSE              # Лицензия (обязательно!)
   CHANGELOG.md         # История изменений
   ```

4. **Зависимости**:
   ```
   requirements.txt     # Основные зависимости (опционально)
   ```

5. **Исключения**:
   ```
   .gitignore          # Временные файлы для Git
   ```

### Структура __init__.py

```python
"""Описание пакета"""

__version__ = "0.1.0"           # Версия (обязательно!)
__author__ = "Your Name"        # Автор
__email__ = "email@example.com" # Email
__description__ = "Краткое описание"

# Экспорты
from .module import Class
__all__ = ['Class']
```

### Конфигурация pyproject.toml

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-package-name"           # Уникальное имя на PyPI
dynamic = ["version"]                # Версия из __init__.py
description = "Краткое описание"     # Краткое описание
readme = "README.md"                 # Полное описание из README
license = {text = "MIT"}             # Лицензия
authors = [
    {name = "Your Name", email = "email@example.com"}
]
keywords = ["python", "package", "example"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
requires-python = ">=3.7"
dependencies = [
    "click>=8.0.0",
    "requests>=2.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0.0",
    "black>=21.0.0",
    "flake8>=3.8.0",
]

[project.urls]
Homepage = "https://github.com/user/repo"
Repository = "https://github.com/user/repo.git"
Documentation = "https://github.com/user/repo/tree/master/docs"
"Bug Reports" = "https://github.com/user/repo/issues"

[project.scripts]
your-command = "your_package.cli:main"

[tool.setuptools]
packages = ["your_package"]

[tool.setuptools.dynamic]
version = {attr = "your_package.__version__"}
```

### ⚠️ **ВАЖНО: Используйте только pyproject.toml**

**Современный подход (рекомендуется):**
- ✅ **Только `pyproject.toml`** - современный стандарт
- ✅ **Нет дублирования** конфигурации
- ✅ **Лучшая читаемость** (TOML формат)
- ✅ **Поддержка всех современных инструментов**

**Устаревший подход (НЕ рекомендуется):**
- ❌ **`setup.py`** - устаревший формат
- ❌ **Дублирование** с `pyproject.toml`
- ❌ **Проблемы синхронизации** между файлами

#### **Почему только pyproject.toml?**

1. **Современный стандарт:** PEP 518, PEP 621
2. **Меньше ошибок:** Одна точка конфигурации
3. **Лучшая поддержка:** Все современные инструменты
4. **Читаемость:** TOML формат более структурирован

#### **Миграция с setup.py:**
```bash
# 1. Удалите setup.py
rm setup.py

# 2. Убедитесь, что pyproject.toml содержит все настройки
# 3. Протестируйте сборку
python -m build

# 4. Проверьте установку
pip install -e .
```

## 🛠️ Подготовка к публикации

### 1. Проверка структуры проекта

```bash
# Структура должна выглядеть так:
your-project/
├── your_package/       # Основной пакет
│   ├── __init__.py
│   └── module.py
├── tests/             # Тесты
├── docs/              # Документация
├── pyproject.toml     # Современная конфигурация (ОБЯЗАТЕЛЬНО!)
├── README.md          # Описание
├── LICENSE            # Лицензия
├── CHANGELOG.md       # История изменений
├── requirements.txt   # Зависимости (опционально)
├── MANIFEST.in        # Файлы для дистрибутива
└── .gitignore         # Исключения Git
```

### 2. Установка инструментов для сборки
Где устанавливать build и twine?  
Рекомендация: В виртуальном окружении  
Преимущества:  
✅ Изолированные версии инструментов  
✅ Нет конфликтов с другими проектами  
✅ Воспроизводимая среда сборки  
✅ Легко переустановить при проблемах  
Недостатки:  
❌ Нужно активировать окружение каждый раз  
❌ Занимает место в каждом проекте  

Альтернатива: pipx (рекомендуется для инструментов)
```bash
# Установка pipx (если нет)
pip install pipx

# Установка инструментов через pipx
pipx install build
pipx install twine
```
Преимущества pipx:  
✅ Глобально доступны  
✅ Изолированы от других пакетов  
✅ Можно использовать из любого окружения  

🚀 Для проекта где есть ВО рекомендуется его активация и установка:
```bash
venv\Scripts\Activate.ps1

pip install build twine

# Проверьте установку
python -m build --version
twine --version
```

### 3. Создание виртуального окружения

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 4. Установка пакета в режиме разработки

```bash
pip install -e .
```

### 5. Тестирование функционала

```bash
# Запуск тестов
python -m pytest tests/ -v

# Тестирование CLI
your-command --help
your-command info
```

## 📦 Сборка пакета

### 1. Очистка старых сборок

```bash
rm -rf build/ dist/ *.egg-info/
```

Очистка репозитория:
```powershell
# Удаление временных файлов
Remove-Item -Recurse -Force build/ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist/ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force *.egg-info/ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force htmlcov/ -ErrorAction SilentlyContinue
Remove-Item -Force .coverage -ErrorAction SilentlyContinue

# Удаление кэша Python
Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force
```

### 2. Сборка дистрибутивов

```bash
python -m build
```

Эта команда создаст:
- `dist/your-package-0.1.0.tar.gz` - исходный дистрибутив
- `dist/your_package-0.1.0-py3-none-any.whl` - wheel дистрибутив

### 3. Проверка дистрибутивов

```bash
twine check dist/*
```

## 🧪 Публикация на Test PyPI

### 1. Регистрация на Test PyPI

1. Перейдите на https://test.pypi.org/
2. Создайте аккаунт
3. Подтвердите email

### 2. Создание API токена

1. Войдите в аккаунт Test PyPI
2. Перейдите в Account Settings → API tokens
3. Создайте токен с scope "Entire account"
4. Сохраните токен в безопасном месте

### 3. Настройка аутентификации

#### Создание файла `~/.pypirc`

**Важно:** Файл `~/.pypirc` создается в **домашней папке пользователя**, а не в папке проекта!

**Расположение файла:**
- **Windows:** `C:\Users\ИмяПользователя\.pypirc`
- **Linux/Mac:** `/home/username/.pypirc`

**Создание файла в Windows PowerShell:**
```powershell
# Перейти в домашнюю папку
cd ~

# Создать файл
New-Item -Path ".pypirc" -ItemType File

# Или через блокнот
notepad .pypirc
```

**Содержимое файла `~/.pypirc`:**
```ini
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-ваш-токен-test-pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-ваш-токен-pypi
```

**Как twine находит этот файл:**
1. Переменная окружения: `TWINE_CONFIG_FILE`
2. Домашняя папка: `~/.pypirc` (по умолчанию)
3. Текущая папка: `./.pypirc`

**Безопасность токенов:**
- ✅ Храните токены в `~/.pypirc` (не в проекте)
- ✅ Не коммитьте токены в Git
- ✅ Используйте `__token__` как username
- ✅ Токен начинается с `pypi-`

### 4. Загрузка на Test PyPI

```bash
twine upload --repository testpypi dist/*
```

### 5. Проверка установки с Test PyPI

**⚠️ Важно:** Test PyPI не содержит все пакеты из основного PyPI! Для установки зависимостей нужно использовать оба репозитория.

#### Создание тестового окружения

```powershell
# Создать новое ВО в папке проекта (рекомендуется)
python -m venv venv_test
venv_test\Scripts\Activate.ps1

# Или создать в отдельной папке
mkdir test_install
cd test_install
python -m venv test_env
test_env\Scripts\Activate.ps1
```

#### Установка пакета из Test PyPI

**Правильная установка с зависимостями:**
```powershell
# Установить пакет из Test PyPI, но зависимости из основного PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kgrv
```

**Что происходит:**
- `--index-url https://test.pypi.org/simple/` - ищет ваш пакет в Test PyPI
- `--extra-index-url https://pypi.org/simple/` - ищет зависимости в основном PyPI

#### Тестирование установки

```powershell
# Проверить установленные пакеты
pip list

# Проверить CLI команду
kgrv --help

# Запустить функционал
kgrv about

# Проверить импорт
python -c "import kgrv; print(f'Версия: {kgrv.__version__}')"
```

#### Ожидаемый результат

```
Collecting kgrv
  Downloading https://test-files.pythonhosted.org/packages/.../kgrv-0.1.0-py3-none-any.whl
Collecting click>=8.0.0 (from kgrv)
  Downloading https://files.pythonhosted.org/packages/.../click-8.1.7-py3-none-any.whl
Collecting colorama>=0.4.0 (from kgrv)
  Downloading https://files.pythonhosted.org/packages/.../colorama-0.4.6-py2.py3-none-any.whl
Collecting requests>=2.25.0 (from kgrv)
  Downloading https://files.pythonhosted.org/packages/.../requests-2.31.0-py3-none-any.whl
Successfully installed kgrv-0.1.0 click-8.1.7 colorama-0.4.6 requests-2.31.0 ...
```

## 🚀 Публикация на PyPI

### 1. Проверка на Test PyPI

Убедитесь, что:
- ✅ Пакет установился без ошибок
- ✅ Все команды работают
- ✅ Зависимости установились корректно
- ✅ Документация отображается правильно

### 2. Загрузка на PyPI

Сборка (возможно надо активировать ВО):

```bash
python -m build
```

Эта команда создаст:
- `dist/your-package-0.1.0.tar.gz` - исходный дистрибутив
- `dist/your_package-0.1.0-py3-none-any.whl` - wheel дистрибутив

Проверка

```bash
twine check dist/*
```
Загрузка
```bash
twine upload dist/*
```

### 3. Проверка установки с PyPI

```bash
# Новое окружение
python -m venv prod_test
prod_test\Scripts\activate

# Установка с PyPI
pip install your-package-name

# Тестирование
your-command --version
```

## ✅ Чек-лист перед публикацией

### Код и структура
- [ ] Корректная структура пакета
- [ ] `__init__.py` с версией и экспортами
- [ ] Все импорты работают
- [ ] CLI команды функционируют
- [ ] Тесты проходят

### Документация
- [ ] README.md с описанием и примерами
- [ ] LICENSE файл
- [ ] CHANGELOG.md с историей изменений
- [ ] Docstrings в коде

### Конфигурация
- [ ] **pyproject.toml корректен и содержит все настройки** ✅
- [ ] MANIFEST.in включает нужные файлы
- [ ] .gitignore исключает временные файлы

### Зависимости
- [ ] **dependencies в pyproject.toml содержат только необходимые зависимости**
- [ ] Версии зависимостей указаны корректно
- [ ] Опциональные зависимости в optional-dependencies

### Сборка и тестирование
- [ ] `python -m build` проходит без ошибок
- [ ] `twine check dist/*` проходит проверку
- [ ] Пакет устанавливается и работает в чистом окружении

## 🔍 Диагностика проблем с конфигурацией

### Проверка конфигурации pyproject.toml

**1. Проверка зависимостей:**
```bash
# Извлечь зависимости из pyproject.toml
python -c "import tomllib; data=tomllib.load(open('pyproject.toml', 'rb')); print('dependencies:', data['project']['dependencies'])"
```

**2. Проверка entry points:**
```bash
# Проверить entry points в собранном пакете
python -m build
unzip -l dist/*.whl | grep entry_points
cat kgrv.egg-info/entry_points.txt
```

**3. Проверка метаданных:**
```bash
# Показать метаданные пакета
python -c "import kgrv; print('Version:', kgrv.__version__)"
python -c "import pkg_resources; print('Installed version:', pkg_resources.get_distribution('kgrv').version)"
```

### Признаки проблем с конфигурацией

**❌ Проблемы:**
- CLI команда не работает после установки
- Зависимости не устанавливаются автоматически
- Разные версии в разных местах
- Ошибки при сборке пакета

**✅ Решение:**
- Проверьте корректность pyproject.toml
- Убедитесь, что все настройки указаны правильно
- Пересоберите пакет после исправлений

## ⚠️ Частые ошибки

### 1. Неправильное имя пакета
```python
# ❌ Неправильно
name="My-Package"  # Имя уже занято

# ✅ Правильно  
name="my-unique-package-name"  # Уникальное имя
```

### 2. Отсутствие зависимостей
```toml
# ❌ Забыли указать зависимости
dependencies = []

# ✅ Указали все необходимые
dependencies = [
    "click>=8.0.0",
    "requests>=2.25.0"
]
```

### 3. Неправильный MANIFEST.in
```ini
# ❌ Включили тесты
include tests/*

# ✅ Исключили тесты
recursive-exclude tests *
```

### 4. Отсутствие лицензии
```toml
# ❌ Нет лицензии
# license = ???

# ✅ Есть LICENSE файл и настройка
license = {text = "MIT"}
```

### 5. Неправильные entry points
```toml
# ❌ Неправильный путь к CLI
[project.scripts]
kgrv-cli = "scripts.cli:main"  # Старый путь!

# ✅ Правильный путь к CLI
[project.scripts]
kgrv = "kgrv.cli_click:cli"    # Новый путь!
```

### 6. Отсутствие build-system
```toml
# ❌ Нет build-system
[project]
name = "my-package"

# ✅ Есть build-system
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
```

### 7. Проблемы с установкой из Test PyPI
```bash
# ❌ Неправильная установка
pip install --index-url https://test.pypi.org/simple/ kgrv
# Ошибка: No matching distribution found for requests>=2.25.0

# ✅ Правильная установка с зависимостями
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kgrv
```

**Причина:** Test PyPI не содержит все пакеты из основного PyPI, только ваши тестовые пакеты.

### 8. Неправильное расположение .pypirc
```bash
# ❌ Создание в папке проекта
touch .pypirc  # Неправильно!

# ✅ Создание в домашней папке
cd ~
touch .pypirc  # Правильно!
```

**Причина:** twine ищет .pypirc в домашней папке по умолчанию.

## 🔄 Обновление пакета

### 1. Обновите версию
В `__init__.py`:
```python
__version__ = "0.1.1"  # Увеличьте версию
```

### 2. Обновите CHANGELOG.md
```markdown
## [0.1.1] - 2025-08-25
### Fixed
- Исправлена ошибка в CLI
```

### 3. Пересоберите и опубликуйте
```bash
rm -rf dist/
python -m build
twine upload dist/*
```

## 📚 Полезные ссылки

- [PyPI](https://pypi.org/) - основной репозиторий
- [Test PyPI](https://test.pypi.org/) - тестовый репозиторий  
- [Python Packaging Guide](https://packaging.python.org/)
- [setuptools документация](https://setuptools.pypa.io/)
- [twine документация](https://twine.readthedocs.io/)

Это руководство основано на реальном опыте публикации пакета KGRV и содержит все необходимые шаги для успешной публикации вашего Python пакета!
