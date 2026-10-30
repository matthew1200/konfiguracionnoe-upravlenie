"""Этап 1: простой REPL с командами-заглушками."""

import os
import re
import shlex
from dataclasses import dataclass
from pathlib import Path


class ShellError(Exception):
    """Ошибка разбора либо исполнения команды."""


@dataclass
class Result:
    """Результат выполнения команды для графического интерфейса."""

    output: str = ""
    clear: bool = False
    exit: bool = False


def parse_command(line, environ=None):
    """Разделить строку и раскрыть переменные реальной ОС."""
    values = dict(os.environ) if environ is None else dict(environ)
    values.setdefault("HOME", str(Path.home()))
    try:
        args = shlex.split(line, comments=True, posix=True)
    except ValueError as exc:
        raise ShellError(f"Ошибка синтаксиса: {exc}") from exc
    pattern = re.compile(r"\$(\w+|\{[A-Za-z_]\w*\})")

    def expand(argument):
        def replace(match):
            name = match.group(1).strip("{}")
            return values.get(name, "")

        return pattern.sub(replace, argument)

    return [expand(arg) for arg in args]


class Shell:
    """Эмулятор команд. На первом этапе команды являются заглушками."""

    def __init__(self, **_unused):
        self.name = "demo-vfs"
        self.cwd = "/"

    def execute(self, line):
        """Разобрать и выполнить пользовательскую строку."""
        args = parse_command(line)
        if not args:
            return Result()
        command, *arguments = args
        if command == "exit":
            if arguments:
                raise ShellError("exit: аргументы не допускаются")
            return Result(exit=True)
        if command in {"ls", "cd"}:
            if len(arguments) > 1:
                raise ShellError(f"{command}: слишком много аргументов")
            return Result(f"Заглушка {command}: аргументы = {arguments}")
        if command == "echo":
            return Result(" ".join(arguments))
        raise ShellError(f"Неизвестная команда: {command}")
