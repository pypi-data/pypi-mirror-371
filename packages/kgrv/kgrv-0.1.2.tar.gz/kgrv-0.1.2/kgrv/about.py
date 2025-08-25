"""
Модуль About для вывода информации о разработчике и проекте.

Этот модуль содержит класс About, который предоставляет
информацию о разработчике, его навыках и проектах.
"""

from typing import List, Dict, Any
import datetime
import requests
from colorama import init, Fore, Style

# Инициализация colorama для Windows
init()


class About:
    """
    Класс для вывода информации о разработчике.
    
    Attributes:
        name (str): Имя разработчика
        github (str): GitHub профиль
        skills (List[str]): Список навыков
        projects (List[str]): Список проектов
    """
    
    def __init__(self, name: str = "kogriv"):
        """
        Инициализация объекта About.
        
        Args:
            name (str): Имя разработчика, по умолчанию "kogriv"
        """
        self.name = name
        self.github = f"https://github.com/{name}"
        self.skills = [
            "Python",
            "JavaScript", 
            "Git",
            "Docker",
            "SQL",
            "MQL5"
        ]
        self.projects = [
            "kgrv - Python пакет для экспериментов",
            "Различные скрипты автоматизации",
            "Торговые роботы на MQL5"
        ]
        self.created_at = datetime.datetime.now()
    
    def get_info(self) -> Dict[str, Any]:
        """
        Получить полную информацию о разработчике.
        
        Returns:
            Dict[str, Any]: Словарь с информацией о разработчике
        """
        return {
            "name": self.name,
            "github": self.github,
            "skills": self.skills,
            "projects": self.projects,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_skills(self) -> List[str]:
        """
        Получить список навыков.
        
        Returns:
            List[str]: Список навыков разработчика
        """
        return self.skills.copy()
    
    def add_skill(self, skill: str) -> None:
        """
        Добавить новый навык.
        
        Args:
            skill (str): Новый навык для добавления
        """
        if skill not in self.skills:
            self.skills.append(skill)
    
    def get_projects(self) -> List[str]:
        """
        Получить список проектов.
        
        Returns:
            List[str]: Список проектов разработчика
        """
        return self.projects.copy()
    
    def add_project(self, project: str) -> None:
        """
        Добавить новый проект.
        
        Args:
            project (str): Новый проект для добавления
        """
        if project not in self.projects:
            self.projects.append(project)
    
    def print_info(self) -> None:
        """
        Вывести информацию о разработчике в консоль.
        """
        print(f"👨‍💻 Разработчик: {self.name}")
        print(f"🔗 GitHub: {self.github}")
        print(f"📅 Создано: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🛠️ Навыки:")
        for skill in self.skills:
            print(f"  • {skill}")
        
        print("\n📂 Проекты:")
        for project in self.projects:
            print(f"  • {project}")
    
    def __str__(self) -> str:
        """
        Строковое представление объекта.
        
        Returns:
            str: Строковое представление информации о разработчике
        """
        return f"About({self.name}): {len(self.skills)} навыков, {len(self.projects)} проектов"
    
    def __repr__(self) -> str:
        """
        Представление объекта для отладки.
        
        Returns:
            str: Представление объекта для отладки
        """
        return f"About(name='{self.name}', skills={len(self.skills)}, projects={len(self.projects)})"
    
    def print_info_colored(self) -> None:
        """
        Вывести информацию о разработчике в консоль с цветами.
        """
        print(f"{Fore.CYAN}👨‍💻 Разработчик: {Fore.WHITE}{self.name}")
        print(f"{Fore.BLUE}🔗 GitHub: {Fore.WHITE}{self.github}")
        print(f"{Fore.YELLOW}📅 Создано: {Fore.WHITE}{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n{Fore.GREEN}🛠️ Навыки:")
        for skill in self.skills:
            print(f"  {Fore.GREEN}• {Fore.WHITE}{skill}")
        
        print(f"\n{Fore.MAGENTA}📂 Проекты:")
        for project in self.projects:
            print(f"  {Fore.MAGENTA}• {Fore.WHITE}{project}")
    
    def validate_github(self) -> bool:
        """
        Проверка существования GitHub профиля.
        
        Returns:
            bool: True если профиль существует, False в противном случае
        """
        try:
            response = requests.get(self.github, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_profile_validation(self) -> Dict[str, Any]:
        """
        Получить информацию о валидации профиля.
        
        Returns:
            Dict[str, Any]: Словарь с информацией о валидации
        """
        github_exists = self.validate_github()
        profile_age_days = (datetime.datetime.now() - self.created_at).days
        
        return {
            "github_exists": github_exists,
            "profile_age_days": profile_age_days,
            "skills_count": len(self.skills),
            "projects_count": len(self.projects),
            "github_url": self.github
        }
    
    def print_validation_info(self) -> None:
        """
        Вывести информацию о валидации профиля с цветами.
        """
        validation = self.get_profile_validation()
        
        print(f"{Fore.CYAN}🔍 Валидация профиля {Fore.WHITE}{self.name}:")
        print(f"  {Fore.BLUE}GitHub профиль: {Fore.WHITE}{validation['github_url']}")
        
        if validation['github_exists']:
            print(f"  {Fore.GREEN}✅ GitHub профиль существует")
        else:
            print(f"  {Fore.RED}❌ GitHub профиль не найден")
        
        print(f"  {Fore.YELLOW}📊 Возраст профиля: {Fore.WHITE}{validation['profile_age_days']} дней")
        print(f"  {Fore.GREEN}🛠️ Навыков: {Fore.WHITE}{validation['skills_count']}")
        print(f"  {Fore.MAGENTA}📂 Проектов: {Fore.WHITE}{validation['projects_count']}")
