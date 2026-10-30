"""Интерпретатор ограниченного набора UNIX-команд для учебной VFS."""

import os
import re
import shlex
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .vfs import VFS, VFSError


class ShellError(Exception):
    """Ошибка разбора либо исполнения команды."""


@dataclass
class Result:
    """Результат выполнения для GUI-терминала."""

    output: str = ""
    clear: bool = False
    exit: bool = False


def parse_command(line, environ=None):
    """Разделить строку с кавычками и раскрыть переменные окружения."""
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
    """Команды работают только с загруженным в память деревом VFS."""

    def __init__(self, vfs_path=None):
        default = Path(__file__).resolve().parent.parent / "data/nested.json"
        try:
            self.vfs = VFS(vfs_path or default)
        except VFSError as exc:
            raise ShellError(str(exc)) from exc
        self.name = self.vfs.name
        self.cwd = "/"

    def execute(self, line):
        """Выполнить команду и вернуть вывод и управляющие флаги."""
        args = parse_command(line)
        if not args:
            return Result()
        name, *arguments = args
        handlers = {
            "ls": self.do_ls, "cd": self.do_cd,
            "tac": self.do_tac, "date": self.do_date,
            "clear": self.do_clear, "echo": self.do_echo,
            "exit": self.do_exit, "cp": self.do_cp,
        }
        if name not in handlers:
            raise ShellError(f"Неизвестная команда: {name}")
        try:
            return handlers[name](arguments)
        except VFSError as exc:
            raise ShellError(str(exc)) from exc

    def do_ls(self, args):
        """Показать содержимое каталога или имя файла."""
        if len(args) > 1:
            raise ShellError("ls: ожидается не более одного пути")
        path = args[0] if args else "."
        return Result("\n".join(self.vfs.list_dir(path, self.cwd)))

    def do_cd(self, args):
        """Перейти в указанный каталог (без аргумента — в корень)."""
        if len(args) > 1:
            raise ShellError("cd: ожидается не более одного пути")
        path = args[0] if args else "/"
        self.cwd = self.vfs.change_dir(path, self.cwd)
        return Result()

    def do_tac(self, args):
        """Вывести строки файла в обратном порядке."""
        if not args:
            raise ShellError("tac: укажите файл")
        chunks = []
        for path in args:
            raw = self.vfs.read_file(path, self.cwd)
            try:
                lines = raw.decode("utf-8").splitlines()
            except UnicodeDecodeError as exc:
                raise ShellError(
                    f"tac: файл {path} не текстовый UTF-8",
                ) from exc
            chunks.extend(reversed(lines))
        return Result("\n".join(chunks))

    def do_date(self, args):
        """Показать локальную дату; поддержать формат +FORMAT."""
        if len(args) > 1 or (args and not args[0].startswith("+")):
            raise ShellError("date: допустим необязательный аргумент +FORMAT")
        now = datetime.now().astimezone()
        fmt = args[0][1:] if args else "%Y-%m-%d %H:%M:%S %Z"
        try:
            return Result(now.strftime(fmt))
        except ValueError as exc:
            raise ShellError(f"date: неверный формат: {exc}") from exc

    def do_clear(self, args):
        """Очистить экран GUI без изменения VFS."""
        if args:
            raise ShellError("clear: аргументы не допускаются")
        return Result(clear=True)

    def do_echo(self, args):
        """Дополнительная команда: показать разбор переменных окружения."""
        return Result(" ".join(args))

    def do_exit(self, args):
        """Закрыть приложение."""
        if args:
            raise ShellError("exit: аргументы не допускаются")
        return Result(exit=True)

    def do_cp(self, args):
        """Копировать файл; для каталогов требуется флаг -r."""
        recursive = False
        if args and args[0] == "-r":
            recursive = True
            args = args[1:]
        if len(args) != 2:
            raise ShellError("cp: формат cp [-r] ИСТОЧНИК НАЗНАЧЕНИЕ")
        self.vfs.copy(args[0], args[1], self.cwd, recursive=recursive)
        return Result()
