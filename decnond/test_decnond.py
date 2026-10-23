import os
import tempfile
import unittest
from decimal import Decimal, localcontext

import decnond


class DecnondTests(unittest.TestCase):
    def test_run_converts_decimal_literals_and_returns_globals(self):
        source = (
            "x = 0.0000000000000000001\n"
            "y = 0.1 + 0.2\n"
            "integer = 12\n"
            "hexadecimal = 0x1e\n"
            "imaginary = 2j\n"
            "text = '0.5'\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "script.py")
            with open(filename, "w", encoding="utf-8") as script:
                script.write(source)

            namespace = decnond.run(filename)

        self.assertEqual(namespace["x"], Decimal("0.0000000000000000001"))
        self.assertEqual(namespace["y"], Decimal("0.3"))
        self.assertIs(type(namespace["x"]), Decimal)
        self.assertIs(type(namespace["integer"]), int)
        self.assertIs(type(namespace["hexadecimal"]), int)
        self.assertIs(type(namespace["imaginary"]), complex)
        self.assertEqual(namespace["text"], "0.5")
        self.assertEqual(namespace["__name__"], "__main__")

    def test_run_supports_py_and_pyw_and_keeps_strings_untouched(self):
        for extension in (".py", ".pyw"):
            with self.subTest(extension=extension):
                with tempfile.TemporaryDirectory() as directory:
                    filename = os.path.join(directory, "script" + extension)
                    with open(filename, "w", encoding="utf-8") as script:
                        script.write(
                            "value = 0.1\n"
                            "text = '0.2'\n"
                            "formatted = f'{0.3}'\n"
                        )

                    namespace = decnond.run(filename)

                self.assertEqual(namespace["value"], Decimal("0.1"))
                self.assertEqual(namespace["text"], "0.2")
                self.assertEqual(namespace["formatted"], "0.3")

    def test_context_precision_applies_to_arithmetic_not_literals(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "script.py")
            with open(filename, "w", encoding="utf-8") as script:
                script.write("literal = 0.123456789\nresult = literal + 0.1\n")

            with localcontext() as context:
                context.prec = 3
                namespace = decnond.run(filename)

        self.assertEqual(namespace["literal"], Decimal("0.123456789"))
        self.assertEqual(namespace["result"], Decimal("0.223"))


if __name__ == "__main__":
    unittest.main()
