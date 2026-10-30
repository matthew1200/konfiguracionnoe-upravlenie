"""Проверка VFS и трёх файловых структур."""

import unittest
from pathlib import Path

from src.vfs import VFS, VFSError

DATA = Path(__file__).resolve().parents[1] / "data"


class VFSTests(unittest.TestCase):
    """Проверки загрузки и навигации виртуального дерева."""

    def test_minimal_vfs(self):
        """Минимальный каталог можно загрузить."""
        self.assertEqual(VFS(DATA / "minimal.json").list_dir("/"), [])

    def test_simple_vfs(self):
        """Несколько файлов доступны для чтения."""
        fs = VFS(DATA / "simple.json")
        self.assertIn("hello.txt", fs.list_dir("/"))

    def test_nested_directories(self):
        """Вложенность не менее трёх уровней поддерживается."""
        fs = VFS(DATA / "nested.json")
        value = fs.read_file("/docs/notes/archive/report.txt")
        self.assertIn(b"Report 2026", value)

    def test_binary(self):
        """Двоичный файл восстанавливается из base64."""
        fs = VFS(DATA / "nested.json")
        self.assertEqual(fs.read_file("/pictures/logo.bin"), b"\0\1\x7f\xff")

    def test_missing_file(self):
        """Отсутствующий файл вызывает ошибку."""
        fs = VFS(DATA / "nested.json")
        with self.assertRaises(VFSError):
            fs.node("/not-found")

    def test_missing_json(self):
        """Ошибка открытия JSON не замалчивается."""
        with self.assertRaises(VFSError):
            VFS(DATA / "missing.json")


if __name__ == "__main__":
    unittest.main()
