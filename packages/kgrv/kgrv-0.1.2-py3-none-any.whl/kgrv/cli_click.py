#!/usr/bin/env python3
"""
CLI интерфейс для пакета kgrv с использованием click.

Предоставляет красивый и удобный командный интерфейс для взаимодействия с пакетом kgrv.
"""

import click
import json
from .about import About


@click.group()
@click.version_option(version="0.1.2", prog_name="kgrv")
def cli():
    """
    KGRV - Python пакет для экспериментов и обучения.
    
    Утилита для работы с информацией о разработчике.
    """
    pass


@cli.command()
@click.option('--name', default='kogriv', help='Имя разработчика')
@click.option('--format', 'output_format', 
              type=click.Choice(['text', 'json', 'colored']), 
              default='colored',
              help='Формат вывода')
@click.option('--add-skill', multiple=True, help='Добавить навык')
@click.option('--add-project', multiple=True, help='Добавить проект')
def info(name, output_format, add_skill, add_project):
    """Показать информацию о разработчике."""
    about = About(name)
    
    # Добавляем дополнительные навыки и проекты
    for skill in add_skill:
        about.add_skill(skill)
    
    for project in add_project:
        about.add_project(project)
    
    if output_format == 'json':
        click.echo(json.dumps(about.get_info(), ensure_ascii=False, indent=2))
    elif output_format == 'colored':
        about.print_info_colored()
    else:
        about.print_info()


@cli.command()
@click.option('--name', default='kogriv', help='Имя разработчика')
@click.option('--format', 'output_format', 
              type=click.Choice(['text', 'json']), 
              default='text',
              help='Формат вывода')
def skills(name, output_format):
    """Показать навыки разработчика."""
    about = About(name)
    skills_list = about.get_skills()
    
    if output_format == 'json':
        click.echo(json.dumps({"skills": skills_list}, ensure_ascii=False, indent=2))
    else:
        click.echo(f"🛠️ Навыки {name}:")
        for skill in skills_list:
            click.echo(f"  • {skill}")


@cli.command()
@click.option('--name', default='kogriv', help='Имя разработчика')
@click.option('--format', 'output_format', 
              type=click.Choice(['text', 'json']), 
              default='text',
              help='Формат вывода')
def projects(name, output_format):
    """Показать проекты разработчика."""
    about = About(name)
    projects_list = about.get_projects()
    
    if output_format == 'json':
        click.echo(json.dumps({"projects": projects_list}, ensure_ascii=False, indent=2))
    else:
        click.echo(f"📂 Проекты {name}:")
        for project in projects_list:
            click.echo(f"  • {project}")


@cli.command()
@click.option('--name', default='kogriv', help='Имя разработчика')
@click.option('--format', 'output_format', 
              type=click.Choice(['text', 'json']), 
              default='text',
              help='Формат вывода')
def validate(name, output_format):
    """Проверить валидность профиля разработчика."""
    about = About(name)
    validation = about.get_profile_validation()
    
    if output_format == 'json':
        click.echo(json.dumps(validation, ensure_ascii=False, indent=2))
    else:
        about.print_validation_info()


@cli.command()
@click.option('--name', default='kogriv', help='Имя разработчика')
@click.option('--skill', prompt='Введите навык', help='Навык для добавления')
def add_skill(name, skill):
    """Добавить навык разработчику."""
    about = About(name)
    about.add_skill(skill)
    click.echo(f"✅ Навык '{skill}' добавлен к профилю {name}")


@cli.command()
@click.option('--name', default='kogriv', help='Имя разработчика')
@click.option('--project', prompt='Введите проект', help='Проект для добавления')
def add_project(name, project):
    """Добавить проект разработчику."""
    about = About(name)
    about.add_project(project)
    click.echo(f"✅ Проект '{project}' добавлен к профилю {name}")


@cli.command()
@click.option('--name', default='kogriv', help='Имя разработчика')
def demo(name):
    """Запустить интерактивную демонстрацию."""
    about = About(name)
    
    click.echo(f"🎮 Интерактивная демонстрация для {name}")
    click.echo("=" * 50)
    
    # Показываем базовую информацию
    about.print_info_colored()
    
    # Показываем валидацию
    click.echo("\n" + "=" * 50)
    about.print_validation_info()
    
    # Показываем JSON
    click.echo("\n" + "=" * 50)
    click.echo("📊 JSON представление:")
    click.echo(json.dumps(about.get_info(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    cli()
