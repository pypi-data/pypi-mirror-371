# Инструкции по очистке репозитория перед публикацией

Этот файл содержит команды для очистки репозитория от временных файлов перед публикацией.

## 📋 Описание удаляемых файлов и папок

### 🔨 **Файлы сборки пакета**

#### `build/` - Папка сборки
- **Назначение**: Временная папка, создаваемая инструментом `build` при сборке пакета
- **Как появляется**: При выполнении `python -m build` или `pip install build && python -m build`
- **Содержимое**: Временные файлы, исходники, метаданные для создания дистрибутивов
- **Когда нужна**: Только во время сборки пакета
- **Можно удалять**: ✅ Да, после каждой сборки

#### `dist/` - Папка дистрибутивов
- **Назначение**: Содержит готовые дистрибутивы пакета (`.whl`, `.tar.gz`)
- **Как появляется**: При выполнении `python -m build`
- **Содержимое**: `kgrv-0.1.0-py3-none-any.whl`, `kgrv-0.1.0.tar.gz`
- **Когда нужна**: Для загрузки на PyPI, локального тестирования установки
- **Можно удалять**: ✅ Да, перед новой сборкой

#### `*.egg-info/` - Метаданные пакета
- **Назначение**: Метаданные пакета в формате egg-info (устаревший формат)
- **Как появляется**: При `pip install -e .` или `python setup.py develop`
- **Содержимое**: `PKG-INFO`, `dependency_links.txt`, `requires.txt`, `top_level.txt`
- **Когда нужна**: При разработке пакета в режиме "editable install"
- **Можно удалять**: ✅ Да, при переустановке пакета

### 📊 **Файлы покрытия тестов**

#### `htmlcov/` - HTML отчеты покрытия
- **Назначение**: HTML-страницы с детальным отчетом покрытия кода тестами
- **Как появляется**: При выполнении `pytest --cov=kgrv --cov-report=html`
- **Содержимое**: `index.html`, папки с отчетами по модулям
- **Когда нужна**: Для анализа покрытия кода тестами
- **Можно удалять**: ✅ Да, отчеты генерируются заново

#### `.coverage` - Данные покрытия
- **Назначение**: Бинарный файл с данными о покрытии кода тестами
- **Как появляется**: При выполнении `pytest --cov=kgrv` или `coverage run`
- **Содержимое**: Бинарные данные о выполненных строках кода
- **Когда нужна**: Для генерации отчетов покрытия
- **Можно удалять**: ✅ Да, данные собираются заново

#### `.coverage.*` - Дополнительные файлы покрытия
- **Назначение**: Дополнительные файлы данных покрытия (для параллельного выполнения)
- **Как появляется**: При параллельном запуске тестов или coverage
- **Содержимое**: Бинарные данные покрытия
- **Когда нужна**: При параллельном тестировании
- **Можно удалять**: ✅ Да

### 🧠 **Кэш Python**

#### `__pycache__/` - Кэш байт-кода Python
- **Назначение**: Кэш скомпилированного байт-кода Python для ускорения импортов
- **Как появляется**: Автоматически при импорте `.py` файлов
- **Содержимое**: `.pyc` файлы с байт-кодом
- **Когда нужна**: Для ускорения загрузки модулей
- **Можно удалять**: ✅ Да, кэш пересоздается автоматически

#### `*.pyc` - Скомпилированные файлы Python
- **Назначение**: Скомпилированный байт-код Python файлов
- **Как появляется**: Автоматически при импорте `.py` файлов
- **Содержимое**: Байт-код Python
- **Когда нужны**: Для ускорения загрузки модулей
- **Можно удалять**: ✅ Да, пересоздаются автоматически

#### `*.pyo` - Оптимизированные файлы Python (устаревшие)
- **Назначение**: Оптимизированные скомпилированные файлы Python (Python 2.x)
- **Как появляется**: При компиляции с флагом `-O` (устаревший)
- **Содержимое**: Оптимизированный байт-код
- **Когда нужны**: В старых версиях Python
- **Можно удалять**: ✅ Да, устаревший формат

### 🧪 **Кэш тестирования**

#### `.pytest_cache/` - Кэш pytest
- **Назначение**: Кэш pytest для ускорения повторных запусков тестов
- **Как появляется**: При выполнении `pytest`
- **Содержимое**: Кэш результатов тестов, метаданные
- **Когда нужна**: Для ускорения повторных запусков тестов
- **Можно удалять**: ✅ Да, кэш пересоздается

### 📝 **Временные файлы редакторов**

#### `*.swp`, `*.swo` - Временные файлы Vim
- **Назначение**: Временные файлы редактора Vim при редактировании
- **Как появляется**: При открытии файлов в Vim
- **Содержимое**: Временные данные редактора
- **Когда нужны**: Только во время редактирования в Vim
- **Можно удалять**: ✅ Да, создаются заново

#### `*~` - Резервные файлы
- **Назначение**: Резервные копии файлов (многие редакторы)
- **Как появляется**: При сохранении файлов в некоторых редакторах
- **Содержимое**: Копии оригинальных файлов
- **Когда нужны**: Для восстановления при сбоях
- **Можно удалять**: ✅ Да, если не нужны резервные копии

