import contextlib
import decimal
import io
import sys
import tempfile
import unittest
from pathlib import Path

import decnond


class RunTests(unittest.TestCase):
    def run_script(self, source):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name, "script.py")
        path.write_text(source, encoding="utf-8")
        return path, decnond.run(path)

    def test_decimal_literals_and_other_numbers(self):
        _, namespace = self.run_script(
            "from decimal import Decimal\n"
            "values = (0.1, 1e3, .25, 1_234.50_0e-2_0)\n"
            "integer = 10\n"
            "imaginary = 1.5j\n"
            "text = '0.1'\n"
            "# 0.2\n"
        )
        self.assertEqual(namespace["values"][:3], (
            decimal.Decimal("0.1"),
            decimal.Decimal("1e3"),
            decimal.Decimal(".25"),
        ))
        self.assertEqual(namespace["values"][3], decimal.Decimal("1234.500e-20"))
        self.assertEqual(namespace["integer"], 10)
        self.assertEqual(namespace["imaginary"], 1.5j)
        self.assertEqual(namespace["text"], "0.1")

    def test_script_semantics_and_state_restoration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "script.py")
            path.write_text(
                "import sys\n"
                "name = __name__\n"
                "filename = __file__\n"
                "argument = sys.argv[0]\n"
                "path_entry = sys.path[0]\n",
                encoding="utf-8",
            )
            old_argv = sys.argv
            old_path = sys.path
            saved_argv = old_argv[:]
            saved_path = old_path[:]

            namespace = decnond.run(path)

            self.assertEqual(namespace["name"], "__main__")
            self.assertEqual(namespace["filename"], str(path.resolve()))
            self.assertEqual(namespace["argument"], str(path.resolve()))
            self.assertEqual(namespace["path_entry"], directory)
            self.assertIs(sys.argv, old_argv)
            self.assertIs(sys.path, old_path)
            self.assertEqual(sys.argv, saved_argv)
            self.assertEqual(sys.path, saved_path)

    def test_state_is_restored_after_script_error(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name, "script.py")
        path.write_text("raise RuntimeError('script failed')\n", encoding="utf-8")
        original_argv = sys.argv
        original_path = sys.path
        saved_argv = original_argv[:]
        saved_path = original_path[:]

        with self.assertRaisesRegex(RuntimeError, "script failed"):
            decnond.run(path)

        self.assertIs(sys.argv, original_argv)
        self.assertIs(sys.path, original_path)
        self.assertEqual(sys.argv, saved_argv)
        self.assertEqual(sys.path, saved_path)

    def test_decimal_literals_in_expressions(self):
        _, namespace = self.run_script("total = 0.1 + 0.2\n")
        self.assertEqual(namespace["total"], decimal.Decimal("0.3"))

    def test_print_formats_decimal_in_fixed_point_and_preserves_arguments(self):
        source = (
            "print(1e-101, 'value', 0.1, sep='|', end='!')\n"
            "output = __import__('io').StringIO()\n"
            "print(1e-101, file=output, flush=True)\n"
        )
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name, "script.py")
        path.write_text(source, encoding="utf-8")
        expected_decimal = "0." + "0" * 100 + "1"
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            namespace = decnond.run(path)

        self.assertEqual(stdout.getvalue(), f"{expected_decimal}|value|0.1!")
        self.assertEqual(namespace["output"].getvalue(), expected_decimal + "\n")

    def test_decimal_helper_does_not_clash_with_script_globals(self):
        _, namespace = self.run_script(
            "__decnond_decimal__ = str\n"
            "value = 0.1\n"
        )
        self.assertIs(namespace["__decnond_decimal__"], str)
        self.assertEqual(namespace["value"], decimal.Decimal("0.1"))

    def test_killrun_uses_normal_float_literals_without_changing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "script.py")
            source = "value = 0.1\n"
            path.write_text(source, encoding="utf-8")

            decimal_namespace = decnond.run(path)
            float_namespace = decnond.killrun(path)

            self.assertEqual(decimal_namespace["value"], decimal.Decimal("0.1"))
            self.assertIsInstance(float_namespace["value"], float)
            self.assertNotEqual(float_namespace["value"], decimal.Decimal("0.1"))
            self.assertEqual(path.read_text(encoding="utf-8"), source)


if __name__ == "__main__":
    unittest.main()
