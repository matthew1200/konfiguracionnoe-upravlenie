"""Виртуальная файловая система из JSON, целиком в оперативной памяти."""

import base64
import binascii
import copy
import json
import posixpath
from pathlib import Path


class VFSError(Exception):
    """Ошибка чтения или обращения к виртуальной файловой системе."""


def validate_node(node):
    """Проверить структуру папок и двоичные данные файла."""
    if not isinstance(node, dict):
        raise VFSError("Узел VFS должен быть объектом JSON")
    kind = node.get("type")
    if kind == "dir":
        children = node.get("children")
        if not isinstance(children, dict):
            raise VFSError("У папки должно быть поле children (объект)")
        for name, child in children.items():
            if (not isinstance(name, str) or not name or
                    name in {".", ".."} or "/" in name or "\\" in name):
                raise VFSError(f"Недопустимое имя элемента: {name!r}")
            validate_node(child)
        return
    if kind == "file":
        raw = node.get("data")
        if not isinstance(raw, str):
            raise VFSError("У файла должно быть поле data (base64)")
        try:
            base64.b64decode(raw, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise VFSError("Неправильные base64-данные файла") from exc
        return
    raise VFSError("Поле type должно быть 'dir' либо 'file'")


class VFS:
    """Загруженный JSON не меняется на диске; узлы изменяются в памяти."""

    def __init__(self, source):
        self.source = Path(source)
        try:
            content = self.source.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            raise VFSError(f"Невозможно загрузить VFS: {exc}") from exc
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise VFSError(f"Неверный JSON VFS: {exc}") from exc
        if not isinstance(data, dict):
            raise VFSError("Корневой JSON должен быть объектом")
        if not isinstance(data.get("name"), str) or not data["name"]:
            raise VFSError("Поле name VFS должно быть непустой строкой")
        validate_node(data.get("root"))
        if data["root"]["type"] != "dir":
            raise VFSError("Корень VFS должен быть каталогом")
        self.name = data["name"]
        self.root = data["root"]

    @staticmethod
    def absolute(path, cwd="/"):
        """Преобразовать относительный UNIX-путь к абсолютному."""
        if not path:
            path = "."
        if path.startswith("/"):
            return posixpath.normpath(path)
        return posixpath.normpath(posixpath.join(cwd, path))

    def node(self, path=".", cwd="/"):
        """Найти файл или каталог по его виртуальному пути."""
        address = self.absolute(path, cwd)
        item = self.root
        for name in address.strip("/").split("/") if address != "/" else []:
            if item["type"] != "dir":
                raise VFSError(f"Не каталог: {address}")
            if name not in item["children"]:
                raise VFSError(f"Файл или каталог не найден: {address}")
            item = item["children"][name]
        return item

    def list_dir(self, path=".", cwd="/"):
        """Получить список элементов каталога или имя файла."""
        item = self.node(path, cwd)
        if item["type"] == "file":
            return [posixpath.basename(self.absolute(path, cwd))]
        return [
            name + ("/" if child["type"] == "dir" else "")
            for name, child in sorted(item["children"].items())
        ]

    def change_dir(self, path, cwd="/"):
        """Проверить каталог и вернуть новый путь."""
        address = self.absolute(path, cwd)
        if self.node(address)["type"] != "dir":
            raise VFSError(f"Не каталог: {address}")
        return address

    def read_file(self, path, cwd="/"):
        """Получить байты файла из JSON-структуры в памяти."""
        item = self.node(path, cwd)
        if item["type"] != "file":
            raise VFSError(f"Это каталог, а не файл: {path}")
        return base64.b64decode(item["data"], validate=True)

    def copy(self, source, target, cwd="/", recursive=False):
        """Скопировать файл или папку без записи исходного JSON на диск."""
        src_addr = self.absolute(source, cwd)
        dest_addr = self.absolute(target, cwd)
        if src_addr == "/":
            raise VFSError("Нельзя копировать корневой каталог VFS")
        source_node = self.node(src_addr)
        if source_node["type"] == "dir" and not recursive:
            raise VFSError("Для копирования каталога используйте cp -r")
        try:
            destination_node = self.node(dest_addr)
        except VFSError:
            destination_node = None
        if destination_node and destination_node["type"] == "dir":
            dest_addr = posixpath.join(
                dest_addr, posixpath.basename(src_addr),
            )
        if dest_addr == src_addr:
            raise VFSError("Нельзя скопировать файл в самого себя")
        if (source_node["type"] == "dir" and
                dest_addr.startswith(src_addr + "/")):
            raise VFSError("Нельзя копировать каталог внутрь самого себя")
        parent_path = posixpath.dirname(dest_addr)
        parent_node = self.node(parent_path)
        if parent_node["type"] != "dir":
            raise VFSError(f"Каталог назначения отсутствует: {parent_path}")
        name = posixpath.basename(dest_addr)
        previous = parent_node["children"].get(name)
        if previous is not None and (
                previous["type"] == "dir" or source_node["type"] == "dir"
        ):
            raise VFSError(f"Место назначения уже существует: {dest_addr}")
        parent_node["children"][name] = copy.deepcopy(source_node)
        return dest_addr
