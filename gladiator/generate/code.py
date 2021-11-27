"""Generate code using templates."""

from pathlib import Path
import re
from sys import stdout
from typing import Iterable, Optional

from gladiator.prepare.enum import PreparedEnum
from gladiator.options import Options
from gladiator.generate.templates import (
    make_template_environment,
    render_template,
    TemplateFiles,
)


class _Writer:
    def __init__(self, path: Optional[Path]):
        self.path = path
        self.file = stdout

    def __enter__(self):
        if self.path:
            self.file = open(str(self.path), "w", encoding="utf-8")
        return self

    def __exit__(self, _t, _v, _tb):
        if self.path:
            self.file.close()

    def write(self, text: str):
        self.file.write(text)


_REMOVE_REPEATING_NEWLINES_PATTERN = re.compile("\n+", re.MULTILINE)
_REMOVE_LEADING_WHITESPACE_PATTERN = re.compile("^[\t ]+", re.MULTILINE)


def _compress(code: str):
    return re.sub(
        _REMOVE_REPEATING_NEWLINES_PATTERN,
        "\n",
        re.sub(_REMOVE_LEADING_WHITESPACE_PATTERN, "", code),
    )


def generate_code(options: Options, enums: Iterable[PreparedEnum]):
    with _Writer(options.output) as output:
        env = make_template_environment(options.template_overrides_dir, options)

        output.write(
            _compress(
                render_template(env, TemplateFiles.ENUM_COLLECTION.value, enums=enums)
            )
        )
