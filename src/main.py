"""Запуск GUI с параметрами VFS и стартового сценария."""

import argparse
import tkinter as tk

from .gui import TerminalApp
from .shell import Shell
from .startup import run_script


def parse_args(argv=None):
    """Прочитать настройки командной строки."""
    parser = argparse.ArgumentParser(description="GUI UNIX-эмулятор, вариант 20")
    parser.add_argument("--vfs", help="Путь к файлу виртуальной ФС (JSON)")
    parser.add_argument("--script", help="Путь к стартовому скрипту")
    return parser.parse_args(argv)


def main(argv=None):
    """Открыть GUI и при наличии выполнить стартовый скрипт."""
    args = parse_args(argv)
    root = tk.Tk()
    app = TerminalApp(root, Shell())
    app.write(f"Конфигурация: VFS={args.vfs}; script={args.script}\n")
    if args.script:
        root.after(0, lambda: run_script(app, args.script))
    root.mainloop()


if __name__ == "__main__":
    main()
