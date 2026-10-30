"""Проверки ls, cd, tac, date и clear."""

import re
import unittest

from src.shell import Shell, ShellError


class CommandTests(unittest.TestCase):
    """Основные команды варианта 20."""

    def setUp(self):
        """Инициализировать чистую VFS для каждого теста."""
        self.shell = Shell()

    def test_ls(self):
        """ls показывает файлы и каталоги в корне."""
        result = self.shell.execute("ls")
        self.assertIn("docs/", result.output)
        self.assertIn("hello.txt", result.output)

    def test_cd_absolute_relative_and_parent(self):
        """cd поддерживает абсолютные, относительные пути и '..'."""
        self.shell.execute("cd /docs")
        self.shell.execute("cd notes")
        self.assertEqual(self.shell.cwd, "/docs/notes")
        self.shell.execute("cd ..")
        self.assertEqual(self.shell.cwd, "/docs")

    def test_cd_missing(self):
        """Нельзя перейти в отсутствующий каталог."""
        with self.assertRaises(ShellError):
            self.shell.execute("cd missing")

    def test_cd_file(self):
        """Нельзя использовать файл как каталог."""
        with self.assertRaises(ShellError):
            self.shell.execute("cd hello.txt")

    def test_tac(self):
        """tac переворачивает порядок строк файла."""
        result = self.shell.execute("tac docs/notes/lines.txt")
        self.assertEqual(result.output.splitlines(), [
            "third", "second", "first",
        ])

    def test_tac_binary_error(self):
        """tac отказывает при некорректном UTF-8."""
        with self.assertRaises(ShellError):
            self.shell.execute("tac pictures/logo.bin")

    def test_date(self):
        """date принимает формат +%Y-%m-%d."""
        result = self.shell.execute("date +%Y-%m-%d")
        self.assertRegex(result.output, r"^\d{4}-\d{2}-\d{2}$")

    def test_date_wrong_args(self):
        """Дата с несуществующей опцией вызывает ошибку."""
        with self.assertRaises(ShellError):
            self.shell.execute("date --nope")

    def test_clear(self):
        """clear даёт GUI сигнал очистить терминал."""
        self.assertTrue(self.shell.execute("clear").clear)

    def test_clear_wrong_args(self):
        """У clear нет аргументов."""
        with self.assertRaises(ShellError):
            self.shell.execute("clear invalid")


if __name__ == "__main__":
    unittest.main()
