# API Документация

## Модуль kgrv

### Класс About

Основной класс для работы с информацией о разработчике.

```python
from kgrv import About
```

#### Конструктор

```python
About(name: str = "kogriv")
```

**Параметры:**
- `name` (str): Имя разработчика, по умолчанию "kogriv"

**Атрибуты:**
- `name` (str): Имя разработчика
- `github` (str): URL GitHub профиля
- `skills` (List[str]): Список навыков
- `projects` (List[str]): Список проектов
- `created_at` (datetime): Время создания объекта

#### Методы

##### get_info()

Получить полную информацию о разработчике.

```python
def get_info() -> Dict[str, Any]
```

**Возвращает:**
- `Dict[str, Any]`: Словарь с полной информацией

**Пример:**
```python
about = About("John")
info = about.get_info()
print(info)
# {
#   "name": "John",
#   "github": "https://github.com/John",
#   "skills": ["Python", "JavaScript", ...],
#   "projects": [...],
#   "created_at": "2025-01-24 12:30:45"
# }
```

##### get_skills()

Получить копию списка навыков.

```python
def get_skills() -> List[str]
```

**Возвращает:**
- `List[str]`: Копия списка навыков

**Пример:**
```python
about = About()
skills = about.get_skills()
print(skills)  # ['Python', 'JavaScript', 'Git', ...]
```

##### add_skill()

Добавить новый навык.

```python
def add_skill(skill: str) -> None
```

**Параметры:**
- `skill` (str): Новый навык для добавления

**Примечание:** Дубликаты не добавляются.

**Пример:**
```python
about = About()
about.add_skill("Machine Learning")
about.add_skill("Docker")
```

##### get_projects()

Получить копию списка проектов.

```python
def get_projects() -> List[str]
```

**Возвращает:**
- `List[str]`: Копия списка проектов

##### add_project()

Добавить новый проект.

```python
def add_project(project: str) -> None
```

**Параметры:**
- `project` (str): Новый проект для добавления

**Примечание:** Дубликаты не добавляются.

##### print_info()

Вывести информацию о разработчике в консоль.

```python
def print_info() -> None
```

**Пример вывода:**
```
👨‍💻 Разработчик: kogriv
🔗 GitHub: https://github.com/kogriv
📅 Создано: 2025-01-24 12:30:45

🛠️ Навыки:
  • Python
  • JavaScript
  • Git
  • Docker
  • SQL
  • MQL5

📂 Проекты:
  • kgrv - Python пакет для экспериментов
  • Различные скрипты автоматизации
  • Торговые роботы на MQL5
```

#### Специальные методы

##### \_\_str\_\_()

Строковое представление объекта.

```python
about = About("John")
print(str(about))
# "About(John): 6 навыков, 3 проектов"
```

##### \_\_repr\_\_()

Представление для отладки.

```python
about = About("John")
print(repr(about))
# "About(name='John', skills=6, projects=3)"
```

## Константы модуля

- `__version__`: Версия пакета
- `__author__`: Автор пакета
- `__email__`: Email автора
- `__description__`: Описание пакета

## Примеры использования

### Базовое использование

```python
from kgrv import About

# Создание объекта для себя
about = About("Иван")

# Добавление навыков
about.add_skill("Python")
about.add_skill("Data Science")

# Добавление проектов
about.add_project("Анализ данных продаж")
about.add_project("ML модель прогнозирования")

# Вывод информации
about.print_info()
```

### Работа с данными

```python
# Получение всех данных
info = about.get_info()

# Работа с навыками
skills = about.get_skills()
print(f"Всего навыков: {len(skills)}")

# Проверка наличия навыка
if "Python" in skills:
    print("Python - есть!")

# Получение проектов
projects = about.get_projects()
for i, project in enumerate(projects, 1):
    print(f"{i}. {project}")
```

### Интеграция с JSON

```python
import json

about = About("Developer")
info = about.get_info()

# Сохранение в JSON файл
with open("profile.json", "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=2)

# Чтение из JSON
with open("profile.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    print(data["name"])
```