## 🗑️ Файлы и папки для удаления

### 1. Временные файлы сборки
```bash
# Удалить папки сборки
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# В Windows PowerShell:
Remove-Item -Recurse -Force build/ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist/ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force *.egg-info/ -ErrorAction SilentlyContinue
```

### 2. Файлы покрытия тестов
```bash
# Удалить отчеты покрытия
rm -rf htmlcov/
rm -f .coverage

# В Windows PowerShell:
Remove-Item -Recurse -Force htmlcov/ -ErrorAction SilentlyContinue
Remove-Item -Force .coverage -ErrorAction SilentlyContinue
```

### 3. Кэш Python
```bash
# Удалить кэш Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# В Windows PowerShell:
Get-ChildItem -Path . -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Name "*.pyc" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Name "*.pyo" | Remove-Item -Force
```

### 4. Кэш pytest
```bash
# Удалить кэш pytest
rm -rf .pytest_cache/

# В Windows PowerShell:
Remove-Item -Recurse -Force .pytest_cache/ -ErrorAction SilentlyContinue
```

### 5. Виртуальные окружения (НЕ удалять активное!)
```bash
# Только если не используете
rm -rf venv_*/

# В Windows PowerShell:
# Remove-Item -Recurse -Force venv_*/ -ErrorAction SilentlyContinue
```

## 🧹 Полная очистка (одной командой)

### 🚀 **Автоматические скрипты очистки**

В проекте созданы готовые скрипты для автоматической очистки:

#### Linux/Mac (Bash):
```bash
# Сделать скрипт исполняемым
chmod +x scripts/cleanup.sh

# Запустить очистку
./scripts/cleanup.sh
```

#### Windows (PowerShell):
```powershell
# Запустить очистку
.\scripts\cleanup.ps1
```

### 📝 **Ручная очистка (если скрипты недоступны)**

#### Linux/Mac:
```bash
# Полная очистка
rm -rf build/ dist/ *.egg-info/ htmlcov/ .coverage .pytest_cache/
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
```

#### Windows PowerShell:
```powershell
# Полная очистка
$folders = @("build", "dist", "htmlcov", ".pytest_cache")
$patterns = @("*.egg-info")
$files = @(".coverage")

foreach ($folder in $folders) {
    Remove-Item -Recurse -Force $folder -ErrorAction SilentlyContinue
}

foreach ($pattern in $patterns) {
    Get-ChildItem -Path . -Recurse -Directory -Name $pattern | Remove-Item -Recurse -Force
}

foreach ($file in $files) {
    Remove-Item -Force $file -ErrorAction SilentlyContinue
}

Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -File -Name "*.pyc" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -File -Name "*.pyo" | Remove-Item -Force
```

## ✅ Проверка очистки

После очистки проверьте, что остались только нужные файлы:

```bash
# Посмотреть структуру проекта
tree -a -I '.git|venv_*'

# Или в Windows:
# tree /f /a
```

Должна остаться структура:
```
kgrv/
├── kgrv/
│   ├── __init__.py
│   ├── about.py
│   └── cli_click.py
├── scripts/
│   ├── __init__.py
│   └── demo.py
├── tests/
│   ├── __init__.py
│   └── test_about.py
├── docs/
│   ├── api.md
│   ├── index.md
│   ├── installation.md
│   └── publishing.md
├── setup.py
├── pyproject.toml
├── MANIFEST.in
├── README.md
├── LICENSE
├── CHANGELOG.md
├── requirements.txt
├── .gitignore
└── .git/
```

## 🚫 НЕ удаляйте эти файлы:

- ✅ `.git/` - история Git
- ✅ `venv_*/` - если это ваше активное окружение
- ✅ Любые файлы с вашим кодом
- ✅ Конфигурационные файлы (setup.py, pyproject.toml, etc.)

## 🔄 Когда выполнять очистку:

1. **Перед каждой сборкой** - удалить build/, dist/
2. **Перед коммитом в Git** - удалить временные файлы
3. **Перед публикацией** - полная очистка
4. **При проблемах со сборкой** - полная очистка и пересборка

## 🎯 **Рекомендуемый workflow очистки:**

### **Для разработки:**
```bash
# Быстрая очистка перед сборкой
rm -rf build/ dist/ *.egg-info/
```

### **Перед коммитом:**
```bash
# Очистка временных файлов
rm -rf __pycache__/ .pytest_cache/ *.pyc *.pyo
```

### **Перед публикацией:**
```bash
# Полная очистка с помощью скрипта
./scripts/cleanup.sh  # Linux/Mac
# или
.\scripts\cleanup.ps1  # Windows
```

### **При проблемах:**
```bash
# Полная очистка + переустановка пакета
./scripts/cleanup.sh
pip install -e . --force-reinstall
```

## 📋 **Чек-лист перед публикацией:**

- [ ] Выполнить полную очистку: `./scripts/cleanup.sh`
- [ ] Проверить, что нет временных файлов: `git status`
- [ ] Запустить тесты: `python -m pytest tests/`
- [ ] Проверить функционал: `python -m kgrv.cli_click --help`
- [ ] Собрать пакет: `python -m build`
- [ ] Проверить дистрибутивы: `twine check dist/*`

Этот файл можно удалить после публикации пакета.
