"""
Setup script для публикации пакета kgrv на PyPI.
"""

from setuptools import setup, find_packages
import os

# Читаем README для длинного описания
def read_readme():
    """Читает README.md файл."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "KGRV - Python пакет для экспериментов и обучения"

# Читаем версию из пакета
def get_version():
    """Получает версию из __init__.py"""
    version_file = os.path.join(os.path.dirname(__file__), 'kgrv', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return "0.1.0"

# Основные зависимости
install_requires = [
    "click>=8.0.0",
    "colorama>=0.4.0", 
    "requests>=2.25.0",
]

# Зависимости для разработки
dev_requires = [
    'pytest>=6.0.0',
    'pytest-cov>=2.10.0',
    'black>=21.0.0',
    'flake8>=3.8.0',
    'mypy>=0.910',
    'twine>=3.4.0',
    'build>=0.7.0',
]

# Зависимости для документации
doc_requires = [
    'mkdocs>=1.2.0',
    'mkdocs-material>=7.0.0',
    'mkdocstrings>=0.15.0',
]

setup(
    name="kgrv",
    version=get_version(),
    author="kogriv",
    author_email="kogriv@github.com",
    description="Python пакет для экспериментов и обучения",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/kogriv/kgrv",
    project_urls={
        "Bug Reports": "https://github.com/kogriv/kgrv/issues",
        "Source": "https://github.com/kogriv/kgrv",
        "Documentation": "https://github.com/kogriv/kgrv/tree/master/docs",
    },
    packages=find_packages(exclude=["tests*", "scripts*", "docs*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        "docs": doc_requires,
        "all": dev_requires + doc_requires,
    },
    include_package_data=True,
    zip_safe=False,
    keywords="python, package, tutorial, learning, example",
    entry_points={
        "console_scripts": [
            "kgrv=kgrv.cli_click:cli",
        ],
    },
)
