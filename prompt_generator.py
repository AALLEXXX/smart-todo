#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from pathlib import Path

# Список файлов относительно корня проекта
FILES = [
    "main.py",
    "pyproject.toml",
    "ui_uploader.py",
    "README.md",
    "Makefile",
    "db.py",
    os.path.join("app", "data", "init_db.py"),
    os.path.join("app", "styles", "base.qss"),
]


def get_project_tree() -> str:
    """
    Выполняет команду tree и возвращает её вывод,
    исключая каталоги/файлы .git, .DS_Store, .idea, .ruff_cache и __pycache__.
    """
    exclude = ".git|.DS_Store|.idea|.ruff_cache|__pycache__"
    try:
        output = subprocess.check_output(
            ["tree", "-a", "-I", exclude], stderr=subprocess.DEVNULL, universal_newlines=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Если tree не установлена или упала — обход вручную с фильтрацией
        all_paths = []
        for p in Path.cwd().rglob("*"):
            parts = set(p.parts)
            if parts & {".git", ".DS_Store", ".idea", ".ruff_cache", "__pycache__"}:
                continue
            all_paths.append(str(p.relative_to(Path.cwd())))
        output = "\n".join(sorted(all_paths))
    return output


def read_file_text(path: str) -> str:
    """Читает текст файла, возвращает сообщение, если файл не найден."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"<Файл {path} не найден>\n"


def build_prompt() -> str:
    """Собирает полный текст промпта."""
    intro = (
        "Привет, ChatGPT! Я разрабатываю приложение на PyQt6 с бэкендом SQLite. "
        "В файле README.md описано, как работает программа. Ты — опытный разработчик на PyQt6 и SQLite, "
        "цель — помогать мне с задачами в следующих запросах. Сейчас познакомься со структурой проекта и кодом.\n\n"
        "Стиль разрабтки:\n"
        "1. Сохранять текущую структуру папок и файлов.\n"
        "2. Если добавляешь переменные-настройки, то выносишь в единый файл config.py.\n"
        "3. Если добавляешь текстовые строки в интерфейсе, то на английском.\n"
        "4. В приложении две темы (dark/light) через base.qss, style_dark.qss и style_light.qss. "
        "Если нужно улучшить интерфейс то добавляй qss в соответствующие файлы\n"
        "5. При генерации UI-файлов (.ui) учитывать современный дизайн и адекватные размеры компонентов.\n"
        "6. Когда даешь ответы не указывай в ним '+' или '-' чтобы показывать что было убрано, а что добавлено. "
        "Показывай код до и после\n"
        "7. Не делай импорт в теле функций или методов, только вначале файла\n"
        "8. Все функции которые оперируют данными в бд напрямую нужно создавать в файле db.py\n\n"
        "Далее актуальная структура проекта:\n"
    )
    tree = get_project_tree()
    parts = [intro, "```", tree, "```"]

    for relpath in FILES:
        parts.append(f"\n---\n**Файл: {relpath}**\n```")
        parts.append(read_file_text(relpath))
        parts.append("```")

    return "\n".join(parts)


def save_prompt_to_file(output_path: str = "prompt.txt") -> None:
    text = build_prompt()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Промпт сохранён в {output_path}")


if __name__ == "__main__":
    save_prompt_to_file()
