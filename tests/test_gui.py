"""Интеграционные проверки GUI (пропускаются без дисплея)."""

import os
import tkinter as tk
import unittest
from pathlib import Path

from src.gui import TerminalApp
from src.shell import Shell
from src.startup import run_script

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    os.name == "nt" or os.environ.get("DISPLAY"),
    "Для GUI-тестов нужен графический дисплей",
)
class GuiTests(unittest.TestCase):
    """Проверка окна и сценария в реальном Tkinter."""

    def setUp(self):
        """Создать независимый терминал для GUI-теста."""
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"Нет доступного GUI-дисплея: {exc}")
        self.root.withdraw()
        self.app = TerminalApp(self.root, Shell())

    def tearDown(self):
        """Закрыть окно, если оно ещё существует."""
        if self.root.winfo_exists():
            self.root.destroy()

    def test_title_and_script(self):
        """Заголовок и ошибки сценария видны на экране."""
        self.assertIn("Эмулятор - [", self.root.title())
        run_script(self.app, ROOT / "scripts/startup_errors.txt")
        content = self.app.output.get("1.0", "end")
        self.assertIn("Ошибка в скрипте", content)
        self.assertIn("ls", content)

    def test_exit(self):
        """exit устанавливает флаг закрытия приложения."""
        self.app.run_line("exit")
        self.assertTrue(self.app.closing)


if __name__ == "__main__":
    unittest.main()
