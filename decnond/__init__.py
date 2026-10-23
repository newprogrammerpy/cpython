"""Run Python scripts with exact Decimal values for decimal-point literals."""

import builtins
import io
import os
import sys
import tokenize
from decimal import Decimal
from token import NUMBER

__all__ = ["run"]


def _is_decimal_literal(text):
    if text.lower().startswith(("0x", "0o", "0b")):
        return False
    return any(char in text for char in ".eE") and not text.lower().endswith("j")


def _transform(source):
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    converted = []
    for item in tokens:
        if item.type == NUMBER and _is_decimal_literal(item.string):
            item = item._replace(
                string=f"__import__('decimal').Decimal({item.string!r})"
            )
        converted.append(item)
    return tokenize.untokenize(converted)


def run(filename, *, run_name="__main__"):
    """Execute *filename*, converting decimal literals to ``Decimal`` first.

    Returns the executed script's global namespace. Exceptions, including
    ``SystemExit``, propagate as they do when running a Python script.
    """
    path = os.path.abspath(os.fspath(filename))
    with tokenize.open(path) as source_file:
        source = source_file.read()

    code = compile(_transform(source), path, "exec")
    namespace = {
        "__name__": run_name,
        "__file__": path,
        "__package__": None,
        "__cached__": None,
        "__builtins__": builtins.__dict__,
    }

    old_argv = sys.argv
    old_path = sys.path
    sys.argv = [path, *old_argv[1:]]
    sys.path = [os.path.dirname(path), *old_path]
    try:
        exec(code, namespace)
    finally:
        sys.path = old_path
        sys.argv = old_argv
    return namespace
