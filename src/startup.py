"""Чтение сценариев эмулятора с поддержкой комментариев #."""

from pathlib import Path

from .shell import ShellError


def read_commands(filename):
    """Получить непустые строки сценария вместе с номерами строк."""
    try:
        text = Path(filename).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise ShellError(f"Не удалось прочитать скрипт {filename}: {exc}") from exc
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        yield number, stripped


def run_script(app, filename):
    """Выполнить скрипт, показывая каждую команду и ошибки."""
    app.write(f"Стартовый скрипт: {filename}\n")
    try:
        for number, line in read_commands(filename):
            if not app.run_line(line):
                app.write(f"Ошибка в скрипте, строка {number}.\n")
    except ShellError as exc:
        app.write(f"Ошибка стартового скрипта: {exc}\n")
