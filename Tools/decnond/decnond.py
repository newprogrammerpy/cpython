import builtins
import io
import re
import sys
import tokenize
from decimal import Decimal
from pathlib import Path


_DECIMAL_FLOAT = re.compile(
    r"(?:[0-9](?:_?[0-9])*\.(?:[0-9](?:_?[0-9])*)?"
    r"|\.[0-9](?:_?[0-9])*)"
    r"(?:[eE][+-]?[0-9](?:_?[0-9])*)?"
    r"|[0-9](?:_?[0-9])*[eE][+-]?[0-9](?:_?[0-9])*\Z"
)


def _decimal_print(*values, sep=" ", end="\n", file=None, flush=False):
    values = (
        format(value, "f") if isinstance(value, Decimal) else value
        for value in values
    )
    return builtins.print(*values, sep=sep, end=end, file=file, flush=flush)


def _replace_decimal_literals(source, helper_name):
    lines = source.splitlines(keepends=True)
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line))

    replacements = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.NUMBER and _DECIMAL_FLOAT.fullmatch(token.string):
            start = line_offsets[token.start[0] - 1] + token.start[1]
            end = line_offsets[token.end[0] - 1] + token.end[1]
            replacements.append((start, end, f"{helper_name}({token.string!r})"))

    for start, end, replacement in reversed(replacements):
        source = source[:start] + replacement + source[end:]
    return source


def _run(path, decimal_literals):
    script = Path(path).resolve()
    with tokenize.open(script) as source_file:
        source = source_file.read()

    namespace = {
        "__name__": "__main__",
        "__file__": str(script),
        "__package__": None,
    }
    if decimal_literals:
        helper_name = "__decnond_decimal__"
        while helper_name in source:
            helper_name += "_"
        source = _replace_decimal_literals(source, helper_name)
        namespace[helper_name] = Decimal
        namespace["print"] = _decimal_print

    code = compile(source, str(script), "exec", dont_inherit=True)

    original_argv = sys.argv
    saved_argv = original_argv[:]
    original_path = sys.path
    saved_path = original_path[:]
    sys.argv = [str(script)]
    sys.path.insert(0, str(script.parent))
    try:
        exec(code, namespace)
    finally:
        sys.argv = original_argv
        original_argv[:] = saved_argv
        sys.path = original_path
        original_path[:] = saved_path
    return namespace


def run(path):
    return _run(path, decimal_literals=True)


def killrun(path):
    return _run(path, decimal_literals=False)
