"""Графический терминал на Tkinter."""

import getpass
import socket
import tkinter as tk
from tkinter import scrolledtext

from .shell import ShellError


class TerminalApp:
    """Окно с историей вывода и отдельным полем ввода."""

    def __init__(self, root, shell):
        self.root = root
        self.shell = shell
        name = getpass.getuser()
        hostname = socket.gethostname()
        self.root.title(f"Эмулятор - [{name}@{hostname}]")
        self.root.geometry("860x510")
        self.root.minsize(520, 320)
        self.root.configure(bg="#20252c")
        self.output = scrolledtext.ScrolledText(
            root, bg="#15191f", fg="#e2e8f0", insertbackground="#ffffff",
            font=("Consolas", 11), state="disabled", wrap="word",
            relief="flat", padx=12, pady=12,
        )
        self.output.pack(fill="both", expand=True, padx=12, pady=(12, 8))
        bottom = tk.Frame(root, bg="#20252c")
        bottom.pack(fill="x", padx=12, pady=(0, 12))
        self.prompt_label = tk.Label(
            bottom, text="", fg="#7dd3fc", bg="#20252c",
            font=("Consolas", 11),
        )
        self.prompt_label.pack(side="left")
        self.input = tk.Entry(
            bottom, bg="#303741", fg="#f8fafc", insertbackground="#fff",
            font=("Consolas", 11), relief="flat",
        )
        self.input.pack(side="left", expand=True, fill="x", padx=(8, 0), ipady=6)
        self.input.bind("<Return>", self.on_enter)
        self.update_prompt()
        self.write("Учебный UNIX-эмулятор (вариант 20).\n")
        self.input.focus_set()

    def update_prompt(self):
        """Обновить видимое приглашение к вводу."""
        self.prompt_label.config(text=f"{self.shell.name}:{self.shell.cwd}$")

    def write(self, text):
        """Вывести текст в терминал, сохраняя историю."""
        if not text:
            return
        self.output.config(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.config(state="disabled")

    def run_line(self, line):
        """Отобразить ввод и результат команды."""
        self.write(f"{self.shell.name}:{self.shell.cwd}$ {line}\n")
        try:
            result = self.shell.execute(line)
        except ShellError as exc:
            self.write(f"Ошибка: {exc}\n")
            return False
        if result.clear:
            self.output.config(state="normal")
            self.output.delete("1.0", "end")
            self.output.config(state="disabled")
        if result.output:
            self.write(result.output.rstrip("\n") + "\n")
        self.update_prompt()
        if result.exit:
            self.root.after_idle(self.root.destroy)
        return True

    def on_enter(self, _event):
        """Принять строку, когда пользователь нажал Enter."""
        line = self.input.get()
        self.input.delete(0, "end")
        self.run_line(line)
