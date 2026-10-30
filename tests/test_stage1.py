"""Проверки разбора строки и обработки ошибок."""

import unittest

from src.shell import Shell, ShellError, parse_command


class ParserTests(unittest.TestCase):
    """Проверки парсера и команд первого этапа."""

    def test_environment_variable(self):
        """Переменная окружения подставляется в аргумент."""
        args = parse_command('echo "Hello $NAME"', {"NAME": "World"})
        self.assertEqual(args, ["echo", "Hello World"])

    def test_braced_environment_variable(self):
        """Поддерживается синтаксис ${NAME}."""
        args = parse_command('echo ${TEST}', {"TEST": "value"})
        self.assertEqual(args, ["echo", "value"])

    def test_broken_quote(self):
        """Незакрытая кавычка вызывает понятную ошибку."""
        with self.assertRaises(ShellError):
            parse_command('ls "wrong')

    def test_unknown_command(self):
        """Неизвестная команда отклоняется."""
        with self.assertRaises(ShellError):
            Shell().execute("unknown")

    def test_exit(self):
        """Команда exit закрывает эмулятор."""
        self.assertTrue(Shell().execute("exit").exit)


if __name__ == "__main__":
    unittest.main()
