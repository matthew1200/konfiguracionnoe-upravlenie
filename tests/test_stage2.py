"""Проверки разбора конфигурации и загрузки скриптов."""

import tempfile
import unittest
from pathlib import Path

from src.main import parse_args
from src.shell import ShellError
from src.startup import read_commands


class ConfigTests(unittest.TestCase):
    """Тесты параметров запуска и комментариев."""

    def test_args(self):
        """Программа получает оба параметра командной строки."""
        args = parse_args(["--vfs", "a.json", "--script", "b.txt"])
        self.assertEqual((args.vfs, args.script), ("a.json", "b.txt"))

    def test_comments(self):
        """Пустые строки и строки # игнорируются."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "demo.txt"
            path.write_text("# comment\n\nls\n# ignore\ncd docs\n")
            self.assertEqual(
                list(read_commands(path)), [(3, "ls"), (5, "cd docs")],
            )

    def test_missing_script(self):
        """Потерянный сценарий даёт осмысленную ошибку."""
        with self.assertRaises(ShellError):
            list(read_commands("file_does_not_exist_1234.txt"))


if __name__ == "__main__":
    unittest.main()
