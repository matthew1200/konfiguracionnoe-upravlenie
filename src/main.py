"""Точка входа для запуска графического эмулятора."""

import tkinter as tk

from .gui import TerminalApp
from .shell import Shell


def main():
    """Открыть окно эмулятора."""
    root = tk.Tk()
    TerminalApp(root, Shell())
    root.mainloop()


if __name__ == "__main__":
    main()
