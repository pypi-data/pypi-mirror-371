# Установка и настройка

## Системные требования

- Python 3.7 или выше
- pip (обычно устанавливается с Python)

## Установка для разработки

### 1. Клонирование репозитория

```bash
git clone https://github.com/kogriv/kgrv.git
cd kgrv
```

### 2. Создание виртуального окружения

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/Mac)
source venv/bin/activate
```

### 3. Установка в режиме разработки

```bash
# Установка пакета в режиме разработки
pip install -e .

# Установка зависимостей для разработки
pip install -r requirements-dev.txt
```

## Установка из PyPI

После публикации пакета на PyPI:

```bash
pip install kgrv
```

## Проверка установки

### Проверка через Python

```python
import kgrv
print(kgrv.__version__)

from kgrv import About
about = About()
about.print_info()
```

### Проверка через CLI

```bash
python scripts/cli.py --version
python scripts/cli.py info
```

### Запуск демонстрации

```bash
python scripts/demo.py
```

## Возможные проблемы

### Ошибка импорта модуля

Если возникает ошибка `ModuleNotFoundError: No module named 'kgrv'`:

1. Убедитесь, что вы в правильной папке проекта
2. Проверьте, что виртуальное окружение активировано
3. Переустановите пакет: `pip install -e .`

### Проблемы с виртуальным окружением

1. Убедитесь, что Python установлен корректно
2. Попробуйте: `python -m pip install --upgrade pip`
3. На Windows может потребоваться: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Кодировка в Windows

Если возникают проблемы с кириллицей в командной строке:

```bash
chcp 65001  # Переключение на UTF-8
```

## Удаление

```bash
pip uninstall kgrv
```
