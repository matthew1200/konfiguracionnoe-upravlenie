"""Проверки cp и неизменности JSON на физическом диске."""

import unittest
from pathlib import Path

from src.shell import Shell, ShellError

DATA = Path(__file__).resolve().parents[1] / "data" / "nested.json"


class CopyTests(unittest.TestCase):
    """Копирование внутри VFS без изменений исходного файла."""

    def setUp(self):
        """Создать независимый экземпляр оболочки для теста."""
        self.shell = Shell(DATA)

    def test_copy_file(self):
        """Копия файла имеет исходные байты."""
        self.shell.execute("cp hello.txt duplicated.txt")
        result = self.shell.vfs.read_file("/duplicated.txt")
        self.assertEqual(result, b"Welcome to variant 20!\n")

    def test_copy_to_existing_folder(self):
        """Назначением может быть существующий каталог."""
        self.shell.execute("cp hello.txt docs")
        self.assertIn("hello.txt", self.shell.vfs.list_dir("docs"))

    def test_recursive_copy(self):
        """С флагом -r целиком копируется дерево папок."""
        self.shell.execute("cp -r docs copy-of-docs")
        value = self.shell.vfs.read_file(
            "/copy-of-docs/notes/archive/report.txt",
        )
        self.assertIn(b"Report", value)

    def test_copy_directory_without_recursive(self):
        """Копирование папки без -r запрещается."""
        with self.assertRaises(ShellError):
            self.shell.execute("cp docs copy-docs")

    def test_copy_into_itself(self):
        """Нельзя скопировать папку в её дочернюю папку."""
        with self.assertRaises(ShellError):
            self.shell.execute("cp -r docs docs/notes")

    def test_copy_over_existing_file(self):
        """Копирование поверх файла заменяет его в памяти."""
        self.shell.execute("cp hello.txt docs/notes/lines.txt")
        value = self.shell.vfs.read_file("docs/notes/lines.txt")
        self.assertEqual(value, b"Welcome to variant 20!\n")

    def test_no_disk_modifications(self):
        """JSON байт-в-байт остаётся исходным после копирования."""
        before = DATA.read_bytes()
        self.shell.execute("cp hello.txt temp.txt")
        self.shell.execute("cp -r docs docs-copy")
        self.assertEqual(DATA.read_bytes(), before)
        self.assertFalse((DATA.parent / "temp.txt").exists())

    def test_cp_missing_arguments(self):
        """Сообщение о неверном числе аргументов."""
        with self.assertRaises(ShellError):
            self.shell.execute("cp hello.txt")

    def test_cp_invalid_destination(self):
        """Нельзя копировать в несуществующий родительский каталог."""
        with self.assertRaises(ShellError):
            self.shell.execute("cp hello.txt /none/new.txt")


if __name__ == "__main__":
    unittest.main()
